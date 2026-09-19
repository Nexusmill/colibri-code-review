# BUG review: tests/test_accel_tiers.py

- source: `tests/test_accel_tiers.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `34a43a1b4f5a9292f96300e628d18dc0c06345539eddc6105c9d5bcf892966ea`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: jCodemunch outline; contract sources accel.get_xp (998-1019), capabilities (71-114), nearest (901-937), _worker_request (1294-1305), scipy_ok (137-140), _torch_device (1022-1031), best_tier (117-127), worker_tier_gap (856-876); _SCIPY_OK assignments (accel.py:131/187/191/255); prior K3 review 6d71a590; remediation rows GROK-AC3 (async probe redesign); live run (crash at line 51) + live flag probe; git log -S (label present since 8ffdf8cd 2026-06-20).
- delta against: .colibri_reviews/tests__test_accel_tiers.py__bug__6d71a590.md (moonshotai/kimi-k3, 2026-07-20)

---
## Verdict
DEAD on this machine: the file aborts on its very first check, before any of its nine sections run, and has since the repo's first commit. When the crash is fixed, its SciPy-tier section will still be measuring numpy against numpy.

## Bugs & vulnerabilities

**[HIGH] A non-cp1252 glyph in the first check label crashes the whole matrix** - `line 51` (`max|Δ vs numpy|`)
- Trigger: any stdout that encodes as cp1252 - this Windows console, and the pipe `_runtests.py` gives it.
- Live: `python tests/test_accel_tiers.py` -> `UnicodeEncodeError: 'charmap' codec can't encode character U+0394` raised from `check()` (line 25) via line 51; exit 1; zero checks executed. `git log -S` puts the label in the initial commit 8ffdf8cd (2026-06-20).
- Impact: every claim in the docstring (numpy/SciPy/torch/CuPy parity, device selection, fallback chain, gpu detection, worker_tier_gap) is unverified on Windows. The K3 review of 2026-07-20 read the file and never ran it.
- Fix: ASCII label (`max|delta vs numpy|`) or `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at the top.

**[HIGH] Section 5 never exercises the SciPy tier it names** - `line 88-94`
- What: `force(scipy=True)` writes `_CAPS["scipy"]`, but `capabilities()` (accel.py:71-114, non-refresh path) overlays `c_snap["scipy"] = scipy_ok()`, which reads the async probe flag `_SCIPY_OK` (accel.py:131, None until a probe finishes). No probe runs before section 7's `refresh=True` (line 112), so `nearest()` (accel.py:901-937) takes the numpy path both times.
- Live probe: after `force(scipy=True)`, `capabilities()["scipy"]` is False, `_SCIPY_OK` is None, and zero `cKDTree` instances are constructed during `nearest()`; `_WORKER` is None so the worker path is not the explanation.
- Impact: "SciPy cKDTree == brute-force truth" (92) and "SciPy and numpy tiers agree" (94) compare numpy with numpy - assertions that cannot fail for the property they name. Cause: the GROK-AC3 async-probe redesign changed the contract under the test.
- Fix: set `accel._SCIPY_OK = True` (and restore it) alongside `force(scipy=True)`, or call `accel.probe_scipy()` synchronously first; spy on `scipy.spatial.cKDTree` to assert the tier actually ran.

## Fixed since last review (K3 6d71a590, 2026-07-20)
- #1 "`sys.modules['gpu']` clobbered without save/restore, no finally" - STILL OPEN (111-120). grok-4.3 re-found it.
- #2 "mocked modules can persist inside accel across parity() calls" - VERIFIED-STALE (refuted): `get_xp` imports cupy/torch inside the call (accel.py:1006/1013), nothing is cached at module level, so `parity()`'s sys.modules restore is sufficient.
- #3 "nearest-neighbour tie-break mismatch" - STILL OPEN, theoretical with float64 random data (LOW).
- #4 "stale `tag` masks which statement failed" - STILL OPEN (101-106), LOW.

## Missing safeguards
- Line 123 hard-fails when SciPy is absent (skip instead).
- None of the section-level `force()` mutations outside `parity()` are try/finally.

## External second opinions (grok-4.3, background)
- gpu mock without finally - adopted as K3 #1 (still open).
- "`_torch_device` cuda/mps checks test the wrong path" - REFUTED: `_torch_device` (accel.py:1022-1031) is a pure kind->`torch.device` mapping and `torch.device("cuda")` constructs without a GPU, so the checks test exactly what the function does.
- "60 s wait is flaky" - not adopted: the bound is deliberate (comment 113-115) and the wait exits early on success.
