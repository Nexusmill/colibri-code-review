# Debug: "override fields still have def in them" (Asset Forge library) — 2026-07-23

Mode: debug (colibri-review Phase D) · Reporter: Damien · Reviewer: Claude Fable (Cowork session)

## Failure signal (captured, not assumed)
`%LOCALAPPDATA%\Programs\Asset Forge\_internal\templates\library.html` L146:
`<input class="ct" type="number" min="0" placeholder="def" title="images/type override">`
Same stale bytes in the addon-bundled copy:
`%APPDATA%\Blender Foundation\Blender\5.1\scripts\addons\PatternSkin\asset_forge\_internal\templates\library.html`
Both files LastWriteTime 2026-06-27 22:39.

## Root cause
NOT a code regression. The repo fix IS in place (both editions, twins identical:
`asset-forge/templates/library.html` + `asset-forge-user/...` L146 `placeholder="auto"`).
The two INSTALLED copies are from a 2026-06-27 PyInstaller build and were never
updated — deployment staleness, the app-bundle sibling of the known "Blender 5.1
addon is a COPY, re-sync after edits" hazard.

## Fix applied (minimal, at the root)
Copied current `asset-forge-user/templates/*.html` into both installed
`_internal/templates` dirs; verified Get-FileHash equality repo==installed for
library.html + index.html, and zero `placeholder="def"` matches remain.
User action: restart Asset Forge / hard-refresh (pywebview may cache).

## ⚠️ Residual risk (flagged, not fixed here)
The installed app bundles are WHOLLY from 6/27 — the packaged Python code misses
~a month of fixes (incl. money-safety: replicate_flux create-once/poll-refetch
glm20-7, library_gen count clamp + 401 fast-fail, secrets/library hardening).
Template sync fixes only the visible symptom. Proper fix: rebuild + reinstall the
bundled app (make_user_edition → package → "Update Asset Forge" flow) or add a
build-freshness check. Decision left to owner.
