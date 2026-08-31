# Colibri Review — bug — PatternSkin/__init__.py

- **Source path:** `PatternSkin/__init__.py`
- **Reviewer:** self (Claude, in-session), Colibri G37 protocol
- **sha256:** `dbb8587988b28bff1bbc00dd982fa504a74c73adb329c54d4ae798320ab72100` (sha8 `dbb85879`) — bytes as committed after this review's own fixes
- **Date:** 2026-07-27
- **Mode:** bug
- **Scope note:** this review targets the code ALTERED this session (PSK-2 + PSK-6 remainder),
  not the entire ~400KB file — the user's instruction was "a bug hunt on altered files", and a
  from-scratch full-file review of every one of ~450 symbols is out of scope for that request.
  Altered surface: `_apply_prepare`, `_subdivide_stepwise`, `apply_pattern`, `_apply_pattern_rest`,
  `_apply_pattern_begin`, `_PSCancellableApply`, `PATTERNSKIN_OT_apply`, `_batch_apply`,
  `_bake_regions`, `_ai_bake_parts` (PSK-2); `_update_seam_score`, `_on_pick_library(2)`,
  `PATTERNSKIN_OT_choose_pattern`, `PATTERNSKIN_OT_make_seamless`, `PATTERNSKIN_PT_pattern.draw`,
  `PatternSkinSettings.ps_seam_score(2)` (PSK-6 remainder).
