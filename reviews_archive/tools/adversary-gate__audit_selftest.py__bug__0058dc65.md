# Colibri review — adversary-gate/audit_selftest.py (bug)

- source: `C:\Users\User\source\repos\Tools\adversary-gate\audit_selftest.py`
- model: claude-fable-5-1 (in-session Phase-3 gate over the external raw z-ai/glm-5.3-flash review, `.colibri_reviews/_external_raw/tools__audit_selftest.py__glm-5.3-flash.md`, run 2026-09-02 at sha `0058dc658e08cbfa…`)
- sha256: `0058dc658e08cbfae9133adcbacf6a2b4a325febdf24fc923cfc8709aa72528e` (current bytes at dispatch, 2026-09-05; unchanged since the raw.)
- date: 2026-09-05
- mode: bug
- context pack: current bytes read end to end; jCodemunch/call-site lookups on this repo; `git log -S` for the fix commits cited below; the raw review; the repo's existing `.colibri_reviews/_manifest.json` (no prior bug-mode record for this file). Every external finding re-traced against the cited lines (Phase 3): CONFIRMED / PLAUSIBLE kept, fixed-since-raw ones recorded verified-stale with their commit, refuted ones listed with the reason (G35: neither class is ever re-fixed).

## Verdict
Two hygiene LOWs; no correctness defect.

**[LOW] The `bad_baseline_errors` probe decodes with the platform codec — CONFIRMED** - `line 130-131`
- The only `subprocess.run` in the file without `encoding="utf-8", errors="replace"`; a non-ASCII byte in the audit's error text raises `UnicodeDecodeError` and the selftest crashes instead of recording a verdict.

**[LOW] The throwaway repo is never removed — CONFIRMED** - `line 54`
- Leaks a repo holding an `.adversary/OVERRIDE` under `%TEMP%` on every run.
