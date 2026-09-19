# Next-ten bug hunt synthesis (2026-09-17) — BUGHUNT12

Owner commission: "do a colibri bug hunt on the next 10 files." Board =
ranks 21-30 by import PageRank past the two hunted boards (the 2026-09-14
top ten and BUGHUNT11's ranks 11-20, which the fresh ranking confirmed hold
ranks 1-20 exactly). Doctrine = the 0.3.0 context-hunt cache: nine files
were byte-identical to their last bug review and got lineage hunts (`_r2`
artifacts); one had changed and got a DELTA review. Fresh-context subagent
per file (model type glm); Phase 3 refutation ran per finding inside each
hunt, and both HIGHs plus the load-bearing cross-file claims were
independently re-verified against current bytes by the orchestrator (the
provenance PUT/append collision read first-hand at provenance.ts:36-42,
vite.caliper.ts:123-133, vite.film.ts:688+, queueStore.ts:136; the four
hardcoded 8188 literals grepped verbatim with a zero-match comfyUrl sweep
of src/). Reviews only — NOTHING is being remediated from this hunt
without the owner's pick.

## The board

| # | File | Pass | New | Worst |
|---|------|------|-----|-------|
| 21 | src/film/store.ts | lineage _r2 | 1 | LOW — initShots' comment claims the analyzer beat-snaps section boundaries; it never has (the snap lived in the retired legacy grid) |
| 22 | src/stores/queueStore.ts | lineage _r2 | 2 | MEDIUM — the reconnect reconcile brands a COMPLETED render "failed / Lost during a disconnect" and then suppresses every recovery path for it |
| 23 | src/providers/keyLiveness.ts | lineage _r2 | 1 | LOW — the eachlabs account extractor reads a wrapped {models} shape the endpoint never answers (the adapter's own BUGHUNT11 guard refutes it); dead enrichment, verdict stays truthful |
| 24 | src/install/tiers.ts | lineage _r2 | 1 | LOW — the module header documents the pre-register three-rung ladder, not the approved five-rung owner law (32/64 registers absent from the summary) |
| 25 | vite.comfy.ts | lineage _r2 | 3 | HIGH — the "one place the neighbor is named" founding contract is FALSE: the client websocket, the graph iframe, the status footer, and the launcher all hardcode 127.0.0.1:8188, so a comfyUrl retarget silently kills queue events while submits keep working |
| 26 | src/stores/screenStore.ts | lineage _r2 | 2 | MEDIUM — deleting an asset or film never closes its screen window; persistence resurrects the zombie on every reload pointing at a recycled file (dead player, no onError truth-speech) |
| 27 | src/stores/provenance.ts | lineage _r2 | 3 | HIGH — the store's whole-file PUT can silently and permanently destroy SERVER-APPENDED provenance records it never saw: a queue-time save after a film run wipes every take appended since boot |
| 28 | src/install/plan.ts | lineage _r2 | 1 | LOW — `partial-manual` collapses "nothing present, all manual" into a label that promises partial presence (no consumer branches on it today) |
| 29 | src/api/ws.ts | delta | 0 | clean delta — both BUGHUNT10 remediations re-verified three ways (server source, consumer, tests); reconnect/backoff/identity byte-unchanged |
| 30 | zipWriter.ts | lineage _r2 | 1 | LOW — >65,535 entries overflows the EOCD count fields as a raw Node RangeError instead of the file's own "refuse loudly" doctrine |

**Totals: 14 new findings — 0 CRITICAL / 2 HIGH / 4 MEDIUM / 8 LOW.**

## Ranked: what deserves fixing first

1. **[HIGH] provenance.ts:36-42 — the stale-snapshot PUT destroys
   server-appended records.** Every client mutation PUTs the ENTIRE
   in-memory cache, and the server PUT handler replaces provenance.json
   wholesale with no merge and no version check — while the film engine
   appends to the same file server-side all run (ten appendProvenance call
   sites in vite.film.ts). The cache refreshes only at boot and on
   Library/Outputs mounts, but queueStore saves at queue time on the
   Generate screen. Ordinary sequence: boot → run a film (server appends
   up to 400 records) → queue a one-off render → the PUT ships the
   boot-time snapshot and every film record is gone — prompts, seeds,
   REPRODUCE formulas, silently. This is the second door to the exact
   catastrophe the 2026-08-28 separate-budget law was written against
   (that fix closed eviction, not clobber). Two windows make it worse
   (B's stale snapshot resurrects what A deleted). Fix: record-level
   server ops (POST/DELETE/PATCH by promptId) so the client never speaks
   for records it does not hold, or optimistic concurrency (version +
   409 on mismatch). CONFIRMED end to end; re-verified by the
   orchestrator. Beside it: legacyRecords lacks the Array.isArray guard
   its sibling has (LOW), and the file header still promises the
   merge-back the 2026-08-22 fix removed (LOW).

2. **[HIGH] vite.comfy.ts:1-5 — the portability knob this file exists for
   does not reach the client.** The header promises "The one place the
   ComfyUI neighbor is named — a cloud-only box or a different install
   root edits config, never code", but comfyUrl is honored by the Vite
   proxy/middleware only: the live websocket (ws.ts:76), the graph iframe
   (GraphSurface.tsx:148), the status footer's displayed address
   (StatusFooter.tsx:37,126), and the launcher's --port 8188
   (start-comfyui.cmd:19) all hardcode the neighbor, and nothing serves
   the configured URL to the browser (comfyUrl appears nowhere in src/).
   Retarget the config → submits succeed through the proxy while
   status/progress/executed events never arrive: every render appears
   permanently stuck, the graph iframe is dead, and the footer asserts an
   untrue address. The prior review's "no other 8188 literals" check was
   wrong on the day it was made (the ws literal landed 2026-08-16).
   Fix: serve the configured origin to the client (a /caliper endpoint or
   a vite define) and derive the ws URL, iframe src, and footer string
   from it — or rewrite the header to say only the middleware honors the
   knob. CONFIRMED; literals re-verified by the orchestrator.

3. **[MEDIUM] queueStore.ts:72-85 — a disconnect brands completed renders
   failed and buries them.** On reconnect, any local queued/running job
   absent from the /queue snapshot is marked "Lost during a disconnect" —
   but absent means finished OR lost, and getHistory answers the
   distinction. A render that completed while the socket was down is
   reported failed, skipped by the assets hydration, never
   provenance-patched, and the terminal guard deafens the store to any
   late truth. Fix: consult getHistory before failing; only a 404 loses.
   CONFIRMED.

4. **[MEDIUM] vite.llm.ts:99-104 — the second malformed-config overwrite
   door.** The known shelf names agent.ts; setLocalBrain (shipped
   2026-09-05, click-reachable from the brain picker) independently
   catch-alls a config read failure to `cfg = {}` and writes
   `{localBrain}` over caliper.config.json — one click can wipe the
   portability settings, the optimizer launch flags, and the applied/UNDO
   ledger, silently. Fix: one shared guarded read-modify-write helper on
   the same serialization chain as agent applies. CONFIRMED.

5. **[MEDIUM, PLAUSIBLE] queueStore.ts:148 vs :135 — an execution_start
   that beats the queuePrompt response is dropped** and nothing else ever
   promotes the job to running: the whole render displays QUEUED with no
   gauge and no ETA while the server executes. Fix: let the executing/
   progress handlers promote non-terminal jobs. PLAUSIBLE (event ordering
   across channels; localhost makes the window real).

6. **[MEDIUM] screenStore.ts:223 — zombie windows after delete.** Library
   DELETE and film-run DELETE never close the deleted item's open window;
   persistence resurrects it every reload, titling a recycled file over a
   dead player (image/video branches have no onError truth-speech).
   Compounds per delete. Fix: a prefix-close the delete flows call.

7. **The eight LOWs** (per-file artifacts carry fixes): the false
   beat-snap comment on revivable film/store code; the dead eachlabs
   account extractor (whose naive fix would LIE — the probe's ?limit=1
   would read as the account's model count); the stale three-rung ladder
   header; the partial-manual label collapse; the zip32 65,535-entry
   RangeError; the config-path quintet with the launcher's silent
   flag-drop; the legacyRecords shape guard; the provenance header's
   merge-back promise. None urgent.

## Doctrine notes (third run of the 0.3.0 cache)

One of ten hunted clean (api/ws.ts — the delta; both BUGHUNT10 fixes
re-verified against the ComfyUI server's own source). The lineage passes
again paid for themselves: provenance, queueStore, and vite.comfy carried
"Clean"/zero-finding verdicts at these EXACT bytes — the fresh-context
hunters found a data-loss HIGH, two event-channel defects, and a false
founding contract the original reviewers and the cache both missed. The
ws.ts delta also demonstrates the loop-closing half of the doctrine: the
prior review's claims were re-checked rather than trusted, and one of
them (the 8188-literal absence) turned out to have been wrong — recorded
in the vite.comfy artifact as lineage evidence, not a restated finding.
Operational note: the first vite.comfy dispatch died to a provider rate
limit (ten parallel subagents) and was re-run solo; also the jcodemunch
index had been clobbered by yesterday's explicit-paths re-index calls and
was rebuilt whole before the board was ranked.

Awaiting the owner's remediation pick; nothing is being fixed from this
hunt without it.
