# Colibri Review - bug (FULL re-audit) - PatternSkin/accel_bootstrap.py

- **Source path:** `PatternSkin/accel_bootstrap.py`
- **Reviewer:** claude-fable-5-1 (in-session fork), Colibri G37 protocol, campaign item 1 (product cores), rank 46
- **sha256 reviewed:** `21afa6a59c6644ba437a5b9fcc5a7914200df2278f4ac8c37b286beb5617f533` (sha8 `21afa6a5`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-06 review, the 08-15 GLM-AB pass and this morning's delta are claims to re-verify, not a baseline)
- **Context pack:** all 865 lines read; the only importer is `__init__.py` (`PATTERNSKIN_OT_install_ml_worker` invoke/execute/`_work`/`_finish`/`cancel` at 3034-3219 and the panel's `_accel_btn` block at 6046-6063, both read); remediation row PS-PARTIAL-ORPHAN-SWEEP, dockets GLM-AB, DRV-DATE-VER-1, KV-PS-CRYPTO-1, PSK-16; `gpu_accel_manifest.json` (one tier, six artifacts, every sha256 and byte count pinned, python standalone pinned); `accel.py`'s in-process pip path (lines 247-249, 444-448: `--no-deps --only-binary=:all:` + find-links) for the "hardened-index path" the docstring cites.

## Verdict
Two CONFIRMED defects reproduced RED (a lock-reclaim race that lets two installers run on one venv; a hard-link escape in the tar guard that overwrote a file outside the destination on this machine) plus one CONFIRMED G17 doctrine gap best docketed (the pinned wheel's transitive dependencies resolve unpinned from PyPI). The GLM-AB state machine otherwise holds; the download path verifies before it trusts.

## Bugs & vulnerabilities

**[MEDIUM] Stale-lock reclaim is stat-then-remove: two waiters can both reclaim and both run the install** - `acquire_lock`, `lines 105-116`
- What: a waiter that finds the lock stale removes it and creates its own. A second waiter that evaluated `_lock_is_stale` before the first's remove+create then removes the FIRST waiter's fresh lock (nothing re-checks what is being deleted) and creates its own - two holders.
- Trigger: a crashed holder's lock older than `stale_after` (1 h) plus two Blender instances (or a re-clicked install after a force-cancel, the case the operator's docstring describes) polling it; the window is the first waiter's remove-to-create interval against the second's stat-to-remove.
- Impact: two `bootstrap_ml_venv` bodies on one venv - `create_venv` wipes the other's half-built venv, both download into `DOWNLOAD_DIR` (per-process partials keep the bytes honest, the venv is not protected), `.ready` may be written over a venv the other process is still populating. The same "two writers on one venv" class GLM-AB #2 closed for the heartbeat path.
- Fix: reclaim by RENAME to a private name (`<lock>.reclaim.<pid>`; only one rename can win), then re-check the age of the file now exclusively owned: stale -> remove it and retry the create; fresh (a live holder recreated it in the window) -> rename it back and fall through to the deadline wait. `os.replace` failing (pinned by AV) keeps GLM-AB #1's fall-through. Probe `reaudit/probe_ps_accel_bootstrap_1.py`: `AB_reclaim_never_steals_fresh_lock` RED on the current bytes (acquired by deleting the fresh lock), GREEN on the patched copy; `AB_stale_lock_still_reclaimed` GREEN both; `glm_ab_lock.py` (9 checks) and `sweep_accel_bootstrap_r3.py` unchanged GREEN against the patched copy.
- Verification: CONFIRMED (deterministic reproduction of the interleaving from the second waiter's view).

**[MEDIUM, latent in product flow] `_safe_extract` resolves a HARD link's target relative to the member's directory; tarfile resolves it relative to the extraction root - an escaping link passes the guard and a later member writes through it onto a file outside dest** - `_safe_extract`, `lines 376-380`
- What: `link_target = join(dirname(target), m.linkname)` is the symlink rule. For a hard link tarfile uses `_link_target = join(dest, linkname)`. Member `a/b/c` with linkname `../../victim` passes (dest/a/b/../../victim is inside dest) while tarfile links dest/../../victim; the following regular member `a/b/c` is opened `wb` through the link.
- Trigger: a crafted archive. Today's only input is the sha256-pinned python-build-standalone tarball, so this is unreachable in the shipped flow - but the docstring promises exactly this protection for the helper's reuse "against something less trusted", and the promise is false.
- Impact: reproduced on this machine (NTFS hard links): a file two directories above the destination was overwritten with archive content; `extractall` runs with no filter, so the stdlib does not catch it either.
- Fix: resolve hard-link targets against `dest_abs`, symlinks against the member's directory; extract with `filter="data"` (3.12+ and the 3.11.4+ backports - Blender 5.1 is 3.13) falling back to the bare call on a `TypeError`; convert `tarfile.TarError` (a `FilterError` or a corrupt member) into `BootstrapError` to keep the documented contract. Probe `reaudit/probe_ps_accel_bootstrap_2.py`: `AB_hardlink_cannot_escape_dest` RED (victim overwritten) -> GREEN on the patched copy (refused, victim intact); `AB_ordinary_archive_extracts` (dirs, files, an in-tree hard link) GREEN both.
- Verification: CONFIRMED (reproduced; the real archive was NOT re-downloaded to test the `data` filter against it - the probe's ordinary archive stands in; the lead may want one download-and-extract run before landing).

**[MEDIUM, doctrine G17 - DOCKET, do not blind-fix] The hash-verified wheel's transitive dependencies are resolved UNPINNED from PyPI at install time** - `install_pinned_wheel`, `line 634` (`pip install --no-cache-dir <wheel>` - no `--no-deps`, no constraints, no `--require-hashes`)
- What: the six artifacts are pinned and verified, but `pip install torch-2.9.1+rocm...whl` pulls torch's dependency tree (sympy, networkx, jinja2, fsspec, filelock, typing-extensions, numpy, ...) at whatever versions PyPI serves that day, with no hash check. The docstring says so ("resolve normally through pip's default index") and cites the in-process path as precedent - but that path (`accel.py` 247-249) runs `--no-deps --only-binary=:all:` with a find-links dir; the venv path has neither.
- Trigger: every install of the AMD worker tier.
- Impact: a non-reproducible worker venv on the customer's machine; an upstream breaking or compromised release of any transitive dependency lands in the venv the geometry worker runs. G17: "Bundled models/deps pinned + hash-verified against a manifest ... never auto-pull latest."
- Fix: DOCKET (the SP-BUILD-PINS shape): generate a constraints file with hashes from one known-good resolve of the pinned wheels (`pip install --dry-run --report` or `pip freeze` in a green venv), ship it beside `gpu_accel_manifest.json`, install with `-c <constraints> --require-hashes`. Not done here - the resolved set is only knowable from a real install of the 2 GB tier, and a blind `--no-deps` would break torch at import.
- Verification: CONFIRMED by the literal command line and the manifest's artifact list (no dependency artifacts).

## Missing safeguards (not fixed)
- `system_python312` never checks that the found interpreter is 64-bit; a 32-bit CPython 3.12 passes the version probe, the venv builds, and pip refuses the win_amd64 wheels only after the multi-GB download (`import struct; struct.calcsize('P') == 8` in the probe script would close it).
- Cancel (`cancel_event`) is honoured between artifacts and between chunks, never inside `install_pinned_wheel` (up to 30 min of pip) or `create_venv`; Esc during pip waits for pip.
- `download_and_verify` follows redirects silently, including https -> http; the hash pin makes this an integrity non-issue, but a manifest URL that starts redirecting would download over plaintext.
- `check_driver`'s date-form versions (DRV-DATE-VER-1) remain open as docketed.
- Cross-file, outside this unit: the panel's draw block (`__init__.py` 6058) calls `load_manifest()` - a disk read + JSON parse - on every redraw when an AMD-without-DirectML machine has no worker yet; the rank-1 reviewer owns draw().

## Adversarial verification pass
- "A `sha256: ''` (empty string) artifact would download in full and then fail the mismatch in capture mode": the manifest carries no such value (all six pinned; unpinned would be absent/null per `tier_installable`), and a missing pin refuses up front - refuted as a live defect, noted as fragile (`sha256_hex is None` vs falsy).
- "`os.replace(partial, dest)` clobbers a concurrent process's verified file": both processes verified the same pinned bytes; the replace is atomic and content-identical - refuted.
- "The heartbeat thread keeps Blender alive on quit": `daemon=True` and joined 2 s in the finally - refuted.
- "`tier_installable` in `draw()` does network": it reads dict keys only; `load_manifest` is the disk read noted above - refuted for G20.
- "`verify_authenticode` interpolates a user path into PowerShell": GLM-AB #4 moved it to an env var; verified at the bytes - refuted.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `fdbc5b143baa4f51b981c6d880c1aa71696d2c4a3395cf1bab57b754cb6f70de`. Rows PS-AB-LOCK-RECLAIM-RACE, PS-AB-TAR-HARDLINK in `docs/remediation_manifest.json`, same commit.

