# colibri bug review - src/surfaces/GenerateSurface.tsx (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 1334981e - 2026-08-25
mode: bug (delta on f355f062, 2026-08-19) - context: App-level consumer; CloudPane seat contract (generateStore mode/model); bundlesStore param contracts; frames detent wiring re-traced after the constraints.ts message interpolation change

## Verdict

Shippable - clean again, second pass in a row.

## New findings

None confirmed. The frames row already interpolates the bundle's own detent (`snaps to {bundle.constraints.frames ?? "8n+1"}`), consistent with this session's constraints.ts truthfulness fix; the FRAMES_MAX ceiling is shared by both controls; the fixed-row dim/inert geometry holds; the snap-chip timer resets per new snap.

## Missing safeguards

- Whole-store subscription (`useBundlesStore()` without a selector) re-renders the surface on every store write - a perf note, not a defect, and consistent with the surface's read of six fields.
