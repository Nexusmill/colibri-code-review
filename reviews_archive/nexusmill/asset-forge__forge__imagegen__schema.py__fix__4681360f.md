# Colibri fix-pass record - asset-forge/forge/imagegen/schema.py
- source: asset-forge/forge/imagegen/schema.py
- model: claude-fable-5 (in-session)
- sha256: 4681360fd3dd35aaaa12157e072f0fd275c75dfe70ba7a7243524b6ad8670679
- date: 2026-08-15
- mode: fix (GROK-SC remediation)
- context pack: jcodemunch outline + find_importers/references (get_schema/get_latest_version/capabilities
  consumed by imagegen/__init__, replicate_flux, library_gen in BOTH twins); deferred_manifest GROK-SC;
  prior review asset-forge__forge__imagegen__schema.py__debug__b7c5cb4f.md at the dispatch sha.

## Verdict
All four docketed findings re-verified CONFIRMED against b7c5cb4f (unchanged since dispatch) and fixed.
See docs/remediation_manifest.json entry `grok-sc-schema` for the full finding/fix/verification text.
Probe: tests/harness/probes/grok_sc_schema.py 10/10. Twin synced byte-identical.

## Fixed since last review
- GROK-SC #1 cache-path collision -> urllib.parse.quote(slug, safe='') (injective)
- GROK-SC #2 _MEM_VERSION None-poisoning -> assign only on a parsed id
- GROK-SC #3 supports_seed fail-closed on empty props -> degrade-open, knobs still hidden
- GROK-SC #4 stale past-TTL fallback pinned in _MEM -> _MEM_STALE 60s retry window (error + no-token paths)
