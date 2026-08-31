# ULTRA GATE: PatternSkin/__init__.py - /code-review ultra run 1 verification

- Source: PatternSkin/__init__.py - reviewed snapshot tree c0ce0d0 (audit/ps-part1), ZERO drift vs working tree at gate time; post-fix sha256 f3282ecac977441a
- Model: claude-fable-5 (in-session gate) over cloud ultra findings - Mode: external-review verification (G37 external-second-opinion law) - Date: 2026-08-13
- Context pack: remediation manifest + 7 prior __init__ colibri reviews cross-checked; source regions 1820-1831, 4870-4899, 5455-5494, 7300-7344, 7440-7481, 1049-1065 read at current bytes.

## Input
/code-review ultra (cloud, free run 1) on audit/ps-part1 (core-runtime snapshot, 10 files / 11,475 lines): 7 raw findings -> 4 verified by ultra's own pipeline. All 4 entered this gate.

## Verdicts (4/4 CONFIRMED, 0 verified-stale, 0 refuted)
- bug_001 [CONFIRMED - worst] NameError `box` line 4885 in the one-click-update banner branch; scope holds lay/hb/r/_bi only; fires for every user the moment a verified release is advertised; panel = sole entry point. FIXED (ultra-gate-1): lay.box().column(align=True).
- bug_004 [CONFIRMED - nit] sel_subsection default STD vs keys SEL_STD/SEL_ADV/SEL_AI (compare at 5464; call sites 5477/5487/5531). FIXED (ultra-gate-1): default SEL_STD.
- bug_005 [CONFIRMED - deferred PSK-ULTRA-5] restore path (1057) caches labels=None/tp=None; consumers 7441/7470/7473 unguarded; every OTHER cache write (6681/6791/7110/7222/7395) stores real tp - the restore path is the sole outlier. Needs Blender-verified lazy-rebuild fix.
- bug_006 [CONFIRMED mechanism - deferred PSK-ULTRA-6] _ap_pp snapshot (7311) reused across mesh-rebuilding iterations (7320/7328-7334). Fix precondition (ps_ai_part attr survival through subdivide) unverifiable from source - needs the Blender experiment before the re-read fix lands.

## Notes
- None of the four appear in the manifest or the seven prior __init__ reviews (nearest neighbor: dbb85879 _ap_start_current queue-advancement finding - different defect).
- Ultra's find->verify->dedupe pipeline discarded 3 of its own 7 raw findings before reporting; the 4 that survived all confirmed here. Strong signal for the tool on a repo it has never seen.
