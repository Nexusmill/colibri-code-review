# Colibri review - atlas/services/model_registry.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\model_registry.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__model_registry.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `3ea148348c03a1f004754ebd8033cd9e00a80df1871c2e970ff8fe0a9a0d3421` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `find_importers`: `atlas/services/__init__.py` + `atlas/services/schema_service.py` (in-package only); fork probe re-run today: RED (`ModelRegistry.get('replicate/minimax/music-1.5')` -> None for the id `get_capability_model('Composer','music_generation')` returns).

## Verdict
CONFIRMED, same root cause as input_schema.py: `ModelRegistry` ids are bare Replicate slugs, `system_config.py` ids carry the `replicate/` routing prefix, so `.get()` on the id the system actually selects returns None - the 'Single Source of Truth for model metadata' cannot see the models in use. Docketed under `FLEET-P0-MODEL-ID-CONVENTION-DRIFT` (owner decision on the convention). The fork's un-numbered safeguards (no Replicate version pinning - G17 class; `cost_per_run` captured but never shown before spend - G19; Vertex/GoogleGenAI provider entries) are the Phase 3 provider-adapter + spend-ledger items already named by the packet.

## Bugs & vulnerabilities (Phase 3 verdicts)
### [MEDIUM] id drift makes every real lookup miss - CONFIRMED (probe RED), DOCKETED - `line 504`
