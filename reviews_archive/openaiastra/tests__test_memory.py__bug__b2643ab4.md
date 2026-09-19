# Colibri bug review: tests/test_memory.py

Source: C:/Users/User/source/repos/OpenAIAstra/tests/test_memory.py
Reviewer: Codex, in-session context-aware review
SHA-256: b2643ab480e8df59f0112fb7e00b3509b73211abb9bd754cf8c6317a1936ea49
Date: 2026-09-18
Mode: bug
Context: Actual lifecycle handle/observed_handle paths, canonical autoindex sync source naming, isolated real databases and MCP restart contract. Reviewed all methods including UTF-8, secret scanning, deletion, snapshot race and persistence.

## Verdict
1 confirmed test-oracle gap(s); the named behavior is not fully protected by the current assertions. Findings concern test evidence, not confirmed runtime failures.

## Bugs & vulnerabilities
**[MEDIUM] T1: Snapshot indexing test can pass using only the archive row** — line 158

The sync-boundary test asserts that any stored row contains cobalt and no row contains the replacement secret (lines 158–162). handle() independently archives the prevalidated original document after autoindex.sync returns (tools/memory_lifecycle.py:131–155). If sync silently does nothing, the archive still supplies cobalt and neither assertion detects the missing docs/calibration/section row. The patched callback is not asserted to have run either. Require callback invocation and a source-filtered docs row with the original content; check archive content separately.

Verification: Confirmed by tracing both row producers and the existential predicate. The source key docs/calibration/section is correct: canonical repo_memory/autoindex.py derives it from path.stem. This is source-level counterexample verification, not an executed mutation.

## Missing safeguards
- Passing ordinary checks is not mutation sensitivity, browser/device quality or a guarantee that all possible defects were found.

## Fixed since last review
No prior canonical bug-mode row for this file. Feature-mode or pre-write clearance is not substituted for this bug review.

## Adversarial verification and validation
Current complete source was read with line numbers. Draft findings were checked against actual callers, producers and project ledgers; only the findings above survived. Findings are source-confirmed counterexamples, not executed mutation tests. Configured native run_checks: passed=true, exit_code=0, tree_unchanged=true; 37 Python tests ran, five skipped, including the nine-suite Node bridge. Tests and implementation were not changed by this review.
