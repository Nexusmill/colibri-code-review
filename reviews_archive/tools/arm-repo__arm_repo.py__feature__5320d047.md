# arm-repo/arm_repo.py - feature review

source: C:\Users\User\source\repos\Tools\arm-repo\arm_repo.py
reviewer: in-session GLM-5.3 (ZCode) · sha256: 5320d047e265e80434db2fb03d5961ebeeb73d3f2a729086ab286a2220c7962f · 2026-10-08 17:46 · mode: feature
context pack: full-source read this session (executed the arming live for this repo); installer children install_gate.py / repo_memory.bootstrap; fleet + general store records of prior armings; no prior feature rows.

## What this module does

The one-command new-repo arming protocol: adversarial git gate install, Claude
project skill-gate rows, ZCode global-plugin verification, global-memory stubs
(AGENTS.md/CLAUDE.md), and the repo-memory store bootstrap — with fail-closed
refusals before any mutation and an idempotent post-install verify.

## Suggested add-ons

- **`--zcode-only` mode** — Value HIGH · Effort S
  What: a flag that arms everything EXCEPT Claude-facing pieces (claude rows and
  the CLAUDE.md stub) while still writing the AGENTS.md stub.
  Why: this session's exact owner constraint ("arm from the z.ai point of view
  without affecting claude or codex") had to be hand-assembled from
  `--skip-claude --skip-stub` plus a manual `write_stub()` call — the workflow
  exists and deserves one switch; verify reports the skipped rows as intentional.
  How: tie the stub loop to the flag; add the row names to the `skipped` set.
  Hook: the flags block + post-install verify.

- **Machine-readable census** — Value MED · Effort S
  What: `--verify-only --json` emitting the rows as one JSON object (and
  `--census --json` passing through install_gate's machine-wide proof).
  Why: the fleet tracks arming state across every repo; today the only output is
  formatted text that a monitoring agent must parse.
  How: `verify()` already returns rows; a serializer flag in `main()`. Hook: the
  verify_only branch.

- **Workspace `.mcp.json` verify row** — Value MED · Effort S
  What: since 2026-10-08 the bootstrap writes a root `.mcp.json` + 
  `.repo-memory.json` pair (standard armed shape); verify should assert the pair
  exists and names the repo's own store.
  Why: the verify rows predate the pair; a half-armed repo (store registered but
  workspace mount missing) reports ARMED today.
  How: two rows reading the pair; mirror of the registry check. Hook: `verify()`.

- **Post-arm jCodemunch reindex step** — Value LOW · Effort M
  What: after the bootstrap indexes the store, offer `--reindex-code` to refresh
  the repo's jCodemunch index (or print the exact command when the CLI isn't
  reachable from the installer).
  Why: a freshly armed repo's code index is usually stale on first session.

## Nice-to-haves

A `doctor` subcommand (one diagnostic pass: gate hooks, stores, mounts, plugin
hook, linters on PATH); arm-date stamping inside `.repo-memory.json` for census
sorting; a `--global-memory` existence check that reports the master's mtime.
