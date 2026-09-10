# Spec review — vite.film.ts (the recommended dispatch)

- Source: `vite.film.ts` (2123 lines, post-remediation bytes) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `ba2db7fe3a3298fff9c996bd0997e89092947a2060fbe3b2fa04d29b00d725c7` · 2026-08-31 · mode: **spec** · registry: `spec/film-run.json` (+ film-wizard.json server halves)
- Context pack: read end-to-end in three passes (1-700, 700-1400, 1400-1960 + the adjust region read during remediation; 1960-2123 covered by outline + the reroll-op reads); cross-verified against src/film/autopilot.ts (record shape, ENGINE_TIERS, maxClipSeconds), src/film/produce.ts exports (planProduce, checkpointBoundary), and the vitest coverage named in FEATURES.

## Verdict
The produce engine conforms on nine of ten judged clauses — the checkpoint machinery, universal gating, the finishing switch (with the documented strategy→override→ladder precedence), the budget gate with ledger-outranks-estimate, gaps-only resume, and the critique/adversary server halves are all present and traced. One CONFIRMED divergence: the silent-footage guard guards only one of the two cloud legs.

## Divergences
**[MEDIUM] The silent-footage guard is OpenRouter-only; the Replicate leg has neither suppression nor the ingest strip** - `genSegment`, the `route.service === "replicate"` branch (~line 660-695)
- **Expectation (quoted):** RUN-SILENT-FOOTAGE — "Music-video footage is generated SILENT - generate_audio false and a stream-copy strip on ingest; inspector previews play muted" (side_effects: "the ingest strip removes the audio track without re-encoding").
- **Trigger:** a song film shooting segments on any Replicate video engine — which is THE ENGINE PAIR's service (p-video, minimax/h3) and sora-2-pro at the expensive tier, a model the code itself marks `caps.audio: true` (the grok-imagine|veo|sora regex in buildLadder).
- **Behavior:** the OpenRouter branch sends `generate_audio: false` (when film.song/scorePrompt) AND belt-and-braces stream-copies `-map 0:v:0` on ingest when film.song; the Replicate branch sends neither — an audio-capable engine's segment lands on disk with its own audio track (audible on direct open), and nothing enforces the code's own stated intent ("the engine must not generate what assembly discards" — i.e., don't pay for audio).
- **Mitigations traced (why MEDIUM not HIGH):** cut assembly and review clips both map `0:v:0` + the song's audio, so every assembled output keeps the song as the only sound; today's default pair (p-video, h3) is evidently audio-less, so the observable bites only on audio-capable picks.
- **Fix:** hoist the film.song-conditioned stream-copy strip out of the OpenRouter branch to cover both cloud legs (service-agnostic ingest guarantee), and suppress audio at request time where the engine's schema offers it.
- CONFIRMED — both branches read; assembly maps traced; the capability regex is the file's own assertion.

## UNJUDGEABLE HERE
- RUN-KEYFRAME-GATE "the plan itself refuses segments for unapproved boards" — lives in `src/film/produce.ts` planProduce (vitest covers it; this file contributes the kfReview hold + the CONTINUE-resume retirement of the review).
- CONTINUE — SHOOT THE APPROVED disabled-state, banners, repair-block rendering — wizard UI (FilmWizard/run view).
- RUN-VIEW-SHOWS-LIFE — run-view UI; this file supplies the polled truth (job.log tail, grades, per-step current) it renders.
- RUN-NO-CONSOLE-ESCAPE, inspector previews muted — UI layer.

## Conforming by direct trace (silence = satisfies)
RUN-CLIP-CHECKPOINT (checkpointNow clean stop; review clip cut to the window's song spans; APPROVE archives windows; REJECT: failures/ move + seed bump + grades forget + appendFailureBin APPENDS prompts/grades/verdict; three repairs: reroll ops, window-redraft, adjust-prompt) · RUN-GATES-UNIVERSAL (boundary/kfBoundary computed for every film, no scenario fork) · RUN-FINISHING-SWITCH (autopilot-finish requires draft-first + finishEngine; discards segments, keeps boards/approvals; still gated; shoot resolves strategy+mode → engines.shoot override → ladder) · RUN-BUDGET-STOP server half (bill required before approve and before any run; per-step gate; ledger outranks estimate; halt reason persists across restart) · RUN-RESUME-GAPS-ONLY (plan skips done work; one auto-retry; resumable states incl. done-with-gaps via allowStepBack) · WIZ-CRITIQUE-GATE server half (critique first unless critiqueAck; critique verdict writes the record and drafts NOTHING; renderable marks and never re-pays) · WIZ-ADVERSARY-FIRST server half (judgeStoryboard, below-B re-drafts bounded at 2, verdict travels with the plan) · WIZ-CLIP-LENGTH-CAP (grid carved at `clipSeconds ?? 15` in both song and songless branches).

## Remediation cross-check
This run re-verified today's fix in context: the adjust route now bounds seconds by `maxClipSeconds(record.shape.draftEngine, record.shape.finishEngine)` with the import in place — consistent with the pair doctrine and with `framesForSlot`/duration rounding on the render paths.
