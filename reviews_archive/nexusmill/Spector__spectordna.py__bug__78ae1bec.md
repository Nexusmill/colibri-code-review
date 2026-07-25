# BUG review: Spector\spectordna.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\spectordna.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:19
- tokens: in 2270 / out 5346
- est cost: $0.0870

---

## Verdict
Safe to ship from a **security** standpoint — this is pure numeric code with no I/O, no deserialization, no secrets, and no attack surface beyond "garbage in." It is **not** fully safe from a correctness standpoint: the module silently produces plausible-looking but wrong DNA vectors on malformed input (negative face indices wrap around, genuine modes get dropped by a sloppy tolerance, shortfalls are zero-padded) instead of failing loudly. Biggest single risk: **silent corruption of the fingerprint database** — bad meshes get indexed with bogus DNA and poison similarity search results with no error raised.

## Bugs & vulnerabilities

**[MEDIUM] Negative face indices silently wrap and corrupt the Laplacian** - `line 29, 33`
- What: `F = np.asarray(F, np.int64)` is used directly for fancy indexing (`V[F[:, a]]`). NumPy wraps negative indices (`-1` → last vertex) instead of raising. There is no check that `0 <= F < nv`.
- Trigger: Any mesh loader that emits `-1` as a "no neighbor"/sentinel value, or a 1-based OBJ-style index that wasn't converted, or simply a corrupt face array containing negatives.
- Impact: The stiffness/mass matrices are assembled from wrong triangles; `shape_dna` returns a confidently wrong fingerprint with no exception. In a search-index pipeline this is a silent, permanent data-corruption bug.
- Fix: After line 29, add `if F.size and (F.min() < 0 or F.max() >= nv): raise ValueError("face index out of range")`.

**[MEDIUM] Zero-mode tolerance can silently discard genuine low eigenvalues** - `line 82-84`
- What: `tol = max(float(vals[-1]) * 1e-8, 1e-12)` uses the *largest computed* eigenvalue as the reference scale, then drops everything below it (`nz = vals[vals > tol]`).
- Trigger: A mesh whose spectrum spans more than ~8 orders of magnitude within the first `k+1` modes (e.g., very fine meshes where λ_max scales like 1/h² while λ₁ stays small — h ≈ 1e-4 suffices), or multi-component meshes whose smallest nonzero mode is tiny.
- Impact: Real, informative low modes are dropped, the DNA shifts (λ₂ becomes "λ₁"), and `scale_invariant` then normalizes by the wrong value (line 86). Fingerprints of the *same* shape at different tessellation densities no longer match — defeating the stated purpose — with no warning.
- Fix: Compare against an absolute/numerical threshold tied to the solver's shift (e.g., `tol = max(abs(sigma) * 10, np.finfo(float).eps * vals[-1] * n)`), or explicitly detect multiplicity of the zero mode via connected-component analysis rather than magnitude thresholding.

**[MEDIUM] Multi-component meshes return fewer than k modes and the shortfall is silently zero-padded** - `line 72, 87-88`
- What: Only `kk = k + 1` eigenvalues are computed, but a mesh with C connected components has C zero eigenvalues (the comment on lines 77-80 acknowledges C exists). After dropping C zeros, only `k + 1 - C` nonzero values remain; `out[:min(k, vals.size)] = vals[:k]` leaves the rest as zeros.
- Trigger: A 3D-print STL with 2+ shells (explicitly called out as "common" in the comment) and `k=50`: you get ≤ 49 real modes and ≥ 1 trailing zero; a part with > k+1 shells yields zero usable modes.
- Impact: Trailing zeros act as "perfect agreement" in `dna_distance`, making unrelated shapes look artificially similar in the high modes. Silent degradation of search quality.
- Fix: Compute `kk = min(k + 1 + C_upper_bound, n - 2)` (or detect C via `scipy.sparse.csgraph.connected_components` first), and raise or return a count of valid modes instead of zero-padding.

**[MEDIUM] ARPACK non-convergence and other solver failures are unhandled** - `line 75`
- What: `_spla.eigsh` can raise `scipy.sparse.linalg.ArpackNoConvergence` (common on large/ill-conditioned meshes, exactly the nonmanifold cases this tool targets) or `RuntimeError` on factorization failure. Nothing catches these; partial results available on the exception object are discarded.
- Trigger: A large or near-degenerate mesh where the shift-invert iterations don't converge in the default iteration budget.
- Impact: Batch indexing jobs crash mid-run with an opaque ARPACK error instead of a diagnostic naming the offending mesh or a retry with more iterations.
- Fix: Wrap the call, catch `ArpackNoConvergence`, and either retry with higher `maxiter`/`ncv` or re-raise a `RuntimeError` that includes mesh size and how many eigenvalues did converge.

