<!-- source: asset-forge 2-HC tail (imagegen/config.py, userlib.py, tracer/config.py, bundle.py, imagegen/prompts.py) | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | 2026-07-22 | mode: bug | context pack: jcodemunch (SECRET_KEYS, callers, twin/WHITELIST status), secrets.py af-secrets-robustness pattern, prior GLM 2026-07-19 + AF-1 adjudications -->

## Verdict
5 files. THREE real (small) fixes shipped, TWO stale/refuted. Recurring genuine class:
empty-`ASSET_FORGE_HOME` -> cwd (already fixed in secrets.py; still open in two more modules).

## imagegen/config.py (twin byte-identical, both fixed)
- **[LOW->real, fixed] empty ASSET_FORGE_HOME resolves to cwd (line 8).** `os.environ.get(k, default)`
  returns "" when the var is set-but-empty; `Path("")`==cwd -> providers.env/settings.json read+written
  in the launch dir. Same class as secrets.py (af-secrets-robustness) which uses `or`. FIX: `... or (Path.home()/".asset-forge")`. Verified empty-HOME no longer == cwd.
- **[MEDIUM->real, fixed] newline injection in save_provider (52,56).** providers.env is line-oriented;
  a value with `\n` writes a second `KEY=VALUE` line (only reachable for the one non-secret key GROQ_MODEL
  - secrets route to the encrypted store and return early; SECRET_KEYS = REPLICATE/GROQ_API_KEY/HF_TOKEN).
  Self-inflicted on a single-user tool, but trivially hardened: strip `\r`/`\n` from value. Verified the
  injected `REPLICATE_API_TOKEN=evil` stays on one GROQ_MODEL line.
- **[HIGH-claimed, ACCEPTED-by-design] silent secret-load swallow (30).** The `except Exception: pass`
  around migrate_legacy+secret_get is deliberate: a momentary keychain hiccup must not brick load_providers;
  plaintext providers.env + real env vars remain the fallback, and a missing token surfaces as a Replicate
  401 at call time (not silent in effect). Not fixed.

## userlib.py (twin byte-identical, both fixed)
- **[HIGH-claimed CRITICAL refuted / real HIGH found] non-UTF-8 filename crash (_id, 19).** The "multi-user
  _INDEX data leak" CRITICAL is refuted (AF is single-user localhost; _INDEX is a per-list ephemeral id->path
  map, no cross-user surface). BUT `rel.encode()` (utf-8) RAISES UnicodeEncodeError on the surrogate-escaped
  str that rglob yields for a non-UTF-8 filename on Mac/Linux -> the ENTIRE library listing 500s for a
  shipped end-user. FIX: `.encode("utf-8","surrogatepass")` (ids are one-way, never decoded). Reproduced the
  crash + verified the fix.
- **[MEDIUM->real, fixed] reference_data_uri missing try/except (68-70).** Its sibling thumb_uri guards
  data_uri; reference_data_uri did not, so a corrupt/oversized user reference image 500s the generate route.
  FIX: same try/except -> None. Verified.
- **[MEDIUM refuted] relative-path-after-cwd-change:** real callers pass ABSOLUTE roots (config.library_dir()
  is absolute), so p is absolute. Not fixed (no reachable trigger).

## tracer/config.py (creator-only, user twin = crypto-free stub; WHITELIST divergence, only creator fixed)
- **[MEDIUM->real, fixed] empty ASSET_FORGE_HOME -> cwd (21).** Same class fix as above.
- **[CRITICAL-claimed -> real-smell, hardened] cwd-first cert search (26).** The cert is PUBLIC (signing uses
  the PIV hardware key, not this file) so a planted cwd cert cannot forge - worst case it breaks the creator's
  OWN manifest verification (self-DoS, requires running from a hostile dir). Reordered so install-dir + HOME
  are checked BEFORE cwd (cwd last, least trusted); doesn't break the legit drop-cert-next-to-app flow.
- **[HIGH TOCTOU + LOW unhandled-IO, both closed] load_cert_pem.** Wrapped the read in try/except OSError ->
  None: closes the exists()->read window and the raw-IOError crash in one change.

## bundle.py — VERIFIED STALE (already remediated)
- ref_image_uri SSRF/arbitrary-read (122,208): the AF-1 fix is PRESENT (line 69-70: any non-`data:` uri ->
  None before it ever reaches Replicate). out_dir traversal (43): out_dir is server-constructed (app builds
  OUTPUT/name), same refutation as generate_set; creator/local. temp-file + signing-downgrade: minor, bundle
  already remediated (2b4d85b). No new fix.

## imagegen/prompts.py — VERIFIED STALE (prior adjudication 2026-07-19)
- None-theme AttributeError + non-int seed + parse nits: already adjudicated in the GLM fresh sweep as
  no-privilege-boundary robustness on a single-user tool where you supply your own theme (the route requires
  theme). Prior decision stands; re-flag. No new fix.
