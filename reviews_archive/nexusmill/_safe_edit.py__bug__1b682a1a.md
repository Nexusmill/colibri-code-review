# BUG review: _safe_edit.py

- source: `C:\Users\User\source\repos\Nexusmill\_safe_edit.py`
- model: claude-fable-5 (in-session, max)
- sha256: `1b682a1a6891b0f968920cbf791bbb8d4b44ae288abcd36047ebf6dd4ec87e5a`
- date: 2026-07-22
- mode: bug
- context pack: jCodemunch get_file_outline + search_text — public API (`safe_write`, `replace_in_file`) imported only by junk/se_smoke.py & junk/v20_tools_verify.py; primary real use is the CLI subprocess (`python _safe_edit.py replace|write|verify`), so callers depend on the EXIT CODE (0=ok / non-zero=original intact) and the printed message, not a return value. Consulted: docs/remediation_manifest.json entry 456885e (2026-07-20, "honor its own 'original intact on failure' promise"); builder junk/se_fix.py (fix intent); repo line-ending survey (git autocrlf=false, no .gitattributes, mixed LF/CRLF); prior K3 review bf5f0e11 (stale).

## Remediation status (G35)
- **456885e (2026-07-20, MEDIUM — "original intact on failure"): PRESENT but INCOMPLETE.** The honest-restore fix is present and holding in `replace_in_file` (lines 114-118: on restore failure `note` becomes "RESTORE ALSO FAILED, file may be corrupt"). But the sibling **CLI `write` path (lines 149-156) never received the same fix** and still violates the identical promise — see BUG 1. This is not a regression of the closed entry; it is a gap the entry's fix did not cover (confirmed by junk/se_fix.py: fix #4 hardened replace_in_file, fix #5 added the write-CLI restore WITHOUT the honest message).
- Verified-present (K3-stale fixes), not re-reported: atomic same-dir temp + `os.replace` write with pre-replace byte-compare (lines 48-58); shrink-guard dead `and len(new) >= len(old)` clause removed (line 91); case-insensitive `.py` gate via `.lower()` (lines 93, 141, 164); broad `except Exception` in `_main` (line 173) and `_py_ok` (line 73).

## Verdict
Not fully honoring its headline promise. The atomic write→fsync→reread→byte-compare→replace core is sound (and its binary compare correctly catches truncation), but two real defects remain: the CLI `write` command can leave a broken .py on disk while printing "(original restored)" — the exact bug 456885e closed, surviving in the twin entry point — and `replace_in_file` silently rewrites every line ending of a CRLF file. Both weigh heavily given this is the repo's anti-corruption backstop.

## Bugs & vulnerabilities

**[MEDIUM] CLI `write` reports "(original restored)" even when the restore silently failed** - `line 149-156`
- What: On post-write compile failure the restore call `safe_write(path, backup.decode("utf-8", "surrogateescape"))` is wrapped in `except Exception: pass` (lines 151-152), yet the following raise hard-codes the string `"(original restored)"` (line 156). If the restore raises, the exception is swallowed and the message lies while the broken new content stays on disk. `replace_in_file` was fixed for exactly this class (lines 114-118, using a `note` that flips to "RESTORE ALSO FAILED, file may be corrupt"); the `write` path was not.
- Trigger: reaching the branch needs post-write compile to fail, which `write` invites because — unlike `replace_in_file` — it does NOT pre-compile the payload before the first write; any broken .py content passed to `write` lands here. Then the restore fails and lies via either: (a) DETERMINISTIC — the original .py is not strictly UTF-8 (e.g. a `# -*- coding: latin-1 -*-` file or a stray high byte): `backup.decode("utf-8","surrogateescape")` produces lone surrogates and safe_write's strict `content.encode("utf-8")` (line 44) raises UnicodeEncodeError → swallowed at line 152; or (b) IN-THREAT-MODEL — the intermittently-truncating mount this tool exists for truncates all 6 restore retries so `safe_write` raises SafeEditError → swallowed.
- Impact: the crown-jewel file `PatternSkin/__init__.py` can be left syntactically broken with its original content destroyed, while stdout claims the original was restored — actively steering an operator away from `git checkout` recovery. Exit code is still non-zero, so pure exit-code callers are protected; humans/agents reading the message are misled (blast-radius case for this infra file).
- Fix: mirror replace_in_file — track restore success in a `note` and only print "original restored" when `safe_write(path, backup...)` actually returned; drop `surrogateescape` (or re-encode with a matching errors mode) so a valid original round-trips cleanly; consider pre-compiling the payload before the first write (as replace_in_file does) to shrink the corruption window.

