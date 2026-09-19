#!/usr/bin/env python3
"""Regression test for the 2026-09-19 doctrine: ES-module and typed JavaScript are code.
scanner.scan() must return .mjs/.cjs/.mts/.cts files and score them as code, on the same
footing as .js/.ts. Exit 0 iff ALL PASS. Standalone script (the repo's convention);
run with `python tests/test_scanner_ext.py`."""
import os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import scanner
_results = {}
def check(name, ok):
    _results[name] = bool(ok)
    print(("PASS " if ok else "FAIL ") + name)
with tempfile.TemporaryDirectory(prefix="scan_ext_") as d:
    for name in ("a.mjs", "b.cjs", "c.mts", "d.cts", "e.js", "f.py"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write("// module\nexport const x = 1;\n" * 4)
    rows = {r["rel"]: r for r in scanner.scan(d)}
    for name in ("a.mjs", "b.cjs", "c.mts", "d.cts"):
        check("scan returns " + name, name in rows)
    js = rows.get("e.js"); py = rows.get("f.py")
    for name in ("a.mjs", "b.cjs", "c.mts", "d.cts"):
        r = rows.get(name)
        check("score of %s == score of e.js" % name, r is not None and js is not None and r["score"] == js["score"])
print("RESULT: " + ("ALL PASS" if all(_results.values()) else "%d FAIL" % sum(not v for v in _results.values())))
sys.exit(0 if all(_results.values()) else 1)
