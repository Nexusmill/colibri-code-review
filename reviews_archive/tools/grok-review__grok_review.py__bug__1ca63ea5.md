# Colibri review — grok-review/grok_review.py (bug)

- source: `C:\Users\User\source\repos\Tools\grok-review\grok_review.py`
- model: claude-fable-5-1 (in-session Phase-3 gate over the external raw z-ai/glm-5.3-flash review, `.colibri_reviews/_external_raw/tools__grok_review.py__glm-5.3-flash.md`, run 2026-09-02 at sha `1ca63ea5f41d835b…`)
- sha256: `1ca63ea5f41d835bc951e0c768234ad9c544248ecd4ebb78534a82f348df9ba3` (current bytes at dispatch, 2026-09-05; unchanged since the raw.)
- date: 2026-09-05
- mode: bug
- context pack: current bytes read end to end; jCodemunch/call-site lookups on this repo; `git log -S` for the fix commits cited below; the raw review; the repo's existing `.colibri_reviews/_manifest.json` (no prior bug-mode record for this file). Every external finding re-traced against the cited lines (Phase 3): CONFIRMED / PLAUSIBLE kept, fixed-since-raw ones recorded verified-stale with their commit, refuted ones listed with the reason (G35: neither class is ever re-fixed).

## Verdict
Two money-adjacent defects on a paid call path, both confirmed.

**[MEDIUM] Unhandled failures after the paid call is spent — CONFIRMED** - `line 194-198`
- Only `HTTPError` is caught; a `URLError`/timeout on read, or a 200 whose body is not JSON, raises a raw traceback after billing. Catch `(urllib.error.URLError, TimeoutError, OSError)` and wrap `json.loads` with a "review lost, tokens spent" exit that includes the first bytes of the body.

**[MEDIUM] `--spec` / `--findings` are loaded but silently ignored outside their mode — CONFIRMED** - `line 241-244, 171-176`
- `_load_spec` runs (and errors on a missing file) for any mode, but the text is only sent when `mode == "spec"` (`--findings` only for `plan`); a `--mode bug --spec ...` run bills a generic review the user believes was conformance-checked. Fix: `ap.error` on the mismatch in `main()`.

**[LOW] Key-file parser over-matches variable names — CONFIRMED** - `line 147`
- `startswith("xaikey")` also matches `xaikey_backup=`; compare the partitioned key exactly.

## Fixed 2026-09-06 (remediation item 9, TDD, gated commit)
- **MEDIUM unhandled failures after the paid call - FIXED.** `review()` now catches
  `(URLError, TimeoutError, OSError, http.client.HTTPException)` after dispatch (the last one
  added on the gate's round-1 note: `IncompleteRead` / `BadStatusLine` from `r.read()` are
  neither OSError nor URLError and would still have tracebacked after billing; its check was
  written together with the fix) with a "review lost, tokens spent; re-run"
  exit, and wraps `json.loads` so a 200 with a non-JSON body exits with the first 300 bytes of
  that body instead of a traceback. The response is decoded with `errors="replace"`.
- **MEDIUM `--spec` / `--findings` silently ignored outside their mode - FIXED.** `main()`
  refuses with `ap.error` (exit 2) BEFORE loading the file or dispatching.
- **LOW key-file parser over-match - FIXED.** The line is partitioned on `=` and the key
  compared exactly (`xaikey_backup=` no longer shadows `xaikey=`).
- Tests: `grok-review/grok_review_selftest.py` (the repo's selftest idiom; `urlopen` stubbed,
  never the network - on the OLD bytes the flag-mismatch check reached the real API with a
  dummy key and was rejected 400 unbilled; the selftest now stubs urlopen for `main()` too and
  asserts the rejection happens before dispatch): 10 checks, 8 RED on the old bytes, 10/10 now.
