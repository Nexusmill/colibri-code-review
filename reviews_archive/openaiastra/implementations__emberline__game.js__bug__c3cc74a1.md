# Reset-menu bug review
Source: C:/Users/User/source/repos/OpenAIAstra/work/reset-menu/game.js
SHA256: c3cc74a1be8a35834fc2dbd34530e4cb413805f210ead5c63bebe3fc02785d4e
Reviewer: /root/dock_music, independent of reset author
Date: 2026-09-08
Mode: bug
Context: docs/tasks/2026-09-08-emberline-reset-menu.md, exact three-file diffs and fresh source hashes, prior cleared iris UI/engine contracts, actual begin/resume/pause/input/frame/selectPreview/updateHUD paths.

## Verdict
CLEAR. No confirmed delta defect remains.

## Bugs & vulnerabilities
None.

## Missing safeguards
No required additions identified.

Reset prompt snapshots prior launch/continue/newseed visibility and hides those actions. begin/resume guard resetReturn, so keyboard/gamepad paths cannot resume/launch while it is open; gamepad edge tracking continues. Escape consumes event and restores controls. Focus starts on Cancel, while intentional native activation of the focused Reset button remains available. Acceptance removes only checkpoint; fresh E.create state resets Garden1, neutral16, three starter weapons/hearts, score0. Menu/atlas/lesson restored, preview0 and explicit Launch; no checkpoint until launch. Saved preferences/high scores untouched. Storage removal throw leaves old state/checkpoint and explicit alert. New expedition is reachable when paused. No source defect found.

## Adversarial verification
Reopened changed source and traced upstream/downstream guards. Input paths call guarded begin/resume, hidden launch controls cannot be normally activated, and focus defaults to Cancel. No finding survived refutation. Independent node --test work/reset-menu/ui.test.cjs: exit0, one Node suite wrapper with24 assertion groups. No production edits or manual paid review.