**[LOW] All-near-zero fallback returns garbage instead of failing** - `line 84`
- What: If every computed eigenvalue is ≤ tol (`nz.size == 0`), the code does `vals = vals[1:]` — dropping only the first entry and keeping the remaining numerically-zero values.
- Trigger: A mesh whose computed spectrum is entirely numerical noise (degenerate/collapsed geometry, or > kk connected components).
- Impact: Near-zero "eigenvalues" flow into the output unnormalized (line 85's guard skips division), producing a meaningless DNA vector that looks like data.
- Fix: `raise RuntimeError("no nonzero eigenvalues; mesh is degenerate")` in this branch.

**[LOW] Invalid `engine` string silently falls back to cotangent Laplacian** - `line 53`
- What: `want_robust` is False for any unrecognized engine string, so `engine="robuts"` (typo) quietly uses `cotan_laplacian` on a possibly nonmanifold mesh.
- Trigger: Typo or wrong config value for `engine` with a triangle mesh.
- Impact: Wrong operator on bad geometry → wrong DNA, no error.
- Fix: `if engine not in ("auto", "cotan", "robust"): raise ValueError(...)` at the top of `_laplacian` or `shape_dna`.

**[LOW] NaN/Inf vertices propagate silently into the output DNA** - `line 29, 76-88`
- What: No finite-check on `V`. NaN coordinates make the Laplacian NaN; after `eigsh`, `np.abs(np.real(vals))` keeps NaNs, `NaN > tol` is False so the NaN entries vanish into the line-84 fallback, and the result is a NaN- or zero-filled vector with no error (or an obscure ARPACK failure).
- Trigger: A mesh containing NaN/Inf vertex coordinates (common in converted/repaired geometry).
- Impact: Corrupt DNA indexed as if valid.
- Fix: `if not np.isfinite(V).all(): raise ValueError("non-finite vertex coordinates")` before building the operator.

**[LOW] `dna_distance` returns 0.0 for empty/overlapping-empty inputs** - `line 94-97`
- What: `n = min(len(a), len(b))`; if either DNA is empty, `n = 0`, the weighted sum is over an empty array → distance `0.0`, i.e., "identical."
- Trigger: An empty row in `library_dna` (e.g., a failed upstream extraction represented as `[]`).
- Impact: A garbage entry sorts to the top of `nearest()` as the best match.
- Fix: `if n == 0: raise ValueError("empty DNA vector")`.

**[LOW] Degenerate triangles get unbounded cotangent weights** - `line 35`
- What: The denominator is clamped with `np.maximum(norm, 1e-12)`, so a near-zero-area triangle yields a cotangent up to ~1e12, injecting enormous weights into L.
- Trigger: Meshes with sliver/zero-area faces (typical in scanned or booleaned geometry).
- Impact: The spectrum is dominated by numerical junk from the slivers; DNA becomes tessellation-noise-sensitive rather than shape-sensitive.
- Fix: Skip or clamp faces with area below a relative epsilon (e.g., `area < 1e-10 * median_area`), or route such meshes to the robust engine.

## Missing safeguards
- **Input validation in `shape_dna`/`cotan_laplacian`:** no checks for `F` index range (see above), `V.shape[1] == 3`, `F.shape[1] == 3` (a `(M,4)` quad array fails with a confusing `IndexError` at line 33 instead of a clear message), `V` finiteness, or `k` being a positive `int` (`np.zeros(k)` raises a bare `TypeError` for float `k` at line 87).
- **Error handling:** no `try/except` around `eigsh` for `ArpackNoConvergence`; no handling of `robust_laplacian` failures (line 59-60) which raise raw on empty/degenerate input.
- **API contract:** `shape_dna` zero-pads to `k` without reporting how many modes are real (line 87-88) — callers cannot distinguish padding from data. Return `(dna, n_valid)` or document/raise.
- **Mass-matrix floor:** isolated vertices get mass `1e-12` (line 47), creating a near-singular generalized problem; they should be detected and rejected or stripped instead of papered over.
- **Tests that should exist:** negative/out-of-range face indices must raise; NaN vertices must raise; a two-component mesh must yield the same DNA as the single-component case for the first `k+1-C` modes (and the count must be reported); `engine="bogus"` must raise; `eigsh` non-convergence path (mock it) must produce a useful error; scale-invariance property test (`shape_dna(V) == shape_dna(3.7*V)`); empty-input handling for `dna_distance`/`nearest`; degenerate-sliver mesh should not explode the spectrum.