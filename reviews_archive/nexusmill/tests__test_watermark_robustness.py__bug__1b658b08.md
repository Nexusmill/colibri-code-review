# BUG review: tests\test_watermark_robustness.py

- source: `C:\Users\User\source\repos\Nexusmill\tests\test_watermark_robustness.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:24
- tokens: in 1907 / out 1473
- est cost: $0.0278

---

## Verdict
Mostly safe to ship — it's a test harness, so security risk is low — but it leaks file handles on every `Image.open` and hardcodes a POSIX-only `/tmp/wm` path that will break or misbehave on Windows (where this repo clearly lives, given `tests\...`). Biggest single risk: unclosed image handles plus the fixed temp directory make the test flaky under parallel/repeated runs and non-portable.

## Bugs & vulnerabilities

**[MEDIUM] Unclosed file handles from `Image.open`** - `lines 44, 47, 69`
- What: `Image.open()` returns lazily-loaded objects holding open file descriptors; none are closed or used as context managers.
- Trigger: Normal execution; worse in a loop or repeated runs (`pytest --count`, watch mode).
- Impact: File-descriptor exhaustion on long sessions; on Windows, open handles also block deleting/overwriting the files (breaks re-runs and the later `.save` to the same paths).
- Fix: Use `with Image.open(...) as im:` everywhere, or `im = Image.open(...); im.load(); im.close()` after materializing.

**[MEDIUM] Hardcoded POSIX temp path breaks portability and parallel runs** - `lines 40, 42, 43, 53, 56, 61, 65, 68-70`
- What: Output directory is literally `/tmp/wm` — invalid/oddly-resolved on Windows (resolves to `<current-drive>:\tmp\wm`), and fixed filenames (`a.png`, `j95.jpg`, ...) collide if two runs execute concurrently (pytest-xdist, CI matrix).
- Trigger: Running on Windows, or two simultaneous runs.
- Impact: `os.makedirs`/`save` failures or interleaved writes producing corrupted images and false pass/fail results (race condition).
- Fix: `tmpdir = tempfile.mkdtemp(prefix="wm_")` (or pytest's `tmp_path`), and build all paths from it.

**[LOW] Unhandled exceptions from attack functions abort the whole grid silently mislabeled** - `lines 76-81`
- What: `path = fn()` and `recover(path)` are unguarded. Any save failure, unsupported resize size, or `extract_png` raising on a malformed/decoded image kills the run before the summary, and there is no per-attack failure record.
- Trigger: A library error in `png_stego.extract_png` (e.g., on the crop or JPEG-then-scale output), or a zero/invalid dimension if image params are ever changed (e.g., tiny `w` in `make_test_image` → `resize` to 0×0).
- Impact: One bad attack hides results for all others; silent failures in the robustness claim this file exists to measure.
- Fix: Wrap each attack in `try/except Exception as e: print(f"{name:28} ERROR {e}"); continue`.

**[LOW] Potential `KeyError` in `recover`** - `line 35`
- What: `info["set"]` / `info["seq"]` assume `verify_serial` always populates those keys when `ok` is truthy. If it returns a partial dict (e.g., a legacy payload form), the test crashes mid-grid.
- Trigger: `verify_serial` returning `ok=True` with a dict missing `set` or `seq`.
- Impact: Unhandled exception aborts the run (compounds the issue above).
- Fix: `info.get("set") == SET_ID and info.get("seq") == 7`.

**[LOW] Trailing-zero token comparison can misclassify** - `line 33`
- What: `tok == TOKEN` compares the extracted token to the embedded one, but many stego extractors return fixed-length buffers with padding stripped differently than `make_token` produced. An exact-match failure here isn't necessarily a real failure, yet anything not exact falls through to serial-verification which may report "recovered-but-mismatch" — a false negative in a measurement test.
- Trigger: Extractor trimming/padding bytes differently than `build_payload`/`make_token`.
- Impact: Wrong robustness numbers (the entire purpose of the file).
- Fix: Compare after normalizing both sides (e.g., `tok.rstrip(b"\0") == TOKEN.rstrip(b"\0")`) or compare parsed payloads.

## Missing safeguards
- No assertion/test outcome: the script only prints; nothing ever fails CI (`assert npass >= threshold`), so regressions pass silently.
- No cleanup of `/tmp/wm` artifacts (grows across runs; also leaks PII-bearing tokens embedded in test images left on disk — minor, but `Jane Buyer / jane@x.com` tokens persist in world-readable `/tmp`).
- No check that `embed_png` succeeded / that `marked.png` exists before opening (line 44 would raise an opaque `FileNotFoundError`).
- No test of the negative path: no attack variant expected to *destroy* the watermark, so the `recovered-but-mismatch` branch (lines 35-37) is never exercised.
- `make_serial`/`make_token` calls at module import time (lines 18-19) run even under test collection — they should be inside `main()` or fixtures so import of the module is side-effect-free.