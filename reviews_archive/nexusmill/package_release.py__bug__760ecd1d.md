# BUG review: package_release.py

- source: `C:\Users\User\source\repos\Nexusmill\package_release.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:59
- tokens: in 1132 / out 1530
- est cost: $0.0263

---

## Verdict
Ship-able as an internal developer tool, but not robust: the zip step packages the **entire** PatternSkin directory verbatim (including symlinks, hidden files, and any stray secrets), and the staging step can silently leave a stale or half-copied bundle. Biggest risk: unintended files (credentials, local artifacts, symlink targets outside the tree) shipping in the release zip.

## Bugs & vulnerabilities

**[HIGH] Release zip includes every file under PatternSkin/ — secrets, OS junk, editor files** - `lines 45-51`
- What: `os.walk(PS)` only excludes `__pycache__` dirs and `.pyc` files. Everything else — `.env`, `.gitignore`'d-but-present files, `.DS_Store`, `Thumbs.db`, `*.log`, test fixtures, API keys — goes into the shipped zip.
- Trigger: any developer leaving a config/credential/log file anywhere under `PatternSkin/` before running the script.
- Impact: secrets or internal artifacts silently distributed to buyers.
- Fix: build an explicit allowlist (e.g., only `*.py`, `asset_forge/**`, manifest files), or assert on a file list before zipping and fail on unexpected entries.

**[HIGH] Symlink following leaks files outside the tree into the zip** - `lines 50-51`
- What: `os.walk` lists symlinked files, and `z.write(fp, ...)` reads the symlink *target*. `shutil.copytree` at line 33 (default `symlinks=False`) similarly dereferences symlinks when staging the build output.
- Trigger: a symlink inside `PatternSkin/` (or inside `dist/AssetForge`) pointing to an absolute/outside path — accidental, or planted via a malicious checkout/build tool.
- Impact: arbitrary files outside the project get bundled and published (path-traversal-style exfiltration into the artifact).
- Fix: skip symlinks (`fp.is_symlink()` check) and pass `symlinks=True` to `copytree`, or explicitly resolve and verify `fp.resolve().is_relative_to(PS)`.

**[MEDIUM] `rmtree(..., ignore_errors=True)` hides locked-file failures; copytree then blows up or stages stale content** - `lines 32-33`
- What: On Windows, AV scans or a running AssetForge.exe commonly lock files, so `rmtree` partially fails — silently. Then `copytree(forge_out, bundle)` hits an existing directory and raises `FileExistsError` (Python ≥3.8 default `dirs_exist_ok=False`), or worse, merges new files over leftover old ones if that default changes.
- Trigger: any lingering handle inside `PatternSkin/asset_forge/`.
- Impact: either a confusing crash or a bundle mixing old/new binaries that ships broken.
- Fix: remove `ignore_errors=True`, catch `OSError` with a clear message ("close AssetForge.exe / disable AV"), and use `dirs_exist_ok=True` only deliberately.

**[MEDIUM] Staging mutates the source tree and is not cleaned up / not atomic** - `lines 31-33`
- What: the built binary tree is copied *into* the source add-on directory permanently. If the script fails after line 32 (e.g., copytree crash), the repo is left with a deleted or half-written `asset_forge/`, and subsequent zips (or a manual zip by the dev) contain the corrupt state.
- Trigger: any exception between lines 32 and 52.
- Impact: inconsistent repo state; a later packaging run may zip a partial bundle without noticing.
- Fix: stage into a temp dir (`tempfile.TemporaryDirectory`) and zip from there, or verify integrity (e.g., re-check `AssetForge.exe` exists) before zipping.

**[LOW] Timestamp-derived "version" is not a version** - `lines 35-36`
- What: `_ver` is `datetime.now()` — two builds a minute apart get different "versions" of identical code, and there's no relation to any real release tag. It also makes builds non-reproducible.
- Fix: derive from a git tag / explicit version file; at minimum log the source commit alongside it.

**[LOW] No exclusion of `release/` or nested build dirs if they ever live under `PS/`** - `line 45`
- What: today `REL` is a sibling, but the walk has no guard against recursively including an output zip or build scratch dir placed under `PS/` — the zip could contain a previous copy of itself.
- Fix: assert `fp` is not under `REL`, or keep the allowlist approach above.

## Missing safeguards
- No validation that `forge_out` actually contains `AssetForge.exe` — only the directory existence is checked (line 27); an empty/partial PyInstaller output passes.
- No error handling around the zip: if `z.write` fails mid-way, a truncated zip remains on disk and the script crashes without removing it.
- No post-build verification (e.g., unzip and confirm `PatternSkin/asset_forge/AssetForge.exe` and `VERSION` exist, or smoke-run the exe with `--version`).
- No test or dry-run mode; a `--check` flag listing what *would* be zipped would catch the secret-inclusion risk.
- `run()` prints args but has no timeout; a hung PyInstaller build hangs the release indefinitely.
- `REL.mkdir(exist_ok=True)` without `parents=True` — fine today, but brittle if `REL` is ever nested.