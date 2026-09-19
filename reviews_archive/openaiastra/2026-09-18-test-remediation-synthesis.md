# Test scan remediation closure — 2026-09-18

## Scope and outcome
All five confirmed findings from the seventeen-file test bug scan are repaired across four test files, with one supporting diagnostic-helper change. Thirteen scan units had no confirmed findings and remain unchanged. Original scan: 2026-09-18-test-bug-synthesis.md. Current-hash per-file bug reports and canonical manifest preserve earlier modes and reports.

- **T1 — tests/test_memory.py:** The sync callback must run exactly once, the live fixture must actually change, docs/calibration/section must contain the validated cobalt content, and a separate archive row must equal the exact original UTF-8 bytes. The same assertion rejects the real archive-only subset. Capturing original bytes avoids assuming LF on Windows; the first run exposed and the correction preserves CRLF.

- **T2 — implementations/emberline/engine.test.cjs:** Each of fifty restored gardens advances the real simulation to two observed enemy objects within a bounded run and compares their types with an explicit expectation table independent of the runtime roster expression. A separate VM runs actual engine source with selection changed to types[0]; the same assertion rejects that mutation at garden zero. Production source on disk remains unchanged.

- **T3 and T4 — implementations/emberline/ui.test.cjs:** The 150 seeded garden route cases independently enumerate HOME, resets, embers, all opening spectrum pickups and the rich patch, checking identities and coordinates before reachability. An enclosed but collision-clear pickup must be reported unreachable, then becomes reachable with walls removed. Both route regressions failed before helper repair. Harness focus now records document.activeElement; the manual summary owns focus before KeyP and the arena must own it afterward. An in-memory game copy without canvas.focus calls leaves the summary focused, proving the oracle distinguishes missing focus. The mutation matches the actual preventScroll call.

- **T5 — implementations/emberline/voice.test.cjs:** Every sample now rejects both +32767 and -32768 saturation rails. Existing audibility, duration, format and asset checks remain. Synthetic positive/negative rail runs and isolated rail samples fail the same assertion, silence fails audibility, and valid interior samples pass.

- **T3 supporting diagnostic repair — tools/emberline-diagnostics.cjs:** Added each state.spectrumPickups item to the destination list with a unique spectrum index label, using the existing BFS, route and clearance calculation. No traversal algorithm, output-path enforcement or gameplay changed. New caller assertions failed on omitted targets before application.

## Verification and boundaries
Native checks after source repairs passed: 37 repository tests, five skipped, exit 0, unchanged tree, including all nine Node suites. First run deliberately preceded the route helper fix: 151 Node tests, 149 passed, two route regressions failed on omitted pickups. It also exposed a test-authoring CRLF mismatch; exact original fixture bytes now supply the archive expectation. Native exact readback matched all five source candidates and jCodemunch reindexed all five without errors.

No gameplay engine, media assets, guard or control-plane implementation changed. Existing hard-link and CLI diagnostic checks remain in the bridge. The observed gate BLOCK/stale-clearance lines during repository tests are isolated intentional negative fixtures, not the task's real closing review. Tests emitted existing canonical ResourceWarning/HF notices; these were not test failures.

Browser/device/listening QA, standalone optional requirements audit and automatic archive byte readback remain unverified. Geometric routes do not establish inertia/enemy-pressure acceptance. Final post-record checks and armed Git commit follow; task record: ../docs/tasks/2026-09-18-test-remediation.md.
