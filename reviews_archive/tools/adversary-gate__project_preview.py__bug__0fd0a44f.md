# Workspace preview delta review

Source: C:\Users\User\source\repos\Tools\adversary-gate\project_preview.py
Reviewer: Codex (in-session)
SHA-256: 0fd0a44f6203e7243486e30f50eec7c5655ed6a1d445e738dea7c6010f96d757
Date: 2026-09-19 14:04
Mode: bug
Context: prior per-file report, commit review gate_20260919-135815, actual adapter exception handler, real TCP regression.

## Verdict
The confirmed malformed-proof exception is handled at the verification boundary.

## Fixed since last review
A real TCP server replying with non-HTTP bytes reproduced http.client.BadStatusLine against the prior source. Catching HTTPException now treats an unusable proof as false; direct policy and actual adapter deny it. The original reviewer claim of a hook bypass is refuted by codex_guard.main, which already catches BaseException and exits 2. The defect was availability and loss of the actionable denial, not a demonstrated host bypass.

## Bugs & vulnerabilities
No remaining confirmed finding in this delta. The regression exercises a real socket, verification, policy and adapter; source catches the explicit HTTPException family, not arbitrary exceptions.

## Adversarial verification
Regression ran RED before source application. See PREVIEW_ACCEPTANCE.md for final GREEN suite. Independent exact-byte pre-write CLEAR artifacts: .adversary/write-reviews/359c096f7bd048e792853c1b85d69fd7.json. Prior report remains historical under its old hash.
