# Feature run round 3 — synthesis (2026-09-05)

24 single-file feature-mode reviews over tier A (the pure film modules + the price
pipeline + the optimizer core) and tier B (the provider adapters, library/export
machinery, install tiers, KB retrieval core, and the custom node). All fresh (no
cache hits); every add-on adversarially checked with cited lines. Combined coverage
after three rounds: **64 files** — every file that carries product behavior except
the settled widget children and thin fetchers.

## Round-3 cross-file findings, ranked

**1. The calibration battery never tests what the owner actually judges engines on.**
BATTERY_PROMPTS are three landscape/object clips with NO people (the first says "no
people" outright) — while the owner's standing two-prompt standard (the people/faces
wall: two persistent characters trading a beat; and the action axis) is recorded
doctrine, and the corpus's two condemned classes (The Super Man's two-character
failure, p-video's face-blindness) are exactly the axes it doesn't probe. Combined
with R1's finding that the live loop runs prompts[0] only, the battery is one-prompt,
one-axis, no-faces. The fix is data + a loop: both standards into the plan, all
prompts executed, per-axis grades feeding a persisted ENGINE_HEALTH. [calibrate +
vite.film]

**2. The measurement loop doesn't record what the estimates need.**
The bench (vite.bench) loads the exact bundles and times them — but records no VRAM
footprint, though R1's VRAM-fit pre-flight add-on needs exactly that table, and the
cold/load timing it deliberately burns as warmup is itself useful knowledge. One
/caliper/vram read around the bench turns every future bench into a row of the
estimate's data. [vite.bench]

**3. Price-truth's third act: collected-but-unconsumed data.**
Two verified dead-ends this round: Replicate's `PriceInfo.rates` map ("for option-
priced estimation," says its own comment) is read only by its test, and the bill's
parseTiers re-scrapes the blob instead; and the OpenRouter sku normalization keeps
only the minimum per-second rate. Plus `refreshReplicatePrices` returns a stub
`stale: 0`, and price CHANGES between refreshes are invisible. The provenance theme
(R1/R2: source badges on bills) now has its supply-side: consume what's collected,
report what failed, and append what changed to the corpus. [replicateBrowser +
vite.replicate + openrouterVideo + openrouter]

**4. The plan judge lacks its physics axis.**
The critique gate names the contact-collision law at the USER prompt; the storyboard
adversary — the gate that runs on every draft AND redraft — never re-checks, so the
brain can draft a collision into shot 7 after the user's prompt passed. The
camera-token gate pattern extends mechanically to a verb-list check. [adversary]

**5. The song's energy arc is computed and then ignored.**
analysis.ts's most expensive output — per-section energy classes — reaches nothing:
shotGrid paces flat 5s everywhere. Energy-aware pacing (quiet holds, peak cuts fast)
is the grammar of music video, implementable as a per-section target table with zero
brain involvement. The UI display of the arc is a separate, commission-needed piece.
[analysis + autopilot's grid]

**6. Two dead/stale data points, cleaned for the record.**
`OPENROUTER_DEFAULT_MODEL` ("glm-5.2:free") has zero consumers — the live default
lives in BRAIN_OPTIONS + brain.json. The catalog's film.keyframe/film.segment roles
are superseded by the routes system but still read as resolving here. Both are drift
hazards of exactly the shape the price-truth doctrine warns about. [openrouter +
catalog]

**7. Reversibility asymmetry in the library.**
Run deletion recycles to the Windows Bin (owner doctrine); library deletion uses
`fs.unlink` — permanent — on the same class of user-confirmed destroy. The recycle
machinery exists; lifting it to a shared module is the whole fix. [vite.library]

**8. The custom node can't prove it's current.**
The canonical↔custom_nodes sha sync is hand-maintained doctrine with no check; a
self-identifying payload field (version + own hash) turns the belief into a
runtime-checkable fact. [caliper_vram.py]

## Top round-3 add-ons

| Add-on | Value · Effort | File |
|---|---|---|
| Owner's two-prompt standard into the battery (+ run all prompts) | High · S-M | calibrate.ts |
| Bench VRAM-footprint recording (feeds the R1 estimate) | High · S-M | vite.bench.ts |
| Physics-plausibility axis in the plan judge | Med · S | adversary.ts |
| Energy-aware shot pacing | Med-High · S-M | analysis.ts |
| Bill price provenance (the code home: line construction) | High · S-M | budget.ts |
| Consume the rates map (option-priced estimation) | Med · S-M | replicateBrowser.ts |
| Honest refresh reporting + price-change history | Med · S-M | vite.replicate.ts |
| Rate-card budget ranking | Med · S | replicateBrowser.ts |
| Plan preview before START THE RUN/FIXES | Med · S | produce.ts |
| Bench param surface beyond steps/cfg | Med · S | llm/tools.ts |
| Library delete → Recycle Bin | Med · S-M | vite.library.ts |
| Node self-identification (version+hash in payload) | Med-High · S | caliper_vram.py |
| Prediction cancel on timeout | Med · S | replicate.ts |
| Export manifest inside the zip | Med · S | vite.library.ts |
| Heading-weighted BM25 | Med · S | kb/bm25.ts |
| last_frame synthesis | Med · S | openrouterVideo.ts |
| Streamed brain answers (theme: 3 hooks) | High · M | openrouter+film+wizard |
| Live "more models" brain rows | Med · S-M | brainProviders.ts |
| Lora strength from the bundle (the code home) | Med · S-M | fill.ts |
| More proven flags + read_vram tool | Med · S | llm/tools.ts |

## Coverage

64 files across three rounds (20 + 20 + 24). Deliberately left: the settled widget
children, thin fetchers (api/keys, api/firstrun, api/library client, install/client),
stores tail (generateStore, routesStore, assetsStore), toUiGraph, storyboard-doc,
i2v, power/state, arcadeSound, and the remaining vite glue (tokens/keys/routes/
eachlabs/openrouter middleware wrappers). These are either settled, tiny, or their
behavior is fully covered by the reviews of their consumers.
