# colibri-review — PatternSkin/__init__.py — bug (DELTA, hunt round 1)

- **Source:** PatternSkin/__init__.py · **Model:** claude-opus-4-8[1m] (in-session, max) · cost $0.00
- **sha256 reviewed:** 53817d4ec763acab83d721c89a764c8fb162a1f12c20a05cb9da3cae54b65528 (321 KB / 6111 lines)
- **Date:** 2026-07-23 · **Mode:** bug · **DELTA** against `PatternSkin____init__.py__bug__c0972561.md`
- **Delta scope:** the reviewed bytes of the prior review are commit `a73cfa5`; this pass reviews
  `a73cfa5..HEAD` = **394 insertions / 17 deletions across ~35 hunks** (commits 4e92bd1, 8ddc88b,
  ac6cc70, edaa4d4). Unchanged code was NOT re-litigated — the prior review stands for it.
- **Context pack:** hunt plan + refuted ledger (`tools/colibri_hunt.ps1 -Load`); 14 remediation rows
  touching this file (PSK-9/10/11, the SVG/XXE cluster, the pip-deadlock fix) — all verified closed
  and excluded up front; `_check_update`/`PS_VERSION_URL` constant; `ai_parts.mesh_signature`,
  `_partial_path`, `save_scan_partial`, `load_scan_partial` for the new resume path; the
  `_classes` registration tuple. Current on-disk bytes re-hashed at dispatch (G36).

## Verdict
The delta's risk is concentrated in one feature: **one-click self-update**, which downloads and
installs code over the paid add-on. Its network layer is genuinely careful — https-only, host
pinned to `downloads.nexusmill.com`, redirects refused, size-capped, sha256 verified before use,
staged-zip version cross-checked before install. The **install step** was not held to the same
standard: it overwrote files in place with no atomicity and no rollback, so a single locked file
left a half-updated add-on. Five defects confirmed, all fixed; two candidate findings refuted.

## Bugs & vulnerabilities

**[HIGH] Self-update overwrites in place with no rollback — a locked file leaves a mixed-version add-on** - `_self_update_worker`, install loop
- **What:** the loop copied every file with `shutil.copyfile(sp_, dp)`, appending failures to
  `failed`, and raised only AFTER the loop finished. Files copied before the failure were already
  overwritten. No backup existed, so nothing could be restored, and the error text —
  *"N file(s) locked … restart Blender and retry"* — implied nothing had been changed.
- **Trigger:** any `OSError` mid-loop: a Windows file lock (AV scanner, OneDrive, an open editor),
  a read-only file, a permission error on a shared install, or a full disk. The code already
  anticipated locking, so the author considered it reachable.
- **Impact:** the paid product is left with some modules at the new version and some at the old —
  import errors or silent version-skew — with no recovery path but a manual reinstall.
  `shutil.copyfile` is also non-atomic per file, so an interrupted write leaves a **truncated .py**
  that cannot be imported at all.
- **Verified CONFIRMED by execution** against the pre-fix bytes: with one of three files locked,
  the add-on directory ended as `['NEW', 'OLD', 'NEW']`.
- **Fixed:** two-phase install — phase 1 proves every destination writable before anything is
  touched; phase 2 stages each file beside its target, keeps a `.psbak`, and `os.replace()`s it in
  atomically, rolling every applied file back on any failure. Post-fix the same scenario leaves
  `['OLD','OLD','OLD']` and reports "Nothing was changed."

**[MEDIUM] `_safe_extract_zip` skipped unsafe members instead of refusing the archive** - traversal guard
- **What:** members escaping the target dir (or on another drive) hit `continue` — silently
  dropped. A security control that fails *open* into a partial extraction: the staged tree then
  passes the version check (it only reads `PatternSkin/__init__.py`) and installs with files
  missing.
- **Trigger:** requires a malformed/hostile zip, which the sha256 pin makes remote — this is
  defence-in-depth, not an open door. Reported because a guard that degrades silently is a real
  weakness, not a style point.
