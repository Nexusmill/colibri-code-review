# Spec review — src/components/FilmWizard.tsx

- **Source:** E:\AI\Caliper\src\components\FilmWizard.tsx (1207 lines)
- **Reviewer:** ZCode fresh-context subagent
- **SHA-256:** cff01eecf3c80eddbf8bdc6517f5585eda8827749885f840591630ddf1c93bb3 (`cff01eec`)
- **Date:** 2026-08-31
- **Mode:** spec conformance (registries: spec/film-wizard.json, spec/film-run.json)
- **Context:** the six-step wizard UI — navigator rail with honest gating, key gate + scenario availability, THE BRIEF placement, critique gate display, THE ENGINES (tier slider, classified lists, clip cap, strategy, live money, interrogative extras), THE PLAN (adversary line, words-only approval), THE BILL (stop + APPROVE SPEND), the run view (LIVE line, log tail, grade rail + framed legend, KF/VID letters, Reroll:N), KEYFRAME REVIEW + CHECKPOINT banners and gated CONTINUE, the finishing switch, reload-resume, no SHOT CONSOLE escape.

## Verdict

**PASS WITH FINDINGS — 3 divergences (2 MEDIUM, 1 LOW), all CONFIRMED; 8 clause-halves unjudgeable here (server/logic owners).** The rail naming/gating, key gate, scenario families + per-scenario idea fields led by THE BRIEF, critique display + both answers, engine tiers/lists/clip cap/default, plan words-only approval + adversary line, bill stop + APPROVE SPEND, run-view life (ticking LIVE line, log tail, framed legend, KF/VID letters, spelled-out Reroll:N, in-place click-open inspector, muted mv previews), checkpoint + three repairs, finishing switch, reload-resume-at-THE-RUN, and no-console-escape are all satisfied and get silence.

Notes (not clause divergences):
- Line 14's header comment ("the classic shot console stays one click away") is stale vs RUN-NO-CONSOLE-ESCAPE's retirement — nothing renders it anywhere (repo search: only this comment; tools/ui-harness.mjs `film-console-legacy` guards the render).
- The KEYFRAME REVIEW EDIT title promises "edit the board prompt", but the ADJUST drawer edits only the shoot prompt (vite.film.ts:1927 `adj.op === "prompt"` patches `shootPrompt` only; no board-prompt op exists). The clause's own wording ("the shot's adjust drawer, then reroll") is satisfied; noted as title-truthfulness, not a finding.
- Auto-resume of a PRODUCING film restores record only; job/grades arrive via the 3s poll (manual resumeRun sets both immediately). Judged within "live progress intact".

## Divergences

### 1. RUN-KEYFRAME-GATE — disabled_state — MEDIUM — lines 1015, 1039 — CONFIRMED

**Expectation (quoted):** "CONTINUE - SHOOT THE APPROVED is disabled until the window is fully approved or rerolled."

**Trigger:** KEYFRAME REVIEW with at least one board REROLLed (and not re-approved), all other boards approved.

**Behavior:** the enable predicate is `win.every((s) => grades?.[s.index]?.boardApproved)` (line 1015) — it counts only approval. The server's reroll-board handler deletes the grade entry's `boardApproved` together with the artifact (vite.film.ts:1977 `delete entry.board; delete entry.boardApproved`), and the client refreshes grades immediately after a reroll op (FilmWizard.tsx:406-409), so a rerolled board reads "awaiting" again and CONTINUE stays disabled (line 1039). The button's own disabled title says "every board must be approved or rerolled first (N/M approved)" — the predicate does not implement the "or rerolled" half. The only path forward is pressing APPROVE on the board just rejected (its keyframe is already deleted, so the run regenerates it — the flow proceeds, but through a contradictory press).

**Fix:** treat a rerolled board as settled in the predicate (e.g. surface a `rerollQueued`/artifact-missing flag the predicate ORs with `boardApproved`), or have the reroll-board op keep `boardApproved` set while queueing the rerender — either way the gate opens when every board is approved or rerolled, as written.

**Status:** CONFIRMED — predicate read at line 1015/1039; server behavior traced at vite.film.ts:1958-1979; grade refresh path read at FilmWizard.tsx:399-414.

### 2. WIZ-SCENARIO-FAMILIES — disabled_state — MEDIUM — lines 428-433, 436-444, 633 — CONFIRMED

**Expectation (quoted):** "unavailable scenarios render disabled with the reason named."

**Trigger:** fresh wizard open at WHAT ARE YOU MAKING (step 0, no scenario ever chosen) on a key set whose ladder has no lyrics-capable music engine (`ladder.score` without `musicCaps[...].lyricsInput`) or no dialogue-capable shoot engine (`ladder.dialogueShoot === 0`).

**Behavior:** the ladder fetch is gated on `draft.stepIdx >= 3 || scenario` (line 430) — at first entry to step 0 neither holds, so `ladder` stays null, the `availability` memo returns null (line 437), and the scenario buttons render enabled with the generic `s.detail` (line 633 `disabled={!!availability?.[s.id]}`). `chooseScenario`'s guard (line 450) is equally inert, so an unavailable scenario can be chosen; the availability gate only becomes live after some scenario is picked or THE ENGINES is reached (the ladder then persists in state, so later visits to step 0 are gated). The disabled_state mechanism exists but is dead exactly when the choice is first made.

**Fix:** fetch the ladder as soon as `defaults` and a cloud key are ready regardless of step (the effect at 428-433 already has both in deps), so `availability` gates the first scenario choice; the reason-named title/detail spans (lines 634, 639) then render as specified.

