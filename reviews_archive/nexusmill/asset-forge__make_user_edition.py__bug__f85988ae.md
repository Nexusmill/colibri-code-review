# BUG review: asset-forge\make_user_edition.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge\make_user_edition.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:08
- tokens: in 2611 / out 1830
- est cost: $0.0353

---

## Verdict
Not safe to ship as-is. The single biggest risk: the tracer-package scrub only deletes `*.py` files, so any non-Python creator secret (key, `.pem`, `.crt`) inside `forge/tracer/` is silently copied into the customer build — exactly what this script exists to prevent.

## Bugs & vulnerabilities
Worst first:

**[CRITICAL] Non-Python files in `forge/tracer/` survive the scrub** - `line 110`
- What: After copying `forge/`, the script deletes only files matching `glob("*.py")` in `DST/forge/tracer/`. Key files, certificates, `.pem`, `.p12`, `.so`, or data files shipped alongside the real tracer modules are left intact and bundled into the end-user edition.
- Trigger: The creator tree's `forge/tracer/` contains any non-`.py` file (very plausible: the docstring mentions a certificate and PKCS#11 hardware, and `creator_cert.pem` is checked only at the *top level* of DST on line 129, not inside `forge/tracer/`).
- Impact: Creator signing keys/certs leak to every customer; the "no creator material" verification at the end still prints success because its filename checks only look at `DST / nono` (top level).
- Fix: `shutil.rmtree(DST / "forge" / "tracer")` before re-creating it with stubs, and extend the leak check to recurse (e.g., `DST.rglob("creator_cert.pem")` / `*.pem` / `*.crt`).

**[HIGH] Crash on missing `templates/index.html` (unhandled exception)** - `line 130`
- What: `read_text` on `DST / "templates" / "index.html"` with no existence check. If `templates` is absent from KEEP (line 97 skips missing entries silently), renamed, or `index.html` doesn't exist, this raises `FileNotFoundError`.
- Trigger: Run in a tree where `templates/` or `index.html` is missing.
- Impact: Build dies after partially writing DST, with a raw traceback and no verification of leaked crypto — the whole point of the final step is skipped. Worse, `sys.exit(1)` never runs so a CI wrapper may treat the traceback differently, but the partially-built folder remains.
- Fix: Guard with `.exists()` and add `index.html` missing to `bad` (a missing UI file is itself a build failure).

**[HIGH] Leak detection is trivially evadable string matching** - `lines 124-127`
- What: The scan greps for literal substrings (`"import PyKCS11"`, `"hazmat"`, ...) in `.py` files only. It misses: `from cryptography import hazmat` variants with different spacing? No — substring works — but it misses `importlib.import_module("PyKCS11")`, base64/encoded payloads, compiled `.pyc`/extension modules (`.pyd`, `.so`) which are never scanned, non-`.py` files containing key material, and crypto usage smuggled in templates/JS (not scanned at all, except 5 hand-picked English strings in `index.html`).
- Trigger: Any of the above present in the source tree.
- Impact: Script prints "Verified: no certificate..." while signing code or keys ship. False confidence.
- Fix: Scan all files (or at least also `.pyc/.pyd/.so/.pem/.key`), ban suspicious binary extensions outright, and treat the string scan as advisory only — combine with a fixed allowlist of expected files in DST.

**[MEDIUM] Silent skip of missing KEEP entries masks an incomplete build** - `lines 96-97`
- What: If `app.py`, `forge/`, or `templates/` is missing, the script prints "(skip, not found)" and continues, producing a broken end-user edition that still "verifies clean".
- Trigger: Running from the wrong directory, or a renamed file.
- Impact: A truncated build ships; no failure is raised since the final check only looks for *forbidden* content, never for *required* content.
- Fix: Maintain a REQUIRED list; abort if any required entry is missing.

**[MEDIUM] Unconditional `rmtree(DST)` destroys a sibling directory without confirmation** - `lines 91-92`
- What: `DST = SRC.parent / "asset-forge-user"` is deleted recursively with no check that it was created by this tool. If a user stores work in `asset-forge-user/`, or an attacker/accident makes it a symlink/junction (on Windows, `rmtree` on a directory symlink fails on some versions but on others can traverse), data loss or unintended deletion follows.
- Trigger: Pre-existing `asset-forge-user/` containing anything else.
- Impact: Irreversible deletion of user data.
- Fix: Verify a marker file (e.g., `.generated-by-make_user_edition`) before `rmtree`, or refuse to delete a DST not previously created by the tool; never follow symlinks (`DST.is_symlink()` check).

**[LOW] Stub `watermark_image` crashes on in-place call** - `line 85`
- What: `shutil.copyfile(in_path, out_path)` raises `SameFileError` when caller passes identical paths (the tracer stub at line 41 guards against exactly this; the watermark stub doesn't).
- Trigger: Shared app code watermarking a file in place.
- Impact: Unhandled exception in the shipped end-user build.
- Fix: Add the same `if str(in_path) != str(out_path)` guard.

**[LOW] Stub API inconsistency: `png_stego.embed_png` doesn't copy the file** - `line 66`
- What: `forge/tracer/__init__.py`'s stub `embed_png` copies input→output (line 40-42), but `forge/tracer/png_stego.py`'s same-named stub returns `{"layers": []}` without writing `out_path`. If the shared app imports `png_stego.embed_png` directly and then reads `out_path`, it gets `FileNotFoundError`.
- Trigger: Code path importing the submodule instead of the package facade.
- Impact: Silent failure / crash in the customer build.
- Fix: Give the submodule stub the same copy semantics, or raise `NotImplementedError` loudly.

## Missing safeguards
- No positive verification that the stubs actually import and satisfy the app's call signatures (a quick `python -c "import forge.tracer"` smoke test against DST).
- No scan of non-`index.html` templates for crypto/verify/watermark UI (only one file, only 5 lowercase English phrases).
- No check for leftover secrets anywhere in DST (recursive scan for `*.pem`, `*.key`, `*.crt`, `*.p12`, `BEGIN ... PRIVATE KEY` in all files).
- `write_text`/`copy2`/`rmtree` calls have no error handling; a permission or disk-full failure leaves a half-built directory that looks complete.
- No test that `DROP_IN_FORGE` actually removed anything — if `skin3d.py` moves location, the `unlink` silently no-ops (`p.exists()` guard hides it).
- Overrides copy (line 118) is non-recursive and doesn't fail if `DST/templates` doesn't exist (`copy2` will raise) — unhandled edge when `templates` was skipped.