# Colibri review — hy4-review/hy4_review.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\hy4-review\hy4_review.py`
- **Model:** claude-fable-5 (in-session), gating grok-4.3 findings
- **sha256:** `c5392c005bcafa27...` · **Date:** 2026-09-02 · **Mode:** bug
- **Context:** on-tap OpenRouter reviewer CLI; the ceiling/empty-response guard is deliberate design (honored). Findings verified by reading cited lines.

## Verdict
Two MEDIUM robustness defects; no security/correctness surface beyond error handling.

## Bugs & vulnerabilities

**[MEDIUM] `--context-file` / `--spec` / `--findings` paths read with no existence guard** — `_load_spec` line 111 (`Path(path).read_text`), `main()` context/findings reads
- A missing/unreadable path raises `FileNotFoundError`/`PermissionError` as a raw traceback instead of a clean `SystemExit`. CONFIRMED by read (`_load_spec` reads unguarded at line 111). Fix: `if not Path(p).is_file(): raise SystemExit("no such file: %s" % p)` before each read.

**[MEDIUM] Response handling catches only `HTTPError` — other failures traceback after the paid call** — `_post_retry` (~line 107), `review()` post/empty-retry blocks
- A `URLError`, socket timeout, or malformed/non-JSON body raises past the `except HTTPError` clauses, producing a traceback after billing rather than a readable `SystemExit`. CONFIRMED by read (only `HTTPError` caught). Fix: broaden to `(URLError, json.JSONDecodeError, OSError)` → `raise SystemExit(...)`. (Same class the sibling `adversary_gate._call_one_model` MEDIUM carries.)

## Missing safeguards
- None beyond the above.
