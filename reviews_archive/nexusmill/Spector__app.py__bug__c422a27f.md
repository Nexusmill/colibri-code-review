# Colibri review: Spector/app.py (bug)

- **Source:** C:\Users\User\source\repos\Nexusmill\Spector\app.py
- **Model:** claude-fable-5 (in-session, max)
- **SHA256:** c422a27fd341877945f6864612ece8a4d25896e71648048a93aaa1594f55e9d7 (55332 bytes)
- **Date:** 2026-07-22
- **Mode:** bug
- **Context pack:** jCodemunch outline + importers (none; standalone app); collaborator contracts read at source (warehouse.py _clean_row/_ingest_locked/_find_locked/near_duplicates, spectordna.shape_dna/dna_distance, index.py SearchIndex, templates/index.html); docs/remediation_manifest.json entries 41-48+66 and deferred_manifest APP-1/APP-2/WH-* consulted; G35 exclusions honored.

## Verdict
Not shippable as-is: two HIGH defects sit directly on the dedupe/similarity paths the product is named for - `/api/duplicates`' global-min DNA truncation can report the whole library as one duplicate cluster (a one-click mass soft-delete via resolve), and the `_SIMILAR_CACHE` stamp re-reads `_LIB_VERSION` after the slow scan (the exact bug remediated in `_all_dna` on 2026-07-20, entry 42, left unfixed in its twin).

## Bugs & vulnerabilities

**[HIGH] _SIMILAR_CACHE stamps post-computation _LIB_VERSION - stale results served indefinitely** - `line 622`
- What: `find_similar` computes `results = wh().find_similar(...)` (line 620, the file's own "slowest read path"), then stamps the cache with a FRESH read of `_LIB_VERSION` (line 622) instead of a snapshot taken before the scan.
- Trigger: a mutation (e.g. DELETE /api/parts/x) commits and bumps the version while a slow find_similar is computing; the pre-mutation results get stamped with the post-mutation version.
- Impact: every subsequent hit on that (pid, top) key passes the `hit[0] == _LIB_VERSION` check (line 613) and serves stale similarity results (deleted part listed / new part missing) until the NEXT mutation. This is the identical defect class fixed in `_all_dna` (v0 snapshot, lines 1090/1104-1107; remediation entry 42, HIGH) - the twin site was missed.
- Fix: snapshot `v0 = _LIB_VERSION` inside the first `_SIMILAR_CACHE_LOCK` block (line 611-618) and stamp `(v0, results)` at line 622, mirroring `_all_dna`. No call sites affected (route-internal).
- Verification: CONFIRMED - trigger traced end-to-end; no other invalidation path exists (`_SIMILAR_CACHE` is only touched at lines 611-625).

**[HIGH] /api/duplicates truncates all DNA vectors to the global minimum length - one short blob collapses the whole library into a single "duplicate" cluster** - `line 914`
- What: `n = min(len(v) for v in vecs)`; `M = np.array([v[:n] for v in vecs])` truncates EVERY vector to the shortest one in the library.
- Trigger: one part with a short DNA blob. Ingest always writes k=50 floats, but `.spectorpack` import accepts any blob with `len % 8 == 0` up to `_MAX_DNA_BYTES` and no minimum (warehouse.py `_clean_row` lines 855-864) - an imported pack with one 8-byte blob makes n=1. Because `shape_dna` with scale_invariant (the default) divides by lambda_1, element 0 of every SI part's DNA is exactly 1.0 (spectordna.py lines 103-104) - so at n=1 all pairwise distances are 0.0 < any threshold.
- Impact: `/api/duplicates` returns ONE cluster containing the entire library; a user confirming the advertised flow via `/api/duplicates/resolve` (keep=first) soft-deletes every other part - uncapped (no batch-style 500 limit). Recoverable only part-by-part from trash until a purge. Milder form: any legacy/short vector silently degrades clustering to a few modes for everyone.
- Fix: zero-pad to the max length like the repo's own twins do (warehouse `_find_locked` lines 415-418 and `near_duplicates` lines 570-571 pad to dmax; app's own `find_by_dna` uses per-pair min) - and/or have `_all_dna` skip vectors below a sane floor.
- Verification: CONFIRMED - blob-length path traced through `_clean_row` -> `get_dna` -> `_all_dna` -> line 914; the 1.0-first-element invariant confirmed at spectordna.py source.

