# Fix closure — Spector/launcher.py (SP-LAUNCH)

- **Source path:** `Spector/launcher.py`
- **Model:** claude-fable-5 (in-session)
- **sha256 (post-fix):** `5b8305d367777379311af81ca2475dca2c5fb7030d4b6a54bd8ffa734c419359`
- **Prior review:** `Spector__launcher.py__bug__bbc31181.md` (K3, 2026-07-20; file unchanged at that sha until today, so every finding stood)
- **Date:** 2026-08-15 · **Mode:** fix-closure
- **Context pack:** prior K3 review + the remediated asset-forge-user launcher (LNCH-1 lineage, its fix-closure at f0c90e7d) read side-by-side + jCodemunch importer check (no module imports Spector's launcher; the import-time bind matches the shipped AF pattern).

## Fixed since last review

- **HIGH free-port TOCTOU + trust-any-listener probe → FIXED** — `make_server(HOST, 0)` binds and HOLDS the socket at module init; readiness is a real HTTP GET against that held socket, with an early-exit once `_SERVER_ERR` is set.
- **HIGH orphaned serve loop → ADDRESSED per the accepted AF design** — the rc-gated paths now terminate correctly (a closed window ends the process); the last-resort browser fallback deliberately keeps serving (no reliable lifecycle tie to a tab exists) and now leaves a durable log line saying so. Same trade-off the shipped Asset Forge launcher made.
- **MEDIUM profile leak → FIXED** — `finally: rmtree`.
- **MEDIUM 5-second delegation heuristic → FIXED** — returncode gating on both window paths.
- **LOW unchecked rcs / silent except-pass → FIXED** — rc checks + `_log_last_resort` breadcrumbs on every fallback path; `_show_error` logs before the message box.
- **LOW pywebview unreachable on Windows** — deliberately kept structural parity with the shipped AF launcher (win32 → host → --app browser); noted, not changed.

## Verification

`tests/harness/probes/launcher_unpark.py` 7/7 (live bind-hold/rebind-refusal, live HTTP
readiness serving the real app, sub-2s early exit on server death; source-shape for the
GUI paths). Harness row SP-LAUNCH-LINEAGE. One probe assertion corrected during
verification (naive `_free_port` substring matched the explanatory comment). Remediation
row `sp-unpark-launch` (same commit). **Release flag:** reaches customers only with the
next Spector rebuild + YubiKey re-sign.
