# colibri feature review - colibri-bounty/colibri_bounty/p2_context.py

- source: `colibri-bounty/colibri_bounty/p2_context.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `cd9ef3ae3513b5a3c2fee320453f7802a74fa35224e1f2b6646688c176fca0c2`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0427 (in=4323 out=5675)

## grok-4.7 output (verbatim)

## What this module does

This module builds the compact text pack prepended to every paid review unit: a contest-wide code map (declared types, `@scope` external deps, largest files) plus leave-one-out paid-finding priors clustered from other contests' judging dumps. Priors are capped and never dropped; the code map is prefix-truncated to whatever remains under `PACK_CAP_CHARS`. The scanner gets that pack through `pack_builder`, which closes over the issues dir and contest name and calls `build_pack` at scan time.

## Suggested add-ons

- **Value:** High. **Effort:** S. **What:** Fit the code map by section inside `map_budget`, instead of prefix-slicing the whole string, so the cross-file type surface survives when priors take most of the 9k. **Why it helps the user:** Priors may use up to 6k of the cap, and `code_map` emits the type list last, so the slice in `build_pack` often leaves the reviewer with file sizes only — the same single-file blind spot this pack exists to fix (1/446). **How:** Have `code_map` return the header, deps, type surface, and largest-files as separate strings; in `build_pack`, keep the type surface inside `map_budget` and fill any remainder with largest-files/deps. Do not cut `priors_pack` output.

- **Value:** High. **Effort:** M. **What:** Optional per-unit neighborhood: local imports and inheritance bases of the file under review, prepended so they sit in the reserved map budget. Intra-repo paths only — not counted as external packages. **Why it helps the user:** The pack is contest-global and identical for every unit. Largest files and an alphabetical type cap do not say which other contracts this unit actually integrates with, which is the class of paid bug the module docstring is aimed at. **How:** Add an optional focus path on `build_pack` and `pack_builder` (existing `builder(code_dir)` stays valid). Resolve focus-file imports with `_IMPORT_RE` and a small inherits pattern beside `_DECL_RE`. Leave `_dep_root` unchanged (`@scope/pkg` only).

- **Value:** Med. **Effort:** S. **What:** Rank the 12 prior rows by high-severity weight and how many other contests contributed, and show that spread in the bracket. Keep leave-one-out and the 0.34 Jaccard cutoff. **Why it helps the user:** The pack tells the model to look at these classes first, but `_cluster` sorts only by raw size and `priors_pack` drops contest identity, so one chatty contest's medium titles can fill the cap and hide rarer high-severity classes that actually pay. **How:** Carry contest name on the tuples `priors_pack` passes in; change `_cluster`'s sort key and returned tuple (size, rep, highs, mediums, distinct contests). Still exclude `exclude_contest` before any judging file is opened.

## Nice-to-haves

- In `code_map`, keep the contract/interface/library keyword `_DECL_RE` already matches but discards, so the type surface distinguishes integration boundaries from implementations.
- In `code_map`, print paths relative to `code_dir` instead of `path.name`, so colliding basenames stay distinct in the largest-files line.
- In `build_pack`, append one truncation line when the map or the 60-type cap is cut, so a partial surface is not read as the whole protocol.
- Memoize inside `pack_builder` on the resolved `code_dir` so attaching the same pack to many units does not re-walk every `.sol` and every `*-judging.json`.

- ACCEPT section-fitted map budget - VERIFIED STRONG: code_map() emits the cross-file type surface LAST and build_pack() prefix-slices `code_map(...)[:map_budget]`; priors up to 6k of the 9k cap cut the type surface first - the exact blind spot the module exists to fix.
- ACCEPT per-unit neighborhood (focus-file imports + inheritance bases, intra-repo, inside map budget) - _IMPORT_RE/_dep_root hooks exact; @scope-only rule preserved.
- ACCEPT severity-weighted + contest-spread prior ranking - VERIFIED: _cluster sorts by raw size only and priors_pack drops contest identity; leave-one-out + 0.34 cutoff preserved in the How.
- DEFER 4 nice-to-haves (decl keyword retention, relpath in largest-files, truncation disclosure line, pack_builder memoize).
