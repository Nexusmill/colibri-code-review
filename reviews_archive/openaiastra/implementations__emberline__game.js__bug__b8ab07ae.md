# Initial UI review — findings awaiting correction
Source: work/iris/game.js
Reviewer: /root/dock_music, independent of UI author
SHA256: b8ab07aec5992bac3b5233903beb961ed2c571cad4df9602e7d9a4f0e4a87ca0
Date: 2026-09-08
Mode: bug
Context: Iris task spec; exact engine/terrain and voice contracts; prior cleared docking UI; current UI diff, caller transforms and test harness. No production edits.

## Verdict
Hold. Two confirmed UI regressions require correction. Parent also holds browser rendering acceptance independently.

## Bugs & vulnerabilities
**[MEDIUM] Iris control does not expose actual mute state — line 82**
settings() updates sound/music/motion only. Voice click line96 changes saved.voiceMuted and calls settings(), but no code updates voice text or aria-pressed. The static HTML says Iris on/false even when persisted voice mute is true. Audio silencing itself works. Fix settings state feedback and test both restored/toggled mute. Adversarial check: syncVoice changes player options, not button attributes; there is no alternate control updater.

**[MEDIUM] Projected Flyer countdown exits upper canvas — line 476**
shieldRing chooses above/below using world p.y<70; physicalPlayer line489 then translates all drawing by projected elevation. For p.y75,z52, text baseline75-55-33.8=-13.8 and box top-25.8. This is a valid healthy Flyer location. Existing top-edge y24 test picks the lower branch and misses this interval. Choose placement/clamping in projected canvas coordinates and test the transition boundary. Adversarial check: parent translation applies to the label and rectangle; no later clamping restores y.

## Missing safeguards
No additional confirmed safeguard issue.
