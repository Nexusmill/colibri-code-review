# Colibri broker support review

Source: C:\Users\User\source\repos\Tools\adversary-gate\enforcement_server.py
Reviewer: Codex (in-session)
SHA-256: eb7474872ac01c65cbe127e67b08dd7fb7dd12d0dc8239c4b1614c87cdb31a36
Date: 2026-09-16 05:56
Mode: bug/debug
Context: Tools manifest and history a55ffa5; AST symbol map; current loader, broker, writer, policy, safe_write and their tests; installed Colibri instructions. No prior report for this unit.

## Verdict
The missing whole-file read capability is implemented with a fixed-root, read-only tool. Existing mutation and verification routes are unchanged.

## Bugs & vulnerabilities
Fixed: the broker exposed no current-file content/hash operation, preventing protected Colibri reviews from establishing exact source freshness.
Fixed during acceptance: Windows Python 3.13 Path.stat and os.fstat disagreed on legacy st_ctime_ns (creation versus change time), falsely rejecting overwritten files. _read_stamp omits that incomparable field on Windows while retaining identity, mode, size, mtime and hardlink count; POSIX retains change time.

## Missing safeguards and boundaries
The read scope reuses ReviewedWriter.target, so control-plane files remain unavailable through this reader. DOS aliases and hardlinks are additionally refused. This is supported-tool enforcement, not an OS sandbox against a malicious external filesystem actor. Reads return a bounded snapshot; later external edits require a fresh read. No skill, write or verification credit is granted.

## Adversarial verification
The separate acceptance suite was RED before implementation (missing read_file/ReadDenied and denied policy name). Final broker suite: 36 tests, 35 passed, 1 skipped; loader suite: 16 passed. The skipped real-symlink test requires Windows privilege (WinError 1314); actual junction and hardlink refusals passed. Exact CRLF/Unicode/mixed endings, empty/exact-limit files, changed-file freshness, malformed paths, size/encoding failures, replacement-at-open and no-credit behavior passed.
Fresh MCP stdio read_file returned exact current engine.js bytes: 29502 bytes, SHA-256 306ea0d9089f0a9611ce0011c41a35bd6ed0a98ca754420974c1443fec1971f1. Manifest and state reads also matched; traversal returned an MCP error. Native host tool discovery still has no read_file, so native acceptance is pending.

## Independent exact-byte review
Final source CLEAR: .adversary/write-reviews/63f68726d3154af19c6c34746f962c72.json.
Initial implementation CLEAR b01b1794e55b4aababa1d75b579eb011 preceded the Windows test failure; only the corrected bytes are final.
