# Colibri bug review — src/api/types.ts

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 89a28024e2f50038a81edca7df420641ec7c58c0ee0c31405e7d2e3c5d6af73b

### Meta
- path: src/api/types.ts | sha8: 89a28024 | lines: 59 | context-pack: 21 importers (client.ts, ws.ts, stores, surfaces, vite.film.ts); `WsEvent`/`NodeOutputs` verified against the wire through the snake_case→camelCase translation in src/api/ws.ts:5-43 (direct-to-8188 socket); `SystemStats` cross-checked against the pristine backend E:\AI\ComfyUI\server.py:686-737; `CaliperVram` cross-checked field-for-field against comfy/caliper_vram.py's GET /caliper/vram handler (adapter_bytes/processes{pid,name,bytes}/models{name,loaded_bytes,total_bytes,device}/torch{allocated,reserved,free,total}/argv); git: df9f3db, d212818, 15feeec, 313da0d (the system_stats payload fix).

### Review

## Verdict
**PASS with one confirmed phantom field.** The historical trap classes came back clean where it matters: `WsEvent` is an internal parsed form (ws.ts maps `prompt_id`→`promptId`, `node`→`nodeId`, `nodes`→`nodeIds`, `status.exec_info.queue_remaining`→`queueRemaining` before the type is ever applied — no wire divergence); `CaliperVram` matches the custom node's JSON exactly, including the error path (`{**table, "models":…, "torch":…, "argv":…}` still carries argv when `error` is set, and `torch: {}` when CUDA is down, honestly optional); `OutFile` `{filename, subfolder, type}` matches ComfyUI output entries (extra fields like `format` are simply not modeled); `ObjectInfo`'s picked `input`/`output` are what all four consumers read (`files.ts`, `enums.ts`, `toUiGraph.ts`).

## Bugs & vulnerabilities

- **[LOW] Phantom field: `SystemStats.devices[].vram_used` is declared but the actual server never sends it — the type mirrors a payload that doesn't exist** - `line 40` — CONFIRMED
  - **What:** The type declares `vram_used?: number`. The machine's actual backend (E:\AI\ComfyUI\server.py:709-717) sends per-device `name, type, index, vram_total, vram_free, torch_vram_total, torch_vram_free` — **no `vram_used`** (removed upstream; commit 313da0d already fixed the numeric units but left this field behind).
  - **Trigger:** Read today at two live consumers: src/api/client.ts:134 (`d.vram_used !== undefined ? d.vram_total - d.vram_used : null`) and src/components/StatusFooter.tsx:105 (`d.vram_used ?? (d.vram_free !== undefined ? d.vram_total - d.vram_free : 0)`). Both fallback branches are dead code that compiles only because the type vouches for the field.
  - **Impact:** No wrong behavior today — `vram_free` is unconditionally sent (server.py:714), so the live path always computes correctly. The hazard is the exact "unforwarded/mis-mirrored interface field" trap this repo's history warns about, inverted: a consumer can be written against `vram_used` believing it's a real alternate source; the type silently guarantees bytes that never arrive.
  - **Fix:** Delete `vram_used?: number` from types.ts and simplify both fallbacks to the `vram_free`-only form (cite-fix: client.ts:134, StatusFooter.tsx:105 in the same change). No other call site reads it (21 importers checked).

## Missing safeguards
- Every boundary fetch applies these types as bare `as` casts with zero runtime validation (client.ts:44 `getObjectInfo`, :111 `getSystemStats`, :117 `getCaliperVram`; ws.ts:28 `as NodeOutputs`). A future backend payload drift (the exact 313da0d scenario) fails silently — stale/undefined values render instead of erroring. Cheap targeted hardening: validate `CaliperVram.adapter_bytes`/`argv` and `SystemStats.devices` array-ness at the boundary; the rest is display-only.
- `SystemStats.system` marks `os/ram_total/ram_free/python_version/pytorch_version` optional although this server always sends them (server.py:721-731) — the harmless direction (forces null-handling); conversely it omits fields that ARE sent (`devices[].index`, `system.argv`, `embedded_python`) — harmless since no consumer reads them. No behavioral consequence; noted for the next payload reconciliation pass rather than fixed.
- `ObjectInfoComboNode.input.required` is non-optional, but ComfyUI builds `input` straight from `INPUT_TYPES()` (server.py:756); a node returning only `optional` would make `required` `undefined`. All current consumers optional-chain past it (`oi[n]?.input.required[f]?.[0]`), so no crash — but the type overpromises.
