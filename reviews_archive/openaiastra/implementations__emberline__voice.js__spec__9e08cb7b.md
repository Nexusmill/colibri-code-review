# Iris independent spec review

Source: C:/Users/User/source/repos/OpenAIAstra/work/iris/voice.js

Reviewer: dock_engine, not the voice author

SHA256: 9e08cb7bc5278da298ad59eca6c373d16092df2bf74c250312071d13a11e1516

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

## Verification / cross-file synthesis

Five existingtests pass. Independentstaleadvice reproducer above confirmed. All319 WAV hashes/lengths/PCM channels/rate/samplewidth/duration/peak match author manifest through Python wave parsing; exact perasset clearance stored separately. UI currently supplies only violetCount, so voice cannot infer other currenteffects without contract addition. Root/UI/author notified. No audio listening claim.
