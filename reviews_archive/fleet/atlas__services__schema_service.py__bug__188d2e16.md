# Colibri review - atlas/services/schema_service.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\schema_service.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__schema_service.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `188d2e162f75dceb8e8cbe53456750498796902a2035c24e3c8497aadbfc91fd` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `find_importers`: in-package (asset_validator, ui_generator, __init__) + `tests/test_schema_service_control_inference.py` (9 passing tests, the only live consumer); no fork probe from this file's side; fork: 1 PLAUSIBLE, 3 refuted.

## Verdict
The fork's single PLAUSIBLE (line 173: `ReplicateSchemaProvider` expects a bare slug, `system_config.py` ids carry `replicate/`) is the same id-convention drift proven RED from the input_schema/model_registry side - kept PLAUSIBLE here (unverified because: no probe drives `ReplicateSchemaProvider` without the network) and folded into `FLEET-P0-MODEL-ID-CONVENTION-DRIFT`. Nothing else; the fork's three refutations were re-read and stand (the control-inference behaviour is covered by the 9 passing tests).
