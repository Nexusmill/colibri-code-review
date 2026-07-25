# BUG review: PatternSkin\ai_parts.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\ai_parts.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:08
- tokens: in 22151 / out 4642
- est cost: $0.1361

---

## Verdict
Not safe to ship as-is. The single biggest defect is in `_sam2_masks` (the paid SAM-2 path): a duplicated `except HTTPError` clause swallows every HTTP error except the first-attempt 422, so auth failures and most API errors silently retry and then crash with a raw `AttributeError: 'NoneType'` — and the user is never told their key or request was rejected.

## Bugs & vulnerabilities

**[HIGH] Duplicate `except HTTPError` swallows all HTTP errors; `pred` stays `None` and crashes** - `line 196`
- What: Two consecutive `except urllib.error.HTTPError` handlers (lines 196 and 199). Python only ever enters the *first*; the second is dead code. The first handler only acts on `e.code == 422 and attempt == 0` — for every other HTTP error (401 bad token, 404, 402 quota, 422 on later attempts) it falls through doing nothing, the loop iterates with no sleep and no error, `pred` remains `None`, and after 5 silent iterations line 212 raises `AttributeError: 'NoneType' object has no attribute 'get'`.
- Trigger: Any non-422 HTTP error from Replicate in the SAM-2 path — most commonly an invalid/expired API token (401) or insufficient credit (402).
- Impact: The user pays the wait, gets a cryptic `AttributeError` instead of "Replicate 401: …", and the real error (bad key / no quota) is permanently hidden. This is the main money-spending entry point.
- Fix: Merge into one handler: `except urllib.error.HTTPError as e:` → handle the `422 and attempt == 0` retry, handle the retryable codes, else `raise RuntimeError(...)` exactly as the (currently dead) second block does. Also guard line 212 with `if pred is None: raise RuntimeError("Replicate request failed after retries")`.

**[MEDIUM] Grounding-DINO boxes treated as pixels; the model returns normalized [0,1] coords** - `line 690`
- What: `_text_votes` does `x0 = max(0, int(bx[0]))` etc., clamping to `[0,W]`. `adirik/grounding-dino` returns bounding boxes normalized to `[0,1]` (the code comment at line 618 admits the schema was never verified). `int(0.5) == 0`, so every box collapses to a ≤1-pixel strip at the image origin and is discarded by the `x1 <= x0` check.
- Trigger: Any successful grounding-dino call in `mode="box"`.
- Impact: `box` mode silently selects nothing, every time — a paid API call that always returns an empty selection with no error.
- Fix: Detect normalized output (`max(box) <= 1.5`) in `_parse_boxes` and scale by `(W, H, W, H)` — but `_parse_boxes` currently has no access to W/H, so pass them in from `grounding_dino_boxes` (which knows the render res), or scale in `_text_votes`.

**[MEDIUM] Boundary edges with `-1` in the dual graph corrupt the connected-component clean** - `line 733`
- What: `E = np.asarray(pctx.dual).reshape(-1, 2); a, b = E[:, 0], E[:, 1]` then `sel[a] & sel[b]`. If `pctx.dual` uses `-1` as the "no neighbour" sentinel for boundary edges (the standard convention, and consistent with the `-1` sentinels used everywhere else in this file), `sel[-1]` silently indexes the *last* face, creating a phantom adjacency between an arbitrary boundary face and the last face.
- Trigger: Text-select on any open mesh (a mesh with boundary loops) in `text_finalize(clean=True)`.
- Impact: Two unrelated regions get fused into one "component", so the `min_faces` noise filter keeps junk or drops real selection.
- Fix: Filter first: `E = E[(E[:, 0] >= 0) & (E[:, 1] >= 0)]` before indexing.

**[MEDIUM] `p3sam_export_glb` destroys the user's selection and leaks a mesh datablock** - `line 1043`
- What: (a) Lines 1048–1050 deselect *all* objects and select only the temp export object; the original selection/active object is never restored. (b) `tmp.data = obj.data.copy()` creates a new mesh datablock, but the `finally` only removes the object — the copied mesh stays in `bpy.data.meshes` orphaned, one leaked datablock per P3-SAM run.
- Trigger: Every `p3sam_export_glb` call.
- Impact: User's selection state silently lost (destructive UX side effect in a modal tool); session file bloats with `_ps_p3sam_export.001`-style orphan meshes over repeated scans.
- Fix: Save/restore `bpy.context.selected_objects` + active object, and add `bpy.data.meshes.remove(tmp.data)` after removing the object (keep a reference before `objects.remove`).

**[MEDIUM] `load_scan_path` crashes on corrupt/truncated cache files** - `line 594`
- What: `np.load(path)` and the `z["..."]` key accesses are unguarded. A partial write (crash during `save_scan`), disk-full truncation, or a cache written by a newer/older version raises `ValueError`/`KeyError`/`BadZipFile`. The sibling `load_parts` (line 1213) *does* wrap this in try/except — `load_scan`/`load_scan_path` don't.
- Trigger: Any corrupt `~/.patternskin/ai_cache/<sig>.npz` (e.g. Blender killed mid-save, which is exactly the restart-survival scenario this cache exists for).
- Impact: Auto-load on startup raises instead of falling back to a fresh scan.
- Fix: Wrap the whole body in `try/except Exception: return None`, matching `load_parts`.

