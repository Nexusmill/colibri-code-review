# colibri review — birdcam/config.py (delta + security hunt)

- source: `birdcam/config.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: cbf3975a20bb8ef0175068e41ffb0f1ee328c7553947c283876a36e6ca22f7b2
- date: 2026-10-05 03:20
- context pack: prior bug review 6f05cdb4 (hy4, f04d93d bytes — enrich null-crash MEDIUM, fixed
  in-session; deferred the legacy-validation TypeError pattern to "a future sweep"); git delta
  73225de→c88d8b6 (songs publish + songs_upload_token, person_detection section, state hardening);
  jCodemunch outline (28 symbols); secrets covenant (env-only credentials, no value logging).

## Verdict

Sound on the security axis that matters here: credentials are read strictly from .env-backed env
vars, never logged, YAML is safe_load'd, and the new person_detection validations are
fail-closed and sha-pinned. The deferred legacy-validation crash pattern is now formally recorded
(two LOWs below); no MEDIUM/HIGH.

## Fixed since last review

- Enrich null/non-numeric crash (prior MEDIUM): isinstance guards present at 172-186 — verified.
- person_detection section is new and correctly fail-closed: null `enabled` is rejected (194-195),
  bool-vs-int distinction handled for threshold/interval (197, 201), model path and 64-hex sha
  validated and normalized (206-217).

## Bugs & vulnerabilities (new findings only)

**[LOW] Legacy numeric validations crash with TypeError instead of ConfigError** - `lines 158-171`
- What: the five pre-enrich checks (`since_days`, `metadata_pages`, `download_delay_seconds`,
  `max_uploads_per_run`, `processing_timeout_minutes`) compare user YAML values directly; a bare
  `since_days:` (null) or a quoted string raises `<` TypeError as a raw traceback, not the
  module's guided ConfigError. This is the exact pattern the prior review deferred to a future
  sweep — this is that sweep, recording it in an artifact.
- Trigger: hand-edited config.yaml with a null or string numeric value.
- Impact: confusing traceback for the least technical user; no security impact.
- Fix: fold the same isinstance((int, float), bool-excluded) guard used at 172-186 into the five
  checks (a tiny `_number(merged, section, key, lo, hi)` helper would unify all nine).
- CONFIRMED (guards verifiably absent in current bytes at the cited lines).

**[LOW] A typo'd top-level section name is silently ignored, producing a misleading error** - `line 147`
- What: merge iterates `DEFAULTS` sections only; a config.yaml whose section is misspelled
  (`blinkk:`) is dropped without a peep, and the run then fails at the `blink.cameras is empty`
  check (227-230) — an error that sends the user editing the WRONG place (their cameras ARE
  listed, under the typo'd heading).
- Trigger: one-character section typo in config.yaml.
- Impact: misleading self-service failure; no security impact.
- Fix: after the per-section unknown-key check, reject unknown TOP-LEVEL keys too
  (`set(user) - set(DEFAULTS)`).
- CONFIRMED (trace: merge at 147 ignores non-DEFAULTS top-level keys; unknown-key loop at 150-156
  iterates DEFAULTS only).

## Missing safeguards

- Credential getters each call `load_dotenv` (241, 256, 271) — idempotent and harmless; noted only
  for completeness.

Adversarial pass: both LOWs re-traced line-by-line (guard absence verified at 158-171; merge
semantics verified at 147 against the 150-156 loop). Credential handling audited clean: values
never logged, never embedded in messages, ConfigError texts point at .env.example.
