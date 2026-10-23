# colibri bug review — tests/test_assetforge.py

- source: tests/test_assetforge.py · model: GLM-5.3-Flash (in-session)
- sha256: (fresh row, full sha in manifest) · reviewed_at: 2026-10-14 · mode: bug
- context pack: live execution (ALL PASSED, exit 0); the open G35 row's BOTH halves verified in current bytes — Mock.generate carries `extra=None` with the AF-SCHEMA-UI scar (l.28-32) AND library_gen.py:899's run_job docstring documents "`extra` is the job's schema_extra dict or None (AF-SCHEMA-UI); mocks must accept it".

## Verdict
Clean — no defects. Resume-correctness (m2.n == 3), pause-before-work, merged-library PNG counting, and the estimate math are all real rows.

## Bugs & vulnerabilities
None CONFIRMED.

## G35 closure
The row "tests/test_assetforge.py (Mock.generate) + asset-forge/forge/library_gen.py (run_job docstring)" is verified-stale IN FULL (both halves above).

## Missing safeguards
- `line 50`: `root = tempfile.mkdtemp()` never removed (the established leak class).
