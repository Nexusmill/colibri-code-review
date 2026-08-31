# colibri gate — PatternSkin/ai_parts.py (grok round 6)

- **source:** PatternSkin/ai_parts.py
- **model:** grok-4.6 bug (external, .grok_reviews/2026-08-22_ai_parts_grok46.md) gated in-session by claude-fable-5
- **sha256:** 80bcabbfc7037866... (current bytes at dispatch, G36) — delta vs GROK-AIP2/GROK-AI/AIS3/top-20 history (pre-declared)
- **date:** 2026-08-22 · **mode:** bug (grok round 6)
- **context pack:** the paid SAM/VLM money-path invariants + all closed GROK-AIP2/GROK-AI/AIS3 items + the mesh_signature stale-cache deferral pre-declared; verified scan_lineage/cache_key/_paid_cache_candidates/save_scan/_sam2_masks/_poll_prediction/p3sam_poll/p3sam_labels_from_glb/p3sam_export_glb.

## Verdict
Not clean — the strongest round-6 file. 7 findings, all survive verification (3 HIGH, 2
MEDIUM, 2 LOW; one LOW is PLAUSIBLE-not-fully-traced), 0 refuted. Two are genuine billing
gaps and one is a real security (path-traversal) primitive, none covered by prior rounds.

## Findings after adversarial verification

**[HIGH, CONFIRMED — path traversal, write+delete primitive] `scan_lineage` returns the raw `ps_scan_lineage` custom prop unvalidated** — scan_lineage:837 (`return str(lid)`)
- Verified: `cache_key` → `scan_lineage` returns `str(obj["ps_scan_lineage"])` with no validation; `save_scan` does `os.path.join(_ps_cache_dir(), sig + ".npz")`. `ps_scan_lineage` is a Blender object custom property — settable by any .blend file or via the Custom Properties UI. An absolute value (`/tmp/x`, `C:\...`) makes `os.path.join` discard the cache dir; a `../` value escapes it. Completing a paid scan then writes/`os.replace`/`os.remove` (clear_scan_partial) an attacker-chosen path OUTSIDE `~/.patternskin/ai_cache`. Realistic vector: a user opens a shared/third-party .blend carrying a poisoned prop and runs a scan → arbitrary file write/delete.
- Fix (Grok's, correct): accept only the minted form — `re.fullmatch(r"[0-9a-f]{16}", lid)` (matches `uuid.uuid4().hex[:16]`); reject path seps / `..` / `os.path.isabs`. Never `str()` a raw ID-prop into a filename.

**[HIGH, CONFIRMED — silent re-bill] paid artefacts are written ONLY under the lineage key, so a lineage minted but not persisted orphans the file** — save_scan:931 (and save_scan_partial/save_text_select/save_parts)
- Verified against `_paid_cache_candidates` (GROK-AI #1, readers never mint, probe lineage THEN signature): the first scan of a fresh object mints a lineage L1 IN MEMORY, writes `{L1}.npz`, stamps `obj["ps_scan_lineage"]=L1`. If the .blend is not saved and Blender closes, L1 is lost. Reopen → the object has no lineage → readers fall to the `{signature}.npz` candidate, which was NEVER written (save wrote only `{L1}.npz`) → miss → re-bill. Works within a session and across saves; the gap is scan → close-without-save → reopen. Violates "never re-bill when a cache exists" (a cache DOES exist on disk, undiscoverable).
- Fix (Grok's, correct): when lineage ≠ signature, also write (or hardlink) the artefact under the signature key; readers/clear already walk both.

**[HIGH, CONFIRMED — double-bill] create loops let a `JSONDecodeError` on a 200 body escape unwrapped** — `_sam2_masks`:221 (`pred = json.loads(r.read())`); same shape in grounding_dino_boxes, vlm_nouns, grounded_sam_mask, sam3_mask, p3sam_start
- Verified in _sam2_masks: the create POST uses `Prefer: wait`; `json.loads(r.read())` runs inside the try, but the except chain is only `HTTPError`/`URLError`/`OSError`. `json.JSONDecodeError` is a `ValueError` — NOT caught. A 200/201 with an empty/HTML-gateway/truncated body (the prediction was CREATED and bills) raises raw out of the function with no prediction id and no "check replicate.com" warning. The user retries → second create → double-bill. The poll side (`_poll_prediction`) already handles this under a broad `except Exception`; the create side does not. Distinct from GROK-RF (that was replicate_flux.py) and from the closed OSError-on-read guard here (that is a connection drop, not a successful read of a non-JSON body).
- Fix (Grok's, correct): after a successful HTTP response catch `ValueError`/`TypeError` and raise the same billed-create RuntimeError used on the OSError branch (carry `pred.get("id")` if a partial object parsed); do NOT re-POST.

**[MEDIUM, CONFIRMED — re-bill] `p3sam_poll` has no null-check and no billed-id wrap and never goes through `_poll_prediction`** — p3sam_poll:2182 (`return json.loads(r.read())`)
- Verified: unlike `_poll_prediction` (which null-checks every body, retries transient errors, and raises with the prediction id + billed warning), `p3sam_poll` returns `json.loads(r.read())` directly. A JSON `null` body → returns None → the caller's next `.get(...)` AttributeErrors mid-flow; a transport error escapes raw. After the ~$0.06 P3-SAM create, a modal failure with no id is easy to "fix" by calling `p3sam_start` again → double-bill.
- Fix: route through `_poll_prediction`, or add the same null-check + `RuntimeError(pred.get("id") + billed warning)` + transient wrap.

**[MEDIUM, CONFIRMED — datablock leak] `p3sam_labels_from_glb` imports the GLB BEFORE the try/finally** — p3sam_labels_from_glb:2216-2219
- Verified: `bpy.ops.import_scene.gltf(...)` and the `imported`/`new` bindings sit ABOVE the `try:`. If the import raises after creating some objects/meshes/materials/images/node_groups (corrupt/partial P3-SAM GLB), `imported` is never bound and the `finally` teardown never runs → orphan datablocks persist in the user's .blend after a billed run. GROK-AI #10 added the materials/images/node_groups cleanup but only inside the try that the import must complete to enter.
- Fix (Grok's, correct): put the import inside the try; in the finally compute "name not in the `before`/`_pre` snapshot" directly from `bpy.data` (not from the possibly-unbound `imported`) and run the existing teardown.

**[LOW, PLAUSIBLE — temp orphan] `render_view_png` / `render_view_natural_png` / `render_sdf_png` don't unlink their mkstemp PNG on save failure** — (not individually traced)
- Grok reports these three do `fd, png = tempfile.mkstemp(...); os.close(fd); _save_png_rgb(..., png)` with no except-unlink, while `_segment_geometry` unlinks in `finally`. Consistent with the confirmed pattern elsewhere in the file; labeled PLAUSIBLE because I did not pull all three bodies. LOW (a temp PNG orphan on a rare disk-full/bpy failure).
- Fix: `try: _save_png_rgb(...); return png` / `except: os.remove(png); raise`.

**[LOW, CONFIRMED — temp orphan] `p3sam_export_glb` leaves the temp .glb on export failure** — p3sam_export_glb:2098-2100
- Verified: `fd, path = tempfile.mkstemp(suffix=".glb"); os.close(fd)` then `bpy.ops.export_scene.gltf(filepath=path, ...)`; the `finally` removes the temp OBJECT/mesh but NOT the file. On an export exception the (potentially large) GLB stays in the system temp dir; the path is only returned/cleaned on success.
- Fix: `os.remove(path)` in an `except` before re-raising.

## Refuted and dropped
None — all 7 hold.
