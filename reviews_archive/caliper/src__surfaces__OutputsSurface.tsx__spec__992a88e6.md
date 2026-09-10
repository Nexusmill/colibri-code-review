# Colibri spec review — src/surfaces/OutputsSurface.tsx

- source: E:\AI\Caliper\src\surfaces\OutputsSurface.tsx (213 lines)
- reviewer: ZCode fresh-context subagent
- sha: 992a88e676ed5b2d42558d0992ffad90286c5ed74c74cbbf42412ea32f6255a0
- date: 2026-08-31
- mode: spec conformance (registry: E:\AI\Caliper\spec\library-outputs.json)
- context: The Outputs archive surface — FILM ASSETS case files (FilmPanel/FilmFileCell), MODEL ASSETS one-off shelf (ModelCard), and the two REPRODUCE handoffs into the screenStore formula-sheet slot. Judged only against the four archive clauses (LIB-TWO-DIVISIONS, LIB-CASE-FILE-ORDER, LIB-REPRODUCE-SHEET, LIB-REPRODUCE-FILM); the library-window clauses are owned by other files. Adversarial pass used live call-site evidence: screenStore.ts (openAsset/openReproduce/ReproducePayload), assetsStore.ts (pickFiles/AssetItem/hydrate), api/film.ts (filmList/autopilotStatus), api/client.ts viewUrl (film route), components/ReproduceSheet.tsx (sheet internals), and vite.film.ts:514 / vite.replicate.ts:234 / vite.openrouter.ts:238 / vite.eachlabs.ts:58 (provenance records with `type: "film"` outputs).

## Verdict

B — one CONFIRMED degradation of the LIB-TWO-DIVISIONS quiet clause (film-owned renders leak into MODEL ASSETS whenever the film list is empty — failed fetch, or fetch slower than provenance hydrate), plus one PLAUSIBLE flow-shape deviation on LIB-REPRODUCE-FILM. LIB-CASE-FILE-ORDER and LIB-REPRODUCE-SHEET conform in this file.

## Divergences

### 1. Film-owned renders leak into MODEL ASSETS when the films list is empty — LIB-TWO-DIVISIONS (quiet clause) — CONFIRMED

- Expectation (quoted verbatim): "anything a film owns lives ONLY in that film's case file."
- Trigger: `filmList()` rejects — line 136 swallows it silently: `void filmList().then((fs) => setFilms(...)).catch(() => {})`. It is fetched exactly once on mount; there is no retry and no error surface (`filmError` is written only by `reproduceFilm`). The same state exists transiently whenever provenance hydrate (line 134, parallel fetch) settles before `filmList` does.
- Behavior: With `films === []`, `filmIds` (line 156) is empty, so the one-off filter at line 157 — `all.filter((it) => !it.outputs.some((o) => o.type === "film" && filmIds.has(o.subfolder)))` — matches nothing, and every film-owned provenance record renders as a MODEL ASSETS card. These records exist and carry `type: "film"` (server: vite.film.ts:514, vite.replicate.ts:234, vite.openrouter.ts:238, vite.eachlabs.ts:58 — confirmed producers), so the client-side exclusion is the live mechanism and it is keyed entirely on a fetch this file lets fail in silence. In that state FILM ASSETS shows "No films yet" while film work sits below in MODEL ASSETS, and the shelf's own copy (line 199: "work a film owns lives in its case file above") becomes untruthful — against both the clause and the standing truthfulness rule.
- Fix: Gate the exclusion on the films fetch having settled — hold film-typed outputs out of MODEL ASSETS until `filmList` resolves (film-owned items are never shelf candidates regardless of list contents), and surface a filmList failure (retry or error line) instead of `catch(() => {})`.
- CONFIRMED — the missing guard is fully traceable in this file; the trigger only requires the once-per-mount fetch to fail once.

### 2. Film REPRODUCE routes through an intermediate formula sheet before seeding — LIB-REPRODUCE-FILM — PLAUSIBLE

- Expectation (quoted verbatim): "REPRODUCE on a film seeds a new autopilot run with the old formula and opens the wizard at THE PLAN - the storyboard carried over, the bill re-priced at today's prices, APPROVE spends."
- Trigger: Pressing REPRODUCE on a film case file (line 73-76) → `reproduceFilm` (line 174-186) → `openReproduce({ kind: "film", ... })` opens the formula sheet; the run is seeded only when the sheet's REPRODUCE FILM key is pressed (ReproduceSheet.tsx:127-131: `autopilotCreate` + `autopilotPatch` carrying `storyboard/engines/references/visuals`, then wizard remount "at THE PLAN").
- Behavior: One clause-described action is implemented as two presses. The end state conforms — new run with the old formula, storyboard carried, wizard at THE PLAN, "Cost then $… at the prices of that day" shown as then-prices with the new bill re-priced (ReproduceSheet.tsx:155), and the film panel's button title (line 74) truthfully describes the chain. But the clause names no confirmation step on the film path (the registry reserves the formula-sheet pattern for the model clause), so this is a deliberate-but-unnamed extra step rather than a broken outcome. The routing decision lives in this file (line 180); the sheet UI is another file's.
- Fix: Owner's call — either amend the clause to name the film formula sheet as the confirm step, or make film REPRODUCE seed and open the wizard directly.
- PLAUSIBLE — end-state conformance verified; only the intermediate step diverges from the clause's single-action wording, and it appears intentional (screenStore's ReproducePayload comment documents the film path "through the wizard's plan approval").

## UNJUDGEABLE HERE

- Artifact classification into final/cuts/footage/storyboards/scripts/lyrics/sound/other (feeds LIB-CASE-FILE-ORDER's strip inputs and the extra OTHER FILES bucket) — owner: vite.film.ts `readArtifacts`, server-side.
- LIB-RAIL-DISK-TRUTH, LIB-GESTURE-GRAMMAR, LIB-ZIP-EXPORT, LIB-WINDOW-OS, LIB-ORGANIZER, LIB-PROVENANCE-SHARED — owners: the library window in src/components/ and the server-side provenance store (vite middleware).
- LIB-SOUND-PLATE, LIB-STORYBOARD-COMPOUND — owners: MediaView / rendered-document components and server-side storyboard generation.
- Formula-sheet internals for both REPRODUCE clauses (cost-truth run line wording, LOCK SEED key, editable fields; film bill re-pricing at today's rate card, APPROVE spends) — owner: src/components/ReproduceSheet.tsx plus the wizard/autopilot middleware. Verified present there for context (lines 86, 106, 127-131, 155 — no violation observed); its judgment belongs to that file's review.
- Provenance record shape and budgets (who writes `type: "film"`, film-vs-one-off eviction windows) — owners: vite.film.ts, vite.replicate.ts, vite.openrouter.ts, vite.eachlabs.ts, server-side.
