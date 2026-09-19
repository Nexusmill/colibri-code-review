# Top-10 bug hunt synthesis (2026-09-16)

Owner commission: "id like you to do colibri bug hunt reviews on the top ten
caliper files." Board = the 2026-09-14 top ten by import PageRank. Doctrine =
the 0.3.0 context-hunt cache (shipped the day before): a prior review is
CONTEXT, never a skip — four files were byte-identical to their last bug
review and got lineage hunts (`_r2` artifacts, `new` counts in the manifest);
six had changed and got DELTA reviews (new/changed findings only, prior loop
closed). Fresh-context subagent per file (model type glm); Phase 3 refutation
ran per finding; every finding below is CONFIRMED unless marked PLAUSIBLE.

## The board

| # | File | Pass | New | Worst |
|---|------|------|-----|-------|
| 1 | src/bundles/schema.ts | delta | 1 | MEDIUM — frames_max adoption onto a custom detent silently discards the whole vocabulary migration on every load |
| 2 | src/bundles/constraints.ts | delta | 1 | LOW — pathological detent ("1000n+900") drives the framesMax fallback negative; coerceParams seats frames=-100 |
| 3 | src/api/types.ts | hunt _r2 | 2 | HIGH — `executed.outputs` values are null on ComfyUI's cache-hit path; queueStore.applyEvent throws per cached no-UI node |
| 4 | src/film/worldmodel.ts | delta | 3 | HIGH — post-edit takes stamp the NEW world version while prompts carry the pre-edit anchor; the honesty detector inverts |
| 5 | src/film/autopilot.ts | hunt _r2 | 3 | MEDIUM — buildRedraftPrompt interpolates an undefined anchor: the repair path burns paid brain calls and can never succeed |
| 6 | src/api/client.ts | delta | 1 | MEDIUM — cancel/interrupt/clear treat any HTTP answer (incl. proxy 500) as success against a dead backend |
| 7 | src/providers/modelRoutes.ts | hunt _r2 | 3 | MEDIUM — the modelless cloud default routes cloud-only machines into LOCAL GPU work on image/video |
| 8 | src/install/catalog.ts | hunt _r2 | 1 | HIGH — five MiB-rounded bytes pins are enforced as exact: multi-GB brain downloads complete then delete themselves |
| 9 | src/film/analysis.ts | delta | 0 | comment-only delta since the prior review; wave-7 gate fixes re-verified green |
| 10 | src/stores/uiStore.ts | delta | 2 | MEDIUM — panel-open setters never route to the Generate surface; settings/optimizer palette verbs strand invisible windows |

**Totals: 17 new findings — 0 CRITICAL / 3 HIGH / 5 MEDIUM / 9 LOW.**

## Ranked: what deserves fixing first

1. **[HIGH] catalog.ts:68,77,86,95,112 — the five un-installable brains.**
   The 2026-09-15 verify gate (same day's commit 2c059a1) hardened
   approximate MiB-rounded shelf sizes into exact-match pins; two were
   ground-truthed against the HF tree API (gemma 438,432 bytes off, LFM2
   80,576 off), the other three are the same construction. Every affected
   brain download completes, is deleted by its own verifier, and errors
   with a false "truncated or substituted transfer" sentence. This is a
   regression shipped by the fix, live today. Fix: re-pin exact sizes
   (tree API) or drop the pin to sha-only where rounded; add the
   "no enforced bytes pin divisible by 2**20" test.

2. **[HIGH] worldmodel.ts:66 — the world version stamp can lie.** A world
   EDIT after the storyboard exists (accepted at THE PLAN, no re-draft
   forced) bumps the version but leaves prompts carrying the pre-edit
   anchor; every later take stamps the NEW version. The costume-change
   detector then certifies exactly the takes that contradict the corrected
   constants — real money spent on takes the rail says match. Fix: stamp
   takes with the storyboard's draft-time world version, or refuse/reset
   the run when the world changes under an existing storyboard.

3. **[HIGH] types.ts:16 — the cached-render null crash.** ComfyUI sends
   `executed` with `output: null` for every cache-hit node that produced
   no UI; the adapter casts it as always-objects and queueStore
   dereferences it — an uncaught TypeError per cached no-UI node inside
   the socket handler. Every repeat render walks this. Fix in the adapter
   (skip/coerce null outputs) or type + guard the consumer.

4. **[MEDIUM] autopilot.ts:639 — the bricked repair path.** An anchorless
   storyboard (worldless draft whose brain omitted the field, or a PATCH)
   makes buildRedraftPrompt interpolate the literal "undefined" as the
   frozen continuity law; every RE-DRAFT press burns a paid brain call
   and fails at the re-judge. Root fix: validateStoryboard requires a
   non-trivial anchor when no world exists.

5. **[MEDIUM] modelRoutes.ts:86 — cloud-only profile leak.** The modelless
   cloud default is consumed as executable by the film engine's image/video
   legs and falls through to LOCAL ComfyUI work (VRAM purge included) —
   the exact profile law the route gate exists to enforce, violated by its
   own default. Fix: throw like the speech leg does.

6. **[MEDIUM] uiStore.ts:42 — invisible windows.** Panel-open setters
   assume the Generate surface; the settings and optimizer palette verbs
   don't route, so the window opens invisibly and verb-optimize (a toggle)
   can stop the brain it just started on a second press. Fix in the store:
   every open-branch also sets surface generate.

7. **[MEDIUM] client.ts:95,103,114,184 — dishonest cancels.** The
   fire-and-forget POSTs never check res.ok; against a down backend the
   store marks jobs Cancelled/Cleared while the server queue is untouched.
   The freeVram idiom (with its own incident comment) is already in the
   file — apply it.

8. **[MEDIUM] schema.ts:113 — the silently-discarded migration.**
   withFactoryConstraints adopts factory frames_max without checking the
   bundle's own detent; for custom-detent files the store's recheck drops
   the ENTIRE vocabulary migration, every load, silently. Fix: floor the
   cap onto the file's detent (constraints.ts:57-59 already does this at
   runtime).

9. The nine LOWs are recorded per-file with fixes; none is urgent, and
   three are purely latent (versionOf "2.10", phraseGrid beatsPerPhrase
   guard, snapToBeat unsorted-input note).

## Doctrine notes (first run under 0.3.0)

The context-hunt flow worked as designed: all four same-sha hunts produced
genuinely new findings (2/3/3/1) — none restated its record — so no lock
engaged anywhere (locks need three empty model types; glm found material
everywhere except where there was nothing to find). The DELTA close-the-loop
confirmed the 2026-09-05 remediations hold (worldmodel's four carried items
verified fixed) and that analysis.ts's comment-only delta carried no
regression (re-audited, 0 new). The catalog HIGH is the doctrine's first
catch-of-its-own-tail: the fix shipped yesterday hardened approximate data
into hard pins — the _r2 hunt on identical bytes is exactly the pass that
surfaces it.