- **Context pack:** `mcp__jcodemunch__get_blast_radius` on `apply_pattern` (confirmed callers:
  `tests/harness/bpy_patternskin.py` x4 - all through the plain `apply_pattern()` function,
  unaffected by the operator-level refactor; `PatternSkin/projections.py` - comment references
  only). `mcp__jcodemunch__search_text` for `s.pattern = ` / `s.library_item = ` across the file
  to find every OTHER site that sets the active pattern outside the pick paths PSK-6 wired
  directly. `docs/deferred_manifest.json` PSK-2/PSK-6/PSK-18 entries and `docs/remediation_manifest.json`
  for prior findings in this file (checked none of today's findings were already logged there).
  `junk/psk2_verify.py` / `junk/psk6_verify.py` headless runs (real package-imported add-on, not
  `tests/test_blender_smoke.py`'s raw exec()) as the ground truth for "does this still behave
  like before" rather than reasoning alone.

## Verdict
Shippable after the fixes below (all applied in this same pass, not just reported). The single
biggest risk found was a resource leak + API-misuse pattern in `_PSCancellableApply._ps_start`
that only manifests on the interactive multi-item queue path (batch_apply/bake_regions/
ai_bake_parts run from a real windowed session) — structurally invisible to headless testing,
which is exactly why a code-tracing review (not just "the tests pass") was necessary here.

## Bugs & vulnerabilities

**[MEDIUM] Timer leak + redundant `modal_handler_add` on every item after the first in an
interactive multi-item queue** — `_PSCancellableApply._ps_start` (originally ~line 560)
- What: for `batch_apply`/`bake_regions`/`ai_bake_parts`, `_ps_item_done` advances to the next
  queued item by calling `self._ps_start(...)` again on the SAME operator instance, from inside
  `modal()`'s own call stack. The original code unconditionally did
  `self._ps_timer = wm.event_timer_add(...)` (overwriting the reference to the PREVIOUS item's
  timer without ever calling `event_timer_remove` on it) and unconditionally called
  `wm.modal_handler_add(self)` again, even though Blender already owns this instance as the
  active modal handler from the first item's registration.
- Trigger: any INTERACTIVE (real window) batch_apply/bake_regions/ai_bake_parts run over 2+
  objects/regions/parts. Never triggers in background mode (the only mode headless testing can
  exercise), which is why `junk/psk2_verify.py`'s original pass didn't catch it.
- Impact: a leaked `wm.event_timer_add` handle per item beyond the first (Blender timers are a
  finite, if generous, resource - a long batch run leaks one per item, never cleaned up until
  Blender exits); calling `modal_handler_add` again while already the active handler is not this
  API's documented use and its exact runtime consequence (silently ignored vs. duplicate TIMER
  dispatch) could not be fully traced from Python alone - flagged PLAUSIBLE for that specific
  part, but the timer leak itself is CONFIRMED by direct reasoning (an overwritten reference to
  an un-removed resource is unconditionally a leak, no ambiguity).
- Fix: `_ps_start` now calls `self._ps_stop_timer(context)` before creating the new timer (so
  each item's timer replaces rather than leaks the previous one), and only calls
  `wm.modal_handler_add(self)` once per operator instance, guarded by a new `_ps_modal_registered`
  flag. Applied directly in the same edit (not deferred).
- Verification: CONFIRMED by code trace (the leak); PLAUSIBLE-noted for the double-registration
  consequence (needs a live windowed session to observe Blender's actual behavior either way -
  the fix is correct regardless of which behavior it would have caused).

**[MEDIUM] No guard against a second concurrent apply on the same object** — `PATTERNSKIN_OT_apply`
/ `_batch_apply` / `_bake_regions` / `_ai_bake_parts` (via `_PSCancellableApply._ps_start`)
- What: before this session's PSK-2 refactor, `Apply` was one uninterruptible synchronous call,
  so Blender's entire UI froze for its duration - a second `bpy.ops.patternskin.apply()` on the
  SAME object mid-apply was structurally impossible (nothing could process the click that would
  trigger it). PSK-2 deliberately makes the UI stay responsive while an apply runs (that is the
  point of Esc-cancellability) - which means a user CAN now click Apply again on the same object
  while a previous apply is still mid-subdivision. The original code had no guard for this: a
  second call would start a second `_subdivide_stepwise` generator against the same live mesh;
  since `bm2.to_mesh(me)` only happens once each generator's loop completes, whichever finishes
  LAST silently overwrites/discards the other's work with no error, no warning, no way to tell
  which apply "won".
- Trigger: interactive double-click of Apply/batch_apply/bake_regions/ai_bake_parts on the same
  object before the first invocation finishes. Requires a real window (the async gap PSK-2
  itself introduces); genuinely new risk class this session created, not a pre-existing gap.
- Impact: silent data loss of one apply's settings/result with no user-visible error - the worst
  kind of concurrency bug (wrong answer, not a crash).
- Fix: added a module-level `_PS_APPLY_BUSY` name-keyed set; `_ps_start` refuses (raises
  `RuntimeError` with a clear message) a second apply on an object already in the set, releasing
  the entry on every exit path (success, failure, Esc-cancel, Blender-forced `cancel()`, and the
  background-mode synchronous branch via `try/finally`).
- Verification: CONFIRMED, and now covered by an automated regression check in
  `junk/psk2_verify.py` (`bpy.ops.patternskin.apply()` on a pre-marked-busy object raises the
  expected message; the guard clears and a normal apply succeeds afterward) - 0/N failed.
- Residual, accepted limitation (LOW, not fixed): the guard keys on `obj.name`, matching every
  OTHER per-object cache in this file (`_AI_PARTS_CACHE[obj.name]`, `_APPLY_LOG`'s `obj.name`
  entries) - a rename mid-apply followed by a NEW object reusing the freed name could in
  principle collide with an orphaned busy-set entry, causing one false "already busy" refusal.
  Not fixed: this is the file's existing, accepted identity convention throughout, and the
  failure mode is a mildly annoying false refusal (with a clear message and no data loss), not
  silent corruption - switching this one guard to `id(obj)`/`obj.as_pointer()` while everything
  else keys on `.name` would be an inconsistency for a very low-likelihood, low-severity case.

**[LOW] Three pattern-setting sites left `ps_seam_score` stale after the PSK-6 remainder shipped**
— `PATTERNSKIN_OT_generate_ai.execute()`, `PATTERNSKIN_OT_generate_grip.execute()`, `_load_preset()`
- What: PSK-6 wired the seam-score indicator into `_on_pick_library`/`_on_pick_library2` (the
  thumbnail click), `PATTERNSKIN_OT_choose_pattern` (external browse), and
  `PATTERNSKIN_OT_make_seamless`. Three OTHER call sites also set `s.pattern` directly and were
  missed in the first pass: the AI-texture generator and the grip generator (both of which
  already run the result through `make_seamless()` internally, but never told the panel that),
  and `_load_preset()`'s `except Exception: pass` fallback when `s.library_item = found` fails
  because the preset's pattern is an external file not in the currently-scanned library folder
  (in that branch specifically, `_on_pick_library`'s update callback - which would otherwise have
  scored it - never runs at all, since the failed enum assignment raises before Blender would
  invoke the callback).
- Trigger: generate an AI/grip texture, or load a preset whose pattern lives outside the current
  library folder, right after having picked a DIFFERENT pattern that left a stale score behind.
- Impact: the "Wrap seam: good/visible" indicator this session just built would show a WRONG,
  leftover score for the newly-active pattern - misleading exactly where PSK-6 was supposed to
  help.
- Fix: added `_update_seam_score(s, 1)` calls at all three sites (in `_load_preset`, moved outside
  the try/except so it always runs once `pat_type`/`found` resolves, regardless of which branch
  of the `library_item` assignment ran).
- Verification: CONFIRMED by code trace (each site's control flow before/after is unambiguous);
  not separately re-run through `junk/psk6_verify.py` (which doesn't exercise
  generate_ai/generate_grip/presets), but the fix is a single extra call to an already-verified,
  side-effect-free function (`_update_seam_score`), so the marginal risk of the one-line addition
  itself is judged negligible rather than requiring a new harness for three call sites this pass.

## Missing safeguards
- No test coverage (headless or otherwise) for the INTERACTIVE modal path at all - by
  construction, nothing in this repo's test suite can exercise a real Blender window + event
  loop, so the timer-leak fix and the actual point of PSK-2 (Esc really cancelling) remain
  reasoned-but-unverified pending the user's live Blender/MCP-bridge session.
- `PATTERNSKIN_OT_generate_ai`/`generate_grip`'s existing `_previews_reset()` calls are close
  enough to the new `_update_seam_score()` calls that a future refactor merging them into a
  single "just picked a new pattern" helper (covering `_previews_reset` + `_update_seam_score`
  together) would make it structurally impossible to add a fourth pattern-setting site without
  the score update - noted, not done here (would touch more call sites than this pass's scope).

## Adversarial verification pass
- Re-traced the busy-guard against every one of `_ps_start`'s callers (`PATTERNSKIN_OT_apply`,
  `_batch_apply`'s `_bq_start_current`, `_bake_regions`'s `_br_start_current`,
  `_ai_bake_parts`'s `_ap_start_current`) to confirm sequential same-operator queue items never
  false-positive against each other (each item's busy flag is released via `_ps_release_busy()`
  before the NEXT item's `_ps_start` call happens, in both the modal and the background-sync
  branches) - CONFIRMED no false positives within one operator's own queue, only across separate
  `bpy.ops` invocations.
- Checked `cancel(self, context)` overrides in `PATTERNSKIN_OT_apply` and `_batch_apply` both
  call `super().cancel(context)` FIRST (so the mixin's `_ps_close_gen`/`_ps_release_busy`/
  `_ps_stop_timer` always run before the subclass's extra rollback) - CONFIRMED.
- Traced `get_blast_radius` for `apply_pattern` to confirm every real (non-wildcard) call site
  goes through the plain function, not the new operator classes, and is therefore byte-identical
  in behavior to before this session - CONFIRMED, and cross-checked live via
  `junk/psk2_verify.py` (direct `apply_pattern()` vs. `bpy.ops.patternskin.apply()` produce
  identical geometry within float noise).
- Considered whether the busy-guard's `RuntimeError` breaks any existing caller that expects
  `execute()`/`invoke()` to always return a result dict rather than raise - `bpy.ops`'s own
  documented behavior is to raise for an operator that reports ERROR and returns CANCELLED when
  called from Python, which is exactly what happens here (the guard reports ERROR, returns
  CANCELLED) - CONFIRMED this is the intended, standard Blender pattern, not a new failure mode
  callers weren't already handling for every other `self.report({"ERROR"}, ...)` in this file.
