# colibri-review — asset-forge/templates/library.html (bug, round 1 of the 2026-08-04 hunt)

- **Source:** `asset-forge/templates/library.html` (byte-identical twin: `asset-forge-user/templates/library.html`, G23)
- **Model:** claude-fable-5 (in-session)
- **sha256 (reviewed bytes):** `384485ed3e3aa524c3a0eb92eb1a339cf6b3caa9b6d614b861337d584c18dd40`
- **Date:** 2026-08-04 · **Mode:** bug (delta: UI-1 pricebar work + DOCTRINE-4 estimate line + MODEL-SWEEP null rows)
- **Context pack:** `/api/library_gen/catalog` = `catalog_summary()` which passes `cat["models"]`
  through RAW; catalog.json has held **31 null-priced model rows** since model-sweep
  (2026-08-02). Prior template review bcd1664b (index.html) predates this page's existence.

## Verdict
The MODEL-SWEEP null rows broke this page's entire boot path — a HIGH functional break of
"Generate My Library" that shipped in the 2026.08.01 build era. Fixed in-session with an
executed proof.

## Bugs & vulnerabilities

**[HIGH] boot() crashes on null catalog rows — the whole Generate-My-Library page dead** - `line 145` (pre-fix)
- **What:** the model-select loop read `MODELS[m].price_per_image` for every key. Since
  model-sweep, 31 of 51 catalog model rows are `null` (wired-but-unpriced discipline —
  intentional data). `null.price_per_image` throws a TypeError; `boot()` has **no catch**, so
  everything after the throw never runs: packs grid never renders, pack/count listeners never
  attach, `estimate()` never fires, the Generate button stays enabled-but-context-free, and
  `modelNote()` (same unguarded read) would throw again on any unpriced selection.
- **Trigger:** proven with the exact code shape and a 2-row model dict
  (`junk/hunt_verify_f5.js` — "THROWS: TypeError: Cannot read properties of null").
  The pricebar loop 4 lines earlier already guards `v&&v.price_per_image!=null` — the model
  select was simply missed in the same fix wave (AF-STUDIO-CONTROLS asserts on the pricebar,
  not the model select, which is why the harness stayed green).
- **Impact:** the library generator page is unusable in any build carrying the swept catalog —
  a paid-product feature fully dead, and silently (console-only error).
- **Fix (applied):** filter the model select to priced rows (same guard as the pricebar), and
  `modelNote()` hardened to `(MODELS[m]||{}).license||''`. Unpriced models stay out of the
  picker by design — `estimate()` refuses them server-side anyway (400), so listing them
  would only offer dead choices.

## Phase-3 refutations (not reported)
- *`ms.value=CAT.defaults.model` could select a filtered-out model* — the catalog default is
  `nano-banana-2`, priced ($0.07); an out-of-list assignment leaves selectedIndex 0, a valid
  priced option — degraded gracefully, not broken.
- *poll loop `spent_est` toFixed on undefined* — guarded with `(j.spent_est||0)`.
- *DOCTRINE-4 estimate line* — correctly shows `e.cost` with no upgrade line; `cost_with_margin`
  funding warning intact (G19 substance preserved; registry anchor updated in the same commit
  since `id="pupgrade"` was removed by DOCTRINE-4 — recorded as registry drift, not a code bug).

## Missing safeguards
- No harness anchor covered the model-select loop (only the pricebar). AF-STUDIO-CONTROLS'
  anchor list now points at `cost_with_margin` on this page; a future tester could assert the
  select is non-empty against a null-row catalog fixture.