**[MEDIUM] replace_in_file silently normalizes CRLF -> LF on every edit of a CRLF file** - `line 82`
- What: the source is read in text mode — `open(path, "r", encoding="utf-8")` (lines 82-83) — which applies Python universal-newline translation, collapsing every `\r\n` (and `\r`) to `\n` in `src`. The edited result is written by `safe_write` in BINARY (`content.encode("utf-8")`, line 44; `wb`, line 50), emitting LF only. So a single `old -> new` edit silently rewrites EVERY line ending in the file, and a restore (`safe_write(path, src)`) is NOT byte-identical to a CRLF original — breaking the "original untouched/restored" invariant for such files.
- Trigger: editing any CRLF-terminated file. This repo is `autocrlf=false` with no `.gitattributes` and genuinely mixed endings — e.g. `docs/remediation_manifest.json` is 723/723 CRLF lines, and the docstring (line 23) explicitly advertises `replace_in_file("docs/X.md", ...)`. A one-line edit of such a file flips all its line endings; with autocrlf=false git does not re-normalize, so the LF conversion is committed verbatim.
- Impact: silent whole-file mutation the caller never requested (an unbounded spurious diff — every line), and loss of byte-fidelity that the tool's headline promise implies. Non-destructive (text content preserved) so not HIGH, but it corrupts diffs/reviews and the restore-equivalence guarantee. Note: safe_write's own byte-compare is NOT at fault — it is exact binary; the loss happens upstream in the text-mode READ.
- Fix: read bytes and decode explicitly — `open(path, "rb").read().decode("utf-8")` — or pass `newline=""` to disable translation, so `\r` survives, `old`/`new` match the on-disk bytes, and endings are preserved through edit and restore.

**[LOW] safe_write silently clobbers the target's permission bits** - `line 57`
- What: `tempfile.mkstemp` creates the temp at mode 0600; `os.replace(tmp, path)` (line 57) makes the target adopt the temp's mode, discarding the original file's permissions.
- Trigger: any safe_write / replace_in_file on a POSIX filesystem (the sandbox-python path the docstring supports) against a file whose mode is not 0600 (e.g. a 0644 doc, or a group-readable asset).
- Impact: the file becomes owner-only after an edit; other users/services silently lose read access. Largely moot on the Windows mount, real on the sandbox interpreter. CONFIRMED on POSIX.
- Fix: before the replace, `shutil.copymode(path, tmp)` when the target exists (else apply a sane default honoring umask).

**[LOW] No locking — concurrent writers cause silent lost updates (TOCTOU)** - `line 82`
- What: replace_in_file reads `src` (line 82) then writes much later (line 108) with no lock; two concurrent CLI/API edits of the same path each start from the pre-edit content and the last `os.replace` wins. Atomicity prevents a torn file (no corruption), but one edit vanishes and each process's count/verify checks pass against stale content.
- Trigger: two `_safe_edit` processes/threads editing the same file (multi-entrypoint use noted in the docstring). PLAUSIBLE — unverified because it needs real concurrency, not reproduced here.
- Impact: silent loss of one of two edits.
- Fix: a same-dir exclusive lock file (`O_CREAT|O_EXCL`) or `fcntl`/`msvcrt` advisory lock spanning the whole read -> write.

## Missing safeguards
- No directory fsync after `os.replace`: the temp is fsynced but the rename is not, so a crash can lose an otherwise-durable write (durability gap, not corruption).
- Non-.py files get NO post-replace re-read: safe_write verifies the TEMP before the rename, but nothing re-reads the FINAL target afterward. The .py path has a belt-and-suspenders on-disk compile (lines 109-119); a doc/json corrupted during/after the rename would be undetected and reported OK. (Risk is low — renames don't copy bytes — but the asymmetry is worth a post-replace size/byte check for non-.py.)
- `replace_in_file` has no explicit `old != ""` guard; it is only indirectly saved by `found != count` (`"".count(...)` returns len+1). A caller passing `count=len(src)+1` with `old=""` would splice `new` between every character.
- `write` CLI does not pre-compile the payload before the first write (replace_in_file does), which is what widens the BUG 1 window.
