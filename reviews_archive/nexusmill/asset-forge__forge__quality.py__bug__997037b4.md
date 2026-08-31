# Bug review: `asset-forge/forge/quality.py`

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/quality.py` (creator edition, canonical)
- sha256: `997037b40bf751d63746ff118a046056a72b63db5973ddc81dde64f7e773b3d0`
- Twin parity: `asset-forge-user/forge/quality.py` byte-identical at the same sha (G23 verified
  this pass) — every verdict below applies to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- Context pack: `get_file_outline`; both importers located via jCodemunch after re-indexing a
  stale index (`bundle.py:24`, `library_gen.py:31` — `find_importers` reported 0 against the
  stale index, so the re-index was mandatory); call sites `bundle.py:191-200` and
  `run_job(..., quality_floor=True)` at `library_gen.py:615`; `forge/color_hints.json`
  (the hint pool this floor now adjudicates); `forge/imagegen/prompts.py:274-324, 442, 493`
  (how the pool reaches a prompt); `docs/remediation_manifest.json` rows for `quality.py`
  (2026-07-30 `quality1` refuted-hypothesis row, 2026-08-04 direction-blind-detail row) and
  for `color_hints.json`; commits 487781a (GREY-MUSH-1) and 19db681 (LIB-FLAGGED-1).
- **Round 2 — DELTA against `asset-forge__forge__quality.py__bug__3646fb9d.md`** (2026-08-04,
  claude-fable-5, sha `3646fb9d…`). That review is **on disk but absent from
  `.colibri_reviews/_manifest.json`**, so a Phase-0 cache/delta check driven by the manifest
  alone would have missed it and reported this as a first review. Found by listing the review
  directory directly. The manifest has drifted again — same failure class as the 2026-07-23
  `colibri-manifest-repair` remediation row; see the cross-file synthesis.

## Verdict

Not shippable as it stands. The `MIN_SATURATION` floor added by GREY-MUSH-1 (2026-08-10)
contradicts this product's own colour-hint pool: two of the 69 hints Asset Forge assigns to
library items *ask for* a colourless image, and this gate then rejects the result, spends a
second paid generation retrying it, and files the output under `flagged/` with a false
`quality_warning`. That is precisely the false-positive class this file's own docstring says
it exists to prevent. Compounding it, the saturation metric is unstable at low brightness, so
it fires *backwards*: an equally colourless image passes when dark and fails when bright.

## Bugs & vulnerabilities

**[HIGH] `MIN_SATURATION` rejects images the product deliberately asked to be colourless — doubling spend on ~2.9% of every library run** — `quality.py:50, 109-111`
- **What:** `check()` fails any image scoring `saturation < 0.10`. But `forge/color_hints.json`
  ships `"monochrome"` and `"near-monochrome with one accent"` in its `family` group, and
  `prompts.py:274-312` flattens **every** group into one 69-entry `COLOR_HINTS` pool. With no
  explicit user palette (the default for library generation), `prompts.py:442` sets
  `palettes = list(COLOR_HINTS)` and `prompts.py:493` assigns them round-robin
  (`palettes[i % len(palettes)]`). So on any library run large enough to wrap the pool, items
  are *instructed* to come out monochrome — and then judged by a floor that forbids it.
  A pure greyscale image scores exactly `0.000` against a `0.10` floor; it cannot pass.
- **Trigger:** Any library run whose assignment index lands on either colourless hint. The pool
  is shuffled per theme (`prompts.py:452`) and then cycled, so the rate is **2 of 69 hints =
  ~2.9% of items in expectation**, rising to certainty once a run's item count reaches the
  69-hint pool size and wraps it. Also reachable via an explicit user palette:
  `catalog.json:1285` lists `"monochrome"` in the user-selectable `palettes` pool, and
  `prompts.py:442` gives an explicit palette authority over everything.
  A third path: `prompts.py:654`'s `"Line-art seamless pattern"` style hard-codes
  `"monochrome on white"` into the prompt text.
- **Impact:** Three compounding harms per affected item. (1) **Money (G19):** the caller
  retries once at a deterministic alt seed (`bundle.py:196` `seed ^ 0x5F5F5F`; the matching
  block in `library_gen._attempt`) — the prompt is unchanged, so the retry produces another
  monochrome image and also fails. The customer is billed **twice** for one delivered image.
  (2) **Correctness:** the item is kept but stamped with a `quality_warning` that is false —
  the image is exactly what was ordered — and relocated into `flagged/` by LIB-FLAGGED-1,
  telling the customer their own requested style is defective output. (3) **Doctrine:** the
  module docstring (lines 30-34) states the gate "fires only on output that is degenerate by
  any standard" and produces "ZERO false positives". This is a systematic false positive.
- **Fix:** The floor must not adjudicate an outcome the prompt requested. Make the intent
  available to the gate and skip the saturation check when colour was deliberately suppressed:
  pass the assigned hint/palette (and the `colour_locked` flag) down to `check()` and gate
  `MIN_SATURATION` on it, exactly as `COLOUR-5` already suppresses colour axes for
  `colour_locked` catalog types. The cheaper, equally correct alternative is to remove the two
  colourless hints from the `family` pool so no path can request what the floor forbids —
  but that silently narrows customer-visible choice and leaves the `catalog.json` palette and
  the line-art style still contradicting the floor, so the gate-on-intent fix is the right one.
  Whichever is chosen, the two files must be changed together; they are one contract.
- **Verification: CONFIRMED.** Traced end to end, and one refutation attempted and defeated:
  `_load_color_hints()` only returns the full pool if the JSON has a top-level `groups` key
  (otherwise it falls back to the 9-entry `COLOR_TREATMENTS`, which contains no colourless
  entry and would refute this finding). Read directly: `color_hints.json:6` is `"groups": {`
  and `family` is a member group — the fallback does not apply and the colourless hints are
  live. Pool size counted programmatically: 69 hints, 2 colourless. `quality_floor` defaults
  to `True` at `library_gen.py:615`, so the gate is on by default.
  One honest limit on the *rate*, not the defect: how greyscale the model renders "monochrome"
  varies per model. That the model does render it as genuine greyscale is not speculation —
  `color_hints.json:21`'s own GREY-MUSH-1 note records tracing "a hex_tech image that came out
  pure monochrome silver/black". The contract contradiction is unconditional either way.
- **Decisive supporting evidence — the defect is an incomplete sweep inside one commit.**
  `git show 487781a` (the commit that added `MIN_SATURATION`) shows the same change auditing the
  hint pool for exactly this hazard and fixing it in three groups: `intensity`
  (`"high contrast colors"` → `"high contrast saturated colors"`, same for `"low contrast"`),
  `temperature` (`"neutral tones"` **removed outright**), and `register` (`"clinical colors"` →
  `"clinical cool-toned colors"`). Its stated criterion, quoted from its own note, is that a
  hint with "no hue anchor at all… is honestly satisfied by literal grayscale" and must be
  anchored or removed. The **`family` group was never swept** — and `"monochrome"` /
  `"near-monochrome with one accent"` do not merely *permit* greyscale, they *name* it. The
  commit's own rule, applied consistently, condemns the two hints it left in place, in the very
  change that added the floor which now rejects them. This is a one-commit internal
  inconsistency, not a long-standing latent mismatch.

**[MEDIUM] The saturation metric inverts with brightness — dark colourless images pass the grey-mush floor, bright ones fail** — `quality.py:92`
- **What:** `saturation` is computed as `((mx - mn) / (mx + 1e-6)).mean()` — HSV *S*, which is
  a ratio normalised by brightness and is numerically unstable as `mx → 0`. Equal absolute
  channel noise therefore yields wildly different scores depending only on how dark the pixel is.
- **Trigger:** Any near-neutral image whose pixels are dark. Measured on this exact expression:
  a dark near-grey pixel `(10,11,12)` scores **0.167 — passes** the `0.10` floor, while a
  bright near-grey `(200,201,202)`, no more colourful, scores **0.010 — fails**. A ~17×
  swing driven purely by brightness.
- **Impact:** The floor does the opposite of its purpose on the exact image class that
  motivated it. GREY-MUSH-1 was traced to an image that came out "pure monochrome
  silver/**black**" — dark. A dark, colourless, genuinely-degenerate image with any sensor/
  compression noise clears the floor, while a legitimately pale, low-chroma texture (bleached
  bone, chalk, weathered concrete, "high-key pale colour" — itself a shipped hint at
  `color_hints.json`) is rejected and burns a paid retry. This makes the floor both a miss
  generator and an independent false-positive source, separate from the HIGH above.
- **Fix:** Use brightness-independent chroma — `(mx - mn).mean()` — and recalibrate the
  threshold against the same corpus, or keep HSV *S* but guard the ratio with a value floor so
  near-black pixels contribute 0 rather than a large quotient. The file's own stated
  methodology applies: derive the threshold strictly below the lowest genuinely-coloured
  accepted sample, on a real corpus rather than the 9-image spot check its comment admits to.
- **Verification: CONFIRMED.** The inversion is arithmetic, not inference: computed directly
  from the source expression, numbers above. No upstream guard exists — `measure()` returns the
  raw value and `check():109` compares it straight to the constant.

**[LOW] The docstring's zero-false-positive guarantee no longer covers the gate it documents** — `quality.py:33-34`
- **What:** Lines 30-34 assert the floors are "set strictly BELOW the worst image Damien
  accepted" and produce "ZERO false positives" on the 48-image reference set. That validation
  predates `MIN_SATURATION`, which was added 2026-08-10 and — as its own comment at lines
  61-65 concedes — was calibrated against "a 9-image spot check, not a large corpus". The
  headline claim now describes 4 of the 5 active floors.
- **Trigger:** Read on entry by anyone extending or tuning this module.
- **Impact:** Not a runtime defect; a correctness-of-record one. This exact stale guarantee is
  the mechanism by which the HIGH above slipped in — a reviewer trusting the docstring would
  conclude a false positive is impossible by construction and never check the hint pool. G11:
  a claim that no longer matches the code is a defect in the record.
- **Fix:** Scope the guarantee to the four validated floors and mark `MIN_SATURATION` as
  provisional pending the re-derivation its own comment already schedules.
- **Verification: CONFIRMED** by direct comparison of the docstring against the constant block
  and the remediation-manifest dates (`quality1` 2026-07-30 validation vs GREY-MUSH-1
  2026-08-10 addition).

## Missing safeguards

- **Aspect ratio is destroyed before measurement.** `measure():75-76` does
  `im.resize((512, 512))` whenever `max(im.size) > 512` — an unconditional square, not a
  proportional downsample. For a non-square input the two `detail` axes are scaled by different
  factors, so the `max()` picks a mechanically inflated number. The bias is toward passing, so
  it weakens the gate rather than creating false rejections, and the empirical `MIN_DETAIL`
  re-derivation absorbed it — but the metric is not measuring what the comment says it measures.
  Use `Image.thumbnail`/proportional resize.
- **`detail` is resolution-dependent and only partly normalised.** Images with `max(size) <= 512`
  skip the resize entirely and are measured at native resolution, on a threshold derived from
  512-normalised images. Harmless while every generated asset is ≥1024, but it is an unguarded
  assumption, not an invariant.
- **No guard for degenerate array shapes.** A 1-pixel-tall image makes `np.diff(g, axis=0)`
  empty; `.mean()` of an empty array is `nan` with a RuntimeWarning, and `nan < MIN_DETAIL` is
  `False`, so the image silently passes every floor. Not reachable through the product's own
  generation paths (all outputs are ≥512 square), so it is listed here rather than as a finding.
- **`check()` has no failure contract for unreadable input.** A truncated or corrupt PNG makes
  `Image.open` raise out of `measure()`. In `bundle.py` that exception lands in the
  `except BaseException` that calls `stop.trip("error", ...)`, aborting an entire all-or-nothing
  bundle. Arguably correct for genuine IO failure, but it means a measurement-layer crash and a
  provider failure are indistinguishable to the abort path.

## Fixed since last review (delta vs r1 `3646fb9d`, 2026-08-04)

- **r1's only finding — `[MEDIUM]` `detail` measures vertical gradients only, falsely rejecting
  striped/planked textures — is FIXED.** Current source computes
  `max(mean|Δrows|, mean|Δcols|)` at lines 90-91, and `MIN_DETAIL` was re-derived for the new
  metric against 2,940 accepted images (lines 43-49). Confirmed present; `verified-stale`,
  **not** re-fixed. The matching 2026-08-04 remediation row is closed.
- **r1's Phase-3 refutation of the saturation metric is now STALE, and this round overturns it
  on new grounds — not a re-charge.** r1 recorded: *"`saturation` divides by `mx+1e-6` —
  guarded; black pixels give 0/ε=0, correct."* That is true and remains true for the case it
  examined: a **pure** black pixel (`mx == mn == 0`) does yield 0. Two things changed since.
  (1) The case r1 tested is not the failure case — a *near*-black pixel with any channel noise,
  `(10,11,12)`, yields **0.167**, not 0; the quotient is unstable for small non-zero `mx`,
  which r1 did not evaluate. (2) Decisively, **when r1 ran, `saturation` had no consequence** —
  `measure()` computed it but `check()` never read it (as lines 50-53 of the current file
  state outright). A harmless reporting quirk became a gate on paid output when GREY-MUSH-1
  added `MIN_SATURATION` on 2026-08-10, six days after r1. A refutation of an inert metric does
  not carry over to the same metric used as a money-spending floor.
- r1's remaining Phase-3 refutations (512-resize as a calibration constant; `measure` opening
  without `try` because the caller's ladder owns the error contract) are re-confirmed and not
  re-charged; both are recorded here only as *missing safeguards*, unchanged in severity.
- Prior remediation rows consulted and **not** re-opened: the 2026-07-30 `quality1` row
  (recorded as a REFUTED hypothesis — darkness/flatness does not predict human rejection; this
  review upholds that and does **not** propose re-tightening the tonal floors).
