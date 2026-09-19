source: src/api/modelRoutes.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: 35f2e54fd3d8b7ee8db17daa8814a3fc9dbaa9bf5056781834e75de7ee2f1add
date: 2026-09-19 12:05
mode: bug
context: api-layer route client; contract loop with vite.routes + SettingsConsole

3 findings, all CONFIRMED as defensive-parse gaps, all OPEN for the next remediation session (same class: a 200 with a garbage/empty body resolves through `.catch(() => ({}))` and an unsound cast):
- [MEDIUM] getModelSchema returns {} typed as ModelSchema on an unparsable 200 - callers dereference schema.properties/price.text.
- [MEDIUM] runCloudModel's guard checks only data.file - bytes/file subfields may be undefined against a number/string-typed return.
- [MEDIUM] routePreset returns {} for an empty 200 - a malformed preset action reads as success with no config/presets/replaced.
Full finding text with fixes: %TEMP%/hunt1/api__modelRoutes.md (this session) and the git-history commit message.
