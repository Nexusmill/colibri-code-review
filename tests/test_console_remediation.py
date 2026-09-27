"""Console and analyzer completion regressions; no paid calls or UI server."""
import ast
import hashlib
import marshal
from pathlib import Path
from types import SimpleNamespace

import pytest

import analyzer
import store

ROOT = Path(__file__).resolve().parents[1]


def app_node(name):
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def test_refusals_are_not_complete(monkeypatch):
    monkeypatch.setattr(analyzer, "api_key", lambda: "")
    text, usage = analyzer.review_code("x=1", "a.py")
    assert text and usage.get("complete") is False
    monkeypatch.setattr(analyzer, "api_key", lambda: "test")
    text, usage = analyzer.review_code("x=1", "a.py", mode="spec")
    assert text and usage.get("complete") is False


@pytest.mark.parametrize("content,finish,complete", [
    ("", "stop", False), ("   ", "stop", False),
    ("partial", "length", False), ("refusal", "content_filter", False),
    ("usable review", "stop", True)])
def test_response_completion_requires_final_text(monkeypatch, content, finish, complete):
    response = SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=content, reasoning=None), finish_reason=finish)],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1, cost=0.1))
    class Client:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: response))
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    monkeypatch.setattr(analyzer, "api_key", lambda: "test")
    monkeypatch.setattr(analyzer, "OpenAI", Client)
    _, usage = analyzer.review_code("x=1", "a.py", cfg={
        "max_tokens": 100, "static_ast": False, "static_mypy": False, "static_dis": False})
    assert usage.get("complete") is complete
    assert usage["cost"] == 0.1


class State(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, value):
        self[key] = value


class Console:
    def __init__(self):
        self.sidebar = self
        self.session_state = State()
        self.messages = []
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def markdown(self, text, **kw):
        self.messages.append(text)
    caption = markdown
    error = markdown
    warning = markdown
    def progress(self, *args, **kwargs):
        return self
    def expander(self, *args, **kwargs):
        return self
    def selectbox(self, label, options, index=0, **kwargs):
        return options[index]
    def radio(self, label, options, **kwargs):
        return options[0]
    def toggle(self, label, value=False, **kwargs):
        return value
    checkbox = toggle
    def text_input(self, label, value="", **kwargs):
        return "https://custom.example/v1" if label == "Base URL" else value
    def number_input(self, label, value=0, **kwargs):
        return value
    def slider(self, label, minimum, maximum, value, step):
        return value


def test_auto_limit_uses_selected_endpoint():
    console = Console()
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    sidebar = next(n for n in tree.body if isinstance(n, ast.With)
                   and isinstance(n.items[0].context_expr, ast.Attribute)
                   and n.items[0].context_expr.attr == "sidebar")
    calls = []
    def ceiling(model, base_url=analyzer.DEFAULTS["api_base"]):
        calls.append((model, base_url))
        return 9000 if base_url == "https://custom.example/v1" else 1000
    namespace = {"st": console, "openrouter_models": lambda: [],
                 "PINNED_MODELS": ["test-model"], "DEFAULTS": analyzer.DEFAULTS,
                 "model_max_tokens": ceiling}
    exec(compile(ast.Module(body=[sidebar], type_ignores=[]), "app.py", "exec"), namespace)
    assert calls[-1][1] == "https://custom.example/v1"
    assert namespace["eff_max_out"] == 9000


def test_console_accounts_paid_response_before_failed_save(tmp_path, monkeypatch):
    path = tmp_path / "a.py"
    path.write_text("x=1", encoding="utf-8")
    console = Console()
    def fail(*args, **kwargs):
        raise OSError("disk unavailable")
    monkeypatch.setattr(store, "save_review", fail)
    namespace = {"st": console, "store": store, "os": __import__("os"),
                 "MODES": analyzer.MODES, "cfg": {"model": "test"},
                 "delta_rr": False,
                 "review_code": lambda *a, **k: ("paid", {"cost": 0.25, "complete": True})}
    exec(compile(ast.Module(body=[app_node("process")], type_ignores=[]), "app.py", "exec"), namespace)
    assert namespace["process"](str(tmp_path), [("a.py", "bug")]) == 0.25

def test_selected_meter_counts_every_mode():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    call = next(n for n in ast.walk(tree) if isinstance(n, ast.Expr)
                and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr == "meter")
    captured = []
    namespace = {
        "ui": SimpleNamespace(meter=lambda *args, **kwargs: captured.append(args)),
        "picked": ["a.py"], "modes": ["bug", "quality", "feature"],
        "sel_tok": 10_000, "eff_max_out": 1000, "cfg": {"price_in": 3, "price_out": 15},
        "reasoning": "off", "auto_out": True}
    exec(compile(ast.Module(body=[call], type_ignores=[]), "app.py", "exec"), namespace)
    assert captured == [(3, 30_000, 1000, 3, 15)]


def test_console_hash_identifies_the_reviewed_bytes(tmp_path, monkeypatch):
    import hashlib
    path = tmp_path / "a.py"
    raw = b"old = 1\r\n"
    path.write_bytes(raw)
    original_sha = store.file_sha
    def racing_sha(p):
        path.write_text("new = 2", encoding="utf-8")
        return original_sha(p)
    monkeypatch.setattr(store, "file_sha", racing_sha)
    def reviewer(code, *args, **kwargs):
        assert "old = 1" in code
        path.write_text("new = 2", encoding="utf-8")
        return "old review", {"cost": 0, "complete": True, "finish": "stop"}
    namespace = {"st": Console(), "store": store, "os": __import__("os"),
                 "MODES": analyzer.MODES, "cfg": {"model": "test"},
                 "delta_rr": False, "review_code": reviewer}
    exec(compile(ast.Module(body=[app_node("process")], type_ignores=[]), "app.py", "exec"), namespace)
    namespace["process"](str(tmp_path), [("a.py", "bug")])
    record = next(iter(store.load_manifest(str(tmp_path)).values()))["modes"]["bug"]
    assert record["sha"] == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("relative", [False, True])
