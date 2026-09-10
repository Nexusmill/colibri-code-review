# Spec review — src/api/types.ts

- Source: `src/api/types.ts` (56 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `c1fba39816e6f5c82f577303a73322babd8fbf3897d90f0ae093a4db906dd708` · 2026-08-31 · mode: **spec** · registry: `spec/power-vram.json` (+ generate.json event shapes)
- Context pack: full read; server end verified on disk — comfy/caliper_vram.py:140 returns `{**table, "models": models, "torch": tstats, "argv": list(sys.argv)}`.

## Verdict
One divergence, CONFIRMED: the `CaliperVram` interface omits `argv`, though the payload the contract names carries it.

## Divergences
**[MEDIUM] CaliperVram drops the argv field the VRAM contract names** - `types.ts:50-56`
- **Expectation (quoted):** PWR-VRAM-GROUND-TRUTH — "renders from GET /caliper/vram (resident models[], argv, torch stats)" · PWR-STATUS-TRUTH — "status text quotes the server's own report (/caliper/vram residency, sys.argv flags)".
- **Trigger:** any typed consumer of `getCaliperVram()` needing argv (the apply-honesty comparison and status-truth text are the named consumers).
- **Behavior:** the interface models adapter_bytes/processes/models/torch/error only — `argv` has no field, so the typed client cannot carry what the node demonstrably sends (caliper_vram.py:140). If argv reaches the UI today it does so by cast, invisible to this type.
- **Fix:** add `argv?: string[]` to CaliperVram.
- CONFIRMED — both ends read: server sends it, type lacks it.

## UNJUDGEABLE HERE
- WsEvent shapes vs live server events (runtime contract; ws.ts consumes).
