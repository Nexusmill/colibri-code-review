# Colibri review - atlas/services/input_schema.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\input_schema.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__input_schema.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `9a927ae6cf0745211933e4a8658d551199ee3d97ec58e31d054e3cf4c0dd10a5` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `find_importers`: only `atlas/services/__init__.py`; `search_text` MODEL_INPUT_REGISTRY keys vs `atlas/system_config.py` DEFAULT_SYSTEM_CONFIG ids (bare Replicate slugs vs `replicate/`-prefixed routing ids); sibling findings in model_registry.py / schema_service.py / model_schemas.py; fork probe re-run today: RED (17/17 real ids fall through to the generic fallback; minimax lyrics limit not enforced).

## Verdict
CONFIRMED: every capability-model id `system_config.py` actually advertises (`replicate/minimax/music-1.5` etc.) misses `MODEL_INPUT_REGISTRY` (keyed by bare slug), so `get_max_chars_for_field` returns None and the generic 1000-char fallback applies - the Minimax 600-char lyrics limit is silently not enforced. The same id-convention drift is the root of the model_registry.py (MEDIUM) and schema_service.py (PLAUSIBLE) findings and probably the model_schemas.py coverage gap. Which convention Phase 3 standardizes (routing-prefixed vs bare slug) is an OWNER decision - one deferred row for the whole class, not four patches.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] registry keys drift from the ids in use - 100% miss - CONFIRMED (probe RED), DOCKETED - `line 269`
- Disposition: deferred row `FLEET-P0-MODEL-ID-CONVENTION-DRIFT` (covers input_schema.py, model_registry.py, schema_service.py, model_schemas.py).
