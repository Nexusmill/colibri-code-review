source: src/providers/modelRoutes.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1) + M3 grok-4.6 escalation
sha256: d48260c3c5b176d697c17fe5c35049e020500648ab15f65ea55f2b5c4e1d5fb0
date: 2026-09-19 12:00
mode: bug
context: route core; route-intelligence chain; route-ahead saving design

Findings: 1 HIGH + 2 MEDIUM + 1 LOW.
- [HIGH] REFUTED with evidence: cloud routes accepted for llm (cloudRunnable never enforced in validateRoute/resolveRoute). Two grounds: (a) ModelPicker DELIBERATELY offers route-ahead saves for not-yet-wired types ("the route can still be saved"; the run button gates on canRun = cloudRunnable); (b) resolveRoute/validateRoute have NO production callers (grep: only modelRoutes.test.ts). Residue fixed: the stale cloudRunnable comment ("the picker never offers a route the engine can't run") updated to the route-ahead truth.
- [MEDIUM] PLAUSIBLE-hygiene, deferred: local routes accepted for shelf-less types (music/speech) - caller discipline holds; no production caller.
- [MEDIUM] PLAUSIBLE-hygiene, deferred: resolveRoute returns stored invalid routes unvalidated - same no-production-caller situation; hand-edit paranoia lives in gatedRouteConfig.
- [LOW] PLAUSIBLE-hygiene, deferred: cloud fallback with omitted cloudDefault yields cloudModel: undefined - same caller situation.
M3 (grok-4.6 high, context carried the refutation evidence): "no new findings".
