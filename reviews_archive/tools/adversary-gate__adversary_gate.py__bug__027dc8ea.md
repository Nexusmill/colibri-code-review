# Colibri review — adversary-gate/adversary_gate.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py`
- **Model:** claude-fable-5 (in-session), gating grok-4.6 external findings (raw: scratchpad reviews/grok)
- **sha256:** `027dc8ea784f61166555aca11ea7a578abb0f02d065492782c4388b6960967e7` (grok reviewed the same bytes)
- **Date:** 2026-09-02
- **Mode:** bug
- **Deviation (honest, per Damien's order this session):** external models (grok-4.6, GLM-5.3-flash) ran as PRIMARY reviewers on the large/gate-core files at the owner's explicit instruction; every finding below still passed the in-session Phase-3 gate (drive the real code, refute or confirm) before it was kept. Findings are mine to stand behind.
- **Context pack:** jCodemunch outline; G39 layer doctrine (this file IS layers 0/1/3 — `check`/`record`/`check-push`); sibling `adversary_audit.py` shares the identical `--name-status`/`--diff-filter` parsing (unit-2 review, same session) so both HIGHs below apply there too.
- **Verification:** both HIGHs driven through the REAL module in throwaway repos (scratchpad `gate_probe.py`): quotepath and typechange each proven fail-open. The MEDIUM traced through `_call_model`→`_call_one_model` by read.

## Verdict
Not shippable as the fail-closed wall it claims to be: two staged-file-lister blind spots let a code change pass the gate as "docs-only" with no clearance — and because `record`/`check-push` share the listers, all layers fail open together on the same inputs. The clearance-matching core (sha-keyed, stale-invalidating) is otherwise sound.

## Bugs & vulnerabilities

**[HIGH] Non-ASCII code path bypasses the gate entirely (core.quotepath C-quoting)** — `_staged_code_files` line 99-107, `_staged_removals` line 122, `_changed_code_in_commit` line ~356
- What: all three list paths from `git diff … --name-only/--name-status` WITHOUT `-z`, then `.strip()` each line. Under git's default `core.quotepath=true`, any path with a non-ASCII or control byte is emitted C-quoted (`"caf\303\251.py"`), so `_is_code` sees extension `.py"` (or a `"caf…` prefix) and misses; a literal tab/newline in a name also splits the record.
- Trigger: PROVEN — staged `café.py` containing unreviewed code → `_staged_code_files()` returned `[]` → `cmd_check` treats the commit as docs-only and returns 0 (passes) with no clearance; `cmd_record` writes no note; `cmd_check_push` demands none. Total fail-open for that blob.
- Impact: the gate's central guarantee (no code commits without a fresh CLEAR) is void for any non-ASCII-named source file — accidental or deliberate.
- Fix: use `-z` (NUL-delimited) in all three functions and stop `.strip()`ing paths; for `--name-status -z` consume `status\0path\0` / `status\0old\0new\0`. Alternatively set `-c core.quotepath=false` on every `_run_git` call. Fix the vendored `adversary_audit.py` identically (its `_changed_code` has the same parse).

**[HIGH] Typechange (`T`) is invisible — a gated file can be neutered ungated** — `_staged_code_files` `--diff-filter=ACMR` (line 99), `_staged_removals` `--diff-filter=DR` (line 122), `_changed_code_in_commit` handles only `ACM/R/D` (line ~356)
- What: none of the listers include git status `T` (regular file ↔ symlink ↔ gitlink).
- Trigger: PROVEN — replacing `.githooks/pre-commit` with a symlink entry via plumbing produced `T\t.githooks/pre-commit`; both `_staged_code_files()` and `_staged_removals()` returned empty → the commit gates as docs-only.
- Impact: any gated `.py`/`.githooks/*` path can be replaced wholesale (e.g. hook → symlink to `/dev/null`, or a source file → gitlink) in a commit the gate, the notary, and the push guard all wave through. Directly neuters the gate.
- Fix: treat `T` like `M` in the staged filters (`ACMRT`) and hash `:path` for it; in `_changed_code_in_commit` handle `T` as ACM. Mirror into `adversary_audit.py`. Add a selftest row per case.

**[MEDIUM] A malformed HTTP 200 crashes the run instead of advancing the fallback chain** — `_call_one_model` line 276 & 293, `_call_model` line 233-241
- What: `_call_one_model` wraps only `HTTPError`/`URLError`. A 200 whose body is non-JSON raises `json.JSONDecodeError` at line 276; `{"choices": null}` makes line 293 `for ch in d.get("choices", [])` return `None` → `TypeError`. Neither is `SystemExit`, and `_call_model` (233-241) catches only `SystemExit` to advance the chain.
- Trigger: the primary model (glm-5.3-flash) returns a 200 with a truncated/HTML/error body or a null `choices` — observed-class behavior for flaky OpenRouter providers.
- Impact: the exception propagates out of `_call_model`, so the fallback chain does NOT advance to deepseek and `cmd_run` dies with a traceback. It fails CLOSED for `check` (a crash blocks the commit), so no false CLEAR — but it defeats the multi-model resilience that is the whole reason the default is a chain, and it hands the operator a traceback rather than a clean BLOCK.
- Fix: wrap the body decode + `json.loads` + choices/content extraction; on any parse/shape failure `raise SystemExit("ADVERSARY GATE: unreadable model response: …")` so the existing chain-advance and EV-004 fail-closed logic run. Coerce `d.get("choices") or []`.

## Missing safeguards
- `_staged_removals` catches `SystemExit` from `git show HEAD:old` and substitutes `b""` (line 137-138) — a removed blob that can't be read is hashed as empty, so its clearance key is the sha of empty; low, but means a clearance could in principle be pre-computed for the empty blob. Note, not a confirmed exploit.