@pytest.mark.parametrize("invalid_utf8", [False, True])
def test_confirmation_estimate_includes_prior_prompt(tmp_path, monkeypatch, relative, invalid_utf8):
    path = tmp_path / "a.py"
    path.write_text("x=1", encoding="utf-8")
    output = store.save_review(str(tmp_path), str(path), "a.py", store.file_sha(path), "bug",
                      "P" * 14_000, {"cost": 0, "complete": True}, "test")
    if invalid_utf8:
        with open(output, "ab") as stream:
            stream.write(b"\xff")
    path.write_text("x=2", encoding="utf-8")
    monkeypatch.chdir(tmp_path.parent)
    base = tmp_path.name if relative else str(tmp_path)
    cfg = dict(analyzer.DEFAULTS, static_ast=False, static_mypy=False, static_dis=False)
    namespace = {"st": Console(), "store": store, "os": __import__("os"),
                 "cfg": cfg, "delta_rr": True,
                 "_build_prompt": analyzer._build_prompt, "_PROMPTS": analyzer._PROMPTS, "hashlib": hashlib, "marshal": marshal}
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    candidates = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "queue_tokens"]
    assert candidates, "Full-prompt queue estimation is absent"
    exec(compile(ast.Module(body=candidates, type_ignores=[]), "app.py", "exec"), namespace)
    assert namespace["queue_tokens"](base, [("a.py", "bug")]) > 4000

def test_previous_review_listing_does_not_claim_incomplete_mode():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    loop = next(n for n in ast.walk(tree) if isinstance(n, ast.For)
                and isinstance(n.target, ast.Tuple)
                and [getattr(v, "id", "") for v in n.target.elts] == ["_", "e"])
    messages = []
    namespace = {"m": {"a": {"rel": "a.py", "modes": {"bug": {"complete": False}}}},
                 "st": SimpleNamespace(write=messages.append)}
    exec(compile(ast.Module(body=[loop], type_ignores=[]), "app.py", "exec"), namespace)
    assert "completed: none" in messages[0]
    assert "incomplete attempts: 1" in messages[0]


def test_meter_renders_aggregated_input_as_an_estimate(monkeypatch):
    import importlib.util
    import sys
    rendered = []
    fake = SimpleNamespace(markdown=lambda text, **kwargs: rendered.append(text))
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    spec = importlib.util.spec_from_file_location("meter_under_test", ROOT / "ui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Three 10,000-token inputs at $3/M plus three 1,000-token outputs at $15/M = $0.135.
    module.meter(3, 30_000, 1000, 3, 15, False)
    assert "3 review calls" in rendered[0]
    assert "~&nbsp;$0.14" in rendered[0]
    assert "Excludes prompt overhead" in rendered[0]
    assert "not a spending cap" in rendered[0]


def test_queue_estimates_cache_enrichment_and_refresh_inputs(tmp_path):
    path = tmp_path / "a.py"
    path.write_text("x=1", encoding="utf-8")
    console = Console()
    calls = []
    cfg = dict(analyzer.DEFAULTS, static_ast=True, static_mypy=True, static_dis=True)
    def build(code, rel, mode, settings, **kwargs):
        calls.append((code, mode, dict(settings), kwargs))
        return "prompt " + code + (kwargs.get("prior_md") or "") + (kwargs.get("spec_text") or "")
    namespace = {"st": console, "store": store, "os": __import__("os"), "hashlib": hashlib, "marshal": marshal,
                 "cfg": cfg, "delta_rr": True, "_build_prompt": build, "_PROMPTS": dict(analyzer._PROMPTS)}
    exec(compile(ast.Module(body=[app_node("queue_tokens")], type_ignores=[]), "app.py", "exec"), namespace)
    estimate = namespace["queue_tokens"]
    queue = [("a.py", "bug")]
    first = estimate(str(tmp_path), queue)
    assert estimate(str(tmp_path), queue) == first and len(calls) == 1
    path.write_text("x=2", encoding="utf-8")
    estimate(str(tmp_path), queue)
    assert len(calls) == 2 and calls[-1][0] == "x=2"
    cfg["static_mypy"] = False
    estimate(str(tmp_path), queue)
    assert len(calls) == 3 and calls[-1][2]["static_mypy"] is False
    store.save_review(str(tmp_path), str(path), "a.py", hashlib.sha256(b"x=1").hexdigest(), "bug", "prior review",
                      {"cost": 0, "complete": True}, "test")
    estimate(str(tmp_path), queue)
    assert len(calls) == 4 and calls[-1][3]["prior_md"]
    console.session_state.spec_text = "contract one"
    estimate(str(tmp_path), [("a.py", "spec")])
    console.session_state.spec_text = "contract two"
    estimate(str(tmp_path), [("a.py", "spec")])
    assert len(calls) == 6 and calls[-1][3]["spec_text"] == "contract two"
    assert len(console.session_state.prompt_estimates) == 1
    previous = estimate(str(tmp_path), [("a.py", "spec")])
    system, template = namespace["_PROMPTS"]["spec"]
    namespace["_PROMPTS"]["spec"] = (system + " extra" * 100, template)
    updated = estimate(str(tmp_path), [("a.py", "spec")])
    assert len(calls) == 7 and updated > previous
    def changed_builder(*args, **kwargs):
        return build(*args, **kwargs) + " added builder content" * 100
    namespace["_build_prompt"] = changed_builder
    assert estimate(str(tmp_path), [("a.py", "spec")]) > updated
    assert len(calls) == 8
