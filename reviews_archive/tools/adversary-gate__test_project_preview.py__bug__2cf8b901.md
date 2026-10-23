# Workspace preview delta review

Source: C:\Users\User\source\repos\Tools\adversary-gate\test_project_preview.py
Reviewer: Codex (in-session)
SHA-256: 2cf8b901706c75b2bde5e031d12e50a5f369ab2249bc93b1a8449298667c2e71
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
Regression ran RED before source application. See PREVIEW_ACCEPTANCE.md for final GREEN suite. Independent exact-byte pre-write CLEAR artifacts: .adversary/write-reviews/9b6c5689a49144dabbcffd78fb08cf36.json. Prior report remains historical under its old hash.
