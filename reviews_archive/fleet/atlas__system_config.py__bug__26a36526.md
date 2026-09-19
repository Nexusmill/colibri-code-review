# Colibri review - atlas/system_config.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\system_config.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__system_config.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `26a365266450a70f5184229ec306546fa8a6ab951547beaf79f2fde0b8f803d4` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: fork probe re-run today: RED (`get_or_push_configuration` returns the local default silently while the comment above `load_config` says 'FAIL FAST - Do not use local default'); `get_provider_strategy()` dead (zero callers); the Google-default catalog is under FLEET-P0-DEGOOGLE-PATHS-UMBRELLA.

## Verdict
Two LOWs hold: (1) the 'FAIL FAST' comment at line ~303 is false for the Hub-unconfigured (Phase 0) case - the code silently uses the local default; (2) `get_agent_params()`'s Anthropic-native fallback (line ~343) is a direct vendor path the 2026-09-09 provider ruling forbids but the Google-only DEGOOGLE umbrella does not name. Docketed together as `FLEET-P0-SYSTEM-CONFIG-STALE-COMMENT-AND-ANTHROPIC-FALLBACK` (the provider factory rewrite touches exactly these lines). `get_provider_strategy` dead code: noted, not deleted (karpathy: not this tranche's change).
