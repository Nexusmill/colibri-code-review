# Colibri review — adversary-gate/guard_selftest.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\adversary-gate\guard_selftest.py`
- **Model:** claude-fable-5 (in-session), gating GLM-5.3-flash (smoke-run) finding
- **sha256:** `f8f6152604814319beba3f87c92eff3b8f7b7ccc7a8c577fb0e7b99a06237834`
- **Date:** 2026-09-02 · **Mode:** bug
- **Context:** table-driven block/pass matrix driving the REAL `harness_guard.py` hook via stdin JSON → exit code.

## Verdict
One real MEDIUM (no subprocess timeout → the selftest can hang forever); the second external finding (cwd) is refuted.

## Bugs & vulnerabilities

**[MEDIUM] `run_guard` sets no `timeout` → the selftest hangs forever if the guard blocks** — `run_guard` line 20-21 — CONFIRMED (read)
- `subprocess.run([PY, GUARD], input=payload, capture_output=True, text=True, …)` has no `timeout=`. If a future `harness_guard.py` change blocks on stdin, waits on a child, deadlocks, or prompts, the selftest child hangs with no output, never reaches the summary/exit code, and in CI burns the whole job timeout with zero signal about which case hung.
- Fix: add `timeout=30` and catch `subprocess.TimeoutExpired`, recording it as a FAIL for the current case (thread the case name into `run_guard`).

## Fixed / refuted since external review

**[REFUTED — external LOW] "`run_guard` pins no `cwd`, so results are cwd-dependent"**
- The finding is conditional on "if harness_guard reads repo-relative state." It does not: `harness_guard.decide()` is a pure function of the stdin `tool_name`/`tool_input` JSON (verified in this session's `harness_guard.py` review — it opens no files, consults no cwd-relative state). So the missing `cwd` cannot change any block/pass outcome. GLM flagged this as LOW and hedged "if I'm wrong, disregard." Refuted.

## Note
`harness_guard.py` itself (the code under test) DOES have confirmed bypasses — see its own review this session (comment-substring `.adversary` exemption, Windows trailing-dot segment, hooksPath prefix). This selftest does not yet exercise those cases; adding a RED row per confirmed bypass is the remediation-tranche follow-up.
