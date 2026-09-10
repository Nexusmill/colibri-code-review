# Colibri review — vite.film.ts (feature)

- **Source:** `vite.film.ts` · **sha256:** af1eb46f
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the film product's server (2307 lines) — the whole pipeline: record store, ladder building from live catalogs with the price-truth order, askBrain transport, transcription, the vision grader, produce job with checkpoints/keyframe-review gates/budget gate/throttle recovery/fallback rungs, the wizard's 20+ actions, recycle-bin deletion, the calibration battery; owner rulings 29-43; memory: engine test prompts standard, price floor, replicate quirks; last touch c9bb3bb (2026-09-05).

## What this module does

The film engine. Draft: critique gate → world build (3 attempts, typed validation) → computed grid (song duration + transcribed lyric slots, or shape minutes) → KB-grounded draft with validated re-asks → world-anchored adversary loop (below-B re-drafts, bounded 2). Bill: strategy-aware two-pass pricing at the picked pair. Produce: resumable plan (only gaps rerun), per-shot spend gate answering to the LEDGER, 20s checkpoint windows and keyframe-review gates (universal), silent-footage doctrine, joins-planned dissolve assembly, held-back failed boards with their repair path, throttle waits (not billed), per-shot ladder fallback, auto-retry pass, halt reasons that survive restarts. Plus: recycle-bin run deletion with surfaced failures, window redraft re-judged by the same adversary, ratings into the corpus, film defaults, the runs list with stage truth.

## Suggested add-ons

**Run the full calibration battery — both owner-standard prompts, both axes** — Value High · Effort S-M
- What: the live battery run executes `plan.prompts[0]` only (verified, line 2114) and 4 engines, while `batteryPlan` returns the full prompts×engines plan the dry-run quotes.
- Why: the owner's engine-test standard is TWO prompts (the people/faces wall — two persistent characters trading a beat — and the action axis), and the standing rule is an engine failing either axis fails the brief. A battery that tests one axis produces half a verdict and misprices the ladder's faith in an engine.
- How: loop `plan.prompts` (both entries), grade each clip per axis, record both in the corpus entry; a failed axis can write the ENGINE_HEALTH entry (see next add-on).

**ENGINE_HEALTH as a persisted, re-verifiable record** — Value Med-High · Effort S-M
- What: the denylist is a source literal (lines 181-183) whose own comment says "the ratings corpus's failure loop (Task 8) will own this list." Move it to a gitignored `engine-health.json` (date + reason + verified-by fields) with a re-verify affordance (one battery clip on that engine re-tests and clears).
- Why: a mis-deployed provider model stays invisible forever or until a source edit; the denylist's exit path ("until re-verified") does not exist — nothing can re-verify. The recycle/firstrun/defaults gitignored-file pattern is established here three times over.
- How: read/write beside film.defaults.json; `buildLadder`'s denylist reads it; the battery writes it on axis failure.

**Bill price provenance** — Value High · Effort S-M
- Filed in the autopilot.ts review (BillLine lacks `source`); the wiring lands here at `autopilot-bill` (lines 1709-1761) where `priceSource` is already computed per engine and then dropped before `computeBill`.

**A review-clip artifact class** — Value Low-Med · Effort S
- What: `review_*.mp4` checkpoint clips match no prefix in `readArtifacts` (verified, lines 488-505) and land in the catch-all `other` bucket; one film accumulates one per window.
- Why: "each artifact in its own class, nothing folded" is the classifier's own law; REVIEW is a real pipeline role (the checkpoint evidence), currently folded into OTHER.
- How: one more prefix branch + FilmArtifacts field + the library's kind rendering; or delete the clip after its verdict if retention isn't wanted (an owner call — evidence doctrine favors keeping it classified).

## Nice-to-haves

- Song dedupe: re-uploading the same song stages a new timestamped file and re-pays transcription ($0.01 + API round-trip); a content-hash reuse of films/songs + transcripts is a small saving. Low.
- `transcribePerSong: 0.01` is a hardcoded estimate in the bill — it's an owner-verified constant without the owner-price plumbing; fold into OWNER_PRICES for consistency.

## Notes

- Verified non-gaps: classic console retirement refuses honestly (film-console-legacy row); provenance budgets are separate; the finishing switch demands a priced finish line; joins are planned arithmetic.
