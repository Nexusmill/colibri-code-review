<!-- source: src/api/types.ts | reviewer: glm-5.3-zai-in-session | sha256: 39a2410a47305981bdc00115323ec28f002251689428e919e4ac98785972cbe9 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict
The type layer is mostly faithful to the wire (CaliperVram and SystemStats check out field-by-field against the node and server), but the `WsEvent` union hides two real drifts: an `executed` payload whose values can be `null` on the server's cache-hit path (typed as non-nullable objects), and an `execution_error` node id that the wire keys as `node_id` while the adapter (and therefore the type's promise of a meaningful `nodeId`) never receives it.

## Bugs & vulnerabilities

**[HIGH] `executed.outputs` values are typed non-nullable but the server sends `output: null` for cached no-UI nodes** - `line 16` (shape at `line 9`)
- What: `WsEvent`'s `executed` variant declares `outputs: NodeOutputs` — a `Record` whose values are always objects. The local ComfyUI (`E:/AI/ComfyUI/execution.py` `_send_cached_ui`, ~line 434-437) sends `"executed"` with `"output": cached_ui.get("output", None)` for EVERY cache-hit node, and `cached_ui = cached.ui or {}` means any cached node that produced no UI (checkpoint loaders, CLIPTextEncode, KSampler — the whole graph prefix on a re-render) carries `output: null`.
- Trigger: Any render that hits the output cache — repeat render with the same prompt text (even with seed randomize on, the prefix nodes cache), or the fixed-seed A/B bench renders. The adapter (`src/api/ws.ts:27-28`) only checks `prompt_id`/`node` and casts `{ [d.node]: d.output } as NodeOutputs`, forwarding `{ nodeId: null }`.
- Impact: `queueStore.applyEvent` (`src/stores/queueStore.ts:170-172`) runs `out[key]` over `Object.values(e.outputs)` — a `TypeError: Cannot read properties of null` is thrown inside the socket's `onmessage` handler once per cached no-UI node, skipping the rest of that handler; the app survives only because each message gets a fresh callback, but every cached render throws uncaught exceptions and the trap detonates for any future consumer of the field.
- Fix: Validate in the adapter — only emit `executed` when `d.output` is an object (or coerce to `{}`) — or type the values as `NodeOutputs[string] | null` and guard the consumer loop. CONFIRMED: server source, adapter cast, and consumer dereference all traced.

**[LOW] `execution_error.nodeId` is a phantom field — the wire key is `node_id`, the adapter reads `node`, so it is always `"?"`** - `line 18`
- What: The type promises the failing node's id (`nodeId: string`), but both server error paths (`execution.py` ~lines 521-536 ExecutionBlocker and ~701-713 main) send `node_id`, never `node`. The adapter (`src/api/ws.ts:37`) reads `typeof d.node === "string" ? d.node : "?"`, which always falls to `"?"`.
- Trigger: Every `execution_error` event.
- Impact: Latent — `queueStore` currently uses only `nodeType` + `message` for the error string, so nothing displays the bogus id; but the type ships a field that never carries real data and will mislead the first consumer that trusts it (e.g., a "jump to failing node" feature).
- Fix: Map `d.node_id` in `ws.ts` (fall back to `d.node`), or drop `nodeId` from this variant. CONFIRMED against both server emission sites and the adapter.

## Missing safeguards
- `WsEvent` lacks `execution_success` / `execution_interrupted` (both emitted by this ComfyUI build, `execution.py:824`/`699`) and the adapter silently drops unknown types — job completion rests entirely on the legacy `executing{node:null}` signal from `main.py:394`; nothing in the type layer pins that dependency, and a backend update removing it would hang jobs as "running" until a socket reconnect.
- `ObjectInfoComboNode.input.required` is declared non-optional, but `/object_info` copies `INPUT_TYPES()` verbatim (`server.py` `node_info`) — a node declaring only optional inputs omits `required` on the wire; the sole consumer (`src/workflows/toUiGraph.ts:65`) happens to guard with `?? {}`, nothing enforces it for the next one.

context-pack: prior review cache (39a2410a), src/api/types.ts, src/api/ws.ts, src/api/client.ts, src/stores/queueStore.ts, src/workflows/toUiGraph.ts, src/App.tsx, comfy/caliper_vram.py, vite.film.ts field usage, and the live server truth in E:/AI/ComfyUI (execution.py, server.py, main.py send_sync sites).
new-findings: 2
