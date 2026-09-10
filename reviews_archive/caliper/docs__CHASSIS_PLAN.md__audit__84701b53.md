# Colibri review — docs/CHASSIS_PLAN.md (audit)

- **Source:** `docs/CHASSIS_PLAN.md` @ commit `87ee2fb` (HEAD at review time)
- **sha256 (bytes reviewed):** `84701b53a7ad471d288b4c0aba07e3c035db3e67e68a8c2b4450015158c2aa60`
- **Model:** claude-fable-5 (in-session) · **Date:** 2026-08-18 · **Mode:** audit (doc/plan review)
- **Context pack:** as for the CHASSIS_SPEC unit (same session), plus: `tools/panel_cad.py`,
  `tools/check_slices.py` (full source), `tools/slice_frame.py` outline, all 13 `gen_*.mjs`
  MODEL constants, `package.json`.

## Verdict

The plan's core pivot — model the chassis in Blender to the spec, ortho at 2×, slice with the
existing verified tooling, corners native over tiled rails, nothing scaled in CSS — is sound,
correctly grounded in first-party drift measurements, and its repo claims all verified. Defects
are documentation-level: a conflated window metric, a missing acceptance gate, and unreconciled
item lists.

## Claim verification (G2 labels)

- ✅ `panel_cad.py` quote real (file header, lines 3–5); "written weeks ago" plausible per history.
- ✅ `check_slices.py` does exactly what is claimed: re-measures each border-image's art,
  fails on slice mismatch and on per-side width/slice ratio spread > 0.02; its header records both
  failure classes having shipped (the 54px-deep cut; the 1.97× one-side stretch).
- ✅ All 13 generators use `bytedance/seedream-5-pro` — the "we downgraded our resolution ceiling"
  admission is true; Seedream 5's 1K/2K limit matches recorded memory (replicate-image-model-facts).
- ✅ border-image corner geometry (corner region = intersection of adjacent border widths,
  not decoupleable) — standard CSS border-image behavior; the 8-piece pivot follows.
- ⚠ Could-not-verify offline (none load-bearing; the pivot rests on our own measurements):
  GenEval 2 test structure; FLUX.2 vendor quote; "true alpha — only Ideogram".
- ❌ FALSE (fixed): "in Electron" — package.json is Vite/React only; the app runs as
  `vite preview` from `dist/` in a Chrome window. The WebP-over-atlas conclusion still holds.

## Findings (all survived adversarial verification)

**[HIGH] CONFIRMED — Open decision #1 conflates window outer rect with viewport** — §4.1
- Plan says "currently 1933×1093 CSS"; companion spec's contract box is 1933×1062. Screencap
  audit log proves 3866×2186 device (=1093 CSS) is the *outer* rect; the spec's 3866×2124 is the
  viewport (Δ31px ≈ title bar — probable cause, not load-bearing). "Resize to 1920×1080 for
  native 4K" targets the outer box and would leave the art target at ~1920×1049 — still not 16:9.
- Fix (applied): decision restated in viewport terms (outer ≈ 1920×1111 → viewport 1920×1080) and
  sequenced BEFORE modelling.

**[HIGH] CONFIRMED — Step 2 lighting prescription overshoots** — §3 step 2
- Same defect as the spec's lighting section (see the SPEC unit). "Uniform white world and NO
  lamps" produces the satin read the doctrine rejects. Fix (applied): symmetric structured
  environment + extrusion-invariance rationale; step 8 promoted from "optional" to expected.

**[MEDIUM] CONFIRMED — No acceptance gate on remaking the only approved element** — §3 step 1
- The nav plates are "approved outright"; step 1 remodels them under a new lighting regime.
  Approval was of a rendered artifact, not a method (users-mockup-is-the-brief doctrine).
  Keeping the old rail is not viable (it perpetuates "parts not made together"), so the fix is a
  gate, not an exemption. Fix (applied): step 1a — render the nav rail first, side-by-side
  against `rail-nav.png`, approval before the rest is modelled.

**[MEDIUM] CONFIRMED — Broken-list and fix steps don't reconcile** — §1 vs §3
- Item 5 (`.inset` white boxes) had no corresponding fix step anywhere; checklist round-5 open
  items 13/14 (cavity baking) and 17/18 (per-piece global-diffuse program) are superseded or
  absorbed by the pivot but never dispositioned. The nav lit sheet was absent from the plan
  entirely (see SPEC unit finding). Fix (applied): "Dispositions the steps imply" section; lit
  sheet added to step 4.

**[LOW] CONFIRMED — "in Electron" false** — §2 "Confirmed correct"
- See claim verification. Fix (applied): reworded to the actual runtime.

---

# Synthesis (cross-file, both units)

1. The two companion docs disagreed on the reference height (1093 vs 1062) because each measured
   a different box and both called it "the window". The viewport is now pinned as the contract in
   both; the resize decision is stated in viewport terms and ordered before modelling.
2. The lighting requirement — the spec's self-declared "single hardest requirement" — was the one
   defect capable of wasting the whole build: both docs prescribed featureless-uniform light,
   which reproduces the exact material misread (chrome → white plastic) the plan exists to fix.
   Both now specify one symmetric structured environment, with the proof that structure costs the
   tiling rule nothing.
3. The one approved artifact (nav rail) and its live lit state were the least-specified parts of
   both docs despite being the highest-stakes: now gated (step 1a) and authored from the same
   scene (spec §2 + plan step 4).
4. Everything else in the plan verified against the repo: the method is right, the tooling
   claims are true, and the research errors it admits (Seedream-5 downgrade) are real. Verdict:
   proceed, as amended.
