"""Regression coverage for the September 26 review findings (offline)."""
import ast
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import analyzer
import scanner
import static_context
import store
import run_batch
import agent_error_rates as aer


def save(base, path, body="review", mode="bug", usage=None):
    return store.save_review(str(base), str(path), str(path.relative_to(base)),
                             store.file_sha(path), mode, body,
                             usage if usage is not None else {"cost": 0, "complete": True}, "test")


def test_all_three_counts_only_standard_modes(tmp_path):
    path = str(tmp_path / "a.py")
    manifest = {path: {"modes": {mode: {"sha": "abc"} for mode in ("bug", "spec", "plan")}}}
    assert store.modes_done(manifest, path, "abc") == 1


def test_report_names_preserve_source_identity(tmp_path):
    paths = [tmp_path / "a" / "b.py", tmp_path / "a__b.py"]
    outputs = []
    for number, path in enumerate(paths):
        path.parent.mkdir(exist_ok=True)
        path.write_text("x = 1\n", encoding="utf-8")
        outputs.append(save(tmp_path, path, f"review {number}"))
    assert outputs[0] != outputs[1]
    assert "review 0" in Path(outputs[0]).read_text(encoding="utf-8")
    assert "review 1" in Path(outputs[1]).read_text(encoding="utf-8")


def test_reports_export_after_move_and_from_other_cwd(tmp_path, monkeypatch):
    old = tmp_path / "old"
    old.mkdir()
    source = old / "a.py"
    source.write_text("x = 1", encoding="utf-8")
    save(old, source, "portable report")
    manifest = store.load_manifest(str(old))
    output = next(iter(manifest.values()))["modes"]["bug"]["output"]
    assert not os.path.isabs(output)
    new = tmp_path / "new"
    shutil.move(str(old), str(new))
    monkeypatch.chdir(tmp_path)
    assert "portable report" in store.export_all(str(new))[1]
    assert store.status(store.load_manifest(str(new)), str(new / "a.py"),
                        store.file_sha(new / "a.py"), "bug") == "reviewed"


@pytest.mark.skipif(os.name != "nt", reason="Windows case-insensitive paths")
def test_case_variants_share_cache(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path)
    assert store.status(store.load_manifest(str(tmp_path)), str(path).upper(),
                        store.file_sha(path), "bug") == "reviewed"


def test_incomplete_attempt_is_not_completed_cache(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path, "partial response", usage={"cost": 0.25, "complete": False, "finish": "length"})
    manifest = store.load_manifest(str(tmp_path))
    assert store.status(manifest, str(path), store.file_sha(path), "bug") != "reviewed"
    assert store.total_cost(manifest) == 0.25
    assert "partial response" in store.export_all(str(tmp_path))[1]


@pytest.mark.parametrize("filename", ["user.mapper.ts", "node_modules_helper.py"])
def test_authored_names_are_not_vendor_substrings(tmp_path, filename):
    (tmp_path / filename).write_text("x = 1", encoding="utf-8")
    assert [row["rel"] for row in scanner.scan(str(tmp_path))] == [filename]


@pytest.mark.parametrize("extension", [".mjs", ".cjs", ".mts", ".cts"])
def test_js_module_never_gets_python_signals(extension):
    assert not static_context._is_python("module" + extension, "console.log(value)")


@pytest.mark.parametrize("findings", [None, "none", {}, [None], [{"severity": "HIGH"}],
    [{"severity": "INVALID", "line": 1, "title": "a", "detail": "b", "fix": "c"}],
    [{"severity": "HIGH", "line": True, "title": "a", "detail": "b", "fix": "c"}]])
def test_json_rejects_malformed_schema(findings):
    with pytest.raises(ValueError):
        analyzer._parse_json_review(json.dumps({"verdict": "review", "findings": findings, "notes": []}))


def test_json_accepts_valid_contract():
    value = {"verdict": "Clear", "findings": [], "notes": ["Checked"]}
    assert analyzer._parse_json_review(json.dumps(value)) == value


