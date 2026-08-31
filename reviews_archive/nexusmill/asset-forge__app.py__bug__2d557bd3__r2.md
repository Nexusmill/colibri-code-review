# Bug review: `asset-forge/app.py` — forced full-file redo

- Model: openai/gpt-5.6-luna-pro (in-session)
- Source path: `asset-forge/app.py`
- sha256: `2d557bd38431ce6d15fa4a0038f2e5ecf0dc2e0bee91e05c3cfae7486a1cbb75`
- Date: 2026-08-11
- Mode: bug
- Context pack: current on-disk source; `get_file_outline`; recent commits touching the file; prior Colibri review and manifest; remediation rows covering prior `app.py` findings; route-local source and adjacent generator contracts; historical review result from 2026-08-10. The prior result was narrow and was not reused as a full-file verdict.

## Verdict

Not fully shippable as an HTTP API contract: several malformed or incomplete JSON requests reach unchecked indexing/conversion and become generic 500 responses instead of client errors. No high-confidence traversal, SSRF, secret-disclosure, or paid-spend bypass survived this pass. The defects below are narrow but real because they are reachable before any provider work and violate the route's own validation/error-handling expectations.

## Bugs & vulnerabilities

**[MEDIUM] Missing `seed` turns `/api/preview` into a server error** — `asset-forge/app.py:684`
- **What:** The route validates only `category` and `family`, then unconditionally evaluates `int(d["seed"])`.
- **Trigger:** A local client sends otherwise valid JSON such as `{"category":"<valid>","family":"<valid>"}` without `seed` (or with a non-integer seed).
- **Impact:** `KeyError`/`ValueError` escapes to the global handler and the endpoint returns HTTP 500 with an error report, although this is a client-input validation failure. A stale/older UI or hand-authored local request cannot obtain a preview and the server records avoidable error reports.
- **Fix:** Validate/coerce `seed` before calling `registry.render`, return a 400 with a stable message for missing/invalid seed, and bound it if the generator contract requires a range. Regression-test missing and non-integer seed.
- **Verification:** Confirmed by tracing the route: no earlier `seed` check exists; the only surrounding guard covers `category` and `family`, and the global exception handler maps the resulting exception to 500.

**[MEDIUM] Missing or malformed `seed` turns `/api/generate` into a server error** — `asset-forge/app.py:710`
- **What:** The route validates `category` and `family` and clamps `count`, but unconditionally evaluates `int(d.get("seed", 1000))`; an explicitly supplied non-integer seed raises, while the preview route has no default at all.
- **Trigger:** A local client posts `{"category":"<valid>","family":"<valid>","seed":"not-an-int"}`.
- **Impact:** The request reaches the generation call and fails as a generic 500 rather than a 400. In this route the failure occurs before generation/provider spend, but it still creates a misleading error report and leaves the API contract inconsistent with the handled `count` validation immediately above it.
- **Fix:** Parse and validate `seed` in the route before constructing/using the output path; return 400 for invalid input. Keep the same parser shared with `/api/preview`.
- **Verification:** Confirmed by source trace: `int(d.get("seed", 1000))` is outside a `try` block, and the global handler catches the resulting `ValueError` as 500. No caller-side guarantee was found that every request must provide an integer.

**[LOW] `/api/library/migrate_legacy` reports internal failures as HTTP 200** — `asset-forge/app.py:900-901`
- **What:** The broad exception handler serializes `{"error": ...}` with status 200 for any failure in `_lib_out()` or migration.
- **Trigger:** A filesystem/configuration failure occurs while resolving or migrating the library (for example, a read-only or unexpectedly removed library directory after the request begins).
- **Impact:** Clients and automated callers cannot distinguish a successful migration result from a failed migration by HTTP status. A UI can treat the operation as successful and suppress retry/error handling even though no migration completed; the body is also not normalized with the normal error contract.
- **Fix:** Return an appropriate 5xx status (or a typed 4xx for a known client condition), redact the message if it can contain filesystem details, and preserve the existing 400 validation path for malformed `folders`.
- **Verification:** Confirmed by direct trace: the `try` covers `_lib_out()` and `migrate_legacy_library_folders`; its `except` explicitly returns status 200. This is not the intentional 200 response used by read-only success paths.

## Fixed since last review

- The 2026-08-10 narrow review found no defect in the `_LIB_EXTRA`/`flagged/` exclusions. That conclusion remains valid for the reviewed scope; this redo found no regression there.
- Prior manifest entries for `app.py` covering upload verification, redaction, output-root guards, and job-registry concurrency were consulted and not re-opened as new findings. The current source retains the relevant guards.

## Missing safeguards

- Shared request parsers/validators for required numeric fields (`seed`, and ideally other route-specific numeric knobs) would prevent route drift between preview and generate.
- Endpoint tests should assert both body and HTTP status for malformed JSON/input, not only the success shape.
- The migration endpoint should use a consistent non-2xx error status and redaction policy for filesystem exceptions.

## Adversarial verification notes

- Refuted as findings: path traversal through `download`, `asset_file`, `open_dir`, `output_delete`, and `zip_selected` (all use `_safe_under_output`; selected archive members are basename-only and resolved under the selected directory); deletion of a live job directory (active registry snapshot protects currently running entries); automatic destruction of `flagged/` (explicitly excluded by both detector and migration validation); and arbitrary provider-token leakage in the global error report (the report passes through `_redact`).
- Not promoted: malformed `zip_selected.names` causing a 500. It is a robustness gap for a non-conforming JSON shape, but lower-value than the three contract failures above and not independently important enough to report in this hunt.
