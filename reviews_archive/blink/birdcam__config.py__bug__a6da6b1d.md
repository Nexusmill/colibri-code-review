# colibri review — birdcam/config.py

- source: `birdcam/config.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: a6da6b1d… (128 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: consumers (every cli command via load_config; blink_credentials used by login + check_password); config.yaml/config.example.yaml as the real inputs; secrets covenant (credentials only from env, never committed).

## Verdict

Sound defaults-over-merge design; the one real gap is that a typo'd key in config.yaml crashes
with a dataclass TypeError instead of pointing at the typo.

## Bugs & vulnerabilities

**[LOW] Unknown/misspelled config keys crash with a dataclass traceback** - `line 103` (`blink = BlinkConfig(**merged["blink"])`)
- What: user YAML is merged over defaults and splatted into the dataclass; `exclude_detectons:`
  (typo) raises `TypeError: __init__() got an unexpected keyword argument` — naming a dataclass,
  not the user's line.
- Trigger: any misspelled or obsolete key in config.yaml (the primary edit surface for a
  non-technical owner).
- Impact: confusing crash at every command, worse than the deliberate ConfigError messages the
  module otherwise uses.
- Fix: validate keys against the dataclass fields per section and raise
  `ConfigError(f"unknown key '{k}' in [{section}] - known keys: …")`.

## Missing safeguards

- No range validation: `since_days: 0`, negative delays, `metadata_pages: 0` (breaks blinkpy's
  `range(1, stop)` → empty scan → silently "no clips"), or `privacy_status: publc` all pass
  through to fail later, far from the typo. A few asserted ranges would localize each.
- `load_dotenv` doesn't warn when the file is missing entirely (it silently no-ops); the
  resulting ConfigError from `blink_credentials` covers login, but `check-setup`'s messaging is
  the only path that names the file.

Adversarial pass: the TypeError path reproduced mentally against `BlinkConfig(**{"cameras": [], "typo": 1})` — CONFIRMED (matches CPython kwargs semantics). The metadata_pages=0 → range(1,0)=empty claim traced against blink_client.list_clips/blinkpy's page loop — CONFIRMED (silent-empty direction, hence safeguard not bug).
