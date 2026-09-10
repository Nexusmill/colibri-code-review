# Colibri review — src/film/autopilot.ts (feature)

- **Source:** `src/film/autopilot.ts` · **sha256:** 15ed117c
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** The pure core of the film product — imported wholesale by vite.film.ts; 11 importers of buildDraftPrompt alone; owner rulings 39-43 + the engine-doctrine memory (owner picks: p-video draft + minimax/h3 finish); price-truth doctrine (rate card leads); last touch c9bb3bb (2026-09-05).

## What this module does

The autopilot's brain-side contract in 777 pure lines: the `AutopilotRecord` (the durable run: idea/critique/world/storyboard/adversary/bill/run gates), `sanitizeDefaults`, `validateStoryboard` (words from the brain, TIMINGS FROM THE GRID, deterministic healing), the ceil-carved `shotGrid`, the FILM_MANIFESTO digest riding every call, the critique/world/draft/redraft prompt builders with strict parsers, the two-model ENGINE_CARDS/tiers catalog + `maxClipSeconds`, the interrogative ENGINE_QUESTIONS, `applyRecordPatch` (PATCHABLE + shape guard, forward-only steps), and the learned ladder: seed families by version, win-rates from rated runs, denylist, `deriveMusicCaps` from published schemas.

## Suggested add-ons

**Price provenance on bill lines** — Value High · Effort S-M
- What: carry `priceSource: "owner" | "page" | "estimate"` from the ladder's `LadderEntry` (autopilot.ts:35) through `computeBill` onto `BillLine` (autopilot.ts:95-100 — currently `{leg, count, unit, usd}`, no source), and render the badge at THE BILL.
- Why (verified): the price-truth doctrine ("wrong prices are unaffordable even in testing") built the three-tier source system — and it dead-ends here: `priceSource` exists on every ladder entry, is plumbed through resolveLadder's return, and NO component ever reads it (search: priceSource appears only in autopilot/calibrate/vite.film). An estimate-priced bill line is indistinguishable from an owner-verified one at the moment of approval. The band/worst-case already widens on nulls; provenance is the missing half of honesty.
- How: `BillPrices` entries gain `source`, `BillLine` gains `source`, THE BILL renders OWNER/PAGE/ESTIMATE beside each number. Pure-file change starts here; budget.ts + wizard follow.

**Derive ENGINE_CARDS from the live ladder** — Value Med-High · Effort M
- What: the two-model doctrine's picker catalog (ENGINE_CARDS, lines 479-489: exactly p-video/h3/sora-2-pro) is a closed hardcoded trio; a new engine that enters the live ladder (say a new Replicate i2v leader) can be routed by the ladder but can never be PICKED as a draft/finish pair or cap a clip length without a source edit.
- Why: `maxClipSeconds` reads ENGINE_CARDS only — the doctrine's ceiling math is blind to every engine not in the trio.
- How: build EngineCard rows from live ladder entries (price/maxDuration from the schema where published), keep the owner's strengths/weaknesses prose as an override table keyed by ref. Owner ruling needed for which fields stay curated.

**Win-rate sample-size honesty** — Value Med · Effort S
- What: `winRatesFromRuns` (lines 628-643) averages stars with no sample count — a single 5★ run outranks a ten-run 4.6★ engine in the `best` ordering.
- Why: the ladder LEARNS from ratings; its first rating of any engine is maximally confident. A minimum-n gate (or shrinking toward the price ordering until n≥3) keeps "best-rated" from meaning "luckiest once."
- How: return `{avg, n}` from winRatesFromRuns; `winOf` in resolveLadder (line 744) applies the threshold. Tests exist for the ladder shape.

## Nice-to-haves

- `fitDialogue`'s 2.6 wps is a constant; a per-voice wps (speech engines publish pacing) would make `script-*` splits tighter. Low.
- `runRecordMarkdown` truncates the prompt to 200 chars — the corpus row could carry the scenario+engines verbatim already does; fine.
