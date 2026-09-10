# colibri bug review - src/components/ScreenStage.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 dd6dc0b5 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [LOW] The reload-restore effect (deps [selected]) also fires on every bundle SWITCH while no windows are open - closing everything and switching bundles resurrects an old render. Fix: restore only on first mount per session.
- Pointer math (stage-scale division), ctlbar trio, taskbar focus/minimize semantics traced correct.
