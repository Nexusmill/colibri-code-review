Source: PatternSkin/accel_bootstrap.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 2eeb03329d8c021f734efa319346e3e17c165961abe79853308726e000995e28
Date: 2026-08-06
Mode: bug (DELTA re-review; prior review a9a4aedd was orphaned from .colibri_reviews/_hunt_plan.json
even though its 4 findings WERE fixed same-day, commit bughunt-concurrency-fix)
Context pack: full 794-line file read; find_importers/search_text confirmed the only caller is
PatternSkin/__init__.py's PATTERNSKIN_OT_install_ml_worker (no other importers); cross-read
docs/remediation_manifest.json (confirmed the 07-27 HIGH/HIGH/MEDIUM/MEDIUM concurrency findings
are logged status:"fixed" at commit bughunt-concurrency-fix) and docs/deferred_manifest.json
(ACCEL-1 is about accel.py's k>m divergence, unrelated to this file's remaining surface); manifest
cache entry for this file (sha a9a4aedd) was stale vs current disk bytes (2eeb0332) - treated as a
full re-review rather than trusting the cache, per G36.

## Verdict
Shippable. All four 07-27 concurrency/integrity findings are present and correctly implemented in
the current bytes (ensure_python312's own lock + re-check-inside-lock, the heartbeat thread, the
cancel_event checks, the cached-archive re-hash). No new CONFIRMED defect survived adversarial
verification in the untouched surface (download_and_verify, verify_authenticode, _safe_extract,
install_pinned_wheel, gpu_self_test, tier_installable, the bootstrap_ml_venv main flow).

## Bugs & vulnerabilities
None confirmed this pass.

Candidates traced and REFUTED / downgraded below verification threshold:
- download_and_verify() never asserts the manifest URL's scheme is https:// before calling
  urllib.request.urlopen(). Traced impact: for the customer (pinned) path this is a non-issue --
  sha256 is verified regardless of transport, so a tampered-in-transit download simply fails the
  hash check and is deleted, never installed. For capture mode (CAPTURE_ENV, creator-only, not a
  customer path) an unpinned download's only guard is the ADVISORY (by this file's own documented
  design, see TRUSTED_PUBLISHERS comment) Authenticode check plus manual human review before a
  capture is ever promoted into the manifest (_record_capture's docstring: "a pin is a commit").
  No live exploit path against a shipped build. Not reported as a finding.
- os.replace(staging, install_dir) after shutil.rmtree(install_dir, ignore_errors=True): if the
  rmtree silently fails to fully clear install_dir (locked file), Windows' directory-replace can
  raise a bare OSError instead of the module's own BootstrapError. Traced: this still fails LOUD
  (caught by the enclosing except Exception -> re-raise after cleaning staging), so no corruption,
  just a slightly less-typed exception surfacing to the caller. Cosmetic; not reported.

## Missing safeguards
- _record_capture() does non-atomic read-modify-write on CAPTURE_OUT with no locking (carried
  forward from the 07-27 review; still low severity, still a manual single-operator dev workflow).
