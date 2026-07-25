# colibri-review — asset-forge/forge/bundle.py — bug (hunt round 1, effort=mid) [+ twin]

- **Source:** asset-forge/forge/bundle.py (byte-identical twin, G23) · **Scanner:** general-purpose
  subagent @ claude-sonnet (mid) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3)
- **sha256 reviewed:** df4557bd25641a7256892a334fc93ee557fbdd3b4b23a679a64df65cb9c7d580 · **post-fix:** 1191e93d
- **Date:** 2026-07-24 · **Mode:** bug · round 1. First review of this unit. Prior remediation rows:
  AF-1 ref-uri hardening, provider-result type-guard, reproducible-recipe/temp-leak/INCOMPLETE, SSRF+
  out_dir-traversal (verified-stale). Callers: `app.py:713` (`_run_bundle`, try/except-wrapped) and
  `gen_bundle.py:61` (CLI, **no wrapper**).

## Verdict
One real gap fixed. The generation loop is well-hardened (INCOMPLETE.txt on any failure), but the
~50 lines of setup before the try — buyer/recipe/base_seed shape, `ReplicateProvider(model)` — ran
after `out.mkdir` and outside that net, so bad input left an orphaned, unmarked output dir.

## Bugs & vulnerabilities (CONFIRMED, fixed)
**[MEDIUM] Unvalidated setup inputs crash after `out.mkdir`, before the INCOMPLETE.txt net** - `build_bundle:47-99`
- What/Trigger/Impact/Fix: a malformed `buyer` (not a dict), `recipe` missing `theme`/`items`, or a
  non-numeric `base_seed` crashed (`AttributeError`/`KeyError`/`ValueError`) with `out_dir` already
  created and holding neither a manifest nor `INCOMPLETE.txt`. `app.py::_run_bundle` wraps it (job
  status=error), but `gen_bundle.py` (CLI) gives a raw traceback + a bare unmarked dir. Fixed by
  moving shape validation to the top of `build_bundle`, before `out.mkdir`, mirroring
  `pipeline.generate_set`. **Verified:** pre-fix a bad recipe/base_seed left an orphaned dir; post-fix
  all bad-input cases raise `ValueError` before mkdir and leave no dir (junk/_bundle_test.py 6/6,
  pre-fix 1/6). Validation-only path — no generation, no cost.

## Checked hypothesis (refuted — recorded)
- *"`manifest['signing']` set unconditionally even when nothing is signed (the pipeline.py pattern)"*
  — does NOT apply to bundle.py: the `body`/sign block runs **unconditionally** for every bundle
  (no `is_sale`-style gate), so `signing` and `manifest_signature` are always consistent. Not a bug.

## Refuted (recorded)
- ref_image_uri SSRF/LFI — `data:`-only guard present + `ReplicateProvider` host allowlist; adjudicated
  verified-stale, still true.
- `out_dir` traversal — built by the caller as `OUTPUT / f"bundle_{slug}_…"` with `slug` isalnum-filtered.
- `provider.generate` result untyped — already guarded (`if not isinstance(gen, dict): raise`).
- `regen_from_recipe` recipe_path traversal — only reachable via the local operator CLI, not a web route.

## Missing safeguard (noted, not fixed)
- **[LOW/PLAUSIBLE] Predictable temp name** `_af_raw_{set_id}_{i}.png` in shared tempdir (`build_bundle:106`)
  — TOCTOU on the pre-watermark raw image; low (single-user desktop). Candidate for a `mkstemp` pass
  (same class as other predictable-temp fixes). Left for a later round.
