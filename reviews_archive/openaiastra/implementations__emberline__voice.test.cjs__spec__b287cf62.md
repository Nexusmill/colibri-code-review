# Iris independent spec review

Source: C:/Users/User/source/repos/OpenAIAstra/work/iris/voice.test.cjs

Reviewer: dock_engine, not the voice author

SHA256: b287cf62b7514bd0e5c8a2760d35a5ea58e72d928ecc0e6c1548c5a27e04ad7b

Date: 2026-09-08

Mode: spec

Context pack: iris-worlds task and root-provided actual user clause; engine dock/reset/shieldchange/time events; provisional UI syncVoice/consume; prior author report.

## Verdict

BLOCK: contextual advice diverges from requested current-effect behavior.

## Divergences

Expectation: 'occasionally it should say how your shield items are effecting you'. Root explicitly rules this includes current restored effects and excludes advice for cleared effects.

**[MEDIUM] Advice is not tied to current shield effects** — voice.js lines63,83-85. CONFIRMED. The owner asks for occasional explanation of how shield items are currently affecting the ship. Pending advice survives final cleansing or expiration for up to30s; restored shields have no insertion event so never seed advice. Reproducer: add-black2, complete audio, reset-black remaining0, complete audio, update time20 -> tip-black.wav despite no blackcells. Fix: pass currentcounts snapshot fromUI, select present effects periodically, prune queued/current advice on disappearance. Add regression for fullclear, beneficial expiry and restoredshield.

## UNJUDGEABLE HERE

Real voice playback and subjective quality need parent listening. UI is provisional and separately reviewed.

This test file has no execution bug identified, but its five tests miss current-effect advice conformance: expiry, fullclear and restoredshield. Add real lifecycle assertions. Overall tranche remains blocked by the production source finding.

## Verification / cross-file synthesis

Five existingtests pass. Independentstaleadvice reproducer above confirmed. All319 WAV hashes/lengths/PCM channels/rate/samplewidth/duration/peak match author manifest through Python wave parsing; exact perasset clearance stored separately. UI currently supplies only violetCount, so voice cannot infer other currenteffects without contract addition. Root/UI/author notified. No audio listening claim.
