# Colibri fix-pass record - PatternSkin/ai_parts.py (GROK-AI billing tranche)
- source: PatternSkin/ai_parts.py
- model: claude-fable-5 (in-session)
- sha256: b1e82510de8af227616a266fe4be3a4c6c899b01658fbb8b3258e2e009e45d27
- date: 2026-08-15
- mode: fix (GROK-AI findings 1-5, 7-11)
- context pack: full outline + targeted reads of the cache-key cluster, all five poll tails,
  semantic_finalize, png savers, glb import; __init__.py call sites (text-select res=640
  hard-coded -> legacy migration safe; autoload consumes has/load pairs); mesh_signature
  external callers (Spector index_scan x2, filmstrip thumbs) -> key-stability boundary;
  PSK-ULTRA-2/5 coupling lesson honoured (findings 1+2 landed together, verified on a real
  mesh in real Blender).

## Verdict
All ten findings re-verified present on current bytes (605fb9c8; docket sha 64379693 was
stale after tranche 2 - line drift only, nothing incidentally closed) and fixed. Battery
15/15 in real headless Blender 5.1.2 (repo-tree import, monkeypatched providers, zero spend);
pre-existing PS-SCAN-RESUME / PS-TEXT-CACHE testers pass against the new contracts.
Finding 8 fixed at the harm site (_geo_digest for resume freshness) with mesh_signature
deliberately byte-stable - boundary documented in-source and in the manifest.

## Fixed since last review
- GROK-AI #1 reader lineage minting -> _paid_cache_candidates read-only probes
- GROK-AI #2 resume geometry key -> checkpoint v3 _geo_digest, quote==execution
- GROK-AI #3 poll tails -> shared _poll_prediction (id-carrying raises, null-check, final GET)
- GROK-AI #4 poisoned empty mask -> zero-decode raises, nothing cached
- GROK-AI #5 over-split 0-parts -> explicit non-negative id counter
- GROK-AI #7 stale polypart IndexError -> length-guarded miss
- GROK-AI #8 signature sensitivity -> _geo_digest at the harm site (boundary documented)
- GROK-AI #9 res-less text key -> res keyed + legacy-640 migration
- GROK-AI #10 glb datablock leak -> materials/images/node_groups orphan sweep
- GROK-AI #11 png-saver leak -> try/finally
