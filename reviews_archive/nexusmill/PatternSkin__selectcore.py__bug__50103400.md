# colibri-review — PatternSkin/selectcore.py — bug (hunt round 1, effort=mid)

- **Source:** PatternSkin/selectcore.py · **Scanner:** general-purpose subagent @ claude-sonnet
  (mid effort) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 5010340019d129a1083f0c93f85f0e1836afaa438ab3ef343b2b0173a50bcdf6
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (mid pass)
- **Context pack:** prior review `PatternSkin__selectcore.py__bug__2dc68c2f.md` (K3) + remediation
  rows (commit 1585f5b) — the prior stale-cache-on-vert-content, missing validation, singular-NaN,
  heat-`m` reuse, and dijkstra-unreachable findings all verified FIXED, excluded up front. `_CTX`
  eviction path traced via `find_references(clear_ctx)` = **0 call sites**; caller `_sel_ctx`
  (`__init__.py`) keys on `obj.name + counts + sha1(V)`.

## Verdict
Two real caching defects in the paid product's selection core — one a session-life memory leak, one
a reopening of the stale-cache class the last fix targeted (the vertex half was closed; the face
half was left open). Both fixed in this file alone; both proven by pre/post execution.

## Bugs & vulnerabilities (CONFIRMED, fixed)

**[HIGH] `_CTX` grows unbounded for the session — the sole eviction path is dead code** - `get_ctx` / `clear_ctx` (`selectcore.py:374,379-396`)
- What: `_CTX` was a plain dict with no cap; `get_ctx` only inserts; `clear_ctx` (its only eviction)
  has **zero callers** (`find_references`). The caller `_sel_ctx` builds its key from `sha1(V)`, so
  every geometry edit — including Pattern Skin's own `apply_pattern`, which displaces vertices —
  produces a **new key** and thus a new, permanently-retained entry.
- Trigger: the module's own primary workflow (iterate → re-select → apply). Module state, so it
  survives add-on disable/enable; only an interpreter restart clears it.
- Impact: each retained entry pins `V`, `F`, the dual graph, the cotangent Laplacian + lumped mass,
  and — once any geodesic/cut tool runs — a prefactored SuperLU heat solver (fill-in typically far
  larger than the sparse matrix) plus up to 16 `nv`-length geodesic fields. Unbounded growth in a
  long editing session.
- Fix: LRU-bound `_CTX` at `_CTX_MAX = 8` (touch-on-hit, evict-oldest-on-insert).
- **Verified:** pre-fix the cache reached 40 entries with 40 distinct keys and nothing evicted;
  post-fix it holds ≤ 8 with correct LRU recency.

**[MEDIUM] `get_ctx` signature omits face content — a retriangulation returns a stale ctx** - `get_ctx:388` (`sig = (len(_V), len(faces), sha1(_V))`)
- What: `sig` hashed vertex bytes + counts but only `len(faces)`, never the triangle-index content.
  A topology change that preserves vertex positions, vertex count and triangle count (e.g. a diagonal
  flip / retriangulation) left `sig` unchanged → the cached `MeshCtx` for the OLD triangulation was
  returned silently. This is the exact "wrong selections, no error" class the 2026-07-20 fix closed
  for vertices; it left the face half open.
- Trigger: position-preserving retriangulation (`me.calc_loop_triangles()` re-derives `T` each call).
- Fix: fold `sha1(faces.tobytes())` into `sig`. Because the change is detected inside `get_ctx`, it
  fires even when the caller key is identical — no `__init__` edit needed.
- **Verified:** pre-fix, `get_ctx(k, V, F_permuted)` returned the SAME (stale) object; post-fix it
  rebuilds.

## Quality / deferred (not fixed this round)
- **Dead numpy-fallback branches (SC-2, deferred).** `MeshCtx.__init__` hard-raises `SCIPY_MSG` when
  `not HAVE_SCIPY`, so every `if HAVE_SCIPY: … else: …` fallback in `_prep_heat`/`region_grow`/
  `harmonic`/`region_grow_field`/`dijkstra_path` is unreachable for any constructed context. Not a
  functional bug (the `else` paths never run), but the docstring's "numpy fallback" overstates
  resilience and the dead branches are untested (e.g. dijkstra's fallback fabricates a 2-hop path).
  Deferred: delete-the-branches vs make-the-fallback-real is a design decision.
- Prior-review LOWs unchanged and not re-ranked: non-manifold dual-edge pairing gap
  (`_build_topology`), unused `v`/`c` in `sdf` — both carried, both low impact.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- *"No bounds/empty validation on `source_verts`/`seed_faces`/`fixed_idx`/`src_face`/`dst_face`"* —
  every real call site guards `len(seed)==0` and derives indices from `ctx.F[...]` or Blender-native
  loop-triangle/polygon arrays always in range; `ai_parts.py` never calls the graph methods on its
  proxy ctx. The internal gap exists but has no reachable trigger.
- *"`region_grow_field` is buggy"* — it has 0 references anywhere; unused public surface, not a bug.
- *"Threading race on `_CTX`/`_heat*`/`_geo_cache` lazy mutation"* — this add-on runs operators on
  Blender's main thread (no background-thread call site); PLAUSIBLE-but-unreachable, already the
  prior review's LOW.

## Verify
`junk/_selectcore_test.py` — post-fix **6/6 PASS**, pre-fix **2/6** (the retriangulation-rebuild and
the three LRU checks fail on HEAD bytes; verified by restore-and-rerun). Module is pure-numpy+scipy,
imports headlessly. NOT exercised in a live Blender session.
