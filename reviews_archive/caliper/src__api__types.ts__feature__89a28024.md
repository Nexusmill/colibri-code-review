# Colibri review — src/api/types.ts (feature)

- **Source:** `src/api/types.ts` · **sha256:** 89a28024
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the API vocabulary — WsEvent consumed by queueStore.applyEvent (21 references, the #3 file by PageRank); CaliperVram is the status-truth contract (argv ride); ObjectInfo feeds files.ts + enums; verified layout fact: QueueEntry/QueueResult live in client.ts, not here; last touch df9f3db (2026-08-31).

## What this module does

The typed wire vocabulary: ApiWorkflow/OutFile/NodeOutputs, the seven websocket event variants (status/execution_start/executing null-node completion/progress/executed/cached/execution_error), ObjectInfo's combo-node shape, SystemStats (devices with optional torch fields), and CaliperVram — the custom node's payload: adapter counter, per-process table, resident models, torch allocator numbers, and the server's own argv (the flag-truth readback).

## Suggested add-ons

**One vocabulary home** — Value Low · Effort S
- What: move `QueueEntry`/`QueueResult` (client.ts) and the queue-entry prompt-blob extension (the R1 "what is actually running" add-on) into this file.
- Why: the file is the declared home for wire shapes; the queue types living in client.ts split the vocabulary across two homes for no structural reason. Purely organizational — zero behavior.

**WsEvent runtime validation at the boundary** — Value Low · Effort S-M
- What: an `isWsEvent(x): x is WsEvent` guard run once in ws.ts before applyEvent.
- Why: applyEvent trusts the shape; a malformed server message would throw in the store's reducer. The events are well-formed in practice (tests cover); this is a hardening nicety, honestly Low.

## Nice-to-haves

- None — the file does its one job.
