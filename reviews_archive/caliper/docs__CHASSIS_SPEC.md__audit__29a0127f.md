# Colibri review — docs/CHASSIS_SPEC.md (audit)

- **Source:** `docs/CHASSIS_SPEC.md` @ commit `0c6c4cc` (HEAD `87ee2fb` at review time)
- **sha256 (bytes reviewed):** `29a0127f810115ce8efe4dc66cf1a1fa909bdb00099c129dad12d08649edc129`
- **Model:** claude-fable-5 (in-session) · **Date:** 2026-08-18 · **Mode:** audit (doc/plan review)
- **Context pack:** recorded Caliper doctrine (caliper-edc-restyle, caliper-chassis-build,
  never-scale-art-in-css, diffusion-cannot-author-geometry, replicate-image-model-facts memories);
  RESTYLE_CHECKLIST.md; screencap audit log (window rect evidence); repo verification via
  jCodemunch `local/Caliper` (tokens.css, src/assets inventory, package.json); badge.png pixels
  inspected.

## Verdict

The spec's geometry is internally consistent (all region sums verified; the 217/366px well
resolutions check out against the 88.10% deck) and it correctly encodes the round-1–5 rules
(tuck-under, no CSS scaling, corners larger than rails). Two sections needed correction before
modelling: the lighting section as written would reproduce the satin/plastic defect globally, and
the flex-safety rule had no per-region map.

## Findings (all survived adversarial verification)

**[HIGH] CONFIRMED — Lighting section contradicts the locked chrome doctrine** — "Lighting" §
- What: "Flat global diffuse… no hot speculars… every corner lit exactly as brightly as the
  centre," taken literally, gives specular metal nothing structured to reflect; chrome with no
  highlight structure reads as satin/white plastic — the recorded rejected look ("chrome IS the
  control surface… not muted satin").
- Trigger: model + render exactly to the section as written (uniform featureless world).
- Impact: the entire chassis acquires the defect the spec's own §"Broken" diagnosis attributes to
  the rails; a full model-render-integrate cycle wasted.
- Fix (applied): directionally *symmetric, structured* studio environment (overhead ring /
  vertical-gradient world, mirrored left/right; no cast shadows, no vignette). Tiling-safe by
  construction: an ortho render of a constant extrusion under a distant environment shades
  identically along its length (shading depends only on the normal, constant along a rail).

**[HIGH] CONFIRMED — Reference box mislabeled "window"** — header
- The 1933×1062 figure is the CSS *viewport* (3866×2124 device); screencap proves the window's
  outer rect is 1933×1093 (3866×2186). Companion plan used the outer number. At most one box can
  carry the percentage contract, and it is the viewport. Fix (applied): pinned as "Reference
  viewport", distinction stated.

**[MEDIUM] CONFIRMED — Nav lit state absent** — §2 nav-rail internals
- `nav-lit.png` is a live UI state on the most-used element; the spec authored five plates + a
  nameplate but no lit sheet. Unspecified, it would be generated separately and "parts not made
  together" recurs on the selection highlight. Fix (applied): lit sheet rendered from the same
  scene; also notes the mid-stack gradient defect symmetric lighting retires.

**[MEDIUM] CONFIRMED — Flex zones demanded but never mapped** — §"Constraints on the cut"
- "Rails between fixed features must be plain and uniform" with no per-region statement of which
  spans tile; the deck's "mechanism run" (0.16–0.60) sits exactly in the deck's flex span and a
  mechanism is lengthwise detail. Fix (applied): anchor/tile map table; mechanism left-anchored
  with fixed width, ending in plain floor before the queue pair.

**[LOW] CONFIRMED — Trademark flag not closed on paper** — §"Fields the image must NOT contain"
- Standing flag: `caliper-fused-v4.png` carries legible Mitutoyo trade dress. Verified: not in
  `src/assets` (comment reference in tokens.css only); shipped `badge.png` pixels are clean
  ("Caliper" wordmark, no marks). The modelled nameplate retires the flag; the spec never said so
  or constrained the new engraving. Fix (applied): "No borrowed trade dress" bullet.

## Refuted (deleted, recorded per protocol)

- Draft finding "regions 2–6 begin ~3px inside the ~30px chassis rail (1.40% < 1.55%)" — refuted:
  this is the deliberate round-4 tuck-under (content sits behind the repainted bezel), recorded in
  RESTYLE_CHECKLIST log items 5–7. Not a defect.

## Verified-correct claims (positives)

- Region table arithmetic: nav 1.40+9.10 = deck left 10.50; deck 2.54+11.02 = bay top 13.56;
  bays 10.50+23.38 = 33.88, 33.88+64.72 = 98.60 (mirrors left margin); strip 93.03+4.52 = 97.55 ≈
  rail bottom 97.53. Well widths 0.1276/0.2146 × 1703px deck = 217/366px as stated.
- "Same part in two proportions" for the bay frames = re-render, not CSS scaling — consistent with
  the never-scale-art rule.
- Cut constraints (corners larger than rails, 2× cut drawn 1:1, nothing scaled in CSS) encode the
  recorded hard rules faithfully.
