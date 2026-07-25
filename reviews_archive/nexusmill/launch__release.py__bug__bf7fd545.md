# BUG review: launch\release.py

- source: `C:\Users\User\source\repos\Nexusmill\launch\release.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:23
- tokens: in 1934 / out 1761
- est cost: $0.0322

---

## Verdict
Not quite safe to ship: the script performs non-atomic, non-transactional writes to files that are deployed live and consumed by running apps, so any mid-run failure leaves a half-released state (version.json bumped, zip not rebuilt) or a truncated version.json. The biggest risk is the lack of atomic writes + rollback across steps 1–3.

## Bugs & vulnerabilities

**[HIGH] Non-atomic write of `website/version.json` (corrupts live update feed)** - `line 78`
- What: `json.dump(data, open(VJSON, "w", ...))` truncates the file in place before writing. A crash, disk-full, or exception (e.g., `KeyboardInterrupt`) mid-write leaves a truncated/invalid JSON file.
- Trigger: any failure between open-for-write and flush completing.
- Impact: the deployed site serves a broken version.json; every running copy's update check fails or (worse) parses garbage. Also note line 79 then appends `"\n"` via a second handle while the line-78 file object is only closed via refcount — flush ordering is an accident of CPython.
- Fix: write to `VJSON + ".tmp"`, `json.dump` + `f.flush()` + `os.fsync()`, then `os.replace(tmp, VJSON)` inside a `with` block; drop the separate append (add the newline inside the same write).

**[HIGH] Partial release with no rollback: version.json is bumped before the zip build** - `lines 72-84`
- What: Step 2 rewrites version.json, and only afterwards step 3 compiles and rebuilds `PatternSkin.zip`. If `py_compile` fails, `os.listdir` on icons raises, or the zip write dies, the live metadata already advertises a version whose artifact doesn't exist / still matches the old zip.
- Trigger: a syntax error introduced into `__init__.py` by step 1 (or any I/O error in `build_ps_zip`).
- Impact: users get an "update available" nudge for a build that was never produced; the repo is left in an inconsistent state (bl_info + version.json bumped, zip stale).
- Fix: build the zip *first* (compile + zip to a temp path), and only after all steps succeed atomically commit all outputs (or write each step to temps and rename at the end); on failure, restore the originals.

**[MEDIUM] Wrong default product URL for `asset_forge`** - `line 76`
- What: `entry.get("url", PRODUCT_URL)` hardcodes the PatternSkin Superhive URL as the default for *both* products.
- Trigger: first-ever release of `asset_forge` (no pre-existing `url` in version.json).
- Impact: version.json points Asset Forge users to the PatternSkin product page; the update nudge links buyers to the wrong product.
- Fix: keep a per-product URL map (`{"pattern_skin": "...", "asset_forge": "..."}`) and use it for the default.

**[MEDIUM] No version monotonicity / drift check — silent downgrade or mismatched bump** - `lines 50-69`
- What: The regex validates only format, never that the new version is greater than the current one in `__init__.py`/version.json, nor that app source and version.json agreed beforehand.
- Trigger: typo like `1.1.0` instead of `1.11.0`, or re-running with an older version.
- Impact: silently publishes a downgrade; running clients on a newer version may never see another nudge (or roll back, depending on the checker's comparison).
- Fix: parse the existing version, compare tuples, and `die()` unless `new > current` (or require an explicit `--allow-downgrade` flag).

**[LOW] Unhandled `os.listdir` on the icons directory** - `line 31`
- What: If `PatternSkin/icons` is missing or unreadable, `os.listdir` raises `FileNotFoundError` with a raw traceback (after version.json was already mutated — compounding the HIGH above).
- Fix: wrap in the same `die()`-style error handling, or `os.path.isdir` check with a clear message.

**[LOW] Zip silently omits expected members** - `line 33`
- What: `members = [f for f in files if os.path.exists(...)]` silently drops `LICENSE`, `NOTICE`, `README.md`, etc. if any is missing, producing an incomplete shipping artifact with no warning.
- Trigger: a renamed/deleted doc file.
- Impact: release zip ships without license/readme; nobody notices.
- Fix: treat the core file list as mandatory — `die()` if any is missing; only icons may be optional.

**[LOW] Bare `open()` without `with` throughout** - `lines 56, 61, 64, 68, 72, 78, 79`
- What: Relies on refcount GC to close/flush; on non-CPython runtimes the read-modify-write of the same path can race its own unclosed handle.
- Fix: use `with open(...) as f:` everywhere.

## Missing safeguards
- Atomic write helper (temp-file + `os.replace` + fsync) used for *all* three mutated files.
- Transaction/rollback semantics: build artifacts first, then flip version metadata last.
- Pre-flight checks: repo clean/dirty state, both version sources currently in sync, new version strictly greater.
- Post-write validation: re-parse version.json and re-`py_compile` the edited `__init__.py` before printing success.
- A test (or at least a `--dry-run`) that runs the whole flow against a temp copy of the tree, plus unit tests for the two `re.sub` patterns against the real files so a format change in `__init__.py` is caught by CI rather than at release time.