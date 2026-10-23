# colibri bug hunt synthesis — PatternSkin test suite, tranche 5 (2026-10-13)

- date: 2026-10-13 · model: GLM-5.3-Flash (in-session) · mode: bug
- scope covered: the perfection series — test_perfection_{filmstrip,keyvault,support_report,accel_bootstrap,accel,ai_parts}.py. All six run live: PASS, exit 0 each.
- cumulative: 25 of 193 test-tree files deep-reviewed; hunt series (16) + perfection series (6) complete.

## Findings, ranked
1. **[LOW] keyvault t2_pins' finally destroys `_cli` instead of restoring it** (tests/test_perfection_keyvault.py:139,159) — latent for future appended rows; W3's own save/restore (l.80/113) is the in-file counterexample.
2. **[LOW] support_report t2 mutates USERPROFILE/HOME with no restore** (tests/test_perfection_support_report.py:124) — and the env line is inert for the row it precedes (`sr._support_dir` is monkeypatched below it); delete or restore.
3. **Hygiene:** accel:69 fourth `if False else` dead-capture instance; accel_bootstrap's never-read `urlopen_counts` (l.172/199); keyvault W4's identity `.replace("importable","importable")`; ai_parts' pyflakes-degrades-to-skip.
4. Global stdlib patches (subprocess.run / shutil.which) in keyvault W1 and accel_bootstrap t1 — all finally-restored: acceptable in standalone battery processes, noted.

## Clean units and standout positives
- filmstrip: clean — the single-source literal pin (0.45 exactly once) is the strong form r5 weakened.
- ai_parts: clean — the suite's only truthy-string-hardened check(); the pskpkg import trick; the gate-verdict mirror-probe row.
- support_report's byte-exact multibyte cap ladder (W1e-h) and keyvault's vendored-drift guard (x3 + obs x2 sha match) are the tranche's best rows.

## Program state after 5 tranches
Findings awaiting owner disposition: 4 MEDIUMs (r2-8 vacuous mock, r1 live-inbox write, r4-7 escape-all disjunction, r8 or-True tautology) + tranche-1's pair + the LOW/hygiene ledger. Remaining unreviewed: the domain suites (~18 files: math, projections ×3, ai_sdf/ai_select, part_export, watermark, assetforge, heightmap, critic_freshness, skill_census, session_grounding, zcode_hooks, blender_smoke, e2e) and the 116-file harness/probe tree.
