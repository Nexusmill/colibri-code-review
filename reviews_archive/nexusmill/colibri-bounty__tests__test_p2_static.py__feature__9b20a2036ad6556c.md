# colibri feature review - colibri-bounty/tests/test_p2_static.py

- source: `colibri-bounty/tests/test_p2_static.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `9b20a2036ad6556c32a6ba5a615287edc218d745a194008a33cf7d6bb25d571b`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.1002 (in=6717 out=14462)

## grok-4.7 output (verbatim)

## What this module does
This suite locks `p2_static`, the offline S1 Slither tier: it resolves foundry pins from `foundry.toml` and `remappings.txt`, installs only when a tag format is known (unpinned OpenZeppelin defaults to v4.9.3; anything else is recorded and not installed), and scans each non-banned `.sol` file under a forced solc framework. Solc choice prefers the root or `[profile.default]` foundry pin over the pragma sniff; per-file compile failures and runner crashes are counted, not fatal, and hits can be ranked and capped. Nothing here spends on a live contest.

## Suggested add-ons
- **Value:** High. **Effort:** M. **What:** Hand the pins `prepare_foundry_deps` already resolved to the forced-solc runner as remappings, plus the `allow_root` it already accepts, so sibling and lib imports compile instead of stopping at "source not found". **Why it helps the user:** Recall against judging truth is only meaningful on files the tier actually analyzed; foundry contests otherwise show up as skips, and a low hit count cannot be told apart from a tier that never saw the code before you spend. **How:** Extend `default_runner` argv next to `--compile-force-framework` (do not drop that flag). Have `scan_static` pass prefixes from `_all_pins` / `_remapping_pins` for the root `sol_files` already walks. Leave `prepare_foundry_deps` as it is: unresolved pins still install nothing and that file stays on the existing skip path.

- **Value:** High. **Effort:** S. **What:** Stamp each `scan_static` result with framework, the solc binary actually selected, a full/partial/blocked measurability flag, and any unresolved pin names. **Why it helps the user:** The product is an honest denominator before paid spend. Raw `skip_reasons` strings do not aggregate across the corpus, and a silent contest must not look like a true negative or get merged into the agent-tier figure. **How:** Add fields on the `scan_static` stats dict; do not replace `skip_reasons` or `skip_sample`. Label via `framework_for`; resolve the version `_foundry_solc` or `pragma_version` already chose through `solc_binary`; names come from `prepare_foundry_deps(..., unresolved_out=)`. Blocked = `files_seen > 0` and `files_analyzed == 0`.

- **Value:** Med. **Effort:** S. **What:** When no foundry solc pin exists, pick the newest `installed_versions` entry that satisfies the full pragma range instead of the floor token. **Why it helps the user:** `>=0.8.0 <0.9.0` is specified to become `0.8.0`, which often is not installed, so unpinned repos fall out of recall as skips or `runner_errors` even though a usable compiler is present. Foundry pin still wins, unchanged. **How:** Extend `pragma_version` with range bounds while keeping the current string for the `^0.8.10` cases the tests assert. Use that only in `scan_static`'s no-pin branch; confirm with `solc_binary`. If nothing installed fits, use the existing skip path, not `runner_errors`.

## Nice-to-haves
- `parse_slither_json` / `StaticHit`: also keep the element function name and source_mapping line span, leaving `contract` as the tests assert, so S5 `title_key` can line up with judging titles.
- `prepare_foundry_deps`: resolve repo and tag template only from `FORGE_KNOWN_PINS`, so a new contest lib is a table row; no template still fills `unresolved_out` and installs nothing.
- `sol_files` / `SKIP_DIRS`: add a per-dir exclusion count on `scan_static` stats beside `files_seen`, so test/mock/lib volume is a disclosed omission.
- `prepare_foundry_deps`: note whether each install came from `foundry.toml` or `remappings.txt`, same disclosure idea as the contamination column.

(no triage recorded)
