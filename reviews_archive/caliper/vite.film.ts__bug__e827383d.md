# colibri bug review - vite.film.ts (delta)

source: vite.film.ts · reviewer: ZCode GLM-5.3 in-session · sha256 e827383ddd2a4dd653a2de2911e9d99f99bc9f70de29e0533d993a3b5b7f4c13 · 2026-09-05 · mode: bug (delta vs 5f594a75 @ 6909725 2026-08-25)
context: full current file read end-to-end (2354 lines); delta = base..HEAD (1471 lines, world-model/checkpoint/critique/recycle-delete era); prior review 5f594a75 findings carried; cross-file: produce.ts checkpointBoundary + planProduce boardApproved gate, budget.ts computeBill/gateStep, boardApproved writers grepped repo-wide (only autopilot-adjust + FilmWizard), filmProduce/filmCreate/... callers grepped (none outside src/api/film.ts); jcodemunch refreshed.

## Verdict

Shippable for the autopilot path (the money paths are gated and the state machine holds). Three new findings: the retired classic-film routes are now trapped dead ends, the xfade assembly smears the song at dissolves, and one contradictory log line. The draft-first finishing switch has a bill-vs-run pricing gap (cross-file, see budget.ts + FilmWizard rows).

## Bugs & vulnerabilities (new or changed in the delta)

**[MEDIUM] classic film routes are trapped dead ends under the universal gates** - `vite.film.ts:2326` (`produce`) + `src/film/produce.ts:34`
- What: planProduce plans segments only for `!!s.boardApproved` shots, and the only writers of boardApproved are autopilot-adjust ops (which require an autopilot.json record) and FilmWizard. A classic film (created via `create`, no autopilot record) can therefore never plan a segment step; if it has more than one window of keyframe work, `kfReviewNow` (line 1112) crashes first on `readAutopilot` ENOENT → the run dies in error phase with a filesystem message.
- Trigger: POST action "produce" on a classic film (or `create` → `produce`).
- Impact: no live UI path reaches these actions today (filmCreate/filmProduce/... have zero callers outside src/api/film.ts - verified), so no user hits it; but the route pair is a trap for API use or a UI revival, and the failure mode is a confusing ENOENT, not an honest message.
- Fix: either retire the classic actions outright (409 "films run through the wizard now") or give classic films a degraded gate (auto-approve boards that pass grading >=3 when no autopilot record exists).

**[MEDIUM] xfade assembly crossfades the SONG at dissolves - smear + silent song loss** - `vite.film.ts:928-931`
- What: each cut's audio is the song's own contiguous span (`shot.start..shot.end`); `acrossfade d=0.4` overlaps the last 0.4s of cut i with the first 0.4s of cut i+1 - two DIFFERENT moments of the same song mixed simultaneously (out-of-phase doubling on rhythmic material), and each dissolve consumes 0.4s of song (acc -= XFade), so the film ends 0.4s x N-dissolves short of the song's actual end; that content never plays.
- Trigger: any film with `cutIn === "dissolve"` on 2+ cuts (brain-chosen, validateStoryboard allows).
- Impact: audible artifact at every dissolve in the song bed (the ONLY sound, owner ruling 38) and silent truncation of the song. CONFIRMED by construction; whether the trade is acceptable is an owner ruling.
- Fix direction: keep video xfade, make the audio chain concat (not acrossfade) and rebuild cut audio spans so the song stays contiguous; or trim cut i+1's video by 0.4s so video and audio ellipsis match.

**[LOW] "VID N done" logged for shots that were HELD BACK** - `vite.film.ts:1178`
- What: the done-log guard is `s.phase !== "segments" || film.shots[s.shot!]?.keyframe` - a held-back shot still has its keyframe, so the log prints both "VID 03 HELD BACK" and "VID 03 done in 0s" in the same step. Truthful-status rule violation (log only).
- Fix: also exclude the held-back branch from the done log.

## Missing safeguards (unchanged or new)

- queueAndWait still polls forever when ComfyUI stays reachable but a job never completes (prior finding, still open) - `vite.film.ts:568`.
- transcribeSong's poll fetch has no AbortSignal (bounded by the 80x3s loop, so bounded, but one hung fetch stalls the whole draft) - `vite.film.ts:362`.
- askBrain's cloud fallback silently swaps the brain model on ANY failure (not just quota) - the draft quality changes without a trace in the record.

## Fixed since last review

- [HIGH] gradeAndReroll ungated rerolls - FIXED (gate+est params, halt-check at 1353, est tallied at 1358; traced both call sites).
- [HIGH] local-route → paid-cloud fallback + route poisoning - FIXED (route.backend === "cloud" guard at 1242; local failures log and defer to the auto-retry pass; restore path only under cloud).
- [LOW] audio served as video/mp4 - FIXED and extended (full extension map at 1500 incl. md/txt).
- appendProvenance 200-window eviction flood - FIXED (separate 400 film / 200 one-off budgets at 600-604).

## Verified-correct (adversarial passes, findings deleted)

- The checkpoint/keyframe-review/finish/reject/redraft state machine: record writes are consistent, superseded-run generation guard (produceGen) traced through resume paths, checkpointNow's clip failure degrades to cards, redraft failure clears the poll flag and surfaces run.error, world anchor re-injected on every redraft pass, redraft F-verdict refused wholesale.
- recycle deletion chain: queue-file only process args, serialized chain, 120s kill timer, moving-rows hidden, error rows reappear with deleteError, song-orphan notes drained by the list handler exactly once.
- Ledger-outranks-estimate gate sync (1141-1143) + halt persistence to the record (1322-1329); throttle 429 never billed into the gate (65s waits, no est add); explicit duration+resolution on every cloud shoot (the $7.01 lesson); stripToSilent failure is benign (assembly re-marries the song anyway).
- mv-user-song: no score leg billed or run (hasScore exclusion at 1748, score=null at 1841); draft loop's validate-and-reask actually catches now; critique gate cannot deadlock (critiqueAck persisted before return, renderable pass marks it).
- song-upload / autopilot-ref path containment (timestamp-prefixed sanitized names, resolve+startsWith) - ".." cannot traverse (prefix defeats it, containment verified).
- The kf-gate enforcement IS server-side (segments plan only for approved boards) - the log's "CONTINUE buys no footage until every board is approved" matches planProduce's filter; resume retiring kfReview does not bypass it.
