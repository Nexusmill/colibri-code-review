# Colibri Review - bug (DELTA + R1 wave) - PatternSkin/accel.py

- **Source path:** `PatternSkin/accel.py` (junction twin `blender_dev/addons/PatternSkin/accel.py`, same bytes)
- **Reviewer:** zcode-glm-5.3 (in-session), Colibri G37 + docs/PERFECTION_PROTOCOL.md v3 L1-L2
- **sha256 reviewed:** `f274a31f...` (post-wave + gate amendment; run started at 3648d067, wave
  intermediate ac4c3560, amendment -> f274a31f; gate clearance gate_20260928-013550 covers the
  staged f274a31f bytes)
- **Date:** 2026-09-28 · **Mode:** bug, stale-file DELTA vs the 2026-09-10 full re-audit
  (2d53847c pre-fix / 3648d067 post-fix record) + this run's R1 wave
- **Context pack:** jCodemunch outline (134 symbols) + `accel.` call-site sweep in
  `__init__.py` (17 sites, incl. private pokes `_SCIPY_OK`/`_WORKER`); 14 remediation rows +
  ACCEL-1 deferred row; Blender 5.1 `bpy/utils/__init__.py` `user_resource` source (static
  trace: "" on makedirs failure / non-dir); tests/test_accel_tiers.py harness; battery
  30/31 baseline (r5 = characterized pip-bpy native flake, no accel frame).

## Fixed since last review
- The 2026-09-10 record's three findings (worker-tier IPC import, token-on-argv, 3x memory
  budget) verified present at 3648d067 (rows PS-ACCEL-IPC-IMPORT / PS-ACCEL-TOKEN-ENV /
  PS-ACCEL-NN-TRANSIENT).

