<!-- source: src/film/worldmodel.ts | reviewer: glm-5.3-zai-in-session | sha256: cccc3044893c92f426c464db1b9e4362cc8139e8db5a087dc3ee40895330a610 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

All consumers traced end to end.

## Verdict

The delta (version stamping, castOf, setDrift — ac82399) is advisory-only in the UI and its helpers are sound in isolation, but the version stamp's truthfulness rests on an unenforced process assumption: a world EDIT that is not followed by a re-draft stamps new takes with the new version while their prompts still carry the pre-edit anchor — the costume-change detector then certifies exactly the takes that contradict the corrected constants.

## Fixed since last review

- **carriesAnchor stop-word-less token coverage (prior review's only open item)** — still-open, accepted-by-design: the tokenizer at `line 240` is byte-identical (`(t) => t.length > 2` filter, no stop-word list); the delta's `castOf` deliberately reuses it and neutralizes the concern for names via the all-words-required rule at `line 79`.
- **duplicate-name refusal (carried from 80b059a3, noted fixed in prior review)** — fixed, verified: `refuseDuplicates` at `lines 123-129`, wired for characters and sets at `lines 200-201`.
- **set materials validated twice (carried from 80b059a3)** — fixed, verified: `strList` runs once at `line 179` and the result is reused at `line 194`.
- **anchor lost on the window-redraft path (80b059a3 HIGH)** — fixed, verified outside this file: carriesAnchor gates now ride all four doors — build/pre-spend (vite.film.ts:1630-1635), draft (vite.film.ts:1955-1958), window redraft (vite.film.ts:2388-2395), per-shot edit (vite.film.ts:2684-2686).

## Bugs & vulnerabilities

**[HIGH] Post-edit takes stamp the NEW world version while their prompts still carry the pre-edit anchor** - `line 66`
- What: `WorldModel.version` (doc at `lines 61-67`) promises takes "carry the version they were built under", but nothing links a storyboard to the world version it was drafted under — `withWorldAnchor` (`lines 230-232`) compiles text only. The stamp pipeline takes the world's CURRENT version: film build reads `record.world.version` (vite.film.ts:1658), and every board/segment stamps `shot.worldVersion = film.worldVersion` (vite.film.ts:803/828/911/957/975) — while shot prompts come from `record.storyboard.shots`, whose baked words and anchor are NOT recompiled when the world is patched (the autopilot-patch handler at vite.film.ts:2796-2805 validates + bumps `w.version = (w.version ?? 0) + 1` and swaps `record.world` via `applyRecordPatch` (autopilot.ts:778) — no `withWorldAnchor`, no step reset).
- Trigger: at THE PLAN, SAVE a world edit (FilmWizard.tsx:1474 `patch({ world: next })` — accepted at any step, no re-draft forced; the save banner only SAYS a re-draft recompiles the anchor), then LOCK/approve/run without re-drafting. The pre-spend gate passes because it compares prompts against the STALE `record.storyboard.anchor` (vite.film.ts:1630-1631, old-vs-old).
- Impact: every take rendered after the edit is stamped with the new version while its prompt still describes the old constants (e.g. black hair after the owner corrected it to auburn). The costume-change detector inverts: pre-edit takes are flagged stale and post-edit takes are certified current, so the rail evidence lies in exactly the scenario the feature was built for — real money spent on takes the owner believes match the corrected world.
- Fix: stamp takes with the version the STORYBOARD was drafted under (record the world version onto the storyboard at `withWorldAnchor` time, or onto the record at draft), or make the patch path refuse/reset the run when `record.world` changes after a storyboard exists, forcing the re-draft the UI already prescribes.

**[LOW] castOf tokenizer edges — hyphen/apostrophe names and <=2-char names are always reported absent** - `line 78`
- What: `has` tokenizes names with `/[a-z0-9'-]+/g` (`line 78`) and requires every token `length > 2`. Two failure modes: (a) a hyphenated or apostrophed name ("Jean-Luc", "D'Arcy") is one token `jean-luc`, so a brain-written prompt spelling "Jean Luc" (or a curly apostrophe) never matches — a USED character lands in `absent`; (b) a name whose only token is <=2 chars ("Jo", "Bo") filters to `words.length === 0`, so `line 79`'s guard returns false and it is reported absent even when named in every shot.
- Trigger: WorldPanel's honesty line (FilmWizard.tsx:172-175) renders `castOf(valid, shots).absent` at approval.
- Impact: false "wasted constant" accusations in the approval UI; advisory only, no write path.
- Fix: split names on `[\s'-]+`-style boundaries (matching how prompts hyphenate loosely) and treat a name with zero surviving tokens as used-if-substring (`shotsText.includes(name.toLowerCase())`).

**[LOW] setDrift's containment denominator flags genuinely distinct sets that share one generic word** - `line 98`
- What: `overlap = shared / Math.min(a.size, b.size)` with the `>= 0.5` threshold at `line 104` means two set names sharing half the smaller name's tokens are flagged as the same place — "The Red Bedroom" vs "The Blue Bedroom" ({red, bedroom} vs {blue, bedroom} -> 1/2 = 0.5) are distinct rooms reported as scenery costume change.
- Trigger: WorldPanel's honesty line (FilmWizard.tsx:173, 176-177) at THE PLAN approval.
- Impact: false drift accusation may push the owner to rename or delete a legitimately distinct set; advisory only.
- Fix: require the shared tokens to cover the LARGER name too (Jaccard-style `shared / union`), or raise the containment threshold to 1.0 for the partial-overlap band (keeping superset names like "Alley" contained in "Night Alley" flagged via full containment).

## Missing safeguards

- `validateWorld` passes any finite `version` through untouched (`line 204`) — negative, fractional, or hand-pasted 999 survive and the patch's `+1` keeps them; nothing enforces the "monotonically bumped" integer contract the field doc claims.
- Nothing blocks approve/run on a world whose version exceeds the storyboard's draft world — the entire stamp truthfulness rests on the owner re-drafting after every edit, which is UI-said but never code-checked.
- `castOf`/`setDrift` findings are display-only text in WorldPanel — no gate refuses or even warns at LOCK time, so the honesty lines can be scrolled past before money is spent.

context-pack: jcodemunch outline+importers (FilmWizard.tsx:10/125/1474/172, vite.film.ts:803-2804, autopilot.ts:778, store.ts:30/61, worldmodel.test.ts) + git log ac82399/a0077ba/7c3ad72; prior review 2e218153 diffed.
new-findings: 3
