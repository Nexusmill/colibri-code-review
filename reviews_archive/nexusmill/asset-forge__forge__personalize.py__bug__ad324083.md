# Colibri Review - bug (FULL re-audit) - asset-forge/forge/personalize.py

- **Source path:** `asset-forge/forge/personalize.py` (twin `asset-forge-user/forge/personalize.py` byte-identical - fix applies to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 26
- **sha256 reviewed:** `ad324083bd57e214f7525a6dc13e97d547e2158e4b9ad9c85668cbd855c1042d` (sha8 `ad324083`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL read of the current bytes (owner ruling: pre-gate audits untrusted)
- **Context pack:** importers app.py:17/656/662 (license load/save routes) and app.py:804/1035 (`stamp_dir` after generate_set and after a bundle); pipeline.py writes PNGs via `DualCanvas.to_png` and SVGs via `write_text` with no metadata of their own, bundle.py writes provider PNGs with no dpi/ICC/text chunks (so re-encoding loses nothing); the "atomic buyer stamping" remediation row and the UNIT 9 empty-env-var row (config.py fixed, `personalize.py` not in its file list) loaded as claims; G14/G15 doctrine (this is the ONLY personalisation marketed: a visible, self-entered stamp, no crypto).

## Verdict
Shippable after one LOW fix. The stamp is what doctrine says it is (plain courtesy metadata, sanitised, written atomically, alpha preserved - `PERS_stamp_preserves_alpha_and_metadata` green on the repo bytes); the one defect is the home-directory expression that the rest of the app already fixed.

## Bugs & vulnerabilities

**[LOW] An empty `ASSET_FORGE_HOME` puts `license.json` in the current working directory while the rest of the app stays in `~/.asset-forge`** - `line 14`
- What: `Path(os.environ.get("ASSET_FORGE_HOME", <default>))` returns `Path("")` (= cwd) when the variable exists but is empty; `forge/imagegen/config.py:10` was changed on 2026-08-06 to `os.environ.get(...) or default` for exactly this (its comment: "empty env var must not resolve to cwd"), so the two halves of the app disagree about the home.
- Trigger: `export ASSET_FORGE_HOME=` (macOS/Linux shells keep an empty variable; the pywebview launcher inherits the environment).
- Impact: the buyer's stamp record lands wherever the app was launched from, is lost on the next launch elsewhere ("Licensed to" disappears, files stop being stamped) and can leak into a project folder. Reproduced in a subprocess: personalize.HOME = "." vs config.HOME = ~/.asset-forge.
- Fix: mirror config.py - `os.environ.get("ASSET_FORGE_HOME") or (Path.home() / ".asset-forge")`. Battery `PERS_empty_home_env_matches_config` RED on the repo, GREEN on the patched copy.
- Verification: CONFIRMED (bytes on both sites + reproducer).

## Missing safeguards
- `stamp_png`/`stamp_svg` swallow every exception, including a Windows `PermissionError` on `os.replace` when the viewer has the file open - a silently unstamped file; a log line would help field debugging.
- `save()` sets `_CACHE` before the write succeeds - a failed write leaves the session claiming a stamp that is not on disk until restart.
- `stamp_png` re-encodes with PIL defaults (any future dpi/ICC written by a generator would be dropped unless passed through) - not a defect today, nothing writes them.

## Adversarial verification pass (refuted claims)
- "The buyer name can inject into the SVG `<metadata>`" - `_sanitize` keeps only `[\w \-().@]`, so `<`, `>` and `&` never reach the file.
- "A non-Latin name breaks the PNG tEXt chunk" - PIL's `add_text` falls back to iTXt for non-latin-1 values.
- "Stamping a transparent PNG flattens it" - the image is re-saved in its own mode; probe shows RGBA and the transparent count unchanged.
- "`stamp_dir` follows symlinks out of the set" - files that are symlinks are skipped and `os.walk` does not descend symlinked directories by default.
- "The stamp is creator-only provenance marketed to buyers (G14)" - it is the self-entered personalisation the doctrine allows; no crypto, no tracer import.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `f07c29e3098176737550560654d7d7f82bf4775ec4be2c7b3c21e89eed137750`. Rows AF-PERS-EMPTY-HOME in `docs/remediation_manifest.json`, same commit.

