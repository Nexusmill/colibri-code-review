# voice.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/voice.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: 3121593a917c09e147e8e6121015f266838786902f64b0abd60d11fc06b653f8
Bytes: 6582
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Offline Iris narration and captions using known clips, event priority, stale-message cancellation, present-inventory tips and a truthful teleport warning.

## Suggested add-ons
### Captions that can stay on with voice audio off — Value High · Effort M
- What: Offer a caption-only narrator mode with bounded reading duration, independent of audible speech.
- Why / evidence: pump() lines 32–42 emits a caption then creates/plays audio; clearCurrent() lines 23–26 clears both. update() lines 73–74 disables the entire narrator on muted. game.js syncVoice() line 78 combines Sound/Iris mute and unlockVoice() line 79 couples caption delivery to the audio-backed player.
- How / hook points: Separate notification scheduling from audible output, keep the same priority and stale-state checks, and provide explicit caption/audio preferences. In caption-only mode do not create Audio or emit an audio-duck signal. End text after a bounded reading interval, earlier when invalidated; keep hidden/pause/reset cancellation. Update game.js so captions do not depend on audio permission.

## Adversarial verification
CONFIRMED static opportunity: existing captions are present, but silent operation with retained captions is not. Re-read removal, stale-tip, warning, mute and failure paths to avoid resurrecting already fixed stale advice. Test caption-only with audioFactory that throws if called, muted audio, interrupted reset/warp messages and elapsed reading lifetime. Accessibility usefulness needs user QA.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
Offer concise versus detailed tip frequency later. PLAUSIBLE: preserve urgent warnings and already implemented priority/bounded-queue rules rather than adding uncontrolled chatter.
