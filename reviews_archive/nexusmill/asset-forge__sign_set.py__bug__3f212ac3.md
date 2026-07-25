<!-- source: asset-forge/sign_set.py | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | sha256 3f212ac335631bafcdb518fea9e36b461822382d49e395d5d9d13c73d660a04e | 2026-07-22 | mode: bug | context pack: jcodemunch outline (creator-only CLI, sync_builds whitelist, no user twin), callee sources forge/pipeline.py::generate_set + forge/tracer/signer.py::PivSigner.sign, remediation ledger (03b56ef pipeline guards) -->

## Verdict
CLI itself shippable — but tracing DeepSeek's refuted CRITICAL exposed a REAL ordering defect in
the callee: `generate_set` mkdir'd the output dir BEFORE validating family/category, so unsafe
input left a stray directory outside the output root before the ValueError fired. Fixed at the
choke point (both twins) with a functional reproducer.

## Adjudication of DeepSeek findings

**[CRITICAL] path traversal via `--family` (line 42) — REFUTED as claimed / CONFIRMED root-cause sibling**
- As claimed: refuted. `generate_set` rejects `/`, `\`, `..`, absolute, drive in family/category
  (pipeline.py, 03b56ef) — files are never written to a traversal path; and this is a creator-only
  local CLI (operator = trust boundary).
- BUT the trace showed `out.mkdir(parents=True)` ran BEFORE that validation: any caller (including
  the localhost web app's generate route) passing unsafe family created a stray empty directory
  outside the output root, then errored. **CONFIRMED [LOW/MED], fixed:** validation block now runs
  first, mkdir last (both `asset-forge/forge/pipeline.py` + user twin, byte-identical, sha
  7cb8c830a869). Reproducer: traversal family raises ValueError with zero dirs created; count=0
  likewise. PASS.

**[HIGH] PivSigner session never closed (lines 39-46) — REFUTED**
- `PivSigner.__init__` stores config only; `sign()` opens the PKCS#11 lib+session locally per
  call and closes in `finally` (`sess.logout()` best-effort + `sess.closeSession()`,
  signer.py:120-123). An exception in `generate_set` leaves no session open — there is none
  outside `sign()`.

**[MEDIUM] unvalidated `--count`/`--seed` (lines 26-27) — verified-stale**
- `generate_set` validates `count` positive int and int-casts `base_seed` (pipeline.py, 03b56ef).
  Re-flag of remediated code.

**[LOW] hard-coded Windows PKCS#11 path (line 19) — accepted-by-design**
- Documented Windows/iShield creator tool; `--module` override exists. Won't-fix.

## Missing-safeguards claims
- Buyer name/email "injection": embedded via `json.dumps` (escaped) and signed token payload —
  refuted. Output-dir overwrite: operator choice on a local tool, set_id-unique manifests — noted,
  not a defect. Cert/key-match + PIN-lockout ergonomics: nice-to-haves for a creator tool, logged
  mentally, not defects.
