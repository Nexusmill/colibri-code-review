# Bug review: `asset-forge/forge/bundle.py` — full-file redo (r2)

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/bundle.py` (creator edition, canonical)
- sha256: `d6ab2547ad06facd6c5586ee67885312cb2f867054f82600e26b1ce0fdf2a4f1`
- Twin parity: `asset-forge-user/forge/bundle.py` byte-identical at the same sha (G23 verified
  this pass) — verdicts apply to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- **Forced full-file redo at an already-reviewed sha.** `_manifest.json` holds this exact sha
  from 2026-08-10, but that review (`…__bug__d6ab2547.md`) is explicitly scoped
  *"(LIB-FLAGGED-1 additions)"* — a same-session self-review of the new quality-floor block
  only, not a full-file verdict. Same situation as `app.py`, which was redone for the same
  reason on 2026-08-11. Prior rounds: `df4557bd` (2026-07-24, upfront-validation) and
  `ebe90169` (2026-08-10, pre-fix LIB-FLAGGED-1).
- Context pack: `get_file_outline`; the `extra=` chain traced end to end
  (`app.py:1103` `_clean_schema_extra` + `RESERVED_PROPS` at `schema.py:220` →
  `bundle.py:51/88/175` → `replicate_flux.build_inputs:213-217`); `forge/quality.py` (reviewed
  this pass, Unit 1) and its `check()` contract; `_cc.map_bounded`/`Stop` semantics; callers
  `app.py:_run_bundle` (wrapped) and `gen_bundle.py` (CLI, unwrapped);
  `docs/remediation_manifest.json` rows for this file — `2b4d85b`, `glm20-3` (provider-result
  type guard), AF-1 ref-uri (`af1-ref-uri-verdict`), `af-bundle-upfront-validation`,
  `unit9-2hc-tail` (verified-stale SSRF/traversal), `forgehunt1` (runtime-verified concurrency).

## Verdict

Shippable, with two defects on paths added since the last full review. The concurrency, abort
and temp-file handling are solid and every prior fix is intact. The quality-floor retry added on
2026-08-10 records a seed it did not use and leaves `quality_floor` out of the recipe, so
reproduction depends on current code and constants rather than on the recipe; and recipe-sourced
`model_extra` skips the sanitizer that guards every other route to the same parameter.

## Bugs & vulnerabilities

**[MEDIUM] A quality-floor retry generates at a different seed than every record claims, and `quality_floor` is absent from the recipe — reproduction depends on code state, not the recipe** — `bundle.py:196` vs `:205, :242-243, :299`
- **What:** The floor's retry calls `_generate_once(seed ^ 0x5F5F5F)` (line 196), which is the
  seed actually sent to Replicate and the seed that produced the delivered image. Every
  downstream record, however, uses the **unchanged local `seed`**:
  - line 205 — `payload = build_payload(..., extra={... "seed": seed ...})`, which is signed
    into the token and `embed_png`'d into the delivered PNG;
  - line 242 — the item dict's `"seed": seed`, which lands in `manifest["items"]` and is then
    HMAC- or ECDSA-signed at lines 302-312;
  - line 299 — `recipe_out["items"] = [{"prompt": …, "seed": it["seed"]}]`, the regeneration
    recipe.
  The provider's own return value carries the truth (`ReplicateProvider.generate` returns
  `{"seed": <the seed it was given>, …}`), so the correct value is in `gen` and simply not read.
- **Trigger:** Any item whose first generation fails `_quality.check` and whose retry is then
  used — i.e. exactly the code path LIB-FLAGGED-1 was built for. It fires on both outcomes: if
  the retry passes, a clean item carries a false seed; if it also fails, the item goes to
  `flagged/` *and* carries a false seed.
- **Impact — stated after a refutation pass that removed the stronger claim I first drafted.**
  The alt seed is `seed ^ 0x5F5F5F`, i.e. **deterministically derivable** from the recorded
  value, and a regeneration that re-walks the same path (generate at `seed` → fail the floor →
  retry at `seed ^ 0x5F5F5F`) lands on the same image. So reproduction is *not* categorically
  broken, and the recorded seed is not unrecoverable. What remains is still real:
  1. **Reproduction is coupled to code state rather than to the recipe.** `quality_floor` is a
     `build_bundle` parameter that is used on the recipe path — and it is **not captured in
     `recipe_out`** (verified: the dict's keys are theme, style, model, mode, randomize,
     aspect_ratio, base_seed, seamless, prompt_strength, make_previews, wm_text, the four
     `ref_*`, model_extra, items). A regen with the floor off reproduces the **rejected first**
     image instead of the delivered one. Worse, the path depends on the floor's *constants*:
     `MIN_SATURATION` was added on 2026-08-10, so a recipe written before that date can now take
     a different branch and yield a different bundle. This is exactly the failure
     `recipe_out`'s own comment (296-298) says it exists to prevent.
  2. **The signed manifest and the embedded token state a seed that was never sent to the
     provider.** The signature is valid over content that is inaccurate, so verification passes
     on a false particular (G11). Derivability makes it recoverable, not correct.
  3. For the **default model it is moot in the worst way**: `nano-banana-2` (the catalog default)
     is one of the models with no `seed` parameter at all — `build_inputs` drops it — so neither
     seed reproduces anything, and the recorded value is decorative. That is a pre-existing,
     already-recorded condition (`forgehunt1` MODEL-SEED row), noted here only because it caps
     the real-world impact of this finding.
  Frequency equals the quality-floor rejection rate — which Unit 1 shows is inflated by ~2.9% of
  items rejected for legitimately-requested monochrome, so the two defects compound.
- **Refuted and dropped:** `render_class` and `palette` are also absent from `recipe_out`, which
  looks like the same class of omission. It is not — both feed `expand_theme` only, and the
  recipe path skips expansion entirely (`items_spec = recipe["items"]`, line 96), carrying the
  final prompts verbatim. Correct as designed; no finding.
- **Fix:** Two small changes, the second mattering more than the first. (a) Record the seed
  actually used — `_generate_once` already returns it, so thread out
  `used_seed = gen.get("seed", seed)` and substitute at lines 205, 242 and 299 (keep the
  original for `base_name` if stable filenames matter). (b) **Add `quality_floor` to
  `recipe_out`**, so a regeneration replays the branch the original took instead of inheriting
  today's default and today's thresholds. `library_gen._attempt` already models (a) better —
  its retry writes to a distinct filename encoding the alt seed (`library_gen.py:701`) so the
  evidence survives on disk; bundle.py overwrites the same `raw` and keeps no trace.
- **Verification: CONFIRMED.** Traced by reading the closure: `_generate_once(gen_seed)` binds
  its argument locally and never rebinds the enclosing `seed`, so `seed` is unchanged at lines
  205/242 after the line-196 call. Refutation attempted and failed: there is no later correction
  of the seed anywhere between line 196 and the manifest write at 314, and `gen["seed"]` — the
  one place holding the true value — is read for nothing (only `gen.get("version")` and
  `gen.get("prediction_id")` are used, lines 245-246). Neither the 2026-08-10 LIB-FLAGGED-1
  review nor its pre-fix round mentions seed or reproducibility (grepped both) — this is new.

**[MEDIUM] `model_extra` restored from a recipe skips the sanitizer that guards every other route to it** — `bundle.py:88`
- **What:** Line 88 does `model_extra = recipe.get("model_extra", model_extra)` with no
  filtering. Everywhere else this parameter is scrubbed at the HTTP boundary by
  `app.py:_clean_schema_extra`, which drops `RESERVED_PROPS` — `prompt, seed, aspect_ratio,
  output_format, num_outputs, prompt_strength` plus the reference params (`schema.py:220`) —
  precisely so "the panel must not be able to override the curated money/reproducibility paths".
  `build_inputs` applies `extra` **last** (`replicate_flux.py:213-217`), so an `extra` key wins
  over the `num_outputs = 1` the builder sets at line 204.
- **Trigger:** `regen_from_recipe` (line 320) on a hand-edited `recipe.json` containing e.g.
  `"model_extra": {"num_outputs": 8}`.
- **Impact:** Eight images generated and billed per item where the cost estimate and the price
  shown on the control both assume one, and only `output[0]` is ever downloaded (G19 — the
  price on the control stops being true). A `prompt` or `seed` key in the same dict would
  silently decouple the delivered image from the manifest that describes it, compounding the
  HIGH above. The exposure is **self-inflicted spend on the user's own Replicate key, not a
  third-party attack** — but that is exactly the threat model this function already accepts:
  the very next lines (89-95) exist because "a hand-edited recipe could still point Replicate's
  fetcher at an arbitrary URL", and guard `ref_image_uri` accordingly. `model_extra` was added
  later and did not inherit the treatment.
- **Fix:** Apply the same filter to the recipe-sourced value — cheapest durable version is to
  drop `RESERVED_PROPS` keys inside `build_inputs` itself, so the invariant holds for every
  caller including `gen_bundle.py` and `tools/curated_run.py`, which construct providers
  directly and never pass through `app.py`.
- **Verification: CONFIRMED.** `RESERVED_PROPS` membership read directly at `schema.py:220`;
  `_clean_schema_extra` confirmed to be applied only at `app.py:1103` and `:1286` (both HTTP
  entry points), never on the recipe path; `build_inputs`' last-write-wins ordering confirmed by
  reading lines 194-218 of `replicate_flux.py`.

## Missing safeguards

- **`INCOMPLETE.txt` always reports `0` items produced.** Lines 265-268 read `len(items)`, but
  `items` is only assigned at line 261 — *after* the error check at 258-260 that raises. So any
  abort originating in `map_bounded` writes "aborted after 0/N items" regardless of how many
  actually succeeded on disk. Diagnostic only, but it understates recoverable work in the file
  whose whole job is to describe a partial bundle. Compute the count from `_results` instead.
- **The upfront validation block (57-65) does not cover every recipe field it introduces.**
  It validates `buyer`, `recipe` shape and `base_seed`, but `prompt_strength` (used as
  `float(prompt_strength)` at line 174) and `aspect_ratio` come from the recipe unchecked. A
  non-numeric `prompt_strength` raises inside `_build_one`, which is caught and marked properly
  (so no orphaned directory — the `af-bundle-upfront-validation` fix holds), but it aborts the
  whole all-or-nothing bundle on input that the same block was written to reject early.
- **`count` is not clamped here.** `app.py:1103` clamps to 64; `gen_bundle.py` (creator CLI) has
  no wrapper. Consistent with the existing division of responsibility, noted for completeness.

## Fixed since last review (delta vs `ebe90169` / `d6ab2547`, 2026-08-10; `df4557bd`, 2026-07-24)

- **`NameError: name 'os' is not defined` in the flagged-relocation block — FIXED and correct.**
  Current source uses `pathlib` throughout (`final.stem` / `final.suffix` at line 227); there is
  no `os.` reference anywhere in the file. `verified-stale`, not re-fixed.
- **Silent skip-on-collision in `flagged/` — FIXED.** The numeric-suffix loop is present at
  lines 225-228 and correctly reassigns `final = _fdst`, so the manifest path follows the moved
  file. Traced; correct.
- **Upfront shape validation (`df4557bd`) — intact** at lines 57-65, still ahead of
  `out.mkdir` at line 66.
- **AF-1 recipe `ref_image_uri` restriction — intact** at lines 93-95 (`data:` only).
  `verified-stale`.
- **Provider-result type guard (`glm20-3`) — intact** at lines 176-177.
- **All-or-nothing abort + `stop.trip` ordering (`forgehunt1`, runtime-verified) — intact** at
  lines 250-254 and 256-269; the quality floor correctly does **not** trip the stop, matching
  its documented rule at lines 186-188.
