# colibri bug review - src/film/adversary.ts (delta)

source: src/film/adversary.ts · reviewer: ZCode GLM-5.3 in-session · sha256 68ff09e3 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 7432c2d8 @ 49c2bd2 2026-08-30; cited lines re-opened fresh)
context: diff 24+6; prior review 7432c2d8 (1 HIGH, 2 MEDIUM, 2 LOW) carried; current lines 185-235 read fresh to verify each closure.

## Verdict

Shippable - the delta is exactly the remediation of the prior hunt's findings; one LOW remains open.

## Bugs & vulnerabilities

None new in the delta.

## Fixed since last review (all verified in current bytes)

- [HIGH] shorthand gate read the mandated anchor as camera/timing spec (fail-open for every world-anchored film) - FIXED: actionOf() strips the anchor before both CAMERA_TOKENS and TIMING_TOKENS tests (lines 185-186).
- [MEDIUM] SIZE_WORDS matched anchor vocabulary ("wide-brimmed hat") - FIXED: sizes judged on actionOf(s.boardPrompt) (line ~165).
- [MEDIUM] camera-token inflection asymmetry (false C on "camera zooms in"/"orbiting her") - FIXED: zoom(?:s|ing)?, dolly(?:ing)?, crane[s]?, whip(?:s|ping)?, orbit(?:s|ing)? (line 178).
- [LOW] "graded A-F" overstated B - FIXED: header now states findings emit only C/F and B is the pass threshold.
- Missing-safeguard seconds<=0 - FIXED: explicit discipline finding (lines 192-196).

## Still open (carried)

- [LOW] the 20s engine ceiling remains a hard literal (line 201) duplicating maxClipSeconds knowledge - a future >20s engine gets false C findings until this is edited. Fix: accept the cap in opts like scenario/durationSec.
- actionOf strips only the FIRST exact anchor copy (prior note, unchanged) - a near-duplicated anchor echo still inflates cram measures.

## Verified-correct (adversarial passes)

- The remediated gates traced with anchor-bearing prompts: anchor tokens can no longer satisfy shorthand/size checks; the inflection set now covers the common conjugations; worst() fold unchanged and correct.