**Status:** CONFIRMED — load condition read at 428-433, memo at 436-444, button at 628-641; `filmLadder` has no other call site in the file.

### 3. WIZ-STRATEGY-AND-MONEY — cost — LOW — line 844 — CONFIRMED

**Expectation (quoted):** "estimates are labelled worst case by strategy and cover both engines."

**Trigger:** THE ENGINES with strategy ALL CHEAP or STRAIGHT TO FINISH selected.

**Behavior:** the money line labels only the draft-first branch with the qualifier — `draft-first worst case ≈ $… (rehearsal + finishing)`; the other two strategies render `all-cheap ≈ $X` and `straight-finish ≈ $X` with no worst-case words. Both engines are quoted per film and per 20s window on every branch (cover-both-engines half satisfied); the worst-case labeling is not carried across strategies — and the numbers are single-rate products, so with rerolls they are floors the label is supposed to disclose.

**Fix:** carry "worst case" on all three strategy branches (e.g. `all-cheap worst case ≈ …`, `straight-finish worst case ≈ …`).

**Status:** CONFIRMED — literal render string at lines 840-845.

## UNJUDGEABLE HERE

- **WIZ-BRIEF-OUTRANKS** ("the brain reads every lyric, script, and prompt through it… the brief's words outrank the brain's interpretation") — owner: src/film/autopilot.ts (draftPrompt carries THE BRIEF as leading material; verified present at autopilot.ts:401-404) + vite.film.ts for non-MV paths. UI half (brief is the first field of THE IDEA, labeled "the brain reads every lyric and script through it") judged satisfied.
- **WIZ-CRITIQUE-GATE** — "the critique precedes any storyboard spend" and "the reasons each naming its law" — owner: vite.film.ts (autopilotDraft runs the critique before drafting; reasons text is server-authored). UI half (banner, reasons, SUGGESTED, EXAMPLE, USE/KEEP, no draft until acted on) judged satisfied.
- **WIZ-ADVERSARY-FIRST** — four-axis judging, below-B re-drafts bounded at two passes, and the storyboard.md side effect — owners: src/film/adversary.ts + vite.film.ts. UI half (grade, passes, findings-on-hover traveling with the plan) judged satisfied.
- **WIZ-CLIP-LENGTH-CAP** — boundary "only holds longer than 20s (past every engine's ceiling) are flagged" — owner: src/film/adversary.ts (adversary.test.ts: "only PAST-ENGINE-MAX holds do"). Chooser half (min-of-pair cap via maxClipSeconds, default 15s, past-ceiling lengths unchoosable, clamped on every pair change) judged satisfied.
- **WIZ-ENGINE-TIERS / WIZ-INTERROGATIVE-EXTRAS data** — tier seatings (MEDIUM = p-video 720-standard $0.02/s draft + minimax/h3 768 $0.08/s finish; EXPENSIVE promotes h3 to draft, sora-2-pro $0.30/s 720 / $0.50/s 1080) and the three question labels — owner: src/film/autopilot.ts (ENGINE_TIERS/ENGINE_CARDS/ENGINE_QUESTIONS; read and verified matching). FilmWizard renders them faithfully.
- **WIZ-PLAN-WORDS-ONLY** — "no footage exists before approval, and the draft with the KB loaded obeys the craft doctrine" — owner: vite.film.ts. UI words-only approval pane judged satisfied.
- **RUN-GATES-UNIVERSAL / RUN-KEYFRAME-GATE side effects / RUN-RESUME-GAPS-ONLY** — plan refusing segments for unapproved boards regardless of scenario, approved segments shooting before next window's boards, reroll clearing approval+artifact, gaps-only resume — owners: src/film/produce.ts (planProduce; verified in src/film/produce.test.ts) + vite.film.ts (reroll clears verified at 1964/1977). UI renders the gates for every scenario.
- **RUN-CLIP-CHECKPOINT side effects/boundaries** — failures/ move, failure-knowledge append, review clip cut to its span of the song, final window running straight to assembly — owner: vite.film.ts. UI half (checkpoint banner, APPROVE — SHOOT THE NEXT 20s, REJECT THE LOT, three repairs incl. the ADJUST drawer path) judged satisfied.
- **RUN-SILENT-FOOTAGE server half** — generate_audio false + stream-copy strip on ingest — owner: vite.film.ts. UI half (inspector previews `muted` for `mv-*` scenarios, line 1144) judged satisfied.
- **RUN-FINISHING-SWITCH route priority** — "answers to strategy+mode first, then the manual engines.shoot override, then the ladder" — owner: vite.film.ts. UI half (FINISH — REROLL THE FILM ON <finish model>, shown only when strategy is draft-first and mode is not finish) judged satisfied.
- **RUN-BUDGET-STOP cost discipline** — "money figures quote the provider page rate card, never a median; a no-stop freezes everything rather than spending blind" — owners: vite.film.ts (bill arithmetic from the rate card; budget guard that HALTEDs) and src/film/autopilot.ts (ENGINE_CARDS per-second data). UI stop + APPROVE SPEND + spent-of-approved readouts judged satisfied.
- **RUN-NO-CONSOLE-ESCAPE repo-wide scope** — "renders anywhere" spans the whole app; owner: the surfaces (nothing renders a SHOT CONSOLE per repo search; tools/ui-harness.mjs `film-console-legacy` enforces it). This file renders no escape.
