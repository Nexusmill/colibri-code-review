#!/usr/bin/env python3
"""Regression tests for the 2026-09-02 phase-2 sweep fixes. Exit 0 iff ALL PASS.

  * run_batch --budget is enforced with --workers>1 (bounded dispatch on completion).
  * store.save_review's manifest read-modify-write survives concurrent cross-process writers.

Standalone script (the repo's convention); run with `python tests/test_sweep_fixes.py`.
"""
import importlib.util, json, os, sys, tempfile, time, types, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
_results = {}


def check(name, ok):
    _results[name] = bool(ok)
    print(("PASS " if ok else "FAIL ") + name)


def _load(mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(ROOT, mod + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


# ── worker mode for the cross-process store test ──────────────────────────────
if len(sys.argv) >= 4 and sys.argv[1] == "store-worker":
    store = _load("store")
    base, i = sys.argv[2], int(sys.argv[3])
    p = os.path.join(base, "f%02d.py" % i)
    open(p, "w").write("x=%d\n" % i)
    store.save_review(base, p, "f%02d.py" % i, ("%064d" % i), "bug",
                      "# r%d\n" % i, {"cost": 0.0, "prompt_tokens": 1, "completion_tokens": 1}, "m")
    sys.exit(0)


def test_budget():
    rb_path = os.path.join(ROOT, "run_batch.py")
    # stub `analyzer` (real one needs openai/py3.13) before run_batch imports it
    fake = types.ModuleType("analyzer")
    fake.api_key = lambda: "fake"
    fake.model_max_tokens = lambda m: 8000
    def _rev(code, rel, mode, cfg, prior_md=None, fmt="md", spec_text=None):
        time.sleep(0.03)
        return ("## Verdict\nok\n", {"cost": 0.05, "prompt_tokens": 1, "completion_tokens": 1, "finish": "stop"})
    fake.review_code = _rev
    sys.modules["analyzer"] = fake
    spec = importlib.util.spec_from_file_location("run_batch", rb_path)
    rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)

    d = tempfile.mkdtemp(); N = 40
    for i in range(N):
        open(os.path.join(d, "f%02d.py" % i), "w").write("x=%d\n" % i)
    out = os.path.join(d, "rev")
    sys.argv = ["run_batch.py", d, "--model", "fake", "--mode", "bug",
                "--workers", "4", "--budget", "0.30", "--glob", "*.py", "--out", out]
    rb.main()
    s = json.load(open(os.path.join(out, "_batch_summary.json"), encoding="utf-8"))
    check("budget_enforced_with_workers", s["done"] < N and s["spent"] <= 0.30 + 0.05 * 4)


def test_store_lock():
    store = _load("store")
    base = tempfile.mkdtemp(); N = 20
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), "store-worker", base, str(i)])
             for i in range(N)]
    for p in procs:
        p.wait()
    man = store.load_manifest(base)
    present = sum(1 for i in range(N)
                  if any(isinstance(e, dict) and e.get("rel") == "f%02d.py" % i for e in man.values()))
    check("manifest_no_lost_update", present == N and len(man) == N)


def main():
    test_store_lock()
    test_budget()
    bad = [k for k, v in _results.items() if not v]
    print("\n%d/%d PASS" % (len(_results) - len(bad), len(_results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
