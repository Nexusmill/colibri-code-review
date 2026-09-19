<!-- source: src/film/autopilot.ts | reviewer: glm-5.3-zai-in-session | sha256: d5bc2d8e83f71c1a1ddaab231639466f904e29173c43d5f56a06a762f441855b | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict
The pure core is largely sound, but the redraft prompt has one unguarded optional that both feeds the brain garbage and deterministically bricks the repair path for anchorless plans; two smaller latent defects sit in version parsing and tier-price rebasing.

## Bugs & vulnerabilities
**[MEDIUM] buildRedraftPrompt interpolates the optional anchor unguarded — the literal string "undefined" becomes the frozen continuity law, and repair is deterministically bricked** - `line 639`
- What: `ANCHOR (frozen continuity block - copy CHARACTER-FOR-CHARACTER into every boardPrompt and shootPrompt, exactly as written):\n${sb.anchor}` — `sb.anchor` is optional (`Storyboard.anchor?`) and `validateStoryboard` (line 332) never requires it; the world-stamp `withWorldAnchor` only fires when `record.world` exists (vite.film.ts:1928/1942).
- Trigger: a worldless draft whose brain omits or shortens the anchor field ships anyway — the draft loop exits on the 2-pass limit with the verdict recorded, no F refusal in the draft path — and all four anchor gates in vite.film.ts (1955, 1631, 2391, 2684) are conditioned on `record.world && ...anchor`, so the film produces. A storyboard can also arrive anchorless via PATCH (applyRecordPatch checks only "is an object"). First checkpoint reject -> window-redraft -> this line.
- Impact: the repair brain is instructed to copy "undefined" character-for-character into every prompt (continuity guidance replaced by a garbage token); then the apply-site re-judge (adversary.ts:85-87, `anchor.length < 20` -> continuity F -> vite.film.ts:2408 refuses) rejects every attempt — each press of RE-DRAFT burns a full minutes-long brain call (paid, on the cloud brain) before failing with an error that names the redraft, not the missing anchor. The repair path can never succeed for such a film.
- Fix: at line 639 use a guarded value — `sb.anchor?.trim() || compileAnchor(record.world)` — or throw a clear build-time error ("the plan has no frozen anchor - re-draft the film") so the refusal happens before the brain call; root fix is validateStoryboard requiring a non-trivial anchor when no world exists, matching the draft contract at line 493 which already demands the field. CONFIRMED by end-to-end trace.

**[LOW] versionOf collapses "2.10" to 2.1 — minor versions >= .10 rank below .9 in seed-family resolution** - `line 814`
- What: `Number.parseFloat(m[1]!)` turns a trailing "2.10" into 2.1, so `versionOf("music-2.10") < versionOf("music-2.9")`.
- Trigger: any seed family whose slugs carry a two digit minor/patch version (none today — 2.6, 03 — purely latent).
- Impact: `resolveLadder` lines 860-862 picks the wrong "highest version" per service and mis-orders across services — the ladder law ("resolve to the highest version that service carries") silently inverts.
- Fix: split on "." and compare major/minor numerically (tuple compare). CONFIRMED arithmetic; latent trigger.

**[LOW] deriveEngineCards rebases pricePerSec from the live shelf but not tier prices — a tiered card can speak two rates at once** - `line 557`
- What: `cards.push({ ...owner, pricePerSec: e.priceUsd ?? owner.pricePerSec, ... })` honors "the live price outranks the card's recorded one" for the base rate only; `owner.tiers` (h3's 768P $0.08 / 2K $0.13) and the strengths prose are copied unchanged.
- Trigger: the ladder's `priceUsd` for a tiered engine (replicate/minimax/h3) diverging from the card's recorded 0.08 — exactly the drift scenario the fallback exists for.
- Impact: the card's own `pricePerSec` and the FINISH RESOLUTION estimate (FilmWizard's `tieredPrice` reads `card.tiers`) disagree, while the server bill prices from its separate tierOf sources (vite.film.ts:2018) — estimate/ledger divergence the owner sees as two different rates for one engine.
- Fix: when overriding from the shelf, either scale/drop `tiers` or skip the override for tiered cards. PLAUSIBLE — unverified because no live ladder/card price divergence exists today to observe.

## Missing safeguards
- `validateStoryboard` (line 332) never requires an anchor for worldless films although the draft contract (line 493), the adversary's continuity axis, and all four downstream gates assume one — the root of the MEDIUM finding.
- `applyRecordPatch` validates only top-level section kinds, not inner enums: a `shape` patch with a garbage `quality` crashes `QUALITY_LABEL[record.shape.quality].toLowerCase()` (line 406) with a bare TypeError; `strategy`, `finish`, `finishResolution`, and `visuals` accept any string (garbage `visuals` silently degrades to lyrics-lead at line 451).
- `validateStoryboard` accepts any lowercased `cutIn` (line 301) while `parseRedraft` enforces CUTIN_CANON (line 665) — a draft can ship a transition word the redraft contract forbids.
- AUTO-resolved engine picks are never written back into `record.engines` at produce time (overrides only, vite.film.ts `pick(leg)` resolves at runtime), so default runs feed nothing to `winRatesFromRuns` — the ladder's learned ordering only learns from explicitly overridden legs.
- `winRatesFromRuns` credits one film's star rating to every leg's engine simultaneously and merges engines across legs by ref — film-level outcome attribution by design, but a bad shoot engine drags the board/score engines' rates with it.

context-pack: autopilot.ts pure core (tier catalog, ladder, prompts, patches); prior review was vocabulary-only with zero open bugs; consumers traced in vite.film.ts (draft 1928-1968, redraft 2342-2430, bill 1975+, patch 2808), adversary.ts anchor axis, worldmodel.ts carriesAnchor/withWorldAnchor, FilmWizard.tsx tier pricing.
new-findings: 3
