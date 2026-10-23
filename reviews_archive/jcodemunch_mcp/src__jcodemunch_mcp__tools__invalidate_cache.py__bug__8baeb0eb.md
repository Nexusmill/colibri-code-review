# Colibri review — src/jcodemunch_mcp/tools/invalidate_cache.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\invalidate_cache.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `8baeb0eb12bbe31f0ec2fd3fbede22cf0709df98032e05342575abbc26b26798` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 LOW with a sketched fix it flagged as unverified against the cache key shapes; 3 refuted - kept); `invalidate_cache` 18-79; the two caches it clears: `config._REPO_PATH_CACHE` (config.py 897-945: keyed by BOTH `display_name` and `owner/name` → resolved source root, plus negative entries) and `parser.imports._sql_stem_cache` (imports.py 810-833: keyed by a frozenset of `.sql` paths, max 4). No prior `.colibri_reviews` record.

## Verdict
Record-only. The sub-agent's finding does not survive the key shapes: the global clears are the correct conservative choice, and its sketched per-repo pops would have introduced a stale entry and a no-op.

## Refuted
- **"Global `_REPO_PATH_CACHE.clear()` / `_sql_stem_cache.clear()` should be per-repo pops" (LOW) — REFUTED.** `_REPO_PATH_CACHE` maps every alias of a repo (its `display_name` AND its `owner/name`) to one resolved path; popping `f"{owner}/{name}"` alone leaves the display-name alias pointing at the deleted repo's root - a stale positive the clear exists to prevent. `_sql_stem_cache` is keyed by a frozenset of `.sql` paths (content identity), so `pop(f"{owner}/{name}")` is a no-op; its entries are derived from paths only and a same-path set yields the same stems, so a stale entry is harmless and the clear is at worst redundant. Cost of the clear: one `list_repos()` on the next miss, bounded at 512 entries. Not a defect.
- The three claims the sub-agent already refuted (unlink failure leaving the LRU entry - `_cache_evict` runs unconditionally; `_force_full_reindex` never cleared - `index_folder` discards it where it consumes it; branch deltas orphaned - `delete_index` rmtrees `{slug}@*`) stand refuted.

## Adversarial verification (Phase 3)
- Both cache key shapes read from the defining sites (cited above); nothing to pin, nothing changed.