- **Fixed:** raises `RuntimeError` naming the offending member. Verified: a `../escaped.py` member
  now aborts and writes nothing outside the target.

**[MEDIUM] Paid AI-scan resume ignores the object TRANSFORM — silently mixes votes from two orientations** - `ai_parts.load_scan_partial` / `save_scan_partial` (cross-file; introduced by this delta's resume feature)
- **What:** the checkpoint is keyed by `mesh_signature(obj)`, which hashes **local-space** vertex
  data only (counts, rounded bbox, sampled digest) — `obj.matrix_world` is not in it. But
  `load_scan_partial` re-derives the fibonacci cameras from **world-space** positions of the
  current transform. Rotating or scaling the object between a crashed scan and its resume keeps
  the key identical while the cameras move.
- **Trigger:** start a paid scan → it fails/cancels at view k → rotate or scale the object → re-run.
  The caller (`PATTERNSKIN_OT_ai_parts.execute`) validates only `n_views` and `deep`.
- **Impact:** views `0..k-1` voted under the old orientation, views `k..n` under the new one; the
  vote table finalises into a wrong part segmentation. Silent, on a feature that spends the user's
  money, and the UI states "earlier views already paid" — reinforcing trust in the result.
  Translation alone is safe (cameras follow the centroid); rotation and scale are not.
- **Fixed:** the checkpoint stores `matrix_world` (`version=2`) and the loader returns `None` on
  mismatch, falling back to a fresh scan. v1 checkpoints have no key and also fall back.

**[MEDIUM] Fixed, predictable temp paths for both downloaded zips** - `_self_update_worker`, `_auto_upgrade_companions`
- **What:** `os.path.join(tempfile.gettempdir(), "ps_self_update.zip")` (and `ps_spector_update.zip`)
  — a constant name in a shared directory, opened `"wb"`, which follows symlinks.
- **Trigger:** on Linux/macOS `/tmp` is world-writable, so another local user can pre-create the
  path as a symlink and have the download overwrite an arbitrary file the user can write. Two
  clicks of "Update now" also collide on the same file, and one thread's `finally: os.remove(tmp)`
  can delete the other's download mid-flight.
- **Fixed:** `tempfile.mkstemp()` for both, unique per run and created 0600.

**[LOW] `PATTERNSKIN_OT_self_update.execute` crashes when called from a script** - operator
- **What:** `execute` read `self._info`, which only `invoke` sets. `bpy.ops.patternskin.self_update()`
  (EXEC_DEFAULT) skips `invoke` → `AttributeError` instead of a reported error.
- **Fixed:** `execute` falls back to `_UPDATE` / `_check_update()` and reports cleanly when no
  verified update is available.

## Missing safeguards
- `_forge_copy_install` runs `robocopy /MIR`, which **deletes** anything in the installed Asset
  Forge directory that is not in the bundle — now reached automatically by the companion
  auto-upgrade rather than only by an explicit install click. Guarded by a version comparison, so
  not a live defect, but a mirror-delete on an auto path deserves an explicit note in the confirm
  dialog. Recorded, not fixed.
- Nothing prevents two concurrent self-updates (the `mkstemp` fix removes the file collision, but
  two threads can still install simultaneously). A module-level "in progress" flag would close it.
- `_SELF_UPDATE["cancel"]` is honoured only inside the download loop; Esc during install/stage does
  nothing, which is correct but undocumented in the UI text.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- *"The sha256 pin arrives over an unauthenticated channel"* — `PS_VERSION_URL` is the hardcoded
  constant `https://nexusmill.com/version.json`; TLS with default cert validation. An origin
  compromise defeats any client-side check anyway.
- *"Resume reuses stale mesh geometry after the user edits the mesh"* — `mesh_signature` includes a
  sampled-vertex digest, so any edit changes the key and the checkpoint is simply not found. Only
  the **transform** variant is real (confirmed above).
