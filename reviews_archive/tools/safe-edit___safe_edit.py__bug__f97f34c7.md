# Colibri review — safe-edit/_safe_edit.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\safe-edit\_safe_edit.py`
- **Model:** claude-fable-5 (in-session), gating GLM-5.3-flash findings
- **sha256:** `f97f34c7eb167837e371b63432ec5a94b7033fcffa59c30494616428abdc202e` (GLM reviewed the same bytes)
- **Date:** 2026-09-02 · **Mode:** bug
- **Context:** the G8 STANDING-ORDER write tool — every repo file write in every session routes through `safe_write`/`replace_in_file` (write→fsync→reread→byte-compare→atomic replace, py_compile gate). Defects here touch all repos, so the bar is high.
- **Verification:** the newline finding was driven through the real module (scratchpad `safeedit_probe.py`); fsync/lost-update by read.

## Verdict
The core write-verify-replace path is sound, but `replace_in_file` silently rewrites newline style on any non-uniform file — a real corruption in the tool trusted to never corrupt.

## Bugs & vulnerabilities

**[MEDIUM] `replace_in_file` rewrites the whole file's newline style, corrupting mixed / lone-CR files** — `crlf = b"\r\n" in orig_bytes` + `out.replace("\n","\r\n")` — CONFIRMED (probe)
- Driven: a file with ONE CRLF line among five LF lines came back with ALL five lines CRLF (`\r\n` count 1→5, bare-LF 5→0). The docstring promises "the file's original newline style is preserved" — true only for uniformly-LF or uniformly-CRLF files. A lone-CR file is likewise fully converted, and the rewrite fires even on a no-op edit.
- Impact: bytes far outside the intended span change silently; the resulting diff touches every line (review/gate noise) and can flip a file's endings under the author's feet. Because this is the universal write tool, any source file carrying a stray CRLF (docstring, cross-platform edit) is exposed.
- Fix: only convert newlines inside the replaced span, or refuse a non-uniform file loudly; skip the write entirely when `out == src`.

**[MEDIUM] `safe_write` swallows a real `fsync` failure, then reports verified success** — `except OSError: pass` on `os.fsync` — CONFIRMED (read)
- A genuine I/O error (ENOSPC/EIO) is swallowed identically to "fsync unsupported here"; the reread is served from page cache so the byte-compare passes and `os.replace` lands — the self-verifying contract is voided exactly when the disk is failing. Fix: re-raise unless `errno in (EINVAL, ENOTSUP, EBADF)`; keep the exemption for the Windows dir-fsync.

**[MEDIUM] `replace_in_file` is an unguarded read-modify-write (lost update)** — read at top vs `safe_write` at bottom — PLAUSIBLE (per GLM; construction-level, matches the store.py/manifest race class)
- Two concurrent edits of one file both read the original and both replace; `os.replace` atomicity hides the interleaving. [[nexusmill-concurrent-sessions]] (Damien runs 2+ sessions) makes this reachable. Fix: advisory lock or re-stat-before-replace.

**[LOW] retry loop only retries on mismatch, not transient `OSError`, and has no backoff** — CONFIRMED (read). A transient Windows sharing violation on `os.replace` aborts instead of retrying — the exact failure the retry exists for. Fix: count `OSError` as retryable + small sleep between attempts.

**[LOW] `verify` on a non-UTF-8, non-`.py` file raises instead of reporting size/lines** — `open(path,"r",encoding="utf-8")` — CONFIRMED (read). Fix: read `"rb"`, count `b"\n"`.
