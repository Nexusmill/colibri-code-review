# hy4 spec-conformance run - top 5 PatternSkin files (gate record)
model: tencent/hy4-preview (effort high; ai_parts+accel re-run at medium after 64k reasoning
exhaustion returned no content) | date: 2026-08-30 | mode: spec (expectations = spec-harness
controls + features registries, per-file packs + 15-item already-fixed context)
dispatch shas: __init__ b370104579e5331b / filmstrip 2bbb0778e055d6ef / replicate eb311bdf798d22be
raws: .hy4_reviews/PatternSkin__*__spec__2026-08-30.md
verdicts below are the COLIBRI GATE (every finding re-verified against current bytes).

## CONFIRMED (8 total: 5 below + 3 in the ADDENDUM)
1. HIGH  MULTIVIEW SCAN ABORTS ON FIRST FAILURE (__init__.py:7222) - PATTERNSKIN_OT_ai_parts.modal
   hard-CANCELLEDs the whole paid scan on the first SAM-2 error; the named scan (7648) has the
   missed-vote + 3-streak tolerance the contract states. GATE ADDENDUM: text-select (7440) has the
   SAME hard abort. Provenance note: the multiview row's streak clause was generalized by the spec
   author from the named-scan ruling (d82f8de) - intent plausible (money-safety parity), Damien
   confirms before code moves. -> HY4-MV-STREAK
2. MEDIUM FILM_CELL TOGGLE-OFF RELEASES FACES ONLY (filmstrip.py PATTERNSKIN_OT_film_cell.execute)
   - deselect clears polygons but leaves the part's vert/edge selection; the stale verts flush
   back UP on the next edit-mode entry (the exact accumulation class of the 2026-08-29 field bug).
   -> HY4-FILMCELL-DESELECT
3. MEDIUM DRESS SHARE THRESHOLD UNENFORCED (filmstrip.py:310 + _dress_majority_part) - registry
   row PS-FILMSTRIP promises 'ONE scan part with high share (>=0.6)'; the helper returns the
   argmax share and NO caller compares it to anything - a 0.35-share mismatch silently assigns a
   paid texture to the wrong part. The E2E fixture passes only because its share is high.
   -> HY4-DRESS-SHARE
4. LOW   SEL_TEXT PRICE NOT ON THE CONTROL (__init__.py:5633) - icon-only button, ~1-cent price
   lives in the tooltip only; every other paid scan button carries '(~$X.XX)' in its label (G19).
   -> HY4-G19-SELTEXT
5. LOW   REGISTRY ROW STALE: PS-PRESET-AUTOLOAD says the '__none__' sentinel 'changes NOTHING
   else', but _load_preset (:4715) ALSO resets s.mode='AUTO' - and the code comment documents that
   as a DELIBERATE field-bug fix (stale CYLINDRICAL starburst). The ROW is wrong, not the code.
   Also sharpen PS-FILM-FIT-FIX's ambiguous 'readout names the minimums' (satisfied by the alert
   row's '(%.2f nozzle / %.2f layer)'; hy4 read it as min_depth/min_tile on the op report).
   -> HY4-REGISTRY-STALE

## REFUTED (3, deleted per G37 - recorded here only as calibration)
- 'ps_film_sel never set on select': set INSIDE _ai_select_polypart (__init__.py), which
  film_cell calls - cross-file blindness, the known single-file-reviewer failure class.
- 'draw() does network I/O via _model_status': its docstring + body are a CACHED wrapper
  ('never raises, never networks'); the disk half traced to the context pack OVERSTATING the
  canon (G20 forbids NETWORK in draw; isfile/token reads are the codebase's accepted pattern).
- 'fit-fix readout omits the minimums': the alert-row readout names them as authored; clause
  ambiguity, folded into HY4-REGISTRY-STALE as a wording sharpen.

## Files clean vs their packs
replicate_client.py - every judgeable clause satisfied (UA injection, HTTPException billed
framing); everything else correctly deferred. ai_parts.py + accel.py verdicts pending the
medium-effort re-run (first run burned the 64k completion ceiling on reasoning - tool
follow-up docketed: cap/retry on empty+ceiling).

## ADDENDUM - medium-effort reruns gated (ai_parts + accel)

ai_parts.py (sha e19dee3c5c1e53ca): CLEAN - zero divergences on everything living in the
file (money guards, lineage, empty-zip, checkpoint/resume, caches, finalize naming +
absorb incl. the day-old PARTQ code); 26-row deferral ledger interlocks with the __init__
review (it defers the streak clause to the modal, where CONFIRMED #1 lives).

accel.py (sha ded218ea37a3e563): 3 findings, ALL CONFIRMED at the gate:
6. MEDIUM WARMUP vs DEP-LOCK CONTRACT CONFLICT (accel.py:1623 warmup; called from
   register(), __init__.py:8784, as the documented PSK-17 warm-up). PS-DEP-LOCK says
   in-process import of lockable deps happens ONLY at genuine use time; warmup background-
   imports cupy/torch at EVERY startup. finish_pending_installs_async (:8734) runs first
   but is ASYNC - warmup can race a completing install and import a half-written package
   (the self-lock disease in a narrow window). Two recorded intents collide (PSK-17 vs
   DEP-LOCK); downgraded from hy4's HIGH because pending installs are the main vector and
   they are handled. -> HY4-ACCEL-WARMLOCK
7. MEDIUM PROBE_TIMEOUT KNOB UNWIRED - listed in _config's documented env knobs (:1304)
   but no _config("probe_timeout") exists; probes hardcode 90/240s. -> HY4-ACCEL-PROBETIMEOUT
8. LOW-MED SCIPY nearest() MISSING k CLAMP (:923) - scipy branch passes k raw while
   numpy/mathutils clamp to tree size; k > len(tree) returns out-of-bounds indices from
   the scipy backend only, breaking the all-backends-consistent clause. -> HY4-ACCEL-KCLAMP

## Cost (actual, G11 honesty)
~$0.70 total vs the ~$0.27 estimate: outputs ran 3-9x the guess and two high-effort calls
burned 64k reasoning tokens each with no answer ($0.32 lost, re-run at medium ~$0.06).
