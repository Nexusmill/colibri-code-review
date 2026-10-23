# Colibri review — src/jcodemunch_mcp/cli/receipt.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\receipt.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `13d26d36913476d5a7ecc4a78a9d1b4d6d291acbde7d48cf3e9b1815458514ed` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `lifetime_meter` 166-184 ("Returns None when absent/unreadable/empty" - but `data.get` assumed a dict); the producer is the server's per-call savings meter under the index root; `main` 664-805 passes the result to `render_text`/`render_json`. No prior `.colibri_reviews` record.

## Verdict
A syntactically valid `_savings.json` that is not an object crashed the receipt with AttributeError while every other bad input reads as "no meter". Fixed at the one read.

## Bugs & vulnerabilities
**[LOW] Non-dict JSON in `_savings.json` raised instead of reading as absent — CONFIRMED — FIXED** - `line 181`
- Trigger (RED on these bytes): `[1, 2]`, `42`, `"text"`, `null` → `AttributeError: '…' object has no attribute 'get'` out of the CLI.
- Fix: `if not isinstance(data, dict): return None`, next to the existing `(OSError, ValueError)` → None.

## Adversarial verification (Phase 3)
- Pinned: the four non-dict bodies → None; control: a real meter still reads as `{"total_tokens_saved": 12, "anon_id": "x"}`.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `353896dfecc36cac952781c92aac56300ae2bdea77938ecbf4df01cf173591ab`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
