# colibri review — cross-file synthesis (all 21 code files)

- repo: C:\Users\User\source\repos\Blink
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- date: 2026-09-05
- scope: every code file (9 birdcam modules, 1 test module, 3 scripts, 7 launchers, 2 trivial package files, 1 vendored gate auditor)

## Cross-file findings (ranked)

1. **[MEDIUM] Orphaned-duplicate upload loop** — pipeline.py:203-231 with youtube_client.py.
   An accepted-but-unprocessed video is abandoned on failure and the batch re-uploads as a new
   video on the next run. The two files must be fixed together: youtube_client gains
   retry/backoff (its LOW), pipeline gains "failed batches with a recorded video id are polled,
   not re-uploaded".
2. **[MEDIUM] Unverified downloads poison compilations** — blink_client.py:280 with compiler.py.
   A non-200 body written as a clip surfaces days later as a CompileError that skips that day
   forever (the bad clip is never marked failed; it re-blocks every run). Fixing the status check
   at download time removes the poisoning; compiler.py's SKIP behavior is correct for the bytes
   it is given.
3. **[LOW-MEDIUM] Error-translation gaps converge at cli.py:193-201** — CompileError,
   PipelineError, and raw blinkpy 2FA errors (blink_client.py:147) all bypass the clean-message
   handlers. One except-chain remodel fixes three files' worth of user-facing tracebacks.
4. **[LOW] Safety-invariant asymmetry in clean()** — pipeline.py:260 vs README's documented
   invariant: corrupt archive blocks deletion, missing archive permits it. Pick one contract.
5. **[LOW] Silent-empty scan path** — config.py (metadata_pages validation) × blink_client
   (blinkpy page loop): a zeroed/typo'd value yields "no new clips" instead of an error; a range
   check at config load closes it.

## Per-file disposition

Every unit's full report is its own artifact in this directory (sha-keyed). Vendored
`.githooks/adversary_audit.py` was NOT re-reviewed here: it is the owner's canonical gate file
whose live findings are already captured as docket row EV-032 (colibri-code-review
docs/gate_evidence.json, commit e5df876) — re-reviewing it in this store would duplicate that
record.

## Totals

- 1 MEDIUM confirmed + 1 MEDIUM confirmed (cross-file pairs), 4 LOW confirmed,
  1 PLAUSIBLE settled same-session: schtasks quoting ACCEPTED by live probe (schtasks rejected the mangled fragments) and MITIGATED - register_schedule.ps1 rewritten to the Register-ScheduledTask object model, live-registered/verified/unregistered,
  0 CRITICAL. No secrets-handling or injection findings (secrets covenant verified: getpass-only
  password path, .env/secrets/data gitignored, no credential literals in any reviewed file).