def test_batch_directory_discovery_uses_scanner_exclusions(tmp_path):
    for rel in ["good.py", ".secrets/credentials.py", "junk/scratch.py", "vendor/lib.py",
                "custom_env/lib.py", "oversize.py"]:
        path = tmp_path / rel
        path.parent.mkdir(exist_ok=True)
        path.write_text("x = 1", encoding="utf-8")
    (tmp_path / "custom_env" / "pyvenv.cfg").write_text("home = python", encoding="utf-8")
    (tmp_path / "oversize.py").write_bytes(b"x" * 2_000_001)
    assert run_batch.gather([str(tmp_path)], ["*.py"]) == [str(tmp_path / "good.py")]


def batch(tmp_path, monkeypatch, reviewer, *args):
    monkeypatch.setattr(analyzer, "api_key", lambda: "test")
    monkeypatch.setattr(analyzer, "model_max_tokens", lambda *a: 8000)
    monkeypatch.setattr(analyzer, "review_code", reviewer)
    out = tmp_path / "reports"
    monkeypatch.setattr(sys, "argv", ["run_batch.py", str(tmp_path), "--out", str(out),
                                    "--no-static", *args])
    rc = run_batch.main()
    return rc, json.loads((out / "_batch_summary.json").read_text(encoding="utf-8"))


def test_paid_save_failure_stops_and_keeps_cost(tmp_path, monkeypatch):
    for i in range(4):
        (tmp_path / f"a{i}.py").write_text("x = 1", encoding="utf-8")
    calls = []
    def reviewer(*args, **kwargs):
        calls.append(args)
        return "paid review", {"cost": 1, "finish": "stop", "complete": True}
    def fail(*args, **kwargs):
        raise OSError("disk unavailable")
    monkeypatch.setattr(store, "save_review", fail)
    rc, result = batch(tmp_path, monkeypatch, reviewer, "--budget", "10.00")
    assert rc == 1
    assert len(calls) == 1
    assert result["spent"] == 1
    assert result["errors"] == 1
    assert result["files"][0]["cost"] == 1


def test_batch_uses_requested_root_cache(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    path = src / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path)
    def reviewer(*args, **kwargs):
        pytest.fail("Unchanged source was billed again")
    rc, result = batch(tmp_path, monkeypatch, reviewer)
    assert rc == 0
    assert result["skipped"] == 1
    assert result["done"] == 0
    assert not (src / ".colibri_reviews").exists()


def test_batch_hash_matches_reviewed_buffer(tmp_path, monkeypatch):
    path = tmp_path / "a.py"
    old = b"old = 1\r\n"
    path.write_bytes(old)
    original_sha = store.file_sha
    def racing_sha(source):
        digest = original_sha(source)
        path.write_text("new = 2", encoding="utf-8")
        return digest
    monkeypatch.setattr(store, "file_sha", racing_sha)
    def reviewer(code, *args, **kwargs):
        assert "old = 1" in code
        path.write_text("new = 2", encoding="utf-8")
        return "old review", {"cost": 0, "finish": "stop", "complete": True}
    rc, result = batch(tmp_path, monkeypatch, reviewer)
    assert rc == 0 and result["done"] == 1
    entry = next(iter(store.load_manifest(str(tmp_path)).values()))
    assert entry["modes"]["bug"]["sha"] == hashlib.sha256(old).hexdigest()


def fake_notary(monkeypatch):
    def git(root, *args, **kwargs):
        if args[0] == "notes":
            return SimpleNamespace(returncode=0, stdout="note abc\n")
        return SimpleNamespace(returncode=0, stdout="abc\x1f2026-09-26T12:01:00-06:00\x1fAgent\x1fa@b\n")
    monkeypatch.setattr(aer, "run_git", git)


def write_block(root, suffix, count):
    directory = root / ".adversary" / "reviews"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"gate_20260926-120000{suffix}.md"
    path.write_text("model: test | provider: test\n\n" +
                    "".join(f"FINDING {i} HIGH a.py:1 bug\n" for i in range(1, count + 1)) +
                    "\nVERDICT: BLOCK\n", encoding="utf-8")
    return path


