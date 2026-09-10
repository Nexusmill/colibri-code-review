# Colibri spec review — GenerateSurface.tsx

- source: E:\AI\Caliper\src\surfaces\GenerateSurface.tsx (195 lines)
- registry: E:\AI\Caliper\spec\generate.json (7 controls)
- reviewer: ZCode fresh-context subagent
- sha256: 1334981edddcfc8e98aed4d07ec9c008a5965eb37519c9dc4763c7b3e300a35b (sha8 1334981e)
- date: 2026-08-31
- mode: spec
- context: The surface renders only the two glass panes (param pane + render
  pane seating ScreenStage); deck controls were extracted to
  src/components/DeckControls.tsx. The param pane seats CloudPane when the
  generate store holds a chosen cloud model (mode==="cloud" && cloudModel),
  else the local instrumented controls. Evidence gathered via jcodemunch
  (repo local/Caliper): queueStore.ts guard/error paths, DeckControls.tsx
  render button + status well, ScreenStage.tsx artifact markup, repo-wide
  lastQueueError consumers.

## Verdict

B — one confirmed divergence, in a quiet clause (error state suppressed in
cloud mode). All clauses owned by this file's own code are otherwise
satisfied (cloud seat location, error/snap chip in local mode, running chip,
artifact seating); everything else is owned by named components and listed
below.

## Divergences

### 1. GEN-RENDER-LIFECYCLE / error_paths — the queue-failure state is not rendered while the pane seats a cloud model — CONFIRMED

- Expectation (quoted): "every button press produces a visible result: a
  failing render reports the server's failure as state, never a silent hang."
- Trigger: (1) CLOUD source with a chosen model — `cloudSeat` non-null
  (GenerateSurface.tsx:36-37); (2) the deck's "Queue render" key pressed —
  it stays live in cloud mode and still drives the LOCAL bundle
  (DeckControls.tsx `seatsCloud` note, "queue = local", ~line 104-118);
  (3) the queue attempt fails on a path that sets `lastQueueError` without
  creating a job — queueStore.ts:106-110 "The server is unreachable."
  (buildWorkflow throw, queueStore.ts:96-100, is a second path if it can
  out-run DeckControls' `violations` pre-check).
- Behavior: GenerateSurface.tsx:163-165 renders the `(snap || queueError)`
  chip INSIDE the local branch only (it sits in `pane-param-scroll`, lines
  68-166, the `) : (` arm of the cloudSeat ternary at 63-67). In cloud mode
  the param pane renders CloudPane alone. Repo-wide search: `lastQueueError`
  has exactly one consumer — this file — and no job object is created on
  these paths, so the Queue surface gets no row and the DeckControls status
  well falls through to "idle" (activeJob null, lastTerminal null). The
  press produces no visible result anywhere.
- Fix: hoist the `(snap || queueError)` chip out of the cloudSeat ternary
  (render it in `pane-param` after the CloudPane branch as well), since the
  queue key remains armed while the pane seats a cloud model.
- CONFIRMED — full trigger traced through code: subscription is
  unconditional (line 28) but the display is branch-gated (63-68 vs 163-165);
  sole-consumer claim backed by repo-wide search (16 matches; only
  GenerateSurface.tsx renders it, remainder are setters/tests).

Refuted candidates (deleted after adversarial trace): guard-rejection
message hidden in cloud mode (unreachable — the deck button is
`disabled` mid-render when singleGuard, so no press occurs); missing
done+seed chip in this file (DeckControls status well renders
"done · seed {seed}"); artifact not appearing as img/video (ScreenStage,
seated here at line 177, renders `<img>`/`<video>` at its lines 848/886).

## UNJUDGEABLE HERE

- GEN-SOURCE-SELECT (expected + error_paths): the LOCAL|CLOUD keys, the
  type→service→model cascade, catalog rows with prices, catalog
  loading/error/empty states — owned by src/components/DeckControls.tsx
  (SourceSelect, DeckDropdown, BundlePicker). Reload persistence is owned by
  src/stores/generateStore.ts (zustand `persist` confirmed present there).
- GEN-CLOUD-SCHEMA-SEAT (mapping, cost, side_effects): universal input
  mapping, conditional pricing blob, cost-on-the-button RUN, SET AS DEFAULT —
  owned by src/components/CloudPane.tsx; "queue = local" line owned by
  src/components/DeckControls.tsx. This file's own part — seating CloudPane
  in the same center-left `pane-param` the local controls occupy, remounting
  per service:slug — is satisfied (lines 63-68).
- GEN-RENDER-GUARD (expected + disabled_state): the deck key's
  `disabled={... (!!activeJob && singleGuard)}` and the queueStore
  busy/queueInFlight guard — owned by src/components/DeckControls.tsx and
  src/stores/queueStore.ts. This file only displays the "· running" chip.
- GEN-RENDER-LIFECYCLE (expected, partially): "done with its seed" status
  chip owned by src/components/DeckControls.tsx; img/video artifact
  rendering owned by src/components/ScreenStage.tsx (seating here is
  correct). The error_paths half IS judged above because its only rendering
  site lives in this file.
- GEN-ONE-PRICE-PIPELINE: shared catalog/price mapping — owned by
  src/components/ModelPicker.tsx, src/components/DeckControls.tsx, and the
  catalog source under src/api/ (modelRoutes).
- GEN-PICKER-CLOSE-GRAMMAR: close grammar + body portal — owned by
  src/components/ModelPicker.tsx.
- GEN-QUEUE-SURFACE-TRUTH: server-truthful queue list and clear — owned by
  src/surfaces/QueueSurface.tsx (+ src/api/).
