# Colibri bug-hunt synthesis - top 5 files (2026-07-22, claude-fable-5 in-session, max)

First run under G37. 5 unique files (asset-forge twin byte-identical = 6 ranked). 34 findings
survived Phase-3 adversarial verification; 5+ refuted and deleted. Cost $0.00 (in-session).
Per-file reviews in .colibri_reviews/*__bug__*.md. Nothing fixed yet - Damien triages.

## The cross-file pattern (what one-file-at-a-time would miss)
**Money paths are the weakest surface, repo-wide.** Three of five files leak unbounded or
mis-guarded PAID spend, and each was found independently:
- asset-forge/app.py libgen_start (L879): pack/wildcard counts flow UNCLAMPED into paid
  run_job - the bundle path clamps to 64 (L762), libgen doesn't. One JSON field = unlimited spend.
- Spector/app.py duplicates() (L914): global-min DNA truncation can collapse the whole
  library into one "duplicate" cluster; the paired resolve then mass-soft-deletes it.
- Both apps: dry_run / preview flags that silently EXECUTE instead of previewing
  (asset-forge tag/rename L1228; Spector tags_rename bool() L1017 - a regression twin of a
  remediated 07-20 finding).
This directly matches the K3-sweep triage's Tier-1 (docs/K3_FEAT_TOP20_TRIAGE.md): the
money-safety cluster is real and now has exact line numbers. Recommend one focused
"paid-path hardening" pass: clamp+confirm every spend entry, fix the DNA-truncation cluster,
audit every dry_run parse.

**Second pattern: failure paths that lie or half-finish.**
- _safe_edit.py (G8 infra, highest blast radius): CLI write prints "(original restored)"
  when the restore actually failed (L149); and replace_in_file silently flips CRLF->LF on
  every edit (L82 text-mode read) - byte-compare can't catch it, and the repo has CRLF files
  (remediation_manifest.json is 723/723 CRLF). The safe editor corrupts line endings safely.
- PatternSkin apply_pattern (L181): phase-2 exception after the subdivision commits leaves
  the user's mesh densified, CANCELLED, no undo pushed, user untold.
- asset-forge (L749): raw exception text bypasses _redact on job surfaces + on disk.

## Severity roll-up (all CONFIRMED unless noted)
HIGH (4): AF libgen unbounded spend L879 · Spector duplicates DNA-truncation mass-delete L914
 · Spector _SIMILAR_CACHE post-scan stale version-stamp L622 · PatternSkin pip pipe-buffer
 deadlock (no cancel) L2078.
MEDIUM (16): see per-file. Clusters - dry_run/preview execute-not-preview (x3); unbounded/
 unweighted DNA distance + missing @_bounded on Spector export/backup; AF reference silently
 dropped on restart, resume-race marks running job errored, unredacted errors, publish-to-
 library promised-never-called, Windows job.json replace-vs-poll (PLAUSIBLE, needs runtime);
 PatternSkin _previews_reset dangling icons + dens-on-failure; _safe_edit restore-lie + CRLF;
 skin3d y-seam + 10x budget under-estimate.
LOW (10): Spector config int() 500s, changes() lock, find_by_dna 500-not-400; AF tracer-
 language-in-user-build (byte-identical-safe fix) + hf_ token unredactable; PatternSkin
 orphaned preview datablock, modal cancel() cursor/timer leaks, load_heightmap raw traceback;
 skin3d DecompressionBomb leak, unbounded --rows, stale STATUS, signed-bbox false claim;
 _safe_edit perm-bits clobber, no-lock TOCTOU (PLAUSIBLE).

## Protocol notes (first G37 run - kept for tuning)
- The context pack earned its keep: the AF libgen finding is only "HIGH" because Phase 1
  surfaced the bundle path's L762 clamp as the proof the omission is a bug, not a choice.
  The Spector stale-version and _safe_edit restore-lie findings are unfixed TWINS of
  already-remediated entries - only visible because the manifest was loaded first (G35/G36).
- Adversarial pass deleted real drafts: PatternSkin live-mode fallback + ai_settings cursor
  leak (both provably unreachable); skin3d point-cloud crash + GLM's empty-STL claim (didn't
  reproduce on trimesh 4.12). Verification is doing its job - none shipped unproven.
- skin3d_proto.py is a DEAD prototype (0 importers) - severities are tool/doc risk, not ship.
- One external GLM second opinion was consulted (skin3d only, post-in-session) and adopted
  only where runtime-reproduced - the demoted-second-opinion path worked as designed.