def test_missing_parent_reviews_keeps_worktree_denial(tmp_path, monkeypatch):
    fake_notary(monkeypatch)
    parent, worktree = tmp_path / "main", tmp_path / "linked"
    parent.mkdir()
    write_block(worktree, "", 1)
    episodes, unlanded, anomalies = aer.gate_episodes("test", str(parent), [str(worktree)])
    assert len(episodes) == 1 and episodes[0]["new_findings"] == 1
    assert anomalies and not unlanded


def test_same_second_collision_keeps_first_denial(tmp_path, monkeypatch):
    fake_notary(monkeypatch)
    write_block(tmp_path, "-2", 2)
    write_block(tmp_path, "-10", 3)
    first = write_block(tmp_path, "", 1)
    episodes, _, _ = aer.gate_episodes("test", str(tmp_path))
    assert episodes[0]["denial_artifact"] == first.name
    assert episodes[0]["new_findings"] == 1


def test_all_modes_repeat_input_cost():
    # Execute the real function without starting the Streamlit application.
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "per_file_ceiling")
    namespace = {"cfg": {"price_in": 3, "price_out": 15}, "eff_max_out": 1000}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "app.py", "exec"), namespace)
    assert namespace["per_file_ceiling"](10_000, 3) == pytest.approx(0.135)

@pytest.mark.parametrize("changed", [False, True])
def test_failed_retry_preserves_completed_review_and_cost(tmp_path, changed):
    path = tmp_path / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path, "original completed review", usage={"cost": 0.10, "complete": True})
    if changed:
        path.write_text("x = 2", encoding="utf-8")
    save(tmp_path, path, "paid partial retry", usage={"cost": 0.25, "complete": False})
    manifest = store.load_manifest(str(tmp_path))
    assert store.status(manifest, str(path), store.file_sha(path), "bug") == (
        "stale" if changed else "reviewed")
    assert store.total_cost(manifest) == pytest.approx(0.35)
    exported = store.export_all(str(tmp_path))[1]
    assert "original completed review" in exported
    assert "paid partial retry" in exported


def test_export_labels_incomplete_modes_honestly(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path, "partial", usage={"cost": 0.25, "complete": False})
    contents = store.export_all(str(tmp_path))[1].split("\n---\n", 1)[0]
    assert "completed: none" in contents
    assert "incomplete attempts: 1" in contents


