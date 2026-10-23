# Colibri review — src/jcodemunch_mcp/tools/render_diagram.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\render_diagram.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `9e0a155a7858489e34e6045eff8b6ab26ba677541512270c7b040ed12b989995` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `get_file_outline` (`_sanitize_label` 132, `_UNSAFE_RE` 124 for ids, seven renderers, `render_diagram` 1033-1113 with `_PALETTES.get(theme, _PALETTE_FLOW)` at 1059 and `_meta` at 1094); `_render_signal_chains` 440-561 (fixed six-kind tuple at 467 and 507; orphan note at 546 indexing `selected_chains[0]`); the producer `tools/get_signal_chains.py` `_classify_gateway` 88-111 + `_KIND_ORDER` 76-81 (emits exactly http/cli/event/task/main/test today - the unknown-kind path is reachable only through a caller-supplied `source`, which the tool accepts verbatim); `tools/mermaid_viewer.py` `open_diagram` 106 (writes a `.mmd` temp file and spawns an external viewer - no HTML embedding, so the injection primitive is Mermaid-statement-level, not script-level); existing `tests/test_render_diagram*.py` (105 tests); both RED probes re-run on these bytes (probe 1: 2 FAIL, probe 2: 1 FAIL). No prior `.colibri_reviews` record.

## Verdict
Every label the renderers emit is untrusted data from the source payload, and one newline in it ended the statement and started another. Three findings confirmed and fixed; the sub-agent's own XSS escalation of the first stays refuted.

## Bugs & vulnerabilities
**[HIGH] `_sanitize_label` did not fold line breaks - a newline in a label starts an attacker-shaped Mermaid statement — CONFIRMED — FIXED** - `line 132-134`
- What: quotes and angle brackets were escaped, `\n` / `\r` were not. A symbol name, route label or summary carrying a newline (the payload is whatever the caller passes as `source`) closed its `nd["..."]` / `Note over ...:` statement and the remainder landed as its own line - probe 2 placed an unquoted `style nd0 fill:#000000` override verbatim outside the label's node. Corrupts the diagram for every consumer (mmd-viewer, VS Code / GitHub previews).
- Fix: `\r\n`, `\r`, `\n` folded to spaces before the existing escapes; every renderer routes labels through this one function. Ids were already reduced by `_UNSAFE_RE` to `[A-Za-z0-9_]`.
- Refuted (sub-agent's own, agreed): the escalation to a functional `click <id> href "javascript:..."` - the `"` -> `'` substitution already broke the quoted href, and the viewer path writes a file for an external renderer rather than embedding into HTML.

**[MEDIUM] `_render_signal_chains` dropped every chain of a kind outside its six, and crashed (IndexError) on the orphan note when none remained — CONFIRMED — FIXED** - `line 467-472, 544-546`
- What: the selection loop iterated a fixed tuple; a payload whose chains are all another kind rendered nothing and, with `orphan_symbol_pct > 0`, raised out of the tool. The producer emits only the six kinds today, so this is reachable through a caller-shaped or future payload - the sub-agent's HIGH is downgraded to MEDIUM on that basis (a crash on untrusted input, not a loss on the shipped producer's output).
- Fix: known kinds first in their fixed order, then any other kind in first-seen order (capped and counted like the rest); the orphan note anchors on the first selected chain when there is one and on `System` otherwise.

**[MEDIUM] an unknown theme fell back to `flow` while `_meta.theme` echoed the unapplied request — CONFIRMED — FIXED** - `line 1059, 1096`
- What: `_meta.theme` is the response's statement of what was rendered; it named a palette that does not exist. Probe 1 reproduced it (`theme="neon"` -> `_meta.theme == "neon"`, flow palette applied).
- Fix: `_meta.theme` names the palette applied; `_meta.theme_requested` carries the request when it differs. One existing test updated: `tests/test_render_diagram.py::TestThemes::test_invalid_theme_defaults_to_flow` asserted the echo (`# theme name recorded as-is`) with no rationale for it - unlike the `strategy_applied` case in assemble_task_context, where a distinct field carried the truth and the test explained why, here the only field lied and nothing else carried the applied palette. The test now asserts both fields.

## Missing safeguards
- `render_diagram` accepts any dict as `source`; every renderer indexes optimistically (`chain.get(...)` guards most, but shape errors deeper than `_detect_source`'s key signature still surface as exceptions). Not traced to a concrete crash beyond the one above; noted.

## Adversarial verification (Phase 3)
- The newline test asserts both that the injected line is gone AND that the folded label survives in its node (the label is data, not to be dropped).
- Unknown kinds: one test mixes a known and an unknown kind and asserts both chains' edges render with `pruned_count == 0`; another has only unknown kinds plus an orphan percentage - the exact crash input.
- Theme: both the fallback (`neon` -> `flow` + `theme_requested`) and a real theme (`risk`, no `theme_requested`) are asserted.
- All four render test files: 108 passed, 2 skipped on the new bytes.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `b73387483ea7e747f6a72934686a40f2296dfe61044b21d6b7711d46d08d8559`. TDD: `tests/test_render_diagram_reaudit.py` (5 tests) - all 5 RED on the old bytes, GREEN after; probes 1 and 2 ALL PASS.
