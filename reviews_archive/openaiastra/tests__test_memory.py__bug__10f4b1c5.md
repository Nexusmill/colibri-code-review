# Colibri bug remediation: tests/test_memory.py

Source: C:/Users/User/source/repos/OpenAIAstra/tests/test_memory.py
Reviewer: Codex /root, in-session context-aware Colibri review
SHA-256: 10f4b1c578b5b42d094f935b76bea93abd9f4f749b854415cec172320bcf1641
Date: 2026-09-18 03:27 America/Denver
Mode: bug
Context: Lifecycle checked_documents, snapshot autoindex.sync and independent archive producer; prior b2643ab4 scan; real temporary databases under work/.
Prior review: .colibri_reviews/tests__test_memory.py__bug__b2643ab4.md

## Verdict
T1 is repaired and verified through the configured repository checks. No remaining confirmed defect in this remediation delta.

## Fixed since last review
The sync callback must run exactly once, the live fixture must actually change, docs/calibration/section must contain the validated cobalt content, and a separate archive row must equal the exact original UTF-8 bytes. The same assertion rejects the real archive-only subset. Capturing original bytes avoids assuming LF on Windows; the first run exposed and the correction preserves CRLF.

## Bugs & vulnerabilities
No additional confirmed finding in the changed behavior. This review closes the cited scan finding without reopening unchanged findings or substituting for other review modes.

## Adversarial verification
Reviewed the complete current file and traced changed assertions against actual producers/callers, then challenged the oracle with the negative control described above where applicable. Current bytes were read back through the native broker and matched the proposed content exactly. Source checks: 37 repository tests, five skipped, exit 0, unchanged tree, including all nine Emberline Node suites. The preceding red run had 151 Node tests, 149 passed and the two intended route failures; the separate Python archive assertion exposed a CRLF expectation error that was corrected against exact original fixture bytes.

## Missing safeguards
The archive-only negative control filters actual stored rows; it does not claim execution of a no-op sync mutation. Live project lifecycle archive delivery is separate. Optional browser/device/listening lanes and automatic project archive readback are not established by these checks. Final post-record verification and automatic explicit-path Git review remain the closing steps; their result belongs to the closing commit and task response.
