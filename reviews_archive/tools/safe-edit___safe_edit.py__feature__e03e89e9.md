# safe-edit/_safe_edit.py - feature review

source: C:\Users\User\source\repos\Tools\safe-edit\_safe_edit.py
reviewer: in-session GLM-5.3 (ZCode) · sha256: e03e89e973662f0dcae0e9243b9f8076f5dd0e3b7e4634f3835ab4e84b7eab31 · 2026-10-08 17:46 · mode: feature
context pack: jCodemunch outline (safe_write / replace_in_file / _py_ok / _main); exercised live all session via the universal-tools safe_write/safe_replace MCP wrappers (G8's canonical editor); consumers = every agent session on this machine; no prior feature rows.

## What this module does

The G8 canonical file editor: atomic writes (same-dir temp → fsync → reread →
byte-compare → replace), anchored replacements with occurrence-count and
shrink-ratio guards (a result <50% of the original refuses), and py_compile
gating for .py targets — the truncation-proof write path every repo edit goes
through.

## Suggested add-ons

- **Structured verdict output (`--json`)** — Value HIGH · Effort S
  What: the CLI emits a JSON verdict (path, bytes_before/after, lines, sha256
  before/after, outcome) alongside the human line.
  Why: agents parse "OK replace ... 1 replacement(s)" prose today; the MCP
  wrapper re-derives facts (line counts) it could read. A sha pair in the output
  makes every edit self-verifiable downstream without a re-read.
  How: a small result dict threaded from the functions to `_main`. Hook: `_main`.

- **Automatic pre-edit backup shard** — Value MED · Effort S
  What: optional `--backup-dir` writing the ORIGINAL bytes (content-addressed
  name) before mutation, with a retention note; default off to preserve behavior.
  Why: the atomic temp covers crash-mid-write, not author regret; G12/verify
  workflows currently improvise `.bak-DATE` copies by hand (arm_repo does).
  How: `safe_write`/`replace_in_file` gain an optional hook before the replace
  step. Hook: both entry functions.

- **Encoding preservation** — Value MED · Effort M
  What: detect BOM/UTF-16/CRLF per file and round-trip them (today LF-normalized
  UTF-8 is assumed; CRLF files come back LF).
  Why: Windows config files (`.ps1`, `.cmd`, some `.json`) are CRLF-native; the
  editor silently flips line endings, which shows up as whole-file diffs in
  CRLF-normalizing tools (the gate's own warnings show this repo flip-flops).
  How: sniff the leading bytes + dominant EOL before write; restore on output.
  Hook: `_to_lf`/`safe_write`.

- **Diff preview mode (`--dry-run`)** — Value LOW · Effort S
  What: print the unified diff a replace would produce, exit 0 without touching
  the file.
  Why: cheap safety for wide `count>1` replaces; pairs with the shrink guard.

## Nice-to-haves

A `verify --py` convenience (the `_py_ok` gate exposed standalone); retry
backoff note in output when retries>1; stats counter file for edit-volume
telemetry per repo.
