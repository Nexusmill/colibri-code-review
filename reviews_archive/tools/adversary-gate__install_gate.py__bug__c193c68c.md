# Colibri review — adversary-gate/install_gate.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py`
- **Model:** claude-fable-5 (in-session), gating grok-4.3 external findings
- **sha256:** `c193c68c904e6b85bc09e2682ba9d53591d99b16f0dc6df948256433f8361546`
- **Date:** 2026-09-02
- **Mode:** bug
- **Verification:** the claimed HIGH was driven to refutation by reading the three canonical shims + `_canonical_shim`; the two robustness items confirmed by reading the cited paths.

## Verdict
Shippable. The one HIGH from the external pass is a false finding (refuted below); two minor robustness gaps remain.

## Fixed / refuted since external review

**[REFUTED — was flagged HIGH] "`_canonical_shim(CANON_POST/PREPUSH)` unconditionally SystemExits on every run"**
- The finding assumed the post-commit and pre-push shims don't contain `adversary_gate.py` or a `GATE="…"` line, so `_canonical_shim`'s checks (line 79 shebang + `adversary_gate.py` substring; line 84-87 exactly-one `GATE=` line) would always fail.
- Refuted by reading the canonical shims: all three (`pre-commit`, `post-commit`, `pre-push`) begin `#!/bin/sh`, reference `adversary_gate.py`, and carry exactly one `GATE="…"` line. `_canonical_shim` succeeds on all three; the installer is functional (consistent with it being armed across ten repos). Confident-wrong-at-the-edges — the external model never read the shim files.

## Bugs & vulnerabilities

**[LOW] `_git` catches only `FileNotFoundError`, not other `OSError`** — `line 60-63`
- What: the `try/except FileNotFoundError` around `subprocess.run([GIT,…])` returns a graceful `127`; a `PermissionError` (git present but non-executable) or other `OSError` propagates as a traceback.
- Impact: an unusual environment yields a traceback instead of the intended graceful exit-1 path. Minor.
- Fix: `except (FileNotFoundError, PermissionError, OSError) as e:`.

## Missing safeguards
- **[LOW]** The `.gitattributes`/`.gitignore` reads in the arming path assume readability; an existing-but-unreadable file raises rather than returning a clean exit-1 with a message. Wrap in `try/except OSError`. (Robustness only — the installer already reads results back to verify its writes.)
