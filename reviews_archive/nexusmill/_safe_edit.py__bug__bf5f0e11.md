# BUG review: _safe_edit.py

- source: `C:\Users\User\source\repos\Nexusmill\_safe_edit.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:58
- tokens: in 2725 / out 2439
- est cost: $0.0448

---

## Verdict
Not safe to ship as-is: two of its core promises — "original left untouched on ANY failure" and the "shrink guard" — are broken in code. The single biggest risk is that a failed write/compile path can leave a broken or partial file on disk while the tool claims the original was restored.

## Bugs & vulnerabilities

**[HIGH] On-disk py_compile failure leaves the broken file in place** - `line 111-112`
- What: After `safe_write` succeeds, if the final `_py_ok(path)` fails, the function raises but never restores the backup. The docstring (line 14, 84-85) promises "restoring the original on ANY failure."
- Trigger: Any post-write compile failure (e.g., a write that verified byte-for-byte but the interpreter state/encoding differs, or a non-UTF-8-read-related compile error on the real path).
- Impact: A syntactically broken `.py` file is left on disk while the caller is told the operation failed — worst of both worlds, and exactly the corruption this tool exists to prevent.
- Fix: On failure at line 111, re-run the backup-restore loop (factor it out of `safe_write`) before raising.

**[HIGH] Shrink guard is dead code — it can never fire** - `line 92`
- What: `if len(out) < int(len(src) * min_ratio) and len(new) >= len(old)`. Since `out` is `src` with `old`→`new` substituted, when `new >= old` the output can only grow or stay equal; `len(out) < len(src)*0.5` is then impossible. Conversely, when `new < old` (actual shrinkage), the second condition is False so no check happens.
- Trigger: Any edit that shrinks the file, e.g. replacing a 500-line block with a one-liner — precisely the "accidental mass-deletion" the guard claims to prevent.
- Impact: The documented truncation/deletion safety net does nothing.
- Fix: Drop the `and len(new) >= len(old)` clause (the ratio check alone is the guard), or compare against the *expected* size `len(src) - count*(len(old)-len(new))`.

**[MEDIUM] "Original restored" message is false when restore fails or file didn't pre-exist** - `line 61-70`
- What: If the restore loop never verifies, the code silently falls through to `raise ... "original restored"` anyway (the `for` loop has no `else`/failure check). And if the file did not exist before (`backup is None`), the partially-written new file is simply left on disk.
- Trigger: A mount that consistently truncates (the exact failure mode this tool targets), or `safe_write` on a new path.
- Impact: Silent data loss/corruption with a misleading error message; for new files, a torn file is left behind.
- Fix: Track restore success in a flag and include it in the error; if `backup is None` and all retries fail, `os.remove(path)` (best-effort) to avoid leaving a partial file.

**[MEDIUM] Non-atomic in-place write; no concurrency protection** - `line 51, 63`
- What: `open(path, "wb")` truncates the target file before writing. A crash/kill between truncate and write leaves an empty/partial file with the backup only in process memory. Two concurrent invocations can interleave writes, and each one's read-back can pass against the other's content.
- Trigger: Process kill, power loss, or two `_safe_edit.py` processes editing the same file.
- Impact: Permanent loss of the original content — the catastrophic case the tool claims to defend against.
- Fix: Write to `tempfile` in the same directory, verify, then `os.replace()` (atomic on POSIX and Windows), and take a lock file or `msvcrt`/`fcntl` lock around the whole read-modify-write.

**[MEDIUM] Unhandled exceptions in CLI paths crash with traceback** - `line 122-127, 133, 144-145`
- What: Only `SafeEditError` is caught (line 153). `IndexError` (missing args), `binascii.Error`/`ValueError` (bad base64), `UnicodeDecodeError` (non-UTF-8 payload or file), `int(...)` `ValueError` for `--count`, and `FileNotFoundError` all propagate.
- Trigger: `python _safe_edit.py replace f.py !!! xxx` or a truncated argv.
- Impact: Non-zero exit is preserved, but errors are noisy and, worse, a crash *after* `replace_in_file` partially... (in this code all raises happen pre-write, so the main harm is operability, not corruption).
- Fix: Catch `(IndexError, ValueError, binascii.Error, UnicodeDecodeError, OSError)` in `_main` and return 2 with a usage message.

**[LOW] `verify` and `replace` read files as UTF-8 without error handling; `.PY`/case variants bypass the compile gate** - `line 86, 94, 144`
- What: `path.endswith(".py")` misses `X.PY`; non-UTF-8 files raise uncaught `UnicodeDecodeError`.
- Fix: Use `path.lower().endswith(".py")`; wrap reads in try/except and report via `SafeEditError`.

**[LOW] py_compile leaves `.pyc` artifacts behind** - `line 75, 97-105`
- What: `py_compile.compile(tmp)` writes a `__pycache__/*.pyc` into the temp directory that is never removed (only `tmp` itself is deleted); repeated edits accumulate garbage in the temp dir.
- Fix: Pass `cfile=os.devnull` (or a path inside the same temp scope) to `py_compile.compile`.

## Missing safeguards
- Validate `old != ""` in `replace_in_file`: `src.count("")` returns `len(src)+1` and `replace("", new)` splices `new` between every character — with the dead shrink guard, nothing stops this.
- Validate `count >= 1` and `0 < min_ratio <= 1`.
- No test coverage for the failure paths: restore-failure, new-file write failure, shrink guard triggering, or concurrent writers — all the paths that are currently broken.
- `--count` parsing should reject `--count` as the last argv element and non-integer values gracefully.
- `safe_write` should use a temp-file-then-`os.replace` pattern and fsync the directory after rename for real durability.