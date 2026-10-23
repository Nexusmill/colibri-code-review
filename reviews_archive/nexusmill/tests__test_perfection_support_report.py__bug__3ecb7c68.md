# colibri bug review — tests/test_perfection_support_report.py

- source: tests/test_perfection_support_report.py · model: GLM-5.3-Flash (in-session)
- sha256: 3ecb7c6823 (full sha in manifest row) · reviewed_at: 2026-10-13 · mode: bug
- context pack: live execution (PASS, exit 0); the W1 byte-exact cap ladder (W1a→W1h) traced against read_log_tail; env-restore census (zero restores in file).

## Verdict
Shippable — the W1 ladder (rolled-sibling ordering, budget-bytes-not-chars, replace-expansion convergence, all-invalid worst case) is the suite's best cap-semantics battery. One env leak.

## Bugs & vulnerabilities

**[LOW] t2 sets USERPROFILE/HOME and never restores it** - `line 124`
- Verbatim: `os.environ["USERPROFILE" if sys.platform == "win32" else "HOME"] = tmp  # not reliable cross-platform; skip store test if dir differs`
- What: the process env is mutated with no restore (census: zero environ restores in the file). The comment shows awareness of the awkwardness but the row proceeds anyway.
- Trigger: any later row (or a future append) calling expanduser-based code — it resolves to tmp for the rest of the run.
- Broken behavior: none today (R4 uses _get_json only); process-lifetime leak, classic class.
- Fix: save/restore the var around the block, or drop the line (the row below it monkeypatches `sr._support_dir` anyway — the env line is doing nothing for it).
- Status: **CONFIRMED**.

## Missing safeguards
- R2's disjunction (`== "~/x" or startswith("~")`) is the legitimate platform-spelling kind — both terms assert the same property.
