<!-- source: asset-forge/skin_part.py | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | sha256 abc30f765dc9d7485aed96c911b141ecc10d0e620132d833daa871e07d58d869 | 2026-07-22 | mode: bug | context pack: jcodemunch outline+importers (0 importers - standalone creator CLI), forge/skin3d.py callee sources (skin_stl, apply_skin, triplanar_height, _densify), remediation ledger (e71aa59), sync_builds.py creator whitelist -->

## Verdict
Shippable as-is. All 6 DeepSeek findings REFUTED under adversarial verification — zero code
changes warranted. The file is a 54-line creator-only local CLI whose operator IS the trust
boundary, calling a callee that already carries the guards DeepSeek asked for.

## Adjudication of DeepSeek findings (worst-claimed first)

**[HIGH] path traversal via `--out` (line 39) — REFUTED (by design)**
- Local creator CLI on the sync_builds creator whitelist; no user-edition twin. The person
  typing `--out ../../evil.sh` is the machine owner choosing their own output path — no
  privilege boundary is crossed. Same adjudication class as the Spector localhost
  accepted-by-design entries in the remediation ledger.

**[HIGH] arbitrary read via `--stl` (line 41) — REFUTED (by design)**
- Same trust model. The operator can already read any file they name, with any tool.

**[HIGH] arbitrary read via `--pattern` (line 17) — REFUTED (by design)**
- Same trust model; the `os.path.isfile` branch is the documented feature ("--pattern may
  be ... a file path", docstring line 9), not an oversight.

**[MEDIUM] KeyError on `res["watertight"]` (line 49) — REFUTED**
- `skin_stl` (forge/skin3d.py:74-89) returns a LITERAL dict that always contains
  `"watertight"`; every failure path raises instead of returning. The only callee is repo-owned;
  the hypothesized "API change" is not a current defect.

**[MEDIUM] unhandled preview exceptions (lines 45-47) — REFUTED as a defect**
- Reachable only after `skinned.export(out_stl)` succeeded, so the mesh file exists; residual
  failure modes (user deletes file mid-run, renderer missing) end in a visible traceback on a
  dev CLI after the primary artifact is already safely written. No data loss, no silent failure.

**[LOW] missing numeric validation (lines 30-33) — REFUTED / verified-stale**
- The guards live in the callee, where they belong: `apply_skin` raises on `tile_mm <= 0`
  (skin3d.py:60-61, added by e71aa59); `_densify` is hard-bounded (7 iterations AND 1.5M-face
  cap) so `--edge-mm <= 0` cannot hang; empty meshes raise cleanly (skin3d.py:48-49).
  Re-flag of already-remediated code — verified-stale.

## Missing safeguards
- None warranted at this layer. Input existence, mesh validity, and degenerate-parameter
  handling are enforced in forge/skin3d.py; duplicating them in a thin CLI wrapper adds
  drift surface, not safety.
