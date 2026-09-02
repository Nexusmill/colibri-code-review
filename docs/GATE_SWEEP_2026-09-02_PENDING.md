# Post-gate audit — per-file colibri sweep, tranche 1 (2026-09-02)

Campaign phase 2 (per-file colibri sweeps of never-swept armed-repo cores). This tranche
swept **Tools**, **repo-memory**, and **colibri-code-review** cores using GLM-5.3-flash
(background) + Grok (background, largest files) as PRIMARY reviewers by owner order, with
the in-session model gating every finding through colibri-review Phase 3. Raw external
outputs preserved per repo under `.colibri_reviews/_external_raw/`.

## VERIFIED + persisted this tranche (gated reviews in each repo's `.colibri_reviews/`)

In-session foreground (own reviews):
- Tools `adversary-gate/harness_guard.py` — 2 HIGH (comment-substring `.adversary` bypass; Windows trailing-dot segment defeats the file-tool check), MEDIUM-HIGH (hooksPath prefix exemption), LOW (multiline `--no-verify`). All probe-confirmed.
- Tools `adversary-gate/adversary_audit.py` (+ 9 byte-identical vendored twins) — HIGH replace-ref blindness, HIGH `T` typechange skip. Probe-confirmed.
- colibri `store.py` — HIGH cross-process manifest lost-update; MEDIUM absolute-path `output`; LOW filename truncation collision.
- colibri `scanner.py` — HIGH scanner-vs-store sha divergence (text-mode CRLF) → CRLF files perpetually "stale" → re-bill. Empirically confirmed on repo files.
- colibri `ui.py` — clean.

