source: src/components/SettingsConsole.test.tsx
reviewer: tencent/hy4-preview (scan ladder M2, colibri bug mode via headless hy4 CLI)
sha256: 648b6ba36ea03c11b93913dc7d3025c2ae8b8c46df4b4d2c6f9d50544d49f7da
date: 2026-09-19 11:05
mode: bug
context: suite history (04eb6bbf_r2 remediation) excluded up front; newest partial-outage test pinned; test-specific hunt classes named

Two findings, both LOW, both CONFIRMED and remediated the same session:

## Finding 1 [LOW] — mount() leaves its host div in document.body
Every mount appends a host div; unmount only called root.unmount() — DOM accumulated across the file and persisted when a test threw before unmount. FIXED: unmount removes the host.

## Finding 2 [LOW] — StrictMode orphans the first catalog promise in the local-switch test
The releaseCatalog single-variable pattern kept only the second of StrictMode's two resolvers; the first promise stayed pending through unmount. FIXED: every resolver is collected and settled.