def test_one_malformed_manifest_row_does_not_erase_good_rows(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x = 1", encoding="utf-8")
    save(tmp_path, path)
    manifest_path = tmp_path / ".colibri_reviews" / "_manifest.json"
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw[str(tmp_path / "bad.py")] = None
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = store.load_manifest(str(tmp_path))
    assert store.status(loaded, str(path), store.file_sha(path), "bug") == "reviewed"


@pytest.mark.parametrize("foreign", [False, True])
def test_mismatched_relative_path_cannot_replace_existing_entry(tmp_path, foreign):
    source = tmp_path / "a.py"
    source.write_text("x = 1", encoding="utf-8")
    save(tmp_path, source, "authoritative review")
    manifest_path = tmp_path / ".colibri_reviews" / "_manifest.json"
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    other = (tmp_path.parent / "elsewhere" if foreign else tmp_path / "sub") / "a.py"
    raw[str(other)] = {"rel": "a.py", "modes": {"bug": {
        "sha": "wrong", "reviewed_at": "9999-12-31 23:59", "cost": 0,
        "output": "wrong.md", "complete": True}}}
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = store.load_manifest(str(tmp_path))
    assert store.status(loaded, str(source), store.file_sha(source), "bug") == "reviewed"
    assert store.entry_for(loaded, str(other))["modes"]["bug"]["sha"] == "wrong"


def test_paid_response_survives_report_and_summary_disk_failure(tmp_path, monkeypatch, capsys):
    for i in range(3):
        (tmp_path / f"a{i}.py").write_text("x=1", encoding="utf-8")
    calls = []
    def reviewer(*args, **kwargs):
        calls.append(args)
        return "recover this paid review", {"cost": 1, "complete": True, "finish": "stop"}
    def fail(*args, **kwargs):
        raise OSError("report disk full")
    original_write = Path.write_text
    def write(path, *args, **kwargs):
        if path.name == "_batch_summary.json":
            raise OSError("summary disk full")
        return original_write(path, *args, **kwargs)
    monkeypatch.setattr(analyzer, "api_key", lambda: "test")
    monkeypatch.setattr(analyzer, "model_max_tokens", lambda *a: 8000)
    monkeypatch.setattr(analyzer, "review_code", reviewer)
    monkeypatch.setattr(store, "save_review", fail)
    monkeypatch.setattr(Path, "write_text", write)
    monkeypatch.setattr(sys, "argv", ["run_batch.py", str(tmp_path), "--out",
                                     str(tmp_path / "reports"), "--no-static"])
    assert run_batch.main() == 1
    assert len(calls) == 1
    output = capsys.readouterr().out
    assert "spent $1.0000" in output
    recovery = json.loads(output.split("RECOVERY SUMMARY:\n", 1)[1].split("\nDONE:", 1)[0])
    assert recovery["spent"] == 1 and recovery["errors"] >= 1
    assert recovery["files"][0]["review"] == "recover this paid review"
    assert recovery["files"][0]["usage"]["cost"] == 1


def test_batch_root_uses_same_alias_spelling_as_discovery(tmp_path, monkeypatch):
    target, alias = tmp_path / "project", tmp_path / "project-link"
    target.mkdir()
    (target / "src").mkdir()
    (target / "src" / "a.py").write_text("x=1", encoding="utf-8")
    try:
        alias.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        if os.name != "nt":
            pytest.skip("Directory symlinks unavailable on this host")
        import subprocess
        command = str(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe")
        made = subprocess.run([command, "/c", "mklink", "/J", str(alias), str(target)],
                              capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        assert made.returncode == 0, made.stderr.decode(errors="replace")
    def reviewer(*args, **kwargs):
        return "review", {"cost": 0, "finish": "stop", "complete": True}
    rc, result = batch(alias, monkeypatch, reviewer)
    assert rc == 0 and result["done"] == 1 and result["errors"] == 0
    assert (target / ".colibri_reviews" / "_manifest.json").exists()
    assert not (target / "src" / ".colibri_reviews").exists()


@pytest.mark.parametrize("reverse", [False, True])
def test_ambiguous_relocation_preserves_distinct_source_records(tmp_path, reverse):
    first = tmp_path.parent / "former" / "a.py"
    second = tmp_path.parent / "former" / "sub" / "a.py"
    rows = [(str(first), {"rel": "a.py", "modes": {"bug": {"sha": "first"}}}),
            (str(second), {"rel": "a.py", "modes": {"bug": {"sha": "second"}}})]
    if reverse:
        rows.reverse()
    source = tmp_path / "a.py"
    source.write_text("x=1", encoding="utf-8")
    store.save_manifest(str(tmp_path), dict(rows))
    loaded = store.load_manifest(str(tmp_path))
    assert len(loaded) == 2
    assert store.entry_for(loaded, str(first))["modes"]["bug"]["sha"] == "first"
    assert store.entry_for(loaded, str(second))["modes"]["bug"]["sha"] == "second"
    assert store.status(loaded, str(tmp_path / "a.py"), "first", "bug") == "new"

    assert len(store.load_manifest(str(tmp_path))) == 2
    save(tmp_path, source, "new source review")
    persisted = store.load_manifest(str(tmp_path))
    assert len(persisted) == 3
    assert store.entry_for(persisted, str(first))["modes"]["bug"]["sha"] == "first"
    assert store.entry_for(persisted, str(second))["modes"]["bug"]["sha"] == "second"
    assert store.status(persisted, str(source), store.file_sha(source), "bug") == "reviewed"


@pytest.mark.parametrize("body,usage,complete", [
    ("review", {}, False),
    ("review", {"finish_reason": "length"}, False),
    ("review", {"finish_reason": "stop"}, True),
    ("review", {"complete": True, "finish": "length"}, False),
    ("", {"complete": True}, False),
    (None, {"complete": True}, False),
    ({"unexpected": "body"}, {"complete": True}, False),
    ("review", {"complete": True, "finish": "stop", "finish_reason": "tool_calls"}, False),
    ("review", {"complete": True, "finish": "length", "finish_reason": "stop"}, False),
])
def test_completion_evidence_is_required(tmp_path, body, usage, complete):
    path = tmp_path / "a.py"
    path.write_text("x=1", encoding="utf-8")
    save(tmp_path, path, body, usage=usage)
    manifest = store.load_manifest(str(tmp_path))
    assert store.entry_for(manifest, str(path))["modes"]["bug"]["complete"] is complete
    assert store.status(manifest, str(path), store.file_sha(path), "bug") == (
        "reviewed" if complete else "new")


def test_report_path_budget(tmp_path):
    path = tmp_path / "source" / ("component_" * 10 + ".py")
    path.parent.mkdir()
    path.write_text("x=1", encoding="utf-8")
    output = save(tmp_path, path)
    # A 70-character project root must still fit a conventional Windows MAX_PATH.
    representative = "p" * 70 + os.sep + ".colibri_reviews" + os.sep + Path(output).name
    assert len(representative) < 260


def test_failed_batch_copy_does_not_grant_cache_credit(tmp_path, monkeypatch):
    source = tmp_path / "a.py"
    source.write_text("x=1", encoding="utf-8")
    original_write = Path.write_text
    failed_copies = []
    def write(path, *args, **kwargs):
        if path.parent == tmp_path / "reports" and path.suffix == ".md":
            failed_copies.append(path)
            raise OSError("batch copy unavailable")
        return original_write(path, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", write)
    def reviewer(*args, **kwargs):
        return "paid review", {"cost": 1, "finish": "stop", "complete": True}
    rc, result = batch(tmp_path, monkeypatch, reviewer)
    assert rc == 1 and result["spent"] == 1
    assert len(failed_copies) == 1
    assert result["files"][0]["review"] == "paid review"
    assert store.status(store.load_manifest(str(tmp_path)), str(source),
                        store.file_sha(source), "bug") == "new"


def test_deeply_nested_manifest_is_recoverable(tmp_path):
    directory = tmp_path / ".colibri_reviews"
    directory.mkdir()
    (directory / "_manifest.json").write_text("[" * 10000 + "]" * 10000, encoding="utf-8")
    assert store.load_manifest(str(tmp_path)) == {}


def test_invalid_manifest_key_does_not_erase_good_rows(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x=1", encoding="utf-8")
    save(tmp_path, path)
    manifest_path = tmp_path / ".colibri_reviews" / "_manifest.json"
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw["bad\0key"] = {"rel": "bad.py", "modes": {}}
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = store.load_manifest(str(tmp_path))
    assert store.status(loaded, str(path), store.file_sha(path), "bug") == "reviewed"


def test_batch_imports_local_modules_in_safe_path_mode(tmp_path):
    import subprocess
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    result = subprocess.run([sys.executable, "-P", "-B", str(ROOT / "run_batch.py"), "--help"],
                            cwd=tmp_path, env=env, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert b"--budget" in result.stdout


def test_nested_legacy_output_relocates_from_nearest_review_directory(tmp_path):
    base = tmp_path / "new"
    report = base / ".colibri_reviews" / "review.md"
    report.parent.mkdir(parents=True)
    report.write_text("correct report", encoding="utf-8")
    old = tmp_path / ".colibri_reviews" / "old-project" / ".colibri_reviews" / "review.md"
    assert store.output_path(str(base), str(old)) == str(report)
