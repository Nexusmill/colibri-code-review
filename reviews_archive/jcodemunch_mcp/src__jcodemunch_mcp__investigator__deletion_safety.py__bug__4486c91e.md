# Colibri review — src/jcodemunch_mcp/investigator/deletion_safety.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\investigator\deletion_safety.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `4486c91efb8ad1db918c5632f84845d2b88b06eba640c321fb19cdfcd98f5687` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: DELTA against the prior record `…deletion_safety.py__bug__fd3453f2.md` (2026-09-05; three fixes landed 2026-09-06 - see below); the sub-agent's summary (1 CONFIRMED with a RED probe, 0 refuted); Obligation 3 `no_textual_use` 349-410 (`search_text(repo, target_name)` at the 20-line default, only `hits["error"]` inspected, `other_files` from `hits["results"]`); `tools/search_text.py` 88 (`max_results` clamped to 1..100), 128-198 (`truncated` when the line count hits the cap - the outer file loop `break`s too; `timed_out` on the regex budget; both reported in `_meta`); `_split_importers_by_liveness` 94-135 + `_looks_like_root` 142-149 (zero-importer files are unreachable unless root-shaped; unclassifiable counts as reachable); `_verdict` (UNESTABLISHED never yields safe/static_clear). Tests: `tests/test_investigator_deletion_safety.py` (real fixture, no `search_text` mocking), `tests/test_deletion_safety_roots.py`.

## Verdict
The module's one rule - an obligation the evidence cannot settle stays UNESTABLISHED - had a hole via truncation: a text sweep that stopped early inside the target's own file read as "appears only in its own file". Closed; a hit still refutes whether or not the sweep finished.

## Fixed since last review
- All three fd3453f2 fixes are PRESENT on these bytes (re-verified, verified-stale, not re-fixed): the zero-importer root heuristic (`_looks_like_root`, 116-123/138-149), the `deletion_cluster` override gated on `verdict in (SAFE, STATIC_CLEAR)` (530), and the text-sweep `error` branch leaving the obligation UNESTABLISHED (367-371/380-381). This finding is the same hole as the third one, reached through truncation instead of failure.

## Bugs & vulnerabilities
**[HIGH] `no_textual_use` SATISFIED when the `search_text` sweep truncated before scanning the whole repo — CONFIRMED — FIXED** - `line 365, 374-379, 402-406`
- What: `search_text` stops the moment it has `max_results` matching lines (20 by default, 100 at most) and stops scanning FILES too; it says so in `_meta.truncated` (and `_meta.timed_out` for the regex budget). The obligation never read `_meta`, so a target whose own file mentions its name ≥ 20 times (comments, recursion, docstrings) exhausted the budget before the scan reached the file that references it - string dispatch, exactly what this obligation exists to catch - and `other_files == []` produced SATISFIED, `static_clear`, and "nothing in the code references this". Trigger (audit probe, RED on these bytes): 30 self-mentions in `src/a_target.py`, `ACTIONS = {"doWidgetThing": None}` in `src/zzz_dispatcher.py` → `static_clear`.
- Fix: the sweep runs at `max_results=100` (the tool's maximum); `swept_incomplete = _meta.truncated or _meta.timed_out`. A hit in a live file REFUTES whether or not the sweep finished (a hit is a hit). With no live hit: if the sweep stopped early the obligation is UNESTABLISHED with evidence naming why it stopped and that the rest of the repo was not scanned (`detail.sweep_incomplete = True`) - both when every match was in the target's own file and when the only matches were in unreachable files; a COMPLETE sweep keeps both SATISFIED outcomes unchanged.

## Refuted / recorded
- The audit probe now passes through the module's liveness rule instead: at the 100-line cap its 30 self-mentions no longer truncate, the sweep reaches `zzz_dispatcher.py`, and that file - zero importers, not root-shaped - is classed unreachable, so the obligation is SATISFIED "only in unreachable files" by the fd3453f2 design, not by truncation. The battery reproduces the truncation case at 120 mentions (above the hard cap) and pins it UNESTABLISHED; the probe's expectation that a dead dispatch table counts as a use is a question for the liveness rule, out of this finding's scope.
- Missing safeguards, disclosed not filed (per the sub-agent and the module's own comment at 121): `_looks_like_root` is path-shape only (a bare root-level script elsewhere with zero importers is misclassified dead); `deletion_cluster` is populated only from Obligation 2's dead importers, never from Obligation 3's dead-file matches (a design choice that understates the cluster).

## Adversarial verification (Phase 3)
- Pinned end to end through `investigate_deletion_safety` over a real `index_folder` index; each test first asserts what `search_text` itself reports (`_meta.truncated`, which files it reached), so a change in the tool's scan order or cap would surface as a fixture failure, not a silent pass.
- RED on the old bytes: own-file-only truncation → UNESTABLISHED (was SATISFIED); unreachable-only hits + early stop → UNESTABLISHED (was SATISFIED). Controls green throughout: a live-file hit refutes even when the sweep then stops (`bin/` is root-shaped, sorts before `src/`); a complete sweep with no other mention is SATISFIED; a complete sweep with only unreachable mentions is SATISFIED with the same `detail` as before.
- `tests/test_investigator_deletion_safety.py` + `tests/test_deletion_safety_roots.py` unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `01dc3728af550bfa00fa0669c2423f44c221cf78d78d6119531cc93cfc1da956`. TDD: `tests/test_deletion_safety_reaudit.py` (5 tests) - 2 RED on the old bytes, 3 controls green throughout, GREEN after.
