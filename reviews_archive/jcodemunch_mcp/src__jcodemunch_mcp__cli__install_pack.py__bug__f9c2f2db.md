# Colibri review — src/jcodemunch_mcp/cli/install_pack.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\install_pack.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `f9c2f2db9d97b8eb31684a00d5d2f43b9129fff258a550de93ea89df47d9b73a` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline (`_install_pack` 274-477 read in full); `search_text` for `share_savings` across `src/` — the canonical gate is `config.get("share_savings", True)` (`storage/token_tracker.py:1052`), `config.ENV_VAR_MAPPING` maps `JCODEMUNCH_SHARE_SAVINGS` → `share_savings`, and `_apply_env_var_fallback` applies the env var ONLY when config.jsonc does not set the key (config.jsonc > env > default is the repo's documented precedence); `cli/init.py --share-savings` writes the key via `config.apply_share_savings`. Both RED probes re-run against these bytes first. No prior `.colibri_reviews` record.

## Verdict
Not shippable before this tranche: a crafted starter-pack archive could write files anywhere on disk, and the documented telemetry opt-out did not apply to this command. Both fixed in the commit carrying this record.

## Bugs & vulnerabilities
**[HIGH] Zip-slip via an absolute REMAINDER after the `<pack-id>/` prefix strip — CONFIRMED — FIXED** - `line 384-390, 400-414` (pre-fix numbering)
- What: the traversal guard inspected the raw member name (`startswith("/")` / `".."`), but extraction first strips the top-level directory (`info.filename.split("/", 1)[1]`) and then joins `base / relative`. `pathlib` discards the left operand when the right is absolute or anchored, so `pack//tmp/x` (remainder `/tmp/x`, anchored to the drive root on Windows) and `pack/C:/x` both pass the guard and land outside `base`.
- Trigger: a malicious or tampered pack download (the zip is fetched over HTTPS with no signature/hash — see Missing safeguards).
- Impact: arbitrary file write with the user's privileges — `evil.txt` was created outside the install base with rc=0 (probe `probe_jcm_cli_install_pack_1.py`, RED on these bytes; my RED run additionally created `C:\tmp\evil_posix.txt`, removed).
- Fix: `_member_relative()` (one definition of the prefix strip, used by both loops) + `_member_escapes()` (rejects absolute/anchored remainders and requires `(base/rel).resolve().is_relative_to(base.resolve())`), evaluated in the VALIDATION loop so nothing is extracted before the abort — the sub-agent's snippet put the check inside the extraction loop, which would have aborted mid-install with files already written.

**[MEDIUM] Telemetry ignores `config.jsonc` `share_savings=false` — CONFIRMED — FIXED** - `line 462-463` (pre-fix numbering)
- What: the gate was `os.environ.get("JCODEMUNCH_SHARE_SAVINGS", "1") != "0"` only; a user who opted out the documented way (`jcodemunch-mcp init --share-savings=off`, which writes the config key) still POSTed on every install.
- Fix: `_config.get("share_savings", True)` — identical to the token tracker's gate, so the two telemetry paths can no longer disagree. Precedence is the repo's documented one (config.jsonc wins over the deprecated env var; env still opts out when config is silent — pinned by `test_telemetry_env_opt_out_still_respected`). The sub-agent's proposed "env wins when set" would have INVERTED that precedence; not adopted.
- Verification: probe `probe_jcm_cli_install_pack_2.py` RED → ALL PASS.

**[MEDIUM] No hash/signature verification of the downloaded zip (G17 class) — CONFIRMED as a gap, NOT FIXED here** - `line 316, 377-379`
- Real, but needs a server-side manifest of hashes (the catalog API does not publish any today); a client-only change cannot close it. Left OPEN in this record for a design tranche; the zip-slip fix above removes the worst consequence of a tampered archive.

**[LOW] Whole body / whole members buffered in memory — CONFIRMED, NOT FIXED** - `line 378, 414`. Bounded in practice by pack sizes; a size cap is a one-line follow-up when the catalog exposes sizes.

**[LOW] Non-atomic extraction over a live installed `.db` — CONFIRMED, NOT FIXED** - `line 411-416`. A mid-extraction crash leaves a partial install; the marker is written last so `--force` recovers. Extract-to-temp-then-swap is the proper fix; left open.

## Missing safeguards
- Hash/signature on pack downloads (above).

## Adversarial verification (Phase 3)
- Confirmed the escape on Windows semantics specifically: `Path("/tmp/x").is_absolute()` is False but `.anchor == "\\"`, and `WindowsPath("C:/base") / "/tmp/x" == "C:/tmp/x"` — the `anchor` check is what catches the POSIX-absolute shape; the resolve-containment check catches everything else (drive-absolute, UNC).
- Tried to refute "attacker-controlled archive": the download is HTTPS to a fixed host, so tampering requires a compromised host or MITM; the missing hash check (open MEDIUM) is exactly why that cannot be ruled out. The finding stands as HIGH by impact.
- Checked that legitimate packs are unaffected: `test_clean_pack_still_installs` and the existing install-pack/config suites (603 tests) stay green.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `482508a50445a3dd6dd367996310dff4b3d0a286945bca3b2d3c6b70e5ec1ef0`. TDD: `tests/test_cli_install_pack_safety.py` — the two escape tests and the config-opt-out test RED on the old bytes (rc=0 with the file written outside base; telemetry POSTed), GREEN after; three control tests (clean install, default posts, env opt-out) green throughout.
