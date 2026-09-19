# Colibri Review - bug (FULL re-audit) - asset-forge/forge/skin3d.py

- **Source path:** `asset-forge/forge/skin3d.py` (CREATOR-ONLY: make_user_edition.py DROP_IN_FORGE removes it; no user twin)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 36
- **sha256 reviewed:** `e2aeb76ef6717783257a49f5c44a992e996cda976ed1e0955187853874964b2d` (sha8 `e2aeb76e`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL read (owner ruling: pre-gate audits untrusted)
- **Context pack:** the only importer is the creator CLI asset-forge/skin_part.py (`from forge import skin3d as K`); the skin3d_proto records (bb41e92e, 9286cc53, 6405bc71) and the UNIT 4 adjudication of skin_part.py (operator is the trust boundary) loaded as claims; trimesh + numpy contracts checked at the bytes.

## Verdict
Clean for what it is - a creator-side CLI helper: empty-mesh and non-positive tile guards present, the heightmap normalisation is ptp-safe, the triplanar sample wraps its indices, the subdivision loop is bounded by a face budget, and the export reports watertight/winding honestly.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- Degenerate faces give NaN vertex normals; `apply_skin` displaces along them and exports NaN coordinates without warning - the creator sees a broken STL rather than a message. A `np.isfinite(disp).all()` check before export would name it.
- `_densify` can return a mesh over `max_faces` on the last iteration (the guard is checked before, not after, a 4x subdivision).
- `trimesh.load(force="mesh")` concatenates a multi-body scene silently - fine for skins, worth a log line.

## Adversarial verification pass (refuted claims)
- "`a.max()-a.min()` divides by zero on a flat heightmap" - `+ 1e-9`.
- "`tile_mm=0` gives inf coordinates" - guarded in `apply_skin` (ValueError) - the only public path the CLI uses.
- "The preview crashes on an empty mesh" - guarded (ValueError before `mesh.bounds`).
- "This ships to customers with the tracer vocabulary" - the file is dropped from the user edition.
