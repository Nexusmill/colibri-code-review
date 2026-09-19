# Colibri Review - bug (FULL re-audit) - asset-forge/forge/imagegen/schema.py

- **Source path:** `asset-forge/forge/imagegen/schema.py` (twin `asset-forge-user/forge/imagegen/schema.py` byte-identical, G23 - fixes apply to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 24
- **sha256 reviewed:** `d779d0008911440e990bc1a6c79e75c2d5b7d149825a7d5b5f5438b37c135277` (sha8 `d779d000`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 2026-08-15 GROK-SC debug/fix records predate the gate and are untrusted; their four claims re-verified below, not taken as baseline)
- **Context pack:** jCodemunch outline + importers (imagegen/__init__, replicate_flux - get_schema/capabilities/get_latest_version/RESERVED_PROPS, library_gen - capabilities, app.py `_caps` -> transparency_models / _bundle_output_route / model_schema route); remediation rows grok-sc-schema + "slug SSRF validation, no-redirect token safety, cache hygiene"; feature rows AF-SCHEMA, AF-SCHEMA-UI, AF-SCHEMA-TRUST, AF-BUNDLE-ALPHA, AF-REPRODUCIBLE; probe tests/harness/probes/grok_sc_schema.py (monkeypatches `_CACHE_DIR` by attribute - the fix keeps the name); config.py read alongside for the HOME contract. Every one of the 302 lines read.

## Verdict
Shippable after two LOW fixes. The four GROK-SC claims are all present at the bytes (injective cache key, version pinned only on a parsed id, seed degrade-open with knobs hidden, 60 s stale window on both the error and the no-token path); the slug guard, the no-redirect opener, the verbatim enums and the reserved-prop fence hold. The two defects are a per-user-path contract break with config.py and a crash on an odd enum in the layer whose promise is "never lies about a model".

## Bugs & vulnerabilities

**[LOW] The schema disk cache ignores config.HOME (ASSET_FORGE_HOME) - the one per-user path in Asset Forge that does** - `line 26`
- What: `_CACHE_DIR = Path(os.path.expanduser("~/.asset-forge/model_schemas"))`, while config.py resolves every other per-user file under `HOME = Path(os.environ.get("ASSET_FORGE_HOME") or ~/.asset-forge)` (the UNIT-9 empty-env fix lives there). Reproduced: with ASSET_FORGE_HOME=C:\tmp\afhome, `config.HOME` is the temp dir and `schema._CACHE_DIR` is still `C:\Users\User\.asset-forge\model_schemas`.
- Trigger: any relocated home (the env knob the harness's isolation, support bundles and the app probes use), and every isolated test run.
- Impact: a relocated or isolated run READS AND WRITES the real user's schema cache (the batteries that set ASSET_FORGE_HOME for isolation still touch it unless they monkeypatch `_CACHE_DIR`, as grok_sc_schema.py does); a user who moved their home keeps a second cache in the old place.
- Fix: `from .config import load_providers, HOME as _HOME`; `_CACHE_DIR = _HOME / "model_schemas"` (the default resolves to the same path as before). Battery `probe_af_schema_1.py` check A (fresh interpreter with the env set) RED -> GREEN.
- Verification: CONFIRMED (cross-file: config.py line 10 vs schema.py line 26).

**[LOW] capabilities() crashes on a non-string aspect_ratio enum value instead of skipping it** - `line 212`
- What: `[a for a in (ar.get("enum") or []) if _RATIO_RE.match(a)]` - `re.match` on an int/None raises TypeError. Enum values are passed VERBATIM from the fetched schema (and from the 7-day disk cache) by design (AF-SCHEMA-UI: string-typed numbers must not be coerced), so one odd entry reaches this line untouched.
- Trigger: a model whose aspect_ratio enum carries a non-string entry (a numeric or null member), fetched or already cached.
- Impact: the TypeError escapes get_schema's fallback (it is raised in capabilities, after the fetch) into app.py's `_caps` callers: `/api/bundle/estimate` and `/api/bundle/start` 500 via `_bundle_output_route` for a transparent bundle, `transparency_models` counts the model as unreachable, `/api/model_schema` reports has_schema False with the TypeError text - the layer whose contract is "never lies about a model" fails on one enum member. No spend (the crash is pre-create).
- Fix: `isinstance(a, str) and _RATIO_RE.match(a)`. Battery check B RED -> GREEN; the normal-schema control unchanged.
- Verification: CONFIRMED as a deterministic crash on that input; the input's occurrence on Replicate today is unverified (every catalog model's enum is string-typed), which is why it stays LOW.

## Missing safeguards (not fixed)
- `cp.write_text(...)` is not atomic: a crash mid-write leaves a truncated cache file; the next read fails through to a refetch (needs a token), so it self-heals but costs a fetch. tmp -> os.replace would close it.
- `_fetch_remote` reads the whole body with no size cap (trusted host, 30 s timeout, no redirects) - a Replicate incident serving a huge body would be held in memory.
- `cp.stat()` in the TTL test sits outside the try: a cache file removed between `exists()` and `stat()` raises FileNotFoundError out of get_schema (no code path in the app deletes cache files; a user cleaning the folder mid-run could).
- A 401 (bad key) is swallowed into the same stale/empty fallback as an outage, so the UI reads "unreachable" for a misconfigured key; the key is validated where it is saved, so the gap is narrow (G20-adjacent honesty, not a defect in this unit).

## Adversarial verification pass (refuted claims)
- "A 30x from Replicate resends the bearer token to the redirect target" - refuted: `_NoRedirect.redirect_request` returns None, urllib raises HTTPError, the fetch falls to the stale fallback; the token never leaves the first request.
- "A crafted slug traverses the URL or the cache directory" - refuted: `_SLUG_RE.fullmatch` + the '..' guard on every fetch; `quote(safe="")` is injective for the file name.
- "A past-TTL stale copy is pinned for the session" - refuted: `_MEM_STALE` carries a 60 s deadline on both the error and the no-token path (GROK-SC #4 present).
- "get_latest_version pins None after a timeout" - refuted: `_MEM_VERSION` is written only on a parsed id.
- "supports_seed is True on an unreachable schema - the layer lies" - refuted: documented degrade-open (GROK-SC #3, AF-REPRODUCIBLE); has_schema stays False and ui_props empty, so unknown knobs still hide.
- "A corrupt cache file is served or pinned" - refuted: read failures fall through to the fetch and never enter `_MEM`; an empty fetch result is never written to disk.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `5caeff5204b4b8c12fc1728ecf47e807b6c2285bc3639a87844b00e449131b1f`. Rows AF-SCHEMA-CACHE-HOME, AF-SCHEMA-ENUM-TYPE in `docs/remediation_manifest.json`, same commit.

