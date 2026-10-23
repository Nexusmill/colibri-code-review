# colibri review — config.example.yaml (first review, security hunt)

- source: `config.example.yaml`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: a00c55f6727432b726e0735aa703a45de8632b8d1e91ea16a2cb2883f4387783
- date: 2026-10-05 04:15 (CORRECTED 04:40 — see the retraction below)
- context pack: never reviewed as a unit; contract = config.py load_config (reviewed this session
  at cbf3975a); the real config.yaml is gitignored (verified in the leak sweep); cost-disclosure
  doctrine G19; tests/test_enricher.py::test_default_config_has_enrich_disabled.

## Verdict

Clean as a template: zero secrets (empty songs_base_url, no tokens anywhere), realistic
placeholder camera names, and every cost-bearing knob carries its price in the comment.

## Bugs & vulnerabilities (new findings only)

None.

## Retraction (honesty note, G11)

The first version of this artifact claimed `enrich.enabled` defaults to `true` in config.py while
the example says `false`, flagged as a G19-direction concern. That was wrong: DEFAULTS
(config.py:40) is `enabled: False` — the example and the built-in default AGREE, and
test_default_config_has_enrich_disabled locks that in. The misread came from the reviewer's
outline transcription, not the bytes. No finding stands; absence of the enrich section never arms
a paid feature.

Adversarial pass: re-verified against config.py lines 38-49 directly after the test contradiction
surfaced.
