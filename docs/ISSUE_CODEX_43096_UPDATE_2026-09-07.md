# Codex #43096 update — 2026-09-07

Posted and read back on 2026-09-07: https://github.com/openai/codex/issues/43096#issuecomment-5571347041. The update below is the posted text; preserve it as an archive.

## Update: machine-wide commit enforcement and skill-routing evidence

The implementation has advanced since this issue's original 35-event snapshot. Our evidence docket now records 43 events, including three relevant developments:

- **EV-041:** We retracted the assumption that new clones need manual arming. A global Git hook path pointing to an absolute dispatcher directory covers new clones and worktrees automatically on the configured machine. The previous relative path could silently dangle in worktrees on branches predating the hook files. The installer now pins the absolute directory and provides a census.
- **EV-042:** Extensionless canonical hook files were outside the code-extension classifier. They now require review, with a history-anchored rules epoch to avoid retroactively reclassifying old commits.
- **EV-043:** Git partial commits exposed an inherited-index bug in the dispatcher's self-check. Independent review blocked two proposed repairs before the final correction. The documentation records the triggers and remediation evidence.

The Codex integration now points its plugin at the canonical Tools scripts, with no private script copies. On September 7, its adapter selftest passed 19/19 checks and the installer verified the Tools checkout against the machine-wide dispatcher. These checks establish adapter behavior and configuration, not complete coverage of every live tool path.

There is a related skill-routing problem worth making explicit. Our G38 gate requires process skills before edits and verification after edits. The motivating census recorded roughly 2,800 source edits with zero verification-before-completion invocations and two karpathy-guidelines invocations. This is a local observation, not a general benchmark. The proposal and its limitations are described in https://github.com/anthropics/claude-code/issues/92656.

**Codex skill-gate parity is not yet demonstrated.** The plugin wires the current skill gate, but a direct probe using Codex's documented `apply_patch` hook payload found that the Claude-oriented implementation allowed it and recorded zero source edits. That implementation also credits `Skill` invocations; this Codex session has no equivalent native tool. Simply wiring the same command is therefore insufficient. Ordinary reads must not silently be presented as authenticated skill completion.

Codex already documents PreToolUse/PostToolUse hooks for Bash, apply_patch, MCP, and other local tools, along with coverage exceptions: https://learn.chatgpt.com/docs/hooks. The request is consequently more specific than adding hooks: expose trustworthy evidence of skill loading/check execution and bind subsequent mutations to that evidence, with explicit invalidation after further edits. Loading a skill establishes that instructions were supplied; it does not prove that the requested verification actually ran or passed.

Reference documents and the evidence docket: https://github.com/Nexusmill/colibri-code-review/tree/main/docs

This complements the original independent-review proposal: both need a tool action to depend on evidence the author cannot merely assert.
