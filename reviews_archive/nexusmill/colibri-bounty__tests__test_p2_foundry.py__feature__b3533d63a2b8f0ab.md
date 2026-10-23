# colibri feature review - colibri-bounty/tests/test_p2_foundry.py

- source: `colibri-bounty/tests/test_p2_foundry.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `b3533d63a2b8f0ab3f5f8cd3adc785c1c50342a89975fbda479d92bb117b5230`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0474 (in=4116 out=6530)

## grok-4.7 output (verbatim)

## What this module does
This suite locks P2.1 foundry wiring for the S1 static tier: `framework_for` selects foundry when a `foundry.toml` ancestor exists and solc otherwise, and `default_runner` forwards that choice as `--compile-force-framework`. `prepare_foundry_deps` installs known pins (OpenZeppelin v4.9.3 in the fixture), deletes empty unknown lib placeholders, and records failed installs plus unmapped remappings; `sol_files` drops `lib/` and `node_modules`. `scan_static` prepares deps even when `foundry.toml` sits on the code root, and an installer exception is fail-soft and counted in `foundry_prep_errors`.

## Suggested add-ons
- Value: High. Effort: S. What: Fold `prepare_foundry_deps` outcomes into the `stats` dict `scan_static` already returns — installed pins, unresolved remappings, and failed-install identities, next to `foundry_prep_errors`. Why it helps the user: a scan can finish after stripping `mystery-dep` and still look like a clean static pass; replay precision/recall then treats an incomplete compile as a scanner result. The install-failure case is only asserted on the prepare API today, not on the stats the funnel consumes. How: extend `prepare_foundry_deps` (return value plus `unresolved_out`) and `scan_static` so the `foundry_prepare` callback always receives `unresolved_out` and those lists are copied to `stats` (e.g. `foundry_installed`, `foundry_unresolved`). Do not drop `foundry_prep_errors`.

- Value: High. Effort: M. What: Classify files whose project root had a stripped or failed pin as dep-incomplete, distinct from a clean zero-detector file, and count that class in `scan_static` stats. Why it helps the user: deleting an unknown lib makes later Slither runs see missing imports; those zeros are not the same denominator as a foundry file with pins installed. Keeping the class visible preserves like-for-like recall without merging agent-tier and union figures. How: extend `scan_static` to retain the `prepare_foundry_deps` unresolved set per root, and extend `parse_slither_json` / `StaticHit` construction so an import-resolution failure on a stripped root is stamped dep-incomplete instead of an empty detector list. Leave `title_key` and tier priority unchanged.

- Value: Med. Effort: S. What: Let callers pass an extra skip set into file discovery, defaulting to `SKIP_DIRS`, so non-contest vendor trees are excluded the same way `lib/` and `node_modules` already are. Why it helps the user: the suite’s own contract is that dependency source must not consume static time or LLM units; only those two names are locked, so other vendor layouts in the replay corpus still get scanned and dilute the static denominator. How: extend `sol_files` to honor `SKIP_DIRS` plus an optional extra set, and thread that same set through `scan_static` so discovery and `foundry_prepare` stay on one root list.

## Nice-to-haves
- Add foundry-vs-solc file counts to `scan_static` stats from `framework_for`, so the honest table shows the compile mix without changing framework choice.
- Stamp `StaticHit` with the `framework_for` result at the `parse_slither_json` call site for later stratification, without touching dedup keys.
- Record the `pragma_version` / `solc_binary` pair `default_runner` actually used when the framework is solc, as a stats note only — not a `foundry.toml` pin preference.
- Drive the known-pin fixture off `FORGE_KNOWN_PINS` instead of a single OpenZeppelin literal, so a new pin cannot ship unmeasured.

- ACCEPT fold prepare outcomes into scan_static stats (installed/unresolved/failed identities) - VERIFIED with nuance: test_failed_install_and_unresolved_pins_surface_in_stats is named "in_stats" but its body asserts only the prepare API return + unresolved out-list; stats carries the foundry_prep_errors COUNT (exploding-prepare test) but no identities.
- ACCEPT dep-incomplete file class distinct from clean-zero (stripped-root import failures stamped, like-for-like recall).
- ACCEPT optional extra skip set threaded through sol_files + scan_static (vendor layouts beyond lib/node_modules).
- DEFER 4 nice-to-haves (framework mix counts, StaticHit framework stamp, solc pair note, FORGE_KNOWN_PINS-driven fixture).
