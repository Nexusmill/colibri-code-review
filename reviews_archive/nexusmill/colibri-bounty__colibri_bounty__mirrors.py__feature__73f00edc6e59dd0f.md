# colibri feature review - colibri-bounty/colibri_bounty/mirrors.py

- source: `colibri-bounty/colibri_bounty/mirrors.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `73f00edc6e59dd0f213034eb9b45ea9c20e39387ec182e2cb9e132951a3937ae`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0515 (in=2476 out=7758)

## grok-4.7 output (verbatim)

## What this module does
`mirrors.py` keeps a shallow on-disk git mirror of public corpus content (`DEFAULT_MIRRORS`, today `solodit_content`) so later tiers can walk contest source without fetching mid-measurement. `sync_mirror` either `clone --depth 1` or `fetch --depth 1` plus `reset --hard FETCH_HEAD`, and returns a coarse status (`cloned` / `updated` / `error`); `sync_all` runs that over a name-to-URL map with an injectable `runner` and an optional `progress` callback. It does not record which commit landed, and it does not turn a contest id into the project root scanners walk.

## Suggested add-ons
**Pinned revision + offline manifest**
Value: High. Effort: S.
What: Land sync on an optional ref (default `HEAD`, so current callers stay valid) and write a small JSON manifest of status, URL, ref, and resolved SHA next to the mirrors.
Why it helps the user: Precision and recall are only like-for-like if two runs saw the same tree. Today `updated` does not name a commit, and the next `sync_all` moves `origin/HEAD` under the denominator. A manifest lets the honest table cite the corpus commit with no further fetch.
How: Add `ref: str = "HEAD"` to `sync_mirror` and thread it from `sync_all` into `fetch` / `clone`. Do not change the existing `str` status return. On success, `runner("rev-parse", "HEAD", cwd=dest)` inside a new `write_manifest(mirrors_dir, urls, results, runner=default_runner)` that writes `mirrors_dir / "manifest.json"` via stdlib `json`. Pair with `read_manifest(mirrors_dir) -> dict` for S5 to cite. Missing `.git` stays an explicit null SHA, not an omitted row.

**Contest root, remappings, coverage**
Value: High. Effort: M.
What: Resolve a contest id under a synced mirror to the project directory a tier should walk, plus the remappings that tree already ships, and report which expected contest ids had no tree.
Why it helps the user: This module is the path every scanner tier walks, but nothing here maps "contest X" to a directory. Independent searches per tier make a miss look like zero findings, so recall is not like-for-like with judging truth. Slither (live S1) on a Foundry tree without remappings under-reports for import reasons, not because the bug is absent.
How: Add `resolve_contest_root(mirror_dest: Path, contest_id: str) -> Path | None` — pathlib walk for a directory named `contest_id`, then prefer that directory or a descendant containing `foundry.toml`, `hardhat.config.js`, or `remappings.txt`. Return `None` if absent; do not fall back to the mirror root. Add `load_remappings(root: Path) -> tuple[str, ...]` — read `remappings.txt` if present, else `tomllib` on `foundry.toml`'s `remappings` key (stdlib on 3.13); empty tuple if neither. Add `contest_coverage(mirror_dest, contest_ids) -> dict[str, Path | None]` so prep can disclose gaps before a denominator is computed. Read-only: do not write sidecars into the mirror (`reset --hard` would drop them).

**Read-only readiness (no fetch)**
Value: Med. Effort: S.
What: A non-mutating inspect of one mirror destination: missing, SHA, or error.
Why it helps the user: `sync_mirror` / `sync_all` always talk to origin. Offline replay must not fetch just to learn whether the tree is there, and an absent mirror must stay visible rather than be scanned as an empty contest.
How: Add `inspect_mirror(dest: Path, runner=default_runner) -> str` beside `sync_mirror`: `"missing"` if `dest / ".git"` is not a directory, else `runner("rev-parse", "HEAD", cwd=str(dest))` stdout stripped, or `"error"` if that returns non-zero. Leave `sync_all` as the only network entry. Funnel prep calls `inspect_mirror(Path(mirrors_dir) / "solodit_content")` before S1; prefer `read_manifest` when a manifest is already present so git is optional on the measurement box.

## Nice-to-haves
- `timeout` on `default_runner` so a hung origin fails soft instead of stalling prep.
- A distinct status from `sync_mirror` when `dest` exists but `.git` does not, instead of collapsing that case into a bare `"error"`.
- Include the landed SHA in the `sync_all` progress line once `rev-parse` exists.
- In `contest_coverage`, also count `*.sol` under a resolved root so an empty contest directory is disclosed separately from a missing one.

- ACCEPT pinned ref + manifest.json (resolved SHA, read_manifest twin) - VERIFIED: sync records no commit; "updated" moves the denominator under the next sync.
- ACCEPT resolve_contest_root + load_remappings + contest_coverage - VERIFIED: nothing maps contest id -> tree; per-tier independent searches make a miss look like zero findings; aligns with p2_static's remapping lineage.
- ACCEPT inspect_mirror read-only readiness (missing/SHA/error, no fetch).
- DEFER 4 nice-to-haves (default_runner timeout, dest-without-.git distinct status, SHA in progress line, sol count in coverage).
