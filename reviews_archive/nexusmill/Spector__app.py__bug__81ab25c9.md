# BUG review: Spector\app.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:51
- tokens: in 5922 / out 2480
- est cost: $0.0550

---

## Verdict
Mostly shippable for a local-only app: the origin/host guard is solid, uploads are size-capped, and temp files are (mostly) cleaned up. The biggest risks are correctness/robustness issues — temp-file leaks on failed uploads, NaN leaking into JSON responses, and a per-file error in batch ingest that can abort the whole batch.

## Bugs & vulnerabilities

**[MEDIUM] Batch ingest: one bad upload aborts the entire batch and leaks temp files** - `line 257`
- What: `p = _save_upload(f)` sits *outside* the per-file `try`. If `f.save(p)` raises (disk full, read error on the multipart stream), the `finally: _quiet_remove(p)` never runs, the mkstemp'd file is orphaned on disk, and the exception propagates to the global 500 handler — killing the whole batch instead of recording a per-file failure, contradicting the docstring ("per-file results, never all-or-nothing").
- Trigger: a batch upload where one file's stream fails mid-save, or the temp volume fills up.
- Impact: temp-file litter accumulates; one bad file silently discards results for all the others (client gets a bare 500, not partial results).
- Fix: move `_save_upload(f)` inside the `try`, track `p = None` and remove it in `finally` if set.

**[MEDIUM] NaN/Inf in Shape-DNA blob produces invalid JSON** - `lines 235-237`
- What: If the stored DNA vector contains NaN or ±Inf (corrupt blob, degenerate mesh), `vmin`/`vmax` become NaN, the `vmax > vmin` guard is False when NaN is involved (NaN comparisons are False → falls into `v * 0`... actually with one NaN element `v.min()` is NaN, so `vmax > vmin` is False and you emit `v * 0` which is still NaN for that element). `jsonify` serializes bare `NaN`, which is invalid JSON; browser `response.json()` throws.
- Trigger: a corrupt/legacy DNA blob or a part whose geometry produced NaN features.
- Impact: the `/api/dna/<pid>` tile endpoint returns a body clients can't parse — silent UI breakage.
- Fix: `v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)` right after `np.frombuffer`.

**[LOW] `_send_temp` can litter temp files on Windows** - `lines 125-129`
- What: `send_file` may still hold an open handle to `p` when `call_on_close` fires (and on Windows `os.remove` of an open file fails); `_quiet_remove` then silently swallows the failure.
- Trigger: Windows deployment; client disconnects mid-download can also leave the file depending on server teardown.
- Impact: temp directory slowly fills with `.stl`/`.spectorpack` files; failure is silent by design.
- Fix: pass a file object you close+delete in the close callback, or log the failure instead of swallowing it.

**[LOW] `library()` sort/paging inconsistencies** - `lines 195-209`
- What: (a) docstring advertises `sort=date` but it isn't handled (silently ignored — caller thinks it sorted, it didn't); (b) `sort=size` keys on `nfaces`, not any size field, and sorts ascending while SQL default is DESC — inconsistent; (c) `offset` without `limit` is silently ignored (legacy branch returns the full list regardless of offset).
- Trigger: `?sort=date`, `?sort=size`, or `?offset=50` alone.
- Impact: silently wrong/unexpected ordering and paging — silent failure class.
- Fix: implement `date` sort (or reject unknown sorts with 400), key size on the real field, and apply offset even when `limit` is 0.

**[LOW] Non-integer `SPECTOR_MAX_UPLOAD_MB` / `SPECTOR_PORT` crashes the process at startup** - `lines 25, 419`
- What: `int(os.environ.get(...))` with no fallback; a malformed env var raises `ValueError` at import time / `__main__`, killing the app with a bare traceback.
- Fix: wrap in try/except and fall back to the default with a log line.

## Missing safeguards
- No validation that `pid` route params are well-formed (e.g. regex/length) before they're used as DB keys and as `download_name` (Werkzeug sanitizes the header, but a strict whitelist would be cheap).
- `/api/backup` accepts any absolute path with no guard against pointing at the library root itself or a system directory — a "don't back up into your own warehouse" check should exist.
- The origin guard blocks *all* non-browser local clients (curl, scripts) from POST since it requires Origin/Referer; if that's intentional, document it and return a clearer error, otherwise allow a loopback-only token.
- No test coverage evident for: batch ingest partial failure, NaN DNA blobs, corrupt-blob `np.frombuffer` path, paging edge cases (`offset` without `limit`, negative/huge `limit`), and the origin guard's IPv6/bracketed-Host cases.
- Per-request upload cap exists, but there's no cap on *number of files* per batch ingest — a 512 MB request of thousands of tiny files still forces thousands of warehouse transactions in one request.