Grok-lane, gated:
- Tools `adversary-gate/adversary_gate.py` — **2 HIGH probe-confirmed**: non-ASCII path C-quoting (`core.quotepath`) → code file passes the gate as docs-only with no clearance; `T` typechange → gated file neuterable ungated. **All gate layers fail open together** (check/record/check-push share the listers). + MEDIUM malformed-200 crashes instead of advancing the fallback chain.
- Tools `adversary-gate/install_gate.py` — external HIGH **REFUTED** (shims do contain `adversary_gate.py` + one `GATE=` line); LOW `_git` narrow except.
- Tools `screencap/screencap.py` — 3 MEDIUM (region argv off-by-one; burst doesn't wake minimized window; tasklist no-returncode/naive-CSV). Read-confirmed.
- Tools `hy4-review/hy4_review.py` — 2 MEDIUM (unguarded path reads; narrow except after billing). Read-confirmed.
- colibri `analyzer.py` — MEDIUM/LOW fd + socket leaks. Read-confirmed.
- repo-memory `colibri.py` — MEDIUM silent-skip of unreadable review `.md` (downgraded from external HIGH). Read-confirmed.

GLM-lane, verified + gated this tranche:
- Tools `mcp/server.py` — **HIGH** non-object JSON crashes the server (read-confirmed); + MEDIUM screencap-stale-file success, MEDIUM broken-pipe/no-cancel.
- Tools `safe-edit/_safe_edit.py` — **MEDIUM** newline corruption of mixed/lone-CR files (**probe-confirmed**, G8 tool); MEDIUM fsync-swallow; MEDIUM lost-update; LOW retry/verify.
- repo-memory `store.py` — **HIGH** non-atomic delete-then-add data loss (read-confirmed); MEDIUM swallowed-delete duplicates; MEDIUM category filter injection (plausible); MEDIUM query-swallows-all-errors (plausible).
- colibri `run_batch.py` — **HIGH** `--budget` unenforced with `--workers>1` (money; read-confirmed); MEDIUM pre-`try` crash skips summary.

## PENDING VERIFICATION — GLM findings not yet Phase-3 gated (NEXT TRANCHE)

Reported by GLM-5.3-flash, raw evidence in `_external_raw/`. NOT yet confirmed — must be
traced before docketing/fixing (colibri-review law 3). Triaged by apparent severity:

**repo-memory `autoindex.py`** (raw: `repomem__autoindex.py`): 2 apparent HIGH —
(1) `autoindex.docs:false` opt-out purges previously-indexed docs rows (`removed` computed
from `prev_docs` while `cur_docs` is empty) → silent record loss of the external
`extract.py` pipeline's rows; (2) hub-mirror failure persisted as success → permanent
silent skip. Plus 8 MED/LOW (reviews:false freezes change-detection; unlocked non-atomic
`register()`; zero-section files leave stale rows; colibri-row deletion gap; `--force`
skips cleanup; import-time `int(env)`; truthy string bools; no sync serialization).
**These are the highest-value pending items — the data-loss HIGHs are exactly this repo's
top severity class.**

**repo-memory `indexer.py`** (raw: `repomem__indexer.py`): apparent HIGH — `split_sections`
returns `[]` on unreadable file + `batch_upsert(replace_all=True)` purges its prior rows →
silent loss on re-index. + MEDIUM unresolved `repo_root` `relative_to` crash; LOW cross-file
topic-dedup drops distinct content.

**repo-memory `server.py`** (raw: `repomem__server.py`): 4 MEDIUM (`_refresh` doesn't
swallow failures despite its contract; process-global `redirect_stdout` on worker threads
races the MCP transport; `REPO_MEMORY_READONLY` doesn't stop autoindex writes; unsynchronized
shared STORE) + 2 LOW. The readonly + redirect_stdout ones are worth early verification.

**colibri `static_context.py`** (raw: `colibri__static_context.py`): MEDIUM non-SyntaxError
parse failures (null-byte `ValueError`, RecursionError) escape `build_static_context`,
breaking its no-crash contract; + 4 LOW (mypy tmp leak, hot-fn name collision, unvalidated
`static_max_chars`, match-statement unreachable-scan gap).

**colibri `app.py`** (raw: `colibri__app.py`): MEDIUM spec-mode runs with no expectations
loaded (paid garbage verdict); MEDIUM queue spend-ceiling undercounts filtered files; + 3 LOW.

**Tools `gate_selftest.py`** (raw: `tools__gate_selftest.py`): MEDIUM test 15b can false-PASS
(commit silently refused → push "up-to-date" exit 0 → green) — the recurring battery-false-green
class; + 2 LOW (POSIX exec-bit not exercised; tmpdir leak).

**Tools `owner_setup.py`**: MEDIUM uncaught FileNotFoundError in part_b subprocess sites; 2 LOW.
**Tools `install_selftest.py`**: MEDIUM POSIX exec-bit check asserts working-tree mode not index.
**Tools `audit_selftest.py`**: 2 LOW (decode, tmpdir leak).
**Tools `grok_review.py`**: MEDIUM silent `--spec`/`--findings` ignore in wrong mode; MEDIUM
unhandled URLError/JSONDecodeError after billing; LOW key-file over-match.

## Cross-cutting patterns (recurring across the sweep — candidates for a shared fix)
1. **delete/purge-then-add non-atomicity** → data loss on write failure: repo-memory
   `store.py` (HIGH), `indexer.py` replace_all (HIGH), `autoindex.py` docs purge (HIGH),
   and the same shape in the adversary auditor. One durable-write discipline would close all.
2. **Unhandled non-HTTPError after a paid/network call** → traceback after billing:
   `adversary_gate._call_one_model`, `hy4_review`, `grok_review`, colibri `analyzer`.
3. **`--name-status`/`--name-only` without `-z` + no `T`** → gate/audit fail-open on
   non-ASCII names and typechanges (Tools gate + auditor). Fix both together.
4. **Silent `except: continue`/`return []`** hiding archive read failures: repo-memory
   `colibri.py`, `store.py` query, `indexer.py`.

## Not yet swept (remaining phase-2 scope)
jcodemunch-mcp cores (needs chunking — server.py 517KB, extractor.py 443KB), deepagents-quickstarts,
3DPrinting cores, colibri-marketplace. Rig-lane as-a-user proofs and enhancement dockets remain
separate campaign phases.
