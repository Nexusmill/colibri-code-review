# Colibri review - atlas/services/ui_generator.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\ui_generator.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__ui_generator.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `a7ff9a4c52eaa07e762ab917429dfd1cb537895d238239879ab5adaa0a658f19` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_file_outline` (7 symbols); `search_text`: `render_model_config_panel` / `DynamicUIGenerator(` have NO callers outside this module; `find_importers`: only `atlas/services/__init__.py`; fork probe re-run today: RED (float default 0.7 -> 0).

## Verdict
The fork's MEDIUM holds: a NUMBER control whose schema declares no min/max/step defaults `step` to 1, and Streamlit's `number_input` with an int step truncates a float default (0.7 -> 0) - exactly the shape `schema_service.py` produces for an un-ranged numeric property. Unwired today; docketed for the Phase 3 GUI/services pass (the schema-driven UI is also the piece Asset Forge is meant to reuse, per the SERVICES-TEMPFILE-HYGIENE row's unblock).

## Bugs & vulnerabilities (Phase 3 verdicts)

### [MEDIUM] NUMBER control truncates float defaults when the schema has no min/max - CONFIRMED (probe RED), DOCKETED - `line 82`
- Disposition: deferred row `FLEET-P0-UI-GENERATOR-NUMBER-FLOAT-TRUNCATION` (fix shape: infer `step`/`format` from the default's type - `isinstance(default, float)` -> step 0.01/`%.2f`).
