# Next-ten bug hunt synthesis (2026-09-16)

Owner commission: "do a colibri bug hunt on the next top 10 files." Board =
the next ten files by import PageRank past the 2026-09-14 top ten (the ten
the morning BUGHUNT10 covered; worldmodel and uiStore rank inside today's
top twelve and are excluded as hunted). Doctrine = the 0.3.0 context-hunt
cache: a prior review is CONTEXT, never a skip — six files were byte-
identical to their last bug review and got lineage hunts (`_r2` artifacts,
`new` counts recorded as pass2 lineage in the manifest); four had changed
and got DELTA reviews (new/changed findings only, prior loop closed).
Fresh-context subagent per file (model type glm); Phase 3 refutation ran
per finding inside each hunt, and the three HIGHs plus the bundlesStore
discard were independently re-verified against current bytes by the
orchestrator. Reviews only — NOTHING is being remediated from this hunt
without the owner's pick.

## The board

| # | File | Pass | New | Worst |
|---|------|------|-----|-------|
| 1 | src/providers/serviceKeys.ts | lineage _r2 | 1 | MEDIUM — two of six key hints still say "adapter to come" for adapters that are LIVE and spending (the already-booked deferral; fix needs the owner's word under the no-visual-changes rule) |
| 2 | src/api/modelRoutes.ts | lineage _r2 | 0 | clean — five draft findings all refuted (ledger in the artifact) |
| 3 | src/api/queueNodes.ts | delta | 0 | comment-only delta since the prior review; truthfulness of the comment itself improved |
| 4 | src/vram/preflight.ts | lineage _r2 | 1 | MEDIUM — measured VRAM and the bench-eta can come from DIFFERENT corpus entries, and the eta's date is parsed then discarded (undated basis on the queue's ETA) |
| 5 | src/providers/openrouter.ts | lineage _r2 | 4 | HIGH — a mid-stream failure discards the accumulated partial answer (contradicting the file's own half-answer doctrine), and the 120 s timeout aborts streams the file designs for minutes |
| 6 | src/providers/eachlabs.ts | lineage _r2 | 4 | HIGH — the poll loop never checks HTTP status: a 401/404/429 spins the full 10 minutes and misreports "timed out" on the PAID voice leg |
| 7 | src/api/film.ts | lineage _r2 | 3 | HIGH — autopilotStatus blind-casts error bodies: one 404 (run deleted mid-poll, or the non-atomic autopilot.json write race) silently erases the wizard's live producing view |
| 8 | src/providers/openrouterVideo.ts | delta | 0 | clean delta — the only change since August is the end_image block, traced clean end to end |
| 9 | src/stores/bundlesStore.ts | delta | 2 | MEDIUM — the load-recheck containment silently discards the ENTIRE vocabulary migration when a file's own declared presets sit off the adopted grid (the presets sibling of BUGHUNT10's frames_max finding, fixed this morning); MEDIUM — save() refusals are dropped by two of four callers (silent no-op button presses) |
| 10 | src/providers/replicateBrowser.ts | delta | 3 | MEDIUM — the battery's per-clip estimate bypasses the OWNER_PRICES override and discards the basis string; LOW ×2 (per-thousand units priced per unit = 1000x overquote; tier mislabeled as floor) |

**Totals: 18 new findings — 0 CRITICAL / 3 HIGH / 11 MEDIUM / 4 LOW.**

## Ranked: what deserves fixing first

1. **[HIGH] openrouter.ts:124,173 — the brain's partial answer is thrown
   away on a mid-stream failure.** The stream consumer has no error path:
   `await readSseLines(...)` throws, and the content/usage accumulated so
   far — deltas the owner already WATCHED arrive — is discarded, against
   the function's own "a half answer with its truth beats a hang"
   doctrine. Worse, the 120-second request timeout aborts in-flight body
   reads, and the file is explicitly designed for brains that "think for
   minutes": any stream over two minutes is killed by its own timer, the
   console shows a live answer that suddenly errors to nothing, and the
   usage (cost truth) is lost after real spend. Fix: catch in the read
   loop and return the accumulated state; apply the timeout to
   connection, not the body (or raise it to the brain's own 480 s
   ceiling). CONFIRMED end to end.