**[MEDIUM] /api/batch honors dry_run for delete only - a requested tag/rename preview EXECUTES the mutation** - `line 1228`
- What: `dry` is parsed for every op (line 1221) but consulted only in `if dry and op == "delete"` (line 1228); op=tag/rename falls through to the real execution loop (lines 1233-1247).
- Trigger: POST /api/batch {"op":"tag","ids":[...],"tags":"x","dry_run":true} - the caller's model comes from the siblings: `duplicates_resolve` (line 829) and `tags_rename` (line 1017) honor dry_run for all their operations.
- Impact: wholesale overwrite of tags (or names) on up to 500 parts when the user explicitly asked for a preview; `rename(pid, None, tags)` replaces the tags column - no history, no undo. Response contains no "dry_run" field, so the client can't even detect the miss.
- Fix: extend the preview branch to tag/rename ({"id": pid, "would_set": ...}), or 400 on dry_run with unsupported ops. No call sites break (UI does not use batch dry_run; templates/index.html has no reference).
- Verification: CONFIRMED by control-flow trace 1221 -> 1228 -> 1233.

**[MEDIUM] /api/duplicates and /api/find_by_dna use UNWEIGHTED L2 while every other dna_dist in the product is weighted - same threshold/field name, different metric** - `line 925` (and `line 1143`)
- What: `duplicates` clusters on `np.linalg.norm(M - M[i])` (line 925) and `find_by_dna` reports `np.linalg.norm(q[:n] - v[:n])` as "dna_dist" (line 1143). But `wh().find`/`check_dupe`/`_dupe_hit`/the ingest dedup gate all use `index.SearchIndex` = weighted L2 with w_i = 1/i ("reproduces dna_distance exactly", index.py lines 1-6; warehouse.py line 296 comment "the same weighted-L2 SearchIndex find uses").
- Trigger: same default env knob `SPECTOR_DUPE_DIST` feeds both metrics (lines 495, 908, 1199). Since w_i <= 1, weighted dist <= unweighted dist - at the same threshold `/api/duplicates` strictly UNDER-detects relative to the ingest gate.
- Impact: the route's stated purpose - "Retroactive dedupe - check_dupe only catches duplicates at ingest time" (lines 904-905) - is not met: pairs the ingest gate would have merged are silently missed retroactively. And a plugin exporting `/api/dna_raw` then calling `find_by_dna` gets distances/ordering incomparable with uploading the same mesh to `/api/find`, despite the identical "dna_dist" field name and max_dist semantics.
- Fix: multiply vectors by `sqrt(1/i)` (one line, exactly as index.py does) before the norm in both routes, or reuse `spectordna.dna_distance`/`SearchIndex`.
- Verification: CONFIRMED - both sites and both counter-sites read at source; no comment claims the metric change is deliberate.

**[MEDIUM] tags_rename dry_run parsed with bool(...) - REGRESSION of remediation entry 44** - `line 1017`
- What: `dry = bool(d.get("dry_run") or request.args.get("dry_run"))` - the exact pattern entry 44 (2026-07-20) recorded as fixed "across all dry_run + check_dupe flags" via `_truthy`. Every other site complies (lines 493, 517, 650, 704, 711, 829, 1221); this one does not.
- Trigger: POST /api/tags/rename?dry_run=0 (or JSON {"dry_run":"false"}) - bool("0") is True, so the caller explicitly disabling dry-run gets a preview instead.
- Impact: the rename/merge silently does not happen; the response's "changed" count includes would_set rows (line 1042), so a client checking changed>0 believes the typo-tag merge ran. Exact harm class of entry 44.
- Fix: `dry = _truthy(d.get("dry_run")) or _truthy(request.args.get("dry_run"))` - matches lines 829/1221.
- Verification: CONFIRMED (reported as regression/missed-site of the closed finding, with the manifest claim vs line 1017 as evidence).

**[MEDIUM] Thumbnail ETag/immutable caching contract contradicts the thumb-regen endpoints - regenerated thumbnails are never seen** - `line 485` (with lines 478-480, 707-720)
- What: /api/thumb/<pid> serves `Cache-Control: max-age=86400` plus a pid-only ETag `W/"thumb-<pid>"` and a 304 short-circuit on If-None-Match (lines 478-480), commented "thumbnails are immutable per part". But `/api/thumbs/regen?all=1` and `/api/parts/<pid>/thumb/regen` (lines 707-720) exist precisely to REPLACE existing thumbnails.
- Trigger: regen an existing (bad/old) thumb; any HTTP-caching client (the shell webview, a browser) holds the old PNG - for 24h it makes no request at all, and after that its conditional GET matches the never-changing ETag and gets 304 forever. The UI uses bare `/api/thumb/${p.id}` URLs with no cache-buster (templates/index.html line 102), and the regen routes' _LIB_VERSION bump does not reach the thumb URL.
- Impact: the advertised fix flow ("fixes a blank tile", line 716) is invisible whenever a stale thumb was previously served; regen appears broken. (The truly-missing-thumb 404 case recovers, since the 404 carries no cache headers.)
- Fix: derive the ETag from the PNG bytes (e.g. md5 prefix) and drop/shorten max-age for thumbs, or append a version query in the UI. DNA's pid-only ETag (line 451) is fine - nothing regenerates DNA.
- Verification: CONFIRMED at code level (server can never emit a changed representation for a warm conditional client on the same URL).