**[MEDIUM] Mesh signature collisions reuse wrong paid scans** - `line 553`
- What: The cache key is only `vert_count | poly_count | bbox rounded to mm`. Two genuinely different meshes with the same counts and bounding box (extremely common for primitives, symmetric hard-surface parts, kit-bash pieces at the same scale) produce the identical 16-hex-digit key.
- Trigger: A mesh with matching `(nv, npg, mm-bbox)` of a previously scanned mesh.
- Impact: `load_scan`/`load_parts` silently apply the *other* model's part labels — wrong selections with no warning, and the "never re-pay" guarantee becomes "never notice it's wrong".
- Fix: Add a cheap geometry digest to the signature, e.g. `hashlib.sha1(np.ascontiguousarray(V[::max(1, nv//64)]).tobytes())` plus total edge length / centroid, not just the bbox.

**[LOW] Temp-file leak in `_load_mask` on any download/decode error** - `line 239`
- What: `mkstemp` creates `tmp`, but if `urlopen`, `bpy.data.images.load`, or the `np.array(img.pixels[:])` reshape raises, the file is never removed (the `os.remove` at line 247 is only reached on the happy path, and the loaded Blender image also leaks if the reshape throws between load and `remove`).
- Trigger: Network error or a non-image/corrupt response from the mask URL (which is why the caller at line 229 has a bare `except Exception: continue` — the leak is hit exactly when that fires).
- Impact: One orphan PNG per failed mask fetch, per view, per scan; accumulates in `$TMPDIR`.
- Fix: Wrap in `try/finally: os.remove(tmp)` and load the image inside the same try.

**[LOW] `_mask_from_file` leaks the loaded Blender image if the reshape raises** - `line 872`
- What: `np.array(img.pixels[:], ...).reshape(h, w, 4)` runs before `bpy.data.images.remove(img)`; a mismatched pixel count (e.g. a grayscale/16-bit PNG Blender normalizes unexpectedly) raises and the image datablock leaks. Same pattern as `_load_mask`.
- Fix: `try: ... finally: bpy.data.images.remove(img)`.

**[LOW] `mesh_signature` crashes on empty meshes; `build_proxy` returns malformed arrays for empty proxies** - `lines 553, 305`
- What: `V.min(0)` on a 0-vertex mesh raises `ValueError`. Similarly, `Vp = np.array([...])` in `build_proxy` has shape `(0,)` instead of `(0, 3)` for an empty bmesh, breaking downstream indexing with a confusing error.
- Trigger: Operator invoked on an empty mesh object, or a decimate modifier that eats everything.
- Fix: Early-validate `len(me.vertices) > 0 and len(me.loop_triangles) > 0` and raise a clear `RuntimeError("mesh has no geometry")`; reshape empties with `np.empty((0, 3))` / `np.empty((0, 3), np.int64)`.

**[LOW] Mask/result URLs fetched without host validation** - `lines 240, 932`
- What: `_load_mask` and `sam3_mask` fetch whatever URLs the prediction JSON contains. `urllib` follows redirects, so a compromised/buggy API response (or future self-hosted Replicate-compatible endpoint) can make the addon issue arbitrary GETs (local network SSRF from the user's machine).
- Trigger: A malicious or malformed `output`/`individual_masks` URL.
- Impact: Addon fetches attacker-chosen URLs with the user's network privileges (no auth headers leak, at least — they're not attached to these requests).
- Fix: Validate `urlparse(url).scheme == "https"` and restrict/allowlist the host (e.g. `*.replicate.delivery`) before fetching; disable or re-validate redirects.

## Missing safeguards
- **No test for the retry/exception matrix** of the Replicate transport — the dead-code duplicate handler in `_sam2_masks` would have been caught instantly by a test asserting that a 401 raises `RuntimeError` containing "401".
- **No schema contract test for grounding-dino output** — the normalized-vs-pixel box ambiguity is exactly what a recorded-fixture test would pin down; line 618 admits it's unverified.
- **No validation of `polypart` in `render_part_thumbs`** — labels `< 0` (unassigned sentinel used throughout the rest of the pipeline) wrap around via negative numpy indexing at line 133 (`pal[tpart]`), silently painting unassigned faces with the last part's colour.
- **Temp-GLB from `p3sam_export_glb` is never deleted** (line 1051, caller's responsibility, no documented contract) — add a `finally: os.remove(path)` at the call site or return a context manager.
- **`regranulate` dereferences `pctx`/`proxy_labels` with no guard** (line 521) — if both `pctx` and `pctxVF` are absent it's a bare `AttributeError`; raise a descriptive error.
- **Cache writes are not atomic** — `np.savez_compressed(path, ...)` writes in place; write to `path + ".tmp"` then `os.replace` so a crash can't leave the corrupt file that trips `load_scan_path`.
- **No unit tests around `_text_votes`/`_mask_votes` boundary edges with `-1` dual entries** despite both being advertised as "PURE, offline-testable".
- **`progress` callbacks and SAM polling run with no cancellation support** — a 20-minute P3-SAM cold boot can't be aborted; at minimum poll loops should check a cancel flag.