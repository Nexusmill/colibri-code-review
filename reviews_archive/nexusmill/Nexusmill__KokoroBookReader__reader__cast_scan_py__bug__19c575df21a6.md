# scan 19c575df21a6 (batch batch-1790102485-CohugJPtsu6xmG7xurNQ via z-ai/glm-5.3:batch)

Reviewed all five files line-by-line: cast_scan.py (quote_ranges/compile_analysis/chunks/analyze_book/ask_model/ensure_backend/unload/CastScanJob), importers/text.py, importers/epub.py, importers/converter.py, importers/kindle.py, and ui/window.py (ImportJob lifecycle, close/job handshake, update_reading/tick).

Areas checked and ruled out as defects (so they aren't re-litigated): quote_ranges span arithmetic (cross-sentence continuation, paragraph reset, and the compact/merge step are exactly text-preserving — the assert cannot fire); the alias redirect/canonical merge cannot cycle (redirect targets have strictly longer names); the `except LookupError` resume trick cannot swallow KeyError/IndexError from compile_analysis (audited — no such paths exist there); `urllib.error` is usable after `import urllib.request` (urllib.request imports it); the `done_reason=="length"` split recursion terminates and merges cleanly; epub `safe_name` blocks `..` after `normpath`, so legal OPF-relative `../` hrefs stay inside the archive while root-escaping ones are rejected; converter subst cleanup handles both changed and vanished mappings; the window close/job_finished handshake has no double-shutdown, orphaned thread, or temp-dir leak; the run()-finally problem overwrite in CastScanJob is deliberate prioritization (the unload failure is the actionable error and the analysis error resurfaces on retry); the ollama digest comparison matches this app's bundled service (a mismatch would have made every scan fail, contradicting the verified working scan-resume flow).

VERDICT: BLOCK

1. **Unhandled OSError on per-file operations in `manifest()` aborts the whole Kindle scan with a raw error**
   - **File:** KokoroBookReader/reader/importers/kindle.py
   - **Line:** 52 (`size = path.stat().st_size`), 58–59 (`with path.open("rb")` / `stream.read(...)`); same gap reachable via `shutil.copyfile` in `snapshot()` (~line 90)
   - **Trigger:** Any file inside a `*_EBOK` download folder that cannot be stat'd/opened/read while a scan or snapshot runs — most plausibly a file still exclusively locked by the Kindle app during an active download (the exact state the code's own "Download is unavailable; finish downloading and retry." message anticipates), or a sharing violation/ACL error. The walk guards only `directory.iterdir()` (lines 31–34); the per-file `stat`/`open`/`read` calls have no guard, so `PermissionError`/`OSError` propagates raw out of `manifest()`.
   - **Impact:** `scan_kindle()` aborts on the first unreadable file, so **zero** candidates are returned even though every other download is readable; the user sees "Could not import this book: [WinError 32] …" — a raw, mislabeled message (says "import" for a scan) with no recovery guidance, and the book can't be discovered or imported until the lock clears. In `snapshot()` the same gap surfaces a raw OS error mid-import instead of the intended `SourceChanged` guidance.
   - **Fix:** Wrap the per-file block in the same guard used for `iterdir` (SourceChanged is a ValueError, so the `cancelled()` raise inside the loop passes through untouched):
     ```python
     try:
         size = path.stat().st_size
         total += size
         if size > 512 * 1024**2 or total > 1024**3 or len(files) >= 10000:
             raise SourceChanged("Download exceeds the supported size.")
         digest.update(path.relative_to(root).as_posix().encode("utf-8"))
         digest.update(b"\0")
         with path.open("rb") as stream:
             for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                 if cancelled():
                     raise SourceChanged('Import cancelled.')
                 digest.update(chunk)
         digest.update(b"\0")
     except OSError as exc:
         raise SourceChanged("Download is unavailable; finish downloading and retry.") from exc
     files.append(path)
     ```
     Additionally, in `scan_kindle()` catch `SourceChanged` per candidate and skip that directory (recording it as unavailable) so one in-progress download no longer blanks the entire scan result.
