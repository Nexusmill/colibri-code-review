# Colibri review — src/components/FilmWizard.tsx (feature)

- **Source:** `src/components/FilmWizard.tsx` · **sha256:** 77eb2282
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the film product's only door (ruling: film-console-legacy) — 17 api/film endpoints, the engine-pair doctrine, all gate features (critique/kf-review/checkpoint/finishing); owner rulings 27-46; verified absences: no `record.world` render, adjust drawer max=12; last touch c9bb3bb (2026-09-05).

## What this module does

The six-step wizard plus the run view: the key gate; the scenario picker with YOUR RUNS (stage words, resume-at-own-step, DELETE→Recycle pair); THE IDEA (brief leads, per-scenario fields, song upload guarded by the draft-generation token, reference chips with visible intents); THE SHAPE (live draft total); THE ENGINES (the pair: tier slider, classified cards with +/−, clip cap, strategy, per-window money, the three interrogatives, per-leg AUTO picks with caps honesty); THE PLAN (critique block with USE/KEEP, adversary verdict line, board list, APPROVE/RE-DRAFT); THE BILL→THE RUN (bill lines, APPROVE SPEND, produce with the LIVE ticking line + log tail, keyframe review grid with settled counts, checkpoint player with APPROVE/REJECT/FINISH, rejected-window repairs, grade rail with letters + spelled rerolls, in-place click inspector, adjust drawer, WATCH/upscale/rating that holds the door). Local-until-commit draft discipline (localStorage pending), the auto-resume priority chain (live job → pending verdict → saved draft → server draft), and stalled-run truth.

## Suggested add-ons

**THE PLAN shows the built world** — Value High · Effort S-M
- What: render `record.world` at THE PLAN — the compiled anchor human-readable (characters and sets as readable sheets, or compileAnchor's text) with an EDIT affordance (one brain amendment call, recompile).
- Why (verified): THE PLAN (stepIdx 4, the record branch at lines 1123-1154) renders title/adversary/styleBible/shot rows — `record.world` appears NOWHERE in the file; the world is visible only as the inspector's collapsed dim ANCHOR line. The ruling-42 plan explicitly included "THE PLAN shows the world model for approval," and a mis-built constant is only discoverable after money spends. Pairs with the worldmodel.ts review's edit gate (the server pieces all exist: PATCHABLE includes world, compileAnchor is pure).
- How: a world section above the board list; edit = patch world with the correction + one askBrain amendment (new server action or reuse the draft's world loop with a correction field).

**The retime drawer should follow the pair's ceiling** — Value Med · Effort S
- What: the adjust drawer's seconds input is hardcoded `max={12}` (line 1393, title "1-12s") while the SERVER accepts 1 to `maxClipSeconds(draft, finish)` — 15 on the default medium pair. Retiming a shot to 13-15s is legal server-side and unreachable from the UI.
- How: compute `maxClipSeconds(record.shape.draftEngine, record.shape.finishEngine)` (already imported in this file for THE ENGINES) and use it for min/max/title. The 1-12 literal is the exact shape the spec-run-#1 fix removed server-side; the drawer kept it.

**Bill line provenance badges** — Value High · Effort S-M
- The display hook for the R1 autopilot.ts add-on: the bill rows (lines 1204-1210) render `$X` or "unpriced" with no source; OWNER/PAGE/ESTIMATE beside each number is where the price-truth doctrine becomes visible at the moment of approval.

**YOUR RUNS family filter** — Value Low-Med · Effort S
- The runs list is unfiltered; with many runs a family chip (MUSIC VIDEO / VOICE OVER / SCRIPT — the group labels already computed per row) narrows it. Data's all client-side.

## Nice-to-haves

- The checkpoint review player could show the window's span on the song timeline (start–end mm:ss beside the player) — context for what APPROVE endorses; cosmetic-leaning, needs commission.
- RECENT RUNS row could carry spent-so-far visibly (it's in the title only).
