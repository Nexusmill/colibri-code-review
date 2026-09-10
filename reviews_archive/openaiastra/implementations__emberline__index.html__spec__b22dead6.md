# Reset-menu spec review
Source: C:/Users/User/source/repos/OpenAIAstra/work/reset-menu/index.html
SHA256: b22dead6fbbf77bb675b98af8095437d69949160dc762518728e06d160864ecf
Reviewer: /root/dock_music, independent of reset author
Date: 2026-09-08
Mode: spec
Context: docs/tasks/2026-09-08-emberline-reset-menu.md, exact three-file diffs and fresh source hashes, prior cleared iris UI/engine contracts, actual begin/resume/pause/input/frame/selectPreview/updateHUD paths.

## Verdict
CLEAR against reset-menu task acceptance.

## Divergences
None.

## UNJUDGEABLE HERE
Actual rendered prompt/focus behavior requires parent browser QA; source event paths and harness are checked here.

In-page hidden group has descriptive reset consequence, explicit accept/cancel button types and alert for storage failure. IDs match game handlers; original menu/lesson remains reusable. game.js cache token changes independently; no other runtime dependency change. Initial Cancel focus is assigned in source, not an accidental default submit. Existing overlay bounds and actual browser appearance remain parent QA.

## Adversarial verification
Reopened changed source and traced upstream/downstream guards. Input paths call guarded begin/resume, hidden launch controls cannot be normally activated, and focus defaults to Cancel. No finding survived refutation. Independent node --test work/reset-menu/ui.test.cjs: exit0, one Node suite wrapper with24 assertion groups. No production edits or manual paid review.
