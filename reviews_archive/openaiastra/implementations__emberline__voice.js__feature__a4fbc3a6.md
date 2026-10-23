# voice.js — Colibri feature reassessment

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/voice.js
Reviewer: GPT-6 Codex /root, in-session primary reviewer
SHA-256: a4fbc3a6430b82f4c2d9e878b3bca957f1a22acb682b356a13ed7ff63bd2551d
Bytes: 7103
Date: 2026-09-29 10:41 America/Denver
Mode: feature
Context pack: native jCodemunch tree, per-file outlines and importers; exact current runtime and caller bytes; README, AGENT_STATE, ACTIVITY, GUARDRAILS, FEATURES, REMEDIATION, DEFERRED, progression request, earlier synthesis and individual reports. Runtime browser globals were traced directly because import edges alone omit them.
Freshness: owner requested another run, interpreted and announced as forced reassessment. Source changed since prior feature review; delta checked against it. Full file read end to end; separate fresh native read matched the full hash.

## What this module does
Schedules prerecorded Emma clips and independent captions with priority, stale-state cancellation, bounded queue and current-shield tips.

## Fixed since last review
Silent captions remain implemented at 78–82/39. Since the prior source hash, reset coalescing at 65–68 lets current cleansing speech finish; urgent warnings still preempt at 48–53/86. This run confirms source structure, not human listening quality.
Prior feature record: .colibri_reviews/implementations__emberline__voice.js__feature__9307c09f.md (9307c09fe582946a2e90b416b553f353b2b527fc2de9123b04655c8c3ddf6afd). Earlier closure evidence is retained in that separate report; this review does not reopen implemented main proposals.

## Suggested add-ons
### F9: Full and concise navigator modes — Value High · Effort M
Provenance: Developed from the earlier optional tip-frequency idea, refined against the Emma queue changes; still open.

- What: Offer Full (current behavior) and Concise guidance. Concise suppresses recurring low-priority tips and routine added-cell speech while retaining docking, cleansing and urgent teleport messages.
- Why / evidence: update (94–97) schedules tips on a fixed 45-second cadence and handleEvent (69–70) queues additions. Existing choices are audio mute and independent captions; there is no category/frequency preference.
- How / hook points: Add a validated enum passed from game.js syncVoice (88) and saved in preferences. Apply filtering before queue insertion, prune disallowed queued/current low-priority messages on mode changes, and preserve current reset sentences, latest waiting reset count, urgent priority and stale inventory checks. Keep Full as default for existing saves. Define whether concise applies to both speech/captions; initial proposal applies to both while caption availability remains independently controlled. Reuse the same audio assets.

## Adversarial verification
Fresh queue and game sync reread confirms the recent repeated-reset fix; it must not be undone. Tip suppression alone is not warning suppression. Test live Full→Concise with a pending tip, silent-only mode, repeated resets, immediate warning preemption, undock/pause/hidden cancellation and invalid saved enum. Reduced distraction is PLAUSIBLE until listening/player QA.

CONFIRMED refers only to traced existing source/integration points; product benefit, rankings and effort are reviewer estimates. The proposed benefit remains PLAUSIBLE until player acceptance. No proposed behavior was implemented or tested. Preserve offline operation, sequential gardens, assigned craft, held primary versus edge-triggered FIFO reserve, legacy entry saves, mute and reduced motion. Reuse existing simulation and diagnostics rather than duplicate them. This feature review is not a fresh bug/spec clearance.

## Nice-to-haves
Manual replay should be a later, separate feature: replaying an old numerical count could give stale advice.

## Validation boundary
Baseline repository checks in this run: 37 tests, five skipped, exit 0, tree unchanged; these check existing code, not the proposed features. Final post-record checks and explicit-path commit remain separate. Browser/device/listening acceptance and automatic archived-byte readback are unverified.
