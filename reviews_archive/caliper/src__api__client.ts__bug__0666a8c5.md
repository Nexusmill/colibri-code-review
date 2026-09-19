<!-- source: src/api/client.ts | reviewer: glm-5.3-zai-in-session | sha256: 0666a8c5835574aad0a11f6af4141df713af907ddcf6b4cfda189028e78e889c | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict
Shippable. The delta since the prior review is exactly the `backendHealth` block (+15 lines, commit b66fc72); traced end to end it is clean — never rejects, no cache to go stale, honest down-reasons, timeout covers headers and body — and its only consumer's no-catch fire-and-forget is safe because the probe cannot reject. One pre-existing defect class the prior review never recorded survives in the fire-and-forget POST helpers.

## Fixed since last review
- The prior bug review (e5904c0d, 2026-09-06) was verdict-only and recorded zero findings — nothing to close. Its verdict's subject matter is intact: `listGraphBackups` still returns `backups+drifted` (lines 207-211) and `restoreGraphBackup` still passes the optional `file` (lines 213-220).
- The add-on carried three times by the sibling feature review — a shared `backendHealth()` probe — is now BUILT: lines 131-140, with all three answer paths tested (`src/api/client.test.ts:25-35`) and the design adversary's remediations applied (ScreenStage's socket-landing effect retires in-flight words).

## Bugs & vulnerabilities
**[MEDIUM] Fire-and-forget POST helpers treat any HTTP response — including a proxy 500 — as success, so cancels "succeed" against a dead backend** (pre-existing, never reported by the prior review) - `line 95`, `line 103`, `line 114`, `line 184`
- What: `cancelQueued` (94-100), `interrupt` (102-108), `clearQueue`'s `/queue` POST (113-118), and `seedUserWorkflow` (183-189) `await fetch(...)` and never check `res.ok` — they resolve on 4xx/5xx. Only network-level rejection throws.
- Trigger: backend down or mid-restart (the Vite proxy answers 500 with a text body — fetch resolves, `res.ok` false) exactly when the user presses CANCEL or the wedge cleaner. `queueStore.cancel` (`src/stores/queueStore.ts:182-198`) catches only rejection, then marks the job `failed / "Cancelled."`; `clearAll` (queueStore.ts:202-213) marks every in-flight job `"Cleared by user."` while the server queue is untouched.
- Impact: dishonest terminal state in a local app whose standing rule is truthful status — the render later completes server-side and surfaces as an untracked entry; QueueSurface's 500 ms re-fetch (`QueueSurface.tsx:70-73`) partially self-heals but the store's jobs list does not. Code path CONFIRMED by reading; impact scenario PLAUSIBLE (narrow window, but the wedge cleaner is precisely the button pressed during that window).
- Fix: apply the `freeVram` idiom that already exists in this file with its own incident comment (line 170): `if (!res.ok) throw new Error(...)` in `cancelQueued`/`interrupt`/`clearQueue` (and optionally `seedUserWorkflow`) — the consumers' catches and honest error lines are already wired.

## Missing safeguards
- Unguarded `res.json()` with no `res.ok` check in `getObjectInfo` (53-54), `getLiveQueueIds` (59-60), `getQueueEntries` (81-82), `getSystemStats` (123-124): when the backend is away these reject with a SyntaxError on the proxy's text body instead of a legible reason — polling consumers catch it, so the cost is error-message quality only.
- Error-path bodies are dropped: `getVramPreflight` (9), `getCaliperVram` (144), `getNodeSync` (158), `freeVram` (170) throw `route NNN` without reading the response, losing the middleware's reason (e.g., a preflight 400's issue text).
- `getHistory` interpolates `promptId` unencoded into the path (46) — safe for ComfyUI's UUIDs, theoretical otherwise.
- `backendHealth` (132-140) deliberately carries no negative cache — correct for the Caliper failure-TTL defect class; keep it that way if a cache is ever tempted.

context-pack: delta = backendHealth (127-140) only; consumer ScreenStage.tsx:586-603; proxy vite.config.ts:33; tests client.test.ts:25-35; 16 importers unchanged.
new-findings: 1