## Verdict
Shippable. The delta (this run's R1 wave, 4 findings + 1 gate catch) is remediated, gated
CLEAR, and battery-covered; everything else holds at the bytes.

## Bugs & vulnerabilities (this run's findings, all remediated in-wave)

**[MED] PS-ACCEL-USERRES-EMPTY** - `finish_pending_installs` / `repair_scipy` / `ensure_dep_path`
- What: `bpy.utils.user_resource` lawfully returns "" (Blender 5.1 source: makedirs failure or
  non-dir). `os.path.join("", "modules")` = "modules" -> pip `--target` resolved against CWD;
  a successful install consumed the user's pending-queue entry while landing where the add-on
  never reads (S2 class). Trigger: locked-down/roaming profile. Impact: silently-lost
  user-requested installs + CWD pollution; repair's glob cleanup could run against CWD paths.
- Fix: guard all 3 sites (COMPLETE sibling ledger). finish: raise into its pre-existing
  except -> absolute ~/.patternskin/lib. repair: same fallback (gate P2 amendment — the first
  draft SKIPPED the repair on ''; gpt-6-luna-pro BLOCK gate_20260928-013315 caught that the
  fallback could complete it; ACCEPTED, amended, G-P2 verdict-named rows RED->GREEN).
  ensure_dep_path: skip the bpy branch.
- Verification: CONFIRMED - static trace (Blender source) + live RED (pip --target 'modules'
  relative on pre-fix bytes) -> GREEN (absolute lib path).

**[LOW] PS-ACCEL-REPAIR-ERR-STALE** - `repair_scipy` tail
- Stale pre-repair `_SCIPY_ERR` suppressed "still fails its import check after install."
  Fix: clear at repair start; the inner redundant `global _SCIPY_ERR` (SyntaxError after the
  new assignment; py_compile caught the first ordering) removed same tranche. RED->GREEN.

**[LOW] PS-ACCEL-WARMUP-FORCEDCPU** - `warmup`
- Imported cupy+torch even when the user forced the CPU tier. Fix: tier check first in _go,
  logs warmup/skipped_forced_cpu. RED->GREEN. (warm_accel_async ADJUDICATED not-same-shaped:
  hardware detection feeds the panel regardless of tier forcing.)

**[LOW] pyflakes dead-code class** - 3x unused local `import subprocess` (probes use
`_retry_run`), unused `global _CAPS` in probe_gpu_stack, unused bare `import mathutils`.
Pure deletions; live siblings kept. pyflakes exit 0 now (was 5 findings).

## Missing safeguards (unchanged / adjudicated)
- last_install_result() dict-copy race: ZERO callers (find_references + search_text) -
  adjudicated unreachable-in-product; revisit if a caller lands.
- pending-installs queue write non-atomic: reader strips/dedups junk (self-healing),
  allowlist-gated, 1-2 lines; tmp+rename adds an equivalent crash window - adjudicated benign.
- ACCEL-1 deferred row (payload cap, error-reply strike, mark_pending non-allowlist) -
  unchanged, commit-gate revisit.

## Adversarial verification pass (refuted this run)
- "probe_scipy's `_SCIPY_BUSY` forward reference is a NameError" - REFUTED: module global
  bound at import; call sites run post-import.
- "F1c passes pre-fix" - the ensure_dep_path RED was accidental (isdir shield on the relative
  'modules'); the REAL F1 RED lives in finish's --target (recorded RED). Post-fix both green.
- "capabilities() blocks the draw path" - REFUTED: rebuild path kicks async probes, never
  runs a subprocess inline (detect_gpus only from background threads).
- Posture-C re-check of the amendment: the lib-fallback glob cleanup patterns
  (scipy*/numpy*) target the PatternSkin-private lib dir - desired rogue-numpy removal, no
  collateral; healthy()'s env includes the target dir (PYTHONPATH set before the check).

## R2/R3 fresh passes at f274a31f (local-zero)
R2 full re-hunt at the post-wave bytes: zero new findings. R3 cache-bypassed fresh sweep
(introduction-class focus on the final diff + amendment): zero new findings. Both passes saw
only the runnable pin map. Local cap not reached (1 remediation wave). Gate: BLOCK P2 ->
amendment -> CLEAR (different-model gate: gpt-6-luna-pro != author GLM-5.3; full credit).
Battery: tests/test_perfection_accel.py 12/12; full suite 32/32 (r5 characterized flake,
intermittent, no accel frame).

---

# E-loop postscript (2026-09-28, appended same run) — final sha8 a298e3d4

Stage E (owner-approved $0.50 cap; actual $0.051 external + ~$0.06 gate):
- E1 blind (gpt-6-luna-pro, $0.012): 3 findings. F1 "worker connects to literal
  [IP_ADDRESS] placeholder" -> REFUTED at the bytes: the source line reads
  create_connection(("127.0.0.1", port), ...); grep NO-MATCH; payloads sha-pinned clean.
  The SAME substitution reproduced across gpt-6-luna-pro x3, qwen3.8-flash x2 (incl. a
  de-primed clean adjudication) and the kimi-k2 cold pass = a review-TRANSPORT artifact
  (IP literals presenting as [IP_ADDRESS] to reviewers on this stack). Documented; the
  refutation evidence (adj2 payload sha f8b6c577 + verbatim line) is in the run dir.
  LESSON for future runs: never put the denied token in rebuttal prose (my reconcile
  text poisoned e2/e3/e5 - leading the witness), and expect IP-literal->placeholder
  substitution from reviewers; Phase-3 byte checks settle it.
- F2 "diagnostics() blocks UI via detect_gpus" -> ADJUDICATED deferred-LOW (zero
  production callers; operator-only when wired; detect_gpus docstring mandates
  off-UI-thread).
- F3 "gpu_healthy false-positive on silent CPU fallback" -> CONFIRMED, fixed, then
  hardened through 5 more REAL gate catches: test-env determinism (meta-path blocker),
  stranded-KICKED lost update, check-then-act TOCTOU, mid-rebuild stale republish
  (generation-stamped publication, _CAPS_GEN), numerical-branch sibling. Round 8
  (busy-branch) ADJUDICATED and the gate ACCEPTED: the GPU-stack cache's contract is
  INSTALLED-ness (subprocess probe; dep_status/tech_status consumers); runtime health is
  per-operation fallback by design rule #2 - the layers are separate on purpose.
- Cold pass (kimi-k2-0905, $0.017, terse mandate, no ceilings): 1 finding = the
  transport artifact (refuted above); 2 busy-flag check-then-set races self-assessed
  below-MED -> adjudicated LOW-deferred (duplicate-probe waste only, pre-existing).
- Terminal: D2-zero at a298e3d4 (no CONFIRMED MED+ open; every LOW pinned, adjudicated
  or deferred-rowed). Battery 20/20 rows; suite 32/32 except the characterized r5
  pip-bpy native flake; twin byte-identical throughout; 6 productive external
  dispatches, $0.051 of the $0.50 cap.
