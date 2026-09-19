<!-- source: src/film/analysis.ts | reviewer: glm-5.3-zai-in-session | sha256: 94e0bd112f0670c768c2b9a9d8f43800a9bff702dbae9b977b2f5889deb9f14a | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict
Shippable — the delta since the prior reviewed sha (47fe2512 -> 94e0bd11) is a single doc-comment word (line 190, "pacedGrid in autopilot.ts" -> "pacedGrid below", commit d31d7ee): no code path changed, so no new defect can exist in this delta, and the wave-7 gate fixes hold in the current bytes (vitest 69/69 green in a fresh run, plain-node import of the .ts module verified live on Node v26.7.0).

## Fixed since last review
- **Legacy per-section shotGrid retirement — holds (verified, not regressed):** `src/film/analysis.ts` carries no per-section grid; `snapToBeat` is the one snap home (lines 185-191) and `pacedGrid` the wired grid (line 248). Its consumers are on the wired path: `tools/analyze-song.mjs:55-56` calls `pacedGrid` + `phraseGrid`; `vite.film.ts:1892-1893` the same.
- **Snap breaking the carve's own bounds — fixed, still fixed:** the bounds-aware snap is present and unchanged — `hi = Math.min(t + clipSeconds, duration)` (line 264) and `beats.filter((b) => b >= t + floor && b <= hi)` (lines 265-267), with `snapToBeat` keeping the computed time when no candidate survives (empty candidate list -> `bestDist = Infinity > 0.35` -> returns `t`, lines 192/198). Pinned by `src/film/autopilot.test.ts` (beat 15.2 refused past the 15s ceiling; beat 1.7 refused under the 2s floor) — green in the fresh run.
- **[LOW|prior-noted] phraseGrid's tail phrase can run past the song's true end — still-open, by design:** line 219 extrapolates the tail as `start + beatsPerPhrase * beatSec` with no duration clamp. Unchanged and still harmless as consumed (boundaries feed advisory prompt text in `buildDraftPrompt`/`buildRedraftPrompt`).
- **Prior note: the bounds filter assumes ascending beats — still-open note:** line 266's filter and `snapToBeat`'s early break (line 196) rely on `beatGrid`'s ascending output (lines 87-114). Unchanged, consistent with the contract.

## Bugs & vulnerabilities
None. The only changed line is the comment at line 190, which is now factually accurate (pacedGrid is in this file, line 248). Areas re-audited clean: empty-candidate snap returns the computed time (lines 192/198); `pacedGrid`'s loop strictly advances (`raw` or a candidate is always `> t` under the `t < duration - 1e-9` guard, so no non-termination); the 20,000-slot guard throws loudly (line 274); `phraseGrid` handles a single beat and empty beats (lines 210/214); the plain-node ESM constraint holds — analysis.ts has zero imports of its own and `node -e "import(...)"` succeeded, so `tools/analyze-song.mjs`'s `.ts` import works under Node's type stripping.

## Missing safeguards
- `phraseGrid` does not validate `beatsPerPhrase >= 1` — `i += beatsPerPhrase` (line 216) hangs or walks negative on 0/negative, and negative indexes yield `undefined` starts under the non-null assertion. Both live callers hardcode 8 (`vite.film.ts:1893`, `:2367`, `analyze-song.mjs:56`), so untriggered today.
- The section clamp (lines 220-221) can leave a span up to one phrase long uncovered after a clamped end (next slot starts at the raw lattice beat past `sec.end`). Benign while phrases are advisory prompt material; a consumer needing exhaustive coverage would silently miss those spans.
- `snapToBeat`'s early exit `if (b > t + 0.5) break` (line 196) silently mis-snaps on unsorted input — the ascending contract is implicit; sorting or asserting inside would make it self-enforcing for future callers.

context-pack: repo local/Caliper, target read in full (279 lines); delta vs prior sha = 1 comment line (git show d31d7ee); consumers traced (autopilot.ts:14-20 re-export, vite.film.ts:11/1892-1893/2367, analyze-song.mjs:9/55-56); live evidence: node import OK (v26.7.0), vitest analysis+autopilot 69/69 passed.
new-findings: 0
