<!-- source: src/api/ws.ts | reviewer: glm-5.3-zai-in-session | sha256: 0e4981bc8831255b971191b8ad525bccea011836d1d160cab0f3ecd162152187 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: BUGHUNT12 - colibri bug hunt on the next ten files by import PageRank (ranks 21-30); DELTA pass over the file's changes since the recorded review at sha 8d535ac7 (0.3.0 doctrine: prior review = context, loop closed, new/changed findings only). -->

## Verdict

Shippable — delta clean. The file's sha256 verified byte-exact on disk (`0e4981bc…152187`). Exactly one commit touches it since the reviewed state (bd2f0ec, 2026-09-16, diff-verified: two hunks only — the `executed` output coercion at lines 27–37 and the `execution_error` node_id mapping at lines 41–52). Both BUGHUNT10 remediations were re-verified three ways: against the local server's own source (E:\AI\ComfyUI @ b963f4a), against the consumer `queueStore.applyEvent`, and against the shipped tests (ws.test.ts:24–36). No new finding survived the adversarial pass.

## Fixed since last review

The prior review (.colibri_reviews/src__api__ws.ts__bug__8d535ac7.md, 2026-08-19) recorded **zero findings** ("No findings survived verification. Socket identity guards, reentrant connect, backoff reset, and stale-onclose all traced correct; parseWsMessage is total over malformed input.") — there is no open loop to close. Its blessed areas were re-checked in current bytes: the delta did not touch the socket class (diff shows only the two parser hunks), and my independent re-verification concurs — assign-before-announce plus the live-check makes reentrant `connect()` a no-op; a stale `onclose` fails the `ws !== this.ws` identity check and cannot double-schedule; `close()` announces disconnected synchronously because the CloseEvent will miss the identity check; the backoff ladder (1s→2s→4s→8s cap, reset on open) schedules with the pre-doubling value; a pended reconnect timeout surviving a close()/connect() cycle is neutralized by the live check. The two remediation-manifest rows for this file, excluded up front, were verified FIXED in current bytes rather than assumed:

- **[HIGH] executed with output:null (manifest 2026-09-16)** — FIXED, verified. Line 35 coerces `d.output && typeof d.output === "object" ? d.output : {}` (also covers missing/undefined/array/primitive — array passthrough is safe: the store iterates keys of `[]` → none). Server ground truth: `_send_cached_ui` (execution.py:430) sends `"output": cached_ui.get("output", None)` (execution.py:436) — the null shape is real; the comment's citation is accurate. Consumer-safe: `queueStore.applyEvent`'s executed branch iterates `out[key] ?? []` over `{}` → zero files, no throw. Test shipped (ws.test.ts:24–31).
- **[LOW] execution_error.nodeId phantom d.node read (manifest 2026-09-16)** — FIXED, verified. Line 48 reads `d.node_id` with `d.node` fallback. Both server error paths key `node_id` (execution_block_cb, execution.py:525–536; handle_execution_error, execution.py:686–712) and neither ever sent `d.node` — the comment's claim checks out. Tests cover both the node_id key and the legacy fallback (ws.test.ts:19–22, 33–36).

Contract context established during the pass (evidence for future reviews): the prompt-completion signal — `executing {node: null, prompt_id}` → `nodeId: null` → job "done" — is sent from **main.py:394** (not execution.py/server.py; execution.py:835 resets `last_node_id` and server.py:290 is only the reconnect-resume frame, which carries no prompt_id and is correctly dropped by the line-20 guard). The `execution_success` (execution.py:824) and `execution_interrupted` (execution.py:699) events are unparsed; completion rests solely on the main.py signal, which this build does send. Unchanged since the prior review — recorded as context, not a finding.

## Bugs & vulnerabilities

None new. The two changed hunks are total over malformed input (every branch typeof-guarded; the parser still cannot throw), match the server's actual wire shapes, and do not regress the consumer. Reconnect/backoff/identity logic is byte-unchanged since the reviewed sha.

## Missing safeguards

- The repaired `execution_error.nodeId` feeds a field no consumer reads: queueStore's error branch patches only `{ status: "failed", error: nodeType + ": " + message }` — `Job.nodeId`/`nodeType` stay unset on failure, so the BUGHUNT10 repair is currently unobservable (queueStore scope, not this file; the parse itself is correct).
- The coerced `d.output` passes through with its inner shape unvalidated (`images` etc. as `as NodeOutputs`); the store's `for (const f of out[key] ?? [])` would throw on a non-iterable non-null value. Safe against this server (ui() outputs are always arrays) and localhost-trusted; an `Array.isArray` guard at the parse boundary would make the executed branch as total as the rest of the parser. Unchanged behavior — hardening note, not a regression from the fix (the fix strictly narrowed the surface).
- An interrupt raised outside Caliper arrives as unparsed `execution_interrupted`; the job is only failed later by the reconnect reconciliation ("Lost during a disconnect"). Unchanged since the prior review; noting for the record.

context-pack: importers App.tsx (socket→applyEvent/setSocketState, no history-poll fallback for job completion), ws.test.ts, queueStore.ts; consumer contract verified event-by-event against wire shapes grounded in E:\AI\ComfyUI execution.py/server.py/main.py @ b963f4a; remediation-manifest rows for this file confirmed fixed in bytes.

new-findings: 0
