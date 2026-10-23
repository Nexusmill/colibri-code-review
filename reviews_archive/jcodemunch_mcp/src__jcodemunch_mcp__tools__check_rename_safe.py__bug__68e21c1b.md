# Colibri review — src/jcodemunch_mcp/tools/check_rename_safe.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\check_rename_safe.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `68e21c1b89f437ea264d92feb7c130685e2e95043e411dd27390d0abee6d4e8a` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 PLAUSIBLE LOW, 2 refuted - kept); the collision loop 89-99 (`s.get("name", "").lower() == new_name_lower` - case-insensitive); the return 102-113 (`safe` = no conflicts). No prior `.colibri_reviews` record.

## Verdict
Record-only. Case-insensitive collision matching can call a rename unsafe that a case-sensitive language would accept (`parse` → `Parse` beside a class `Parse`). That is a fabricated "unsafe", never a false "safe" - the tool's failure direction is the safe one, and a same-name-different-case pair is a readability collision worth flagging anyway. Declined, recorded so it is not re-raised.

## Refuted (kept from the sub-agent, re-traced)
- Transitive re-exporters missed (this file resolves every file's own specifiers against `sym_file`; anything deeper is `resolve_specifier`/index construction, out of scope); path-normalisation mismatch between `files_to_check` and symbol `file` fields (both come from the same index object's convention).

## Adversarial verification (Phase 3)
- Nothing changed; the over-flag direction verified at 92-99.

