# Colibri bug review — vitest.setup.ts

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: cea2f5be1bd6c44ad5f89cc692aa3e0b06a4dbaf4d0f72dc3684833e4789e29b

### Meta
- path: vitest.setup.ts | sha8: cea2f5be | lines: 10 | context-pack: referenced from vite.config.ts:41 (`test.environment: "jsdom"`, `globals: false`); mechanism fully source-traced against the installed toolchain (vitest 3.1.4 `populateGlobal`/`getWindowKeys` in dist/chunks/index.CmSc2RE5.js, jsdom 26.1.0 lib/jsdom/browser/Window.js:348,470, Node v25.2.1); localStorage consumers: src/stores (persist), ScreenStage, FilmWizard + their tests; no sessionStorage use anywhere in src; sole commit 4b3b889.

### Review

## Verdict
The shim is correct and genuinely load-bearing — every link verified: Node 25.2.1 ships a native configurable `localStorage` accessor that is non-functional by default (`setItem is not a function`, warns about `--localstorage-file`), vitest's `getWindowKeys` drops `localStorage` because it already exists on globalThis and is not in vitest's KEYS list, while jsdom's real Storage instance is copied to globalThis as `_localStorage` (Window.js:348, returned by the `localStorage` getter at :470) — so redirecting the global to `_localStorage` restores jsdom semantics faithfully. No bugs found; two latent gaps below.

## Bugs & vulnerabilities
(none — mechanism traced end-to-end and confirmed sound: same Storage instance jsdom's own `window.localStorage` getter returns, so data, identity, and cross-window storage-event behavior are jsdom's; the get-only configurable descriptor matches jsdom's accessor semantics; the soft no-op when `_localStorage` is absent is the safe direction)

## Missing safeguards
- `sessionStorage` has the identical Node-25 shadowing problem (native accessor present, configurable, filtered by the same `getWindowKeys` rule — verified present on this Node) and is NOT shimmed. Latent only because nothing in src/ or the tests touches sessionStorage today; the first future use will fail cryptically with `setItem is not a function`. Shim it the same way (`_sessionStorage` is defined the same way in jsdom's Window.js) or add a comment marking it as a known gap.
- The shim depends on jsdom's undocumented internal `_localStorage` property name. If a jsdom/vitest upgrade renames it, the `if (jsdomStorage)` guard makes the shim a silent no-op and the failure resurfaces far away as broken store tests. Failing loudly (throw when `_localStorage` is absent while a native `localStorage` exists on globalThis) would convert that into a one-line diagnosis at setup time.
