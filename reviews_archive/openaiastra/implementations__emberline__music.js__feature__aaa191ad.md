# music.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/music.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: aaa191ad12f4739b5567b5f5efee1f6ab366d38bf541851c1cde17f06cb5a57a
Bytes: 7166
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Creates 50 deterministic scores, exports equivalent MIDI note events, and schedules bounded WebAudio voices with pause/mute/visibility gating.

## Suggested add-ons
### Lower soundtrack volume while Iris speaks — Value High · Effort S
- What: Add narration ducking and optionally a music-volume preference so spoken warnings remain distinct from the soundtrack.
- Why / evidence: createPlayer() line 71 fixes the music bus gain at .28; update() lines 93–107 handles play state but no duck amount. voice.js emits onDuck true/false at lines 26 and 37, but game.js unlockVoice() line 79 supplies only onCaption.
- How / hook points: Add a bounded gain-control method/state field that ramps the existing bus to a reduced level while narration is active and restores the configured level on completion, cancellation or failure. Wire onDuck in game.js, retaining duck state if the music player is created later. Keep compose() and toMidi() note events unchanged.

## Adversarial verification
CONFIRMED missing integration: freshly traced voice callback → absent game binding → fixed bus gain. Existing separate mute controls are not volume ducking. Benefit to intelligibility is PLAUSIBLE until listening QA. Future tests should preserve beat/cursor, enforce global mute, restore gain after interrupted/missing audio and avoid gain spikes or extra oscillators.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
Display the current composition title from compose(). PLAUSIBLE low-effort polish; avoid extra sound playback or an autoplay jukebox.