**[MEDIUM] /api/export and /api/backup route around _HEAVY_SEM - same class as remediated entry 45** - `line 762` (and `line 740`)
- What: export_pack (full-library zip written to temp) and backup (full db+blobs copy) are the heaviest disk operations in the file, yet neither carries @_bounded; find/find_similar/reproduce/verify/thumbs_regen/duplicates/check_dupe/find_by_dna all do. Entry 45 added @_bounded to check_dupe for exactly this reason.
- Trigger: double-click / rapid re-poll on Export (a GET - trivially repeatable) stacks N concurrent library-sized zip writes in tempdir plus lock-queued threads.
- Impact: disk thrash and tempdir exhaustion (each pack is approximately library-sized, unbounded count) - the precise failure mode _HEAVY_SEM was built to prevent (lines 66-67).
- Fix: add @_bounded to both routes; the 503+Retry-After contract is already established for the shell. No call-site breakage.
- Verification: CONFIRMED as an unguarded path (thrash severity itself not load-tested; mechanism certain).

**[LOW] /api/changes reads _LIB_VERSION outside the lock that snapshots the items - reported version can exceed the included changes** - `line 895`
- What: items are snapshotted under _METRICS_LOCK (lines 893-894), but the response's "version" is a fresh unlocked read (line 895).
- Trigger: a mutation's after_request bump lands between the two; response says version N+1 but omits change N+1.
- Impact: the client advances since to N+1 and permanently skips that change - one missed UI refresh, self-healing on the next mutation.
- Fix: capture `ver = _LIB_VERSION` inside the same `with _METRICS_LOCK:` block and return it.
- Verification: CONFIRMED (window is small but the append+bump are atomic under the same lock, so a consistent read is free).

**[LOW] /api/config does unguarded int(SPECTOR_PORT) - malformed env turns the config endpoint into a 500** - `line 1179`
- What: `int(os.environ.get("SPECTOR_PORT", "5005"))` with no try/except, while the same env var is deliberately tolerated at startup (lines 1252-1255) and the file's own convention guards every other env int (lines 30-34, 68-71).
- Trigger: SPECTOR_PORT set to any non-integer; app still boots on 5005 but every /api/config call 500s.
- Impact: the native shell's settings probe breaks for a misconfig the rest of the app absorbs. (openapi line 1169 embeds the same raw string in the server URL - cosmetic.)
- Fix: reuse the try/except-with-default pattern.
- Verification: CONFIRMED by inspection.

**[LOW] /api/find_by_dna accepts a nested-list sig and 500s on broadcast instead of 400** - `line 1143`
- What: validation checks only `isinstance(sig, list)` and non-empty; a uniform nested list ([[1,2],[3,4]]) survives `np.asarray` (2-D, size 4), and `q[:n] - v[:n]` then raises a broadcast ValueError outside any handler.
- Trigger: POST {"sig": [[0.1,0.2],[0.3,0.4]]} with at least one part in the library -> 500 "internal error".
- Impact: contract break only (this file 400s every other malformed input); localhost, no security effect.
- Fix: after asarray, `if q.ndim != 1: return 400`.
- Verification: CONFIRMED (shape math traced; ragged lists already 400 via the existing except).

## Missing safeguards
- /api/health walks the entire library tree on every poll (lines 341-346) - O(all blob files) disk IO per readiness probe; cache per version or sample.
- /api/duplicates/resolve has no ids/cluster cap (lines 833-847) while /api/batch caps at 500 with the "runaway client holds the db lock" rationale (line 1233).
- No minimum-length/dimension sanity on imported DNA blobs anywhere app-side (feeds the HIGH truncation finding; warehouse `_clean_row` checks only %8 and max bytes).
- /api/ingest (up to 50 per-file DNA computes) sits outside _HEAVY_SEM; concurrent big batches queue unbounded threads on the warehouse RLock.
- Threshold/number parsers accept "nan"/"inf" (max_dist, band, days, dupe_dist) - NaN silently inverts filter comparisons into no-ops.
- /api/logs level filter is substring-anywhere (line 878): an INFO line mentioning "ERROR" matches level=ERROR - diagnostics noise.

## Notes (G35)
Excluded as closed per docs/remediation_manifest.json entries 41-48 (all verified still fixed at lines 177, 1090/1107, 178-179, 493/517/829/1221 [except the tags_rename regression reported above], 1191, 402-404, 235, 31) and entry 66 accepted-by-design (str(e) JSON errors; _save_upload .stl coercion) - not re-litigated. Deferred APP-1/APP-2 (job queue, SSE) not re-proposed. Doctrine checks: no secrets logged (path-only request log, token never echoed - line 1185 returns a bool); no sentinel markers in payloads; local-only binding intact (line 1256).