2. **[HIGH] eachlabs.ts:93-107 — the poll loop ignores HTTP status.**
   Every terminal poll-level error (401/403/404/429/5xx/HTML) coerces to
   "still running": the loop spins the full 10 minutes and reports a
   false "timed out after 10 min" — on the autopilot's PAID voice leg
   (one bad key or purged prediction = 10 minutes per narration line,
   N × 10 min for a film), while the POST already spent money and the
   artifact is never fetched. It also defeats the autopilot's 429
   recovery (the consumer regex-matches "429" in the thrown message; no
   poll-path message can ever carry it — finding #3 in the artifact).
   Fix: branch on poll.ok — auth/not-found throw immediately, 429/5xx
   back off toward the existing deadline. CONFIRMED end to end.

3. **[HIGH] api/film.ts:191 — one 404 erases the wizard's producing
   view.** autopilotStatus resolves (never rejects) any error body into
   `{record: undefined}`; the wizard's poll adopts it unconditionally, so
   a deleted-run 404 OR the transient non-atomic autopilot.json write
   race tears down the live run view mid-checkpoint — the owner loses the
   APPROVE/REJECT surface while money idles. Two sibling GETs share the
   disease: autopilotList can write `undefined` into the runs store's
   `| null` sentinel (M), and filmList renders every server error as an
   empty library (M) — "your films are gone". Fix: the file's own
   filmBatteryStatus already shows the pattern (check ok/error-body,
   throw); apply it to all three. CONFIRMED end to end.

4. **[MEDIUM] bundlesStore.ts:124-133 — the silent vocabulary-migration
   discard, presets axis.** The morning fix closed the frames_max axis;
   this is the other door: a file whose DECLARED size_presets sit off the
   adopted factory grid fails the load recheck, and the containment drops
   the ENTIRE migration for every bundle, silently, on every boot — no
   VAE-grid snapping, no bounds, nothing said. Fix: surface the discard
   in fileIssues, and gate multiple-adoption on the file's declared
   presets like the hand-edit rule. CONFIRMED dataflow.

5. **[MEDIUM] replicateBrowser.ts:174 + vite.film.ts:2632 — the battery
   estimate speaks the wrong price basis.** The per-clip estimate
   bypasses the OWNER_PRICES override (p-video, owner-priced, is in the
   battery pool) and drops the basis string, so the optimizer's permanent
   memory (measured-results.md) can carry a page/median basis unmarked —
   the exact class the owner-override ruling and film-bill-basis exist
   against. LOWs in the same file: per-thousand units priced per unit
   (1000x overquote, fails safe), tier-rate mislabeled as a floor.

6. **[MEDIUM] openrouter.ts:181/190 — the silent-empty and raw-parse
   pair.** A 200 that is not an SSE body becomes an empty successful
   reply (no content, no error — the agent loop sees nothing); a 200 with
   a non-JSON body throws a raw SyntaxError past the file's own catch
   discipline (and the pricing fetch re-parses on every question after).
   LOW in the same file: NaN/negative cost text ("$NaN") on non-finite
   catalog/usage numbers.

7. **[MEDIUM] eachlabs.ts:76-82 — POST timeout mislabeled "unreachable"
   (retry double-spend risk).** An aborted create may still have been
   accepted and billed; the message says the server was never reached.

8. **[MEDIUM] vram/preflight.ts:37,57 — undated, possibly-mismatched
   bench-eta basis.** measured VRAM and etaMs can select different corpus
   entries (footprint lines are optional, medians unconditional) and the
   eta's parsed date is dropped — the queue's ETA rides an unstated
   basis.

9. **[MEDIUM] serviceKeys.ts:17,20 — the "adapter to come" hints (the
   booked deferral).** Independently re-found; this is open-items item 15
   — the fix touches VISIBLE COPY and waits on the owner's explicit
   permission per the no-visual-changes rule. One word away when ruled.

10. The remaining LOWs (per-thousand pricing and floor-basis labels in
    replicateBrowser; NaN cost text in openrouter; listEachLabsModels
    shape trust) are recorded per-file with fixes; none urgent.

## Doctrine notes (second run of the 0.3.0 cache)

Three of ten files hunted clean at their recorded shas — api/modelRoutes
(0 new, five refutations ledgered for the next hunter), queueNodes
(comment-only delta), openrouterVideo (clean delta, the August→September
waves lived in siblings). One empty pass (glm type) exists now on
api/modelRoutes; a lock needs three DISTINCT model types empty at the
same sha, so nothing locked. The lineage passes again proved the
doctrine's worth: eachlabs and openrouter carried "Clean" verdicts at
these exact bytes for weeks — the fresh-context hunters found real
defects the original reviewers and the cache both missed. The
bundlesStore finding closes a loop with the morning wave: the same
silent-discard containment had TWO doors; BUGHUNT10 + remediation fixed
frames_max, this hunt found presets.

Awaiting the owner's remediation pick; nothing is being fixed from this
hunt without it.
