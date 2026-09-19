# Colibri review — src/api/types.ts (feature)

- **Source:** `src/api/types.ts` · **sha256:** 6cdf2c46
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs 89a28024 @ 2026-09-05)
- **Context pack:** the wire vocabulary (#3 by PageRank — CaliperVram alone has 21 in-degrees); delta = e2328d3 (+3, node self-id); spec review at c1fba398 covers the argv clause; full current read (62 lines).

## What this module does

The typed wire vocabulary: workflow/output shapes, the seven websocket event variants, ObjectInfo's combo-node shape, SystemStats, and `CaliperVram` — the custom node's truth payload, now carrying the server's `argv` (flag readback) AND the deployed node's own identity (`node?: { name; version; sha256 }` — the sync verdict's raw material, added by e2328d3).

## Fixed since last review

- Node self-identity fields → the delta itself; the footer speaks the sync verdict through nodeSync.ts.

## Suggested add-ons

**Per-process identity on CaliperVram.processes** — Value Med · Effort M
- What: extend `processes` entries (`pid, name, bytes` today) with the process command line (or window title) from the node side.
- Why (grounded in this machine's history): the VRAM table names `python.exe`/`msedge.exe`-class entries; the session-pollution incidents (leftover dev/harness servers squatting VRAM/ports) were diagnosed by PID archaeology. A cmdline per row answers "WHICH python" at a glance in the footer — the diagnosis path the owner actually walks.
- How: comfy/caliper_vram.py reads cmdline via psutil (already enumerating processes); type gains `cmd?: string`; footer row tooltip. Requires a canonical-node re-sync (the sha-pairing machinery exists).

**One vocabulary home** — Value Low · Effort S (CARRIED, unbuilt)
- QueueEntry/QueueResult still live in client.ts; purely organizational.

**WsEvent runtime guard** — Value Low · Effort S-M (CARRIED, unbuilt)
- `isWsEvent` before applyEvent; hardening nicety, honestly Low.

## Nice-to-haves

- None — the file does its one job; the node-side add-on is the only one with real owner value.
