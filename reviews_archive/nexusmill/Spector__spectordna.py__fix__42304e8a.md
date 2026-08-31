# Fix closure — Spector/spectordna.py (SDNA-1)

- **Source path:** `Spector/spectordna.py`
- **Model:** claude-fable-5 (in-session)
- **sha256 (post-fix):** `42304e8a43cb5a26145704103a7e9aa97d282c694ae4b38b6f79d91e0fa527c9`
- **Prior review sha:** `b8b3e77c…` (2026-08-08 delta review that deferred SDNA-1)
- **Date:** 2026-08-15 · **Mode:** fix-closure
- **Context pack:** SDNA-1 docket (incl. its unblock condition) + full current-file read + the 2026-08-08 component-count fix this builds on.

## Fixed since last review

- **SDNA-1 CONFIRMED → FIXED** — the relative zero-mode tolerance `tol = max(vals[-1]*1e-8, 1e-12)` is replaced by `_drop_zero_modes(vals, n_components)`: drop exactly the C smallest sorted modes (kernel dimension = component count, counted exactly since 2026-08-08) plus only the absolute `1e-12` floor. The docket's misfire — a genuine low mode below `vals[-1]*1e-8` on a >8-orders-spread spectrum being dropped, shifting the `scale_invariant` divisor — is now impossible by construction.

## Verification

`tests/harness/probes/sdna_unpark.py` 8/8, satisfying the docket's unblock condition:
the retired rule replicated verbatim and shown to drop a genuine 3e-9 mode on a spread
spectrum while the structural drop keeps it; old-vs-new parity proven on typical synthetic
spectra AND on real fan-mesh eigsh spectra (stored DNA unchanged — the docket's stated
comparability risk); ground-truth first-nonzero check; real 2-shell integration; degenerate
raise preserved. Harness row SP-SDNA-DROP. Remediation row `sp-unpark-sdna` (same commit).
