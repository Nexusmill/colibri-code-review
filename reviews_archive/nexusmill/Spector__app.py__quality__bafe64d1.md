# QUALITY review: Spector\app.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:34
- tokens: in 2992 / out 1467
- est cost: $0.0310

---

## Health score
7/10 — Small, readable, and focused, but triplicated upload/cleanup boilerplate and terse style are the main maintainability drags.

## Improvements

**[HIGH] Upload-and-cleanup pattern duplicated three times** - `ingest`/`find`/`import_pack` (lines 99–184)
- Issue: `ingest`, `find`, and `import_pack` share the identical skeleton (get file → `_save_upload` → try → 500 → finally remove with swallowed exceptions). Three copies means fixes (e.g., better error mapping) must be applied in triplicate, and each is one missed edit away from diverging.
- Better: extract a single decorator/helper that owns the upload lifecycle:

```python
from contextlib import contextmanager

@contextmanager
def _uploaded_tempfile():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400  # or raise/abort(400)
    p = _save_upload(f)
    try:
        yield f, p
    finally:
        _quiet_remove(p)
```

Each endpoint then becomes 3 lines of actual logic. Also centralize the `except Exception → {"error": str(e)}` pattern into one error-handler helper (`_fail(e, status=500)`) used by all six endpoints that repeat it.

**[MEDIUM] Bare `except Exception: pass` on temp-file cleanup** - lines 110–111, 125–126, 135–136, 183–184
- Issue: Silently swallowing removal errors hides real problems (permission issues, locked files) and litters temp dirs with no signal. It also appears four times — classic DRY violation.
- Better: one helper:

```python
def _quiet_remove(p):
    try:
        os.remove(p)
    except OSError:
        pass  # temp file best-effort cleanup; OS will reap on reboot
```

Catch `OSError` specifically (not `Exception`) and keep a short comment justifying the silence.

**[MEDIUM] `dna_sig` reaches into warehouse internals** - lines 79–82
- Issue: `wh().db.execute("SELECT dna FROM parts ...")` couples the web layer to the warehouse's schema and storage format (raw `float64` blob). Schema changes break this route silently, and the route is the only one bypassing warehouse's API — inconsistent with every other handler.
- Better: add `Warehouse.get_dna(pid) -> bytes | None` and let the route only do numpy downsampling (or move even that into a `dna.py` helper for testability).

**[MEDIUM] Unclear/magical naming and single-letter variables** - `wh()`, `W`, `s`, `t`, `p`, `d`, `n`, `v`, `lo`, `hi`
- Issue: `W` and `wh()` are needlessly terse — `wh()` reads like noise at every call site. `n = 48` (line 85) is an unexplained magic constant. These force readers to hold context instead of reading it.
- Better: `import warehouse` (drop the alias, it's already short), `def warehouse_client()` or `_get_warehouse()`, `DOWNSAMPLE_BINS = 48`, and full names in `dna_sig` (`vec`, `lo`→`vmin`…).

**[LOW] Function-local imports** - lines 33, 78
- Issue: `urllib.parse.urlparse` and `numpy` are imported inside functions. Stdlib imports at module top are free; numpy's lazy import is a defensible cold-start optimization but should be commented as such.
- Better: move `urlparse` to the top; annotate the numpy import (`# lazy: keeps app startup off numpy's ~200ms import cost`).

**[LOW] Semicolon-joined statements hurt readability** - lines 56, 66, 131, 168
- Issue: `fd, p = tempfile.mkstemp(suffix=ext); os.close(fd); f.save(p); return p` packs four statements on one line; line 168 does file creation and warehouse call on one line. Harder to scan, harder to set breakpoints, against PEP 8.
- Better: one statement per line — zero cost.

**[LOW] Inconsistent error status codes** - lines 108/123 (500) vs 146 (400) vs none in `export`/`rename`
- Issue: `delete` maps all exceptions to 400 while sibling endpoints use 500; `export` (line 168) and `rename` (line 208) don't catch exceptions at all, so they fall through to Flask's HTML error page while everything else returns JSON. Inconsistent API contract.
- Better: register a Flask `@app.errorhandler(Exception)` returning JSON, delete the per-endpoint try/excepts, and let the warehouse raise typed errors mapped to statuses.

**[LOW] `_send_temp` cleanup lambda is cryptic** - line 50
- Issue: `lambda: os.path.exists(p) and os.remove(p)` uses boolean short-circuiting for side effects — clever, not clear.
- Better: `resp.call_on_close(lambda: _quiet_remove(p))` reuses the helper from above.

## Quick wins
- [ ] Split `import os, tempfile` onto two lines (line 4).
- [ ] Rename `_WH`/`wh()` to something pronounceable (`_warehouse_instance` / `_get_warehouse()`).
- [ ] Replace `n = 48` with a named constant `BARCODE_BINS = 48`.
- [ ] One statement per line in `_save_upload`, `stats`, `reproduce`, `export`.
- [ ] Move `from urllib.parse import urlparse` to module top.
- [ ] Update the module docstring (lines 1–3) — it lists 8 routes but the file has 17; stale comments are worse than none.
- [ ] Use `os.remove` → `Path.unlink(missing_ok=True)` (Python 3.8+) to drop the exists-check idiom.
- [ ] `int(request.form.get("top", 6))` (line 121) can raise `ValueError` → returns 500; validate or use `int(..., default)` semantics for a clean 400.

## What's done well
- The `_origin_guard` is genuinely well done: correct threat model, layered checks, and an explanatory docstring that states *why*, not what.
- `_save_upload` and `_send_temp` are good small abstractions — the right instinct, just not applied to the endpoint boilerplate around them.
- Handlers are uniformly thin: HTTP concerns stay in the routes, domain logic stays in `warehouse` (with the one `dna_sig` exception), which keeps the module easy to navigate.