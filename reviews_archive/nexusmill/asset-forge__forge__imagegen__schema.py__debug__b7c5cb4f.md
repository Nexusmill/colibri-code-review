# Debug: "klein 4b showing megapixels, doesn't use that variable, uses resolution"

- Source: asset-forge/forge/imagegen/schema.py (+ asset-forge/app.py, asset-forge/templates/library.html, asset-forge/forge/imagegen/replicate_flux.py, asset-forge/forge/catalog.json)
- Model: claude-sonnet-5 (in-session)
- sha256 (schema.py): b7c5cb4f001b157b4f665ad78ae89cf63c1d3ae1a71d36143b82561b3c6af7e
- Date: 2026-08-09
- Mode: debug
- Context pack: MODELS dict (replicate_flux.py) confirmed 1:1 slug mapping, no collision;
  get_schema/capabilities/ui_props read end to end; live cached schema files for
  flux-2-klein-4b, flux-2-pro, flux-2-max read directly from
  ~/.asset-forge/model_schemas/; frontend renderer (library.html loadModelOpts/
  renderMopts/_sentence) read to check label derivation; twin-build parity checked
  (asset-forge vs asset-forge-user) for schema.py and library.html - byte-identical.
  Damien's report: "klein 4b is showing megapixels and it doesn't use that variable it
  does resolution."

## Hypothesis ledger

1. Wrong slug mapping (klein resolves to a different model's slug) - **checked**:
   `MODELS["flux-2-klein-4b"] = "black-forest-labs/flux-2-klein-4b"`, unambiguous,
   no collision with flux-2-pro/flux-2-max slugs. REFUTED.
2. Stale cache serving an old/wrong schema - **checked**: cache file
   `black-forest-labs__flux-2-klein-4b.json` last modified 2026-08-09 21:58 (hours old,
   well inside the 7-day TTL) and contains `output_megapixels` as a live-fetched,
   current property. REFUTED - not stale, and refreshing would not change the result.
3. Frontend hardcodes/collides labels across models - **checked**: `library.html`
   `loadModelOpts()` fetches `/api/model_schema/<model>` fresh on every model change,
   clears and rebuilds `#moptsgrid` from `caps.ui_props`, no persisted/leftover DOM
   from a prior selection. `_sentence(p.name)` derives the label directly from the
   schema property name (underscore→space, capitalize first letter) - no lookup table,
   no per-family special-casing. REFUTED.
4. Dev/compiled-user trees have drifted (Damien ran the exe, this review read source) -
   **checked**: `schema.py` and `library.html` are byte-identical between `asset-forge/`
   and `asset-forge-user/`. REFUTED.
5. **klein-4b's real Replicate schema genuinely differs from flux-2-pro/flux-2-max's** -
   **checked directly against the live-cached schema files**:
   - `black-forest-labs/flux-2-klein-4b` → property `output_megapixels`, enum
     `["0.25","0.5","1","2","4"]`, description "Resolution of the output image in
     megapixels". No `resolution` property exists in this model's schema at all.
   - `black-forest-labs/flux-2-pro` and `black-forest-labs/flux-2-max` → property
     `resolution`, enum `["match_input_image","0.5 MP","1 MP","2 MP","4 MP"]`.
   These are two different Black Forest Labs model families with two different real
   parameter names for the same underlying idea (image size in megapixels) - BFL did
   not standardize the field name across their own catalog. CONFIRMED as the actual
   state of the live API, corroborated by an existing code comment
   (`ui_props` docstring, written 2026-08-05) that already special-cases "klein's
   output_megapixels" wanting a string-typed enum value.

## Verdict

**No code defect found.** The dynamic per-model options panel (AF-SCHEMA-UI) is
correctly deriving and rendering each model's own live schema, and klein-4b and
flux-2-pro/flux-2-max genuinely expose differently-named parameters for image size on
Replicate's side. What Damien observed ("klein 4b showing megapixels") matches the
model's real, current, freshly-fetched API schema; "resolution" is flux-2-pro/max's
field name, not klein's. Likely explanation: a mix-up between adjacent FLUX-2 models in
the picker, not a schema-representation bug. Reported back to Damien with the two raw
schema excerpts side by side rather than "fixing" non-buggy code (G1/G35) - open to a
follow-up if he has a screenshot or repro showing something this review didn't capture.

## Fixed since last review

N/A - first review of this symptom; no `.colibri_reviews` entry existed for this file
under any mode prior to this session.
