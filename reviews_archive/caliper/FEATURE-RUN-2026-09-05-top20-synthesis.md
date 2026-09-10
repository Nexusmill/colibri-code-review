# Feature run synthesis — top 20 files, 2026-09-05

20 single-file feature-mode reviews (19 new + 1 delta vs the cached 2026-08-18 GameScreen
review). Scope selection: jcodemunch PageRank aggregated per file (data tier) + the skill's
core-first heuristic (API spine, app root, OS components, top surfaces), excluding tests,
tools/, spec/, docs/, and .playwright-mcp. Every add-on adversarially checked: hook points
cited at read lines, absence verified against FEATURES.md + targeted search (one candidate
killed: graph-backup retention already exists). Ranking method and sha table live in the
run's session record; next-in-line files at the foot.

## Cross-file findings, ranked

**1. The constraint vocabulary stops two fields short of the engine.**
`violations()` (constraints.ts:43-56) checks the frames detent, the CFG cap, and positivity
— nothing else. Width/height are the freest controls in the app: GenerateSurface.tsx:119-128
accepts any 64-4096 with no multiple enforcement between the deck and the engine; LTX/Qwen
VAEs quantize to multiples, so a 777-wide ask silently wastes a render. FRAMES_MAX=521 is
UI-local with its own comment saying it belongs in the schema (GenerateSurface.tsx:23), and
lora strength is hardcoded `strength_model: 1` (fill.ts:106). One generalized
constraint-vocabulary wave (dimension steps, step bounds, frames_max, lora strength) closes
the entire class. [schema.ts + constraints.ts + GenerateSurface + fill.ts reviews]

**2. Price provenance dies at the bill.**
The three-tier price-truth system (owner > page rate card > estimate) is computed per engine
in buildLadder, carried on LadderEntry.priceSource — and rendered NOWHERE: no component
reads priceSource (verified by search), and BillLine (autopilot.ts:95-100) cannot carry a
source at all. THE BILL is where a human approves spend, and it cannot say which numbers are
verified versus estimated. The owner's own doctrine ("wrong prices are unaffordable even in
testing") is half-built without the display half. [autopilot.ts + vite.film.ts reviews]

**3. Declared-but-unwired product surface — three instances.**
(a) References declare `scope: film|scene|shot` with character/location/style tags;
`filmReferenceImages` filters `scope === "film"` only and genKeyframe sends
`film.referenceImages[0]` — scoped attachments never ride an engine call. (b)
`carriesAnchor` was built "for tests and future gates" and is imported by nothing in
production. (c) The calibration battery's live loop runs `plan.prompts[0]` only (vite.film.ts
2114) while the owner's engine standard is TWO prompts (the people/faces wall + the action
axis) — an engine failing either axis fails the brief, and the battery tests one. Each
completion is S-M effort against an existing type surface. [film/store.ts + worldmodel.ts +
vite.film.ts reviews]

**4. The optimizer loop has no memory.**
The model-proposes/human-applies doctrine is complete and hardened (allowlist re-validation,
no-op refusal before write, serialized applies, live-server truth in every result) — but no
applied-proposals ledger exists, no undo, the proposal card shows only the target value (the
current value is one scope away in currentState()), and closing the console drops the
transcript and spend tally. The measurement loop's own audit trail is the missing layer.
[vite.agent.ts + ScreenStage.tsx reviews]

**5. The queue knows who, not what; elapsed, not when.**
getQueueEntries drops `entry[2]` (the queued prompt blob), so a bench render or restart
orphan can only be identified by killing it. Nothing projects time-to-done even though the
bench corpus exists for exactly that. Both are S/M adds on data already flowing.
[client.ts + QueueSurface.tsx + queueStore.ts reviews]

**6. Install trust and portability.**
Downloads rename `.part` → target on stream end with no size/hash verification against the
catalog (LLM_MODELS even carries `bytes` for display only) — a clean-looking truncation
lands a broken multi-GB model marked DONE; the song-upload handler already ffprobe-verifies
for precisely this reason. MODEL_ROOTS hardcodes E:/AI/Models paths in source against the
Era-51 COMFY_DIR portability precedent. [vite.caliper.ts review]

**7. The film world is immutable but unreviewable.**
The world model is built first, typed, validated strict, and constant for the run's life —
with no human gate between build and draft. A brain-mis-built constant (wrong hair, wrong
height) poisons every board; the cheapest checkpoint doctrine stop (before ANY spend) does
not exist. PATCHABLE already includes `world`; only the wizard affordance is missing.
[worldmodel.ts review]

**8. The local brain shelf is one-way.**
The install catalog can put multiple GGUF brains on disk; the sidecar hardcodes
LLM_BRAIN_FILE (one Qwen3-4B). Installed brains that can never run — on the 16 GB shared
card where a smaller local brain is a real VRAM lever. [vite.llm.ts review]

## Top add-ons by value/effort (across all 20 files)

| Add-on | Value · Effort | File |
|---|---|---|
| Constraint vocabulary: dimension steps, bounds, frames_max | High · M | constraints.ts |
| Bill price provenance (OWNER/PAGE/ESTIMATE badges) | High · S-M | autopilot.ts |
| World review/edit gate before drafting | High · M | worldmodel.ts |
| Scene/shot-scoped reference routing | High · M | film/store.ts |
| Full two-axis battery + persisted ENGINE_HEALTH | High · S-M | vite.film.ts |
| ENGINE_CARDS derived from the live ladder | Med-High · M | autopilot.ts |
| VRAM-fit pre-flight estimate at queue | Med-High · M | queueStore.ts |
| Local-brain shelf (pick the GGUF) | Med-High · M | vite.llm.ts |
| Stale-route detection vs live catalogs | Med-High · S-M | modelRoutes.ts |
| Optimizer ledger + undo + current-value diff | Med · S-M | vite.agent.ts |
| Prompt history recall + size presets | Med · S | GenerateSurface.tsx |
| Post-install size/hash verification | Med-High · S-M | vite.caliper.ts |
| Console transcript persistence (session) | Med · S | ScreenStage.tsx |
| Arcade PAUSE key | Med · S | GameScreen.tsx |

## GameScreen delta closure

Of the 2026-08-18 deferred list: sound, top-5 tables, multiball, and rival food-stealing are
ALL implemented; screen-shake stays deferred (fitted-glass reasoning unchanged). New
candidates: pause, attract-mode self-play, mute (PLAUSIBLE — arcadeSound.ts out of scope).

## Next-in-line files (not in this run's 20)

vite.power.ts, vite.kb.ts, OutputsSurface.tsx, BundlesSurface.tsx, GraphSurface.tsx,
FilmWizard.tsx, src/api/types.ts, src/bundles/files.ts, src/components/DeckControls.tsx,
vite.comfy.ts — the cut was made at the data/coverage line; these are the honorable
mentions by PageRank and product weight.
