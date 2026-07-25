<!-- source: the 7 re-run DeepSeek reviews (19:38 tranche) | reviewer: claude-fable-5 (colibri-review G37, verify-first) | 2026-07-22 | mode: bug | context pack: jcodemunch (library_gen run_job/_run_job_locked, stubify MARKER-skip), AGENT_STATE (stub architecture by-design, patch_global_memory LEGACY, af-libgen-money-clamp) -->

## Verdict
7 files. ONE real fix (asset-forge-user/library_gen.py 401 fast-fail — shipped product). The rest
refuted/by-design/low (dev tooling, legacy, marketing scratch).

## asset-forge/forge/library_gen.py (+ user twin, both fixed)
- **[HIGH-claimed → real MED, fixed] 401/auth error not fast-failed.** The except ladder pauses on
  credit(402) and rate(429) but a 401/403/unauthorized fell into the generic "other transient error"
  path → retried 3x PER ITEM across the whole job (a bad/expired token burns 3xN calls before each item
  is marked failed). FIX: detect 401/403/unauthorized/forbidden/authentication/invalid-token → pause the
  job immediately with "authentication failed — check your API token". VERIFIED: an AuthFail provider now
  makes 1 call (was 9 for a 3-item job) and pauses with the actionable reason. Twin synced byte-identical.
- **[CRITICAL refuted] "resume double-charges / missing idempotency":** FALSE — the loop skips
  `if it["status"]=="done": continue` and checkpoints each item to job.json after success; resume never
  re-charges a done item. Already covered by the _RunLock (exclusive per-job) + split 429/error retry
  budgets (0b45c35/bb2e047). DeepSeek didn't trace the done-skip.
- **[HIGH refuted] "failed items retried every run":** failed items retry only on an explicit user resume
  (job is already marked done); errored generations don't charge, and retrying a transient failure on
  resume is intended recovery. Accepted-by-design.
- **[MED refuted] no provider timeout:** the provider (replicate_flux) polls with its own timeout. count
  already clamped (af-libgen-money-clamp). wildness/types-validation = LOW build-time nits (skew, not crash).

## tools/stubify_global_claude.py — REFUTED / by-design
- **[CRITICAL refuted] "backup corruption via unconditional date-named backup":** FALSE — `if MARKER in
  src: continue` skips already-stubbed files BEFORE any backup (a stub can never be backed up over the
  original), and `if not os.path.exists(bak)` prevents same-day overwrite. The original fat content in
  .bak-<firstday> is preserved; restore() picks the newest .bak correctly. DeepSeek missed the MARKER skip.
- **[HIGH by-design]** the STUB's absolute @import paths are REQUIRED (Claude @import needs absolute paths,
  verified vs docs — AGENT_STATE stub architecture). restore/handle-leak/APPDATA = dev-tool robustness nits
  on a Damien-run script; not worth churning a working daily tool.

## tools/patch_global_memory.py — LOW, LEGACY (no change)
- Non-atomic write / race: this tool is LEGACY (superseded by the stub+@import architecture; kept only for
  rollback). Not worth hardening a retired tool. Recorded.

## launch/brand/make_showcase_cards.py — LOW, marketing scratch (no change)
- One-off brand-card generator (junk-tier output); a dropped-effect would be visible in the render. Not a
  product path. Recorded, not fixed.

## asset-forge-user/forge/personalize.py — CLEAN
- DeepSeek returned 0 HIGH/CRIT / 0 MED for personalize.py (already remediated 2fb93f6 atomic stamp). Nothing.
