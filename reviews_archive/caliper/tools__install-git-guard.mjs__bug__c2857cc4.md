# Colibri bug review — tools/install-git-guard.mjs

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: c2857cc4791ab1b8952477498a273ad4ddfa064e65964df1f6773dde4196571f

### Meta
- path: tools/install-git-guard.mjs | sha8: c2857cc4 | lines: 61 | context-pack: target cache verified present (tools/universal-tools/1.0.0/hooks/ with the byte-identical payload and hooks.json carrying 4 PreToolUse entries); merge idempotency simulated read-only against the live hooks.json (`present: true` today — a run now refreshes the payload and appends nothing); sole commit 6d44839.

### Review

## Verdict
Shippable and idempotent for today's cache state (verified by simulation), but its two writes are non-atomic: a crash mid-copy or mid-merge leaves the security control silently dead or the plugin's hook config corrupt, and nothing verifies the result afterward.

## Bugs & vulnerabilities
**[MEDIUM] Non-atomic payload copy can leave a truncated guard in the live hook path** - `line 44` — CONFIRMED (write) / PLAUSIBLE (consequence)
- What: `copyFileSync` across drives (E: repo to C: cache) is not atomic; interruption (crash, disk full, AV lock) can leave a truncated `hooks/git-guard.mjs`. A truncated module makes the PreToolUse process die on a SyntaxError with a non-zero exit — non-blocking advisory in this harness family — so the guard fail-opens silently until someone re-runs the installer.
- Trigger: interruption during the copy.
- Impact: the outer protection layer goes dark with no signal (the inner git hook remains, per doctrine, but the installer's whole point is restoring the outer layer).
- Fix: write to `git-guard.mjs.tmp` in the same dir, then `renameSync` over the target (atomic on same volume), and re-read + byte-compare after — the verification step also catches partial copies. Note the consequence chain is PLAUSIBLE rather than CONFIRMED because the harness's exact exit-1 hook handling lives outside this repo.
- Cross-check: a fix here does not disturb the installed flow — hooks.json already points at the same filename.

**[LOW] hooks.json rewrite is non-atomic and unverified** - `line 58` — CONFIRMED
- What: `writeFileSync(hooksPath, ...)` in place. A crash mid-write (or two installer runs racing read-modify-write) leaves truncated JSON; a corrupt hooks.json can take down ALL hooks in the plugin — including the owner's protocol-gate — until reinstall.
- Trigger: crash/concurrency during the merge write.
- Impact: total hook-config loss for the plugin (worse than the entry merely missing).
- Fix: tmp file + `renameSync`; optionally write a `.bak` first.

**[LOW] Idempotency check is coupled to JSON key order** - `lines 51-55` — CONFIRMED
- What: presence is detected by exact `JSON.stringify` string equality against the installer's literal. Any external rewrite of hooks.json that reorders keys (or adds a field to the entry) makes `present` false forever after, so the next run pushes a duplicate matcher entry (guard then executes twice per tool call; stops after one duplicate because the exact string then exists).
- Trigger: any tool that rewrites hooks.json with different key ordering.
- Impact: duplicated hook execution and a subtly divergent file; benign today (verified: current file matches the literal exactly).
- Fix: compare structurally (`matcher`, `command`, first arg) instead of by serialized string.

**[LOW] "Newest version" is chosen lexicographically** - `lines 28-29` — CONFIRMED
- What: `sort()` on dir names picks `1.9.0` over `1.10.0` (string compare: `"1.1..." < "1.9..."`). Today only `1.0.0` exists, so no wrong behavior yet.
- Trigger: plugin cache gains two version dirs with numeric-order inversion.
- Impact: payload installed into a stale version dir while the harness runs a newer one — guard silently absent from the live dir.
- Fix: compare version tuples numerically.

## Missing safeguards
- No post-install verification step (re-read the copied payload and re-parse hooks.json; report a clean "verified" the way AGENTS.md's verification protocol demands of everything else).
- No backup/restore story for hooks.json before rewriting it.
- Version-drift direction is intentionally repo-over-cache ("payload refreshed") — consistent with the charter that the repo copy is canonical; but the installer never warns if the cache payload it is about to overwrite differs from the repo copy in an unexpected way (e.g. an owner hotfix made in cache would be silently reverted) — a one-line diff notice would prevent that footgun.
