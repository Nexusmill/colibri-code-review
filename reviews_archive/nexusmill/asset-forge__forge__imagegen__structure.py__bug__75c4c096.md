# colibri gate — asset-forge/forge/imagegen/structure.py (grok round 6)

- **source:** asset-forge/forge/imagegen/structure.py (+ asset-forge-user twin, G23)
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_structure_grok43.md) gated in-session by claude-fable-5
- **sha256:** 75c4c09617a31ff6... (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** bug (grok round 6, first dedicated review)
- **context pack:** LIB-STRUCT-TWINS deferral + curation doctrine + the by-construction pairwise-distance guarantee pre-declared; verified allocate() source + its only caller library_gen.py:246 + a repo-wide `with_census=True` search.

## Verdict
Shippable; one real-but-LATENT contract inconsistency (Grok rated MEDIUM; downgraded to
LOW — no shipped caller exercises the path). The by-construction distinctness guarantee and
the ValueError-on-over-capacity contract are intact.

## Findings after adversarial verification

**[LOW, CONFIRMED but LATENT — downgraded from Grok's MEDIUM] `allocate(n<=0, with_census=True)` returns `{}` instead of the four-axis census shape** — allocate() line 678
- Verified: the `if n <= 0: return ([], {}) if with_census else []` early return yields an empty dict, while the n>0 path returns `census = {"form":{}, "massing":{}, "edge":{}, "incident":{}}`. A caller doing `slots, census = allocate(..., with_census=True)` then `census["form"]` would KeyError on the n<=0 boundary.
- **Downgraded to LOW because the trigger has ZERO live callers:** the only caller of `structure.allocate` is library_gen.py:246, which passes `with_census` defaulted to False (gets `[]`, never the tuple) and n>=1 (per-type count). A repo-wide search for `with_census=True` finds only the def + the twin — nothing calls it. So the incoherent shape is unreachable in shipped code; it's a latent contract-consistency defect, not a live bug.
- Fix (Grok's, correct and trivial): initialize `census = {"form":{},"massing":{},"edge":{},"incident":{}}` before the `n<=0` test and return `([], census) if with_census else []`. A census-returning function should always return the census shape. Worth doing as cheap hardening (a future census/analysis caller — the deferred LIB-STRUCT-TWINS re-measure work is a likely one — would otherwise hit it).

## Refuted and dropped
- No finding on the near-twin similarity — that is the pre-declared, measured, DEFERRED LIB-STRUCT-TWINS observation, not a new defect.
