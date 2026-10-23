# colibri feature review - colibri-bounty/colibri_bounty/p2_units.py

- source: `colibri-bounty/colibri_bounty/p2_units.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `a624d5d4b2cfdf95fed17623cd4784d3b210e9d03f5fcf87fe86a9ec824864e4`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0510 (in=3214 out=7432)

## grok-4.7 output (verbatim)

## What this module does

`cluster_files` turns a contest's source paths into deterministic review units for the paid prompt: comment-stripped text is scanned for declared-type mentions (`_declared` / `_word_hits`) and relative imports, those edges feed a union-find, and each component is greedily packed under `DEFAULT_UNIT_CHARS` using raw (not stripped) length. Every input path lands in exactly one unit; a file bigger than the budget is a unit by itself. The point of the cluster is that a cross-contract interaction sits inside one prompt instead of being split across per-file reviews.

## Suggested add-ons

### Hub-preserving splits (opt-in)
- **Value:** High
- **Effort:** M
- **What:** When a union-find component does not fit in `max_chars`, start each subsequent bin with the already-packed file that has the most edges into the files still unpacked (the hub), instead of cutting purely by `(-raw_len, name)`.
- **Why it helps the user:** The ceiling this module exists for is cross-file integration bugs. Size-order packing can leave the linking contract in the first bin and ship the rest of the component without it, so the paid prompt never sees the interaction the cluster was built to hold. Repeating one in-budget hub keeps that surface in every slice without a new dependency or a live-contest spend.
- **How:** In `cluster_files`, record undirected edges in the existing `_word_hits` loop and the `import` `re.finditer` loop (they are discarded today after `union`). Add `preserve_hub: bool = False`. In the packing loop (`members` / `cur` / `cur_chars`), on budget overflow, if the flag is set and `raw_len[hub] <= max_chars`, seed the next `cur` with that hub before continuing. Default stays exactly-once so current callers and `tests/test_p2_units.py` do not change. Do not repeat a file that is itself over budget — that case already has its own unit.

### Per-unit link manifest for the prompt header
- **Value:** High
- **Effort:** S
- **What:** Expose, per unit, the concrete joins: declared name, importing path, imported relative specifier, and match line. Do not change the `list[list[Path]]` return of `cluster_files`.
- **Why it helps the user:** The paid prompt currently receives a bag of files. Naming the symbols and imports that put them in the same unit points the reviewer at the integration (the thing the 1/442 ceiling says per-file review misses) instead of spending context rediscovering the cluster.
- **How:** While scanning inside `cluster_files`, append `(src, dst, label, line)` from `_word_hits` / `re.search` spans and from each import `finditer` match. Add `cluster_links(files, max_chars=DEFAULT_UNIT_CHARS, reader=None) -> list[list[tuple]]` that runs the same scan and groups those edges by the units `cluster_files` already returns (an optional `links: list | None = None` out-param on `cluster_files` is enough if a second public function is unwanted). Labels stay plain strings — no new parser dependency; reuse `_declared` and `_strip_comments`.

### Preserved-edge report against the char budget
- **Value:** Med
- **Effort:** S
- **What:** A stdlib-only summary: component count, units emitted, components split by the budget, cross-ref edges whose endpoints share a unit vs edges the pack cut, and chars used vs `max_chars`.
- **Why it helps the user:** This funnel's job is honest, like-for-like measurement before any paid spend. Today there is no denominator for "did the unit actually contain the cross-file link?" A cheap offline report shows whether `DEFAULT_UNIT_CHARS` is what is dropping integrations, so budget changes are justified by a number rather than by another full paid run.
- **How:** Add `cluster_stats(files, max_chars=DEFAULT_UNIT_CHARS, reader=None) -> dict` beside `cluster_files`. Reuse the edge list from the union loops and the final `units` list; an edge is preserved iff both paths fall in the same inner list. Sweeping a few `max_chars` values is a call-site loop over this function — clustering does not spend.

## Nice-to-haves

- In the import loop of `cluster_files`, resolve the relative specifier against the importer's parent and prefer a path-suffix hit before falling back to `g.name == rel`.
- When `_declared` sees the same name in more than one file, union every owner (the owner dict is last-wins today; extra edges only merge, which this file already treats as the safe direction).
- Within a unit, stable-sort imported/declared-in files before their referrers so the prompt reads the callee first.
- Return paths that hit `OSError` in the reader loop (still fail-soft to `""`) so a replay can disclose unreadable inputs instead of silently clustering them as edgeless.

- ACCEPT hub-preserving splits (opt-in; repeat the in-budget hub when a component is cut) - VERIFIED: cross-ref edges are discarded after union(); packing is pure (-raw_len, name) order, so the linking contract can land in a different bin than its referrers.
- ACCEPT per-unit link manifest (declared name + importer + specifier + line, grouped by unit) - points the paid prompt at the interaction instead of a bag of files.
- ACCEPT cluster_stats preserved-edge report (edges sharing a unit vs cut by budget) - offline denominator for whether DEFAULT_UNIT_CHARS is what drops integrations.
- DEFER 4 nice-to-haves (path-suffix import resolution, multi-owner declared unions [owner last-wins is in-code], callee-first ordering, unreadable-file disclosure).
