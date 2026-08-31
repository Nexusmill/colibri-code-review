# PatternSkin AI-selection field debug - filmstrip + part cycling
source: PatternSkin/__init__.py (sha256 57e16dd7a264c150ca792c9667eb3286c79f831cf1a4e4ded19f59e705a6d7c5, POST-fix) + PatternSkin/filmstrip.py (sha256 296dac16b906654143590aa94e58f9cc8bf617f4e0e424d4e48b219c4f1e3781)
model: claude-fable-5 (in-session) | date: 2026-08-28 | mode: debug (Phase D)
context pack: jCodemunch outlines (__init__, filmstrip), live bridge state (Damien's running 5.1.2,
dragon session), field log ~/.patternskin/logs/patternskin.log, git -S archaeology, AGENT_STATE 08-27 arc.

## Failure signals (Damien, 2026-08-28)
1. "theres no film strip, thats gone, what happened to it?" (in the AI selection area)
2. "try cycling through the parts over and over see what happens"

## Hypothesis ledger -> verdicts
- H-REG (17 sub-panels unregistered = strip gone): REFUTED. Only the root panel registers BY DESIGN;
  sub-panel classes are draw-code containers for the single-open accordion (open_ = ui_section == key,
  __init__.py:5013). ui_section was '' (all sections closed; window not rendering - root draw count 0).
  The PS_RegionItem hasattr/already-registered paradox is a bpy exposure quirk, no user impact.
- H-CRASH (_film_draw raises mid-draw, truncating the panel): REFUTED. Every internal driven live:
  _eff_pat/_pat_icon (icon 1597), token_present True, _model_status('sam3') None, thumbnails EXIST
  (~/.patternskin/ai_cache/thumbs/34ad4d36b528eadd_8/part_0.png), _part_names_read full map, _film_fit [].
- H-MOVED (strip removed from the Selection step): CONFIRMED as the root cause of the perception.
  git -S: the strip was BORN in the Pattern step (0948b28); the Selection step's in-place duplicate
  auto-texture block was RETIRED for a signpost row in 8acf4c0 (HIG pass, R4 one-home). After a scan
  finishes in step 4 the strip is one closed accordion section away; the signpost row
  ("Assign patterns per part in 2 - Pattern") did not land in the field. -> PSK-STRIP-HANDOFF (deferred,
  needs Damien's ruling; spec row will be PROVISIONAL).
- H-CYCLE (part cycling corrupts state): REFUTED mechanically. 18 consecutive ai_nav steps over the live
  8-part dragon: perfect modulo wrap (1..7,0,1..), deterministic per-part face counts across wraps
  (25708/18356/15188/20278/5707/3411/2672/116), active always in range, no errors, undo intact.
- H-CYCLE-UX (cycling FEELS broken): CONFIRMED, two defects:
  (a) F2 nav text: "Part 0/7" - zero-based over n-1, ignoring the names the paid scan produced. FIXED
      this commit: PatternSkin/ui_text.py::_part_nav_text (sha256 fd3977bf6bb39872a534ad4952f85bc5fd7800fe0de34378c4d5448a8cf895be) wired at BOTH sites
      (SELECT nav label + ai_nav INFO report). Battery tests/harness/probes/ai_nav_names.py (pure, RED
      first) + headless bpy live-drive green ("'lid' - part 1/2 (3 faces)" / "'base' - part 2/2 (3 faces)").
  (b) F3 scan output quality: part 0 = 'dragon' (25,708 faces) - the unmatched-remainder bucket inherits
      the whole-model caption name; tail fragmented into 'tail'/'tail 2'/'tail 3' (116-face sliver).
      Cycling parades these. -> PSK-SCAN-PARTQ (deferred; expected-outcome spec needs Damien's ruling).
- film_edit == -9: REFUTED as a bug - documented 'no slot open' sentinel (default -9).

## Live-session hygiene
All instrumentation removed; scene state restored exactly as found (ui_section '', active part 0
reselected, 25708 faces). Damien's session still runs the PRE-fix nav text until the add-on reloads
(restart or the sys.modules purge + re-enable recovery); the fix is source-side.

## Verdict
No filmstrip regression exists; the field perception traces to the 8acf4c0 one-home cleanup without a
strong-enough post-scan handoff (ruling owed). Cycling mechanics sound; nav text fixed (F2); scan part
quality docketed (F3). First spec rows for this surface land in pilot T4 with statuses from this record.
