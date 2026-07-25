# Colibri review — PatternSkin/selectcore.py (bug) — ROUND 2

- **source:** `PatternSkin/selectcore.py`
- **model:** claude-opus-4-8[1m] (in-session; lead verification of a primed sonnet scanner)
- **sha256:** `ab0edae14d201c5e8f19f6d34a726cbbdd066815ef92c10a9568ecd1cebd1445`
- **date:** 2026-07-24
- **mode:** bug · ROUND 2 (stale-file DELTA vs r1)
- **context pack:** `get_symbol_source` on `MeshCtx.harmonic` / `MeshCtx.geodesic_verts`; call-site
  reality from `find_references` — the ONLY live callers of `harmonic()` are
  `PATTERNSKIN_OT_sel_strokecut._cut` and `PATTERNSKIN_OT_sel_clickcut.execute` (both in
  `__init__.py`), each passing `fixed_val = [0]*len(va) + [1]*len(vb)` (0/1 constraints).
  r1 (streak reset) fixed the unbounded `_CTX` cache + face-content cache signature. This DELTA
  round reviews only what is new since r1.

## Verdict
Shippable as-is. A primed sonnet scanner raised one **[HIGH]** (`harmonic()` PDE-inconsistent field
under overlapping Dirichlet sets) plus three LOW/defensive items. **Phase-3 verification against the
real bytes + live call sites REFUTED the HIGH as a *live* defect** and showed the proposed dedup fix
would *change* working cut behaviour. Net code change this round: **none** (correctly). 0 live defects
confirmed.

## Fixed since last review
- r1's `_CTX` LRU bound + face-content signature — still present, unchanged. No regression.

## Findings — Phase-3 dispositions

**[HIGH → REFUTED as a live defect; LATENT only] `harmonic()` overlapping-Dirichlet inconsistency** — `line 207-226`
- **Claim:** when the two constraint groups share a vertex, `Wfb = W[fi][:, fixed_idx]` keeps a
  DUPLICATED column, so `rhs = -Wfb.dot(fixed_val)` SUMS both target values into the free equations
  while `x[fixed_idx] = fixed_val` stamps last-wins → `W@x != 0` at the seam (scanner probe: residual 0.50).
- **Phase-3 (proof, `junk/_selectcore_harmonic_verify.py` on HEAD bytes):** the algebra collapses to
  `residual = -W·(sum − last_stamp)` at the shared vertex. The **only** live callers pass **0/1**
  constraints, for which `sum(0+1) == last-wins(1)` **identically** → residual **5.55e-16**, a fully
  consistent harmonic field. The inconsistency needs *conflicting NONZERO* values (probe with 0.3/0.7
  → residual **0.15**), which **no call site passes**. The scanner's probe used non-representative
  values. Applying the dedup fix would FLIP shared-vertex values 1→0 (first-wins) and **alter live cut
  output near seams for zero correctness gain** — an untestable-in-Blender behaviour change. **Refuted
  for live; recorded LATENT → deferred SC-3.** (A future robust fix must preserve the 0/1 result.)

**[MEDIUM → DEFENSIVE only, not a live bug] `geodesic_verts()` no finiteness guard** — `line 125-167`
- Asymmetric with `harmonic()`'s `isfinite` check. Phase-3: for any valid mesh the heat solve is
  regularised (`W − 1e-8·I`) and `div` is built with `1e-12`-floored denominators → `phi` is **always
  finite**; the guard would be **dead defensive code** that never fires. Not a live defect; the honest
  disposition is to *not* add never-firing code this round. Folded into SC-3 (add only alongside a real
  degenerate-input path).

**[LOW] degenerate (zero-area) triangle → `[0,0,0]` normal** — `line 23-25`, `__init__ 33-42`
- Real but low-magnitude: a repeated-vertex face yields a null normal that mildly biases the
  dihedral/concavity classification. Reject-or-warn needs a decision (existing meshes may pass the
  current tolerance). Deferred SC-3.

**[LOW] `_geo_cache` eviction is FIFO not LRU** — `line 163-164`
- Cache-efficiency nit (drops oldest-inserted, not least-recently-used). Deferred SC-3.

## Missing safeguards
- None actionable this round without risking a working path. All four items are latent / defensive /
  nit and are scoped in deferred manifest **SC-3** with exact patches + the constraint that any
  harmonic change must preserve the live 0/1 cut result.

## Outcome
- **Live defects fixed:** 0. **Code changed:** none (reverted the exploratory dedup after Phase-3).
- **Refuted:** 1 (harmonic HIGH as a live defect — banked in `_refuted_ledger.json`).
- **Deferred:** SC-3 (4 items).
- clean_streak this round: +1 (zero live-confirmed).
