# Colibri delta review

Source: adversary-gate/reviewed_write.py
Reviewer: Codex (in-session)
SHA256: 45c2a81065e1e933636c7d7154fb187a3e02cad58314c16014e2996a412620ae
Date: 2026-09-27
Mode: bug
Context: canonical Tools history, marketplace byte parity, pre-write findings, snapshot call sites, ReviewedWriter and regression tests.

## Fixed since last review

Separated the prewrite file bound (450000 bytes) from staged inline budget. Added complete serialized UTF8 payload cap at existing MAX_TOTAL_BYTES=900000. Original and proposed text stay complete; secret checks, exact hashes, independent strict CLEAR, and concurrent edit rejection are unchanged. Large-file and escaped-expansion RED cases now pass.

## Verdict

No further confirmed finding in this change. Independent Luna pre-write CLEAR retained in the paired sync artifact.

## Cross-file synthesis

Canonical Tools owns these repairs; marketplace ships only its established gate payload. The broker stays Tools-owned. Colibri evidence references are repaired through the bounded broker and committed separately.
