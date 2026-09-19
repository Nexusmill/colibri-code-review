source: src/components/SettingsConsole.tsx
reviewer: tencent/hy4-preview (scan ladder M2, colibri bug mode via headless hy4 CLI)
sha256: df27520769f50f8886bee617d98cc4e4cdfcc10f6a620e139805d519909d7e36
date: 2026-09-19 11:00
mode: bug
context: settings-window role + truthful-status/invitation invariants; per-leg failure states, keyedServices memo, generation guards listed as already-fixed; remediation manifest excluded up front

The scan ladder's first M2 pass (owner order 2026-09-19). Six findings, all adversarially verified CONFIRMED against the bytes before remediation (same session): 4 MEDIUM, 2 LOW, no HIGH (no M3 escalation).

## Finding 1 [MEDIUM] — getFilmDefaults failure hides the whole section and its error
The mount/refetch effect catches into setStatus, but `if (!defaults) return null` unmounts the entire FILM DEFAULTS block — the recorded error is never rendered, no retry. CONFIRMED (line 371-383 at scan sha).

## Finding 2 [MEDIUM] — Initial getRoutes failure is silently swallowed
Mount `getRoutes().catch(() => {})` — routes stays null, rows render routeText defaults ("cloud (default)") and "no saved presets yet" over a table that was never read. CONFIRMED (line 54-57).

## Finding 3 [MEDIUM] — getRoutes failure after ModelPicker close leaves stale rows silently
The picker-close refresh had the same empty catch — the console kept showing pre-change picks with no word. CONFIRMED (line 319).

## Finding 4 [MEDIUM] — Unsaved defaults edits are clobbered when keyedServices changes
The defaults fetch rode the `[loadCatalogs]` effect — every key save/clear refetched the record and overwrote an in-progress budget edit. The OPTIONS depend on keys; the record does not. CONFIRMED (line 371-374).

## Finding 5 [LOW] — Budget input does not enforce its own min/max before saving
min={0} max={500} are advisory for typed numbers; the blur saved the raw value. CONFIRMED (line 448-460).

## Finding 6 [LOW] — Saved-pick option says "gone from the catalog" when no service is keyed
An unkeyed leg's Promise.all([]) settles ok having read NOTHING — its saved pick claimed a delisting verdict no catalog produced. CONFIRMED (engineRow label + trace).

All six remediated in the same session with pin tests; see docs/remediation_manifest.md 2026-09-19 rows.
