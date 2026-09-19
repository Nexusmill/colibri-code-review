# Colibri Review - bug (FULL re-audit) - asset-forge/forge/imagegen/replicate_flux.py

- **Source path:** `asset-forge/forge/imagegen/replicate_flux.py` (twin `asset-forge-user/forge/imagegen/replicate_flux.py` byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF stale units)
- **sha256 reviewed:** `d072e86ca40cc8004bb046479c0f94edd10dc87466151e8893200b88b27c5a39` (sha8 `d072e86c`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review (pre-gate ruling)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the unit's 07-22..08-15 reviews predate the gate and are untrusted); jCodemunch get_file_outline + find_importers; every remediation/deferred row naming the file loaded as CLAIMS and re-checked at the bytes; call sites traced (app.py bundle job + prog callback, library_gen, gen_bundle.py, concurrency.map_bounded/imap_bounded/Stop). Twin asset-forge-user/<same path> byte-identical (sha256 equal) - one review covers both.

## Verdict
Shippable after two fixes. The money ladder is sound at the bytes: create-POST retries only the provably-unbilled set (429, refused, DNS), everything that may have reached Replicate is a BilledFailure that no caller re-POSTs, the poll re-fetches the SAME prediction, the download is free and redirect hops are re-validated against the CDN allow-list without an Authorization header, the poll URL is pinned to api.replicate.com, the slug is regex-validated. The two defects are on the abandon path and in the receipts.

## Bugs & vulnerabilities

**[MEDIUM] `_wait` silently gives up after 240 s and `generate` writes a still-running, paid prediction off as a failure - never cancelled, image never fetched** - `line 381-394` (+ 357)
- What: the poll loop `break`s when `time.time() - start > 240`; `generate` then sees `status == "processing"` (or `"starting"` while queued) and raises `BilledFailure("generation processing: None")`. The prediction is never cancelled, so it keeps running (and billing where billing is per-second) and its finished output is never downloaded.
- Trigger: any prediction still queued or running after ~4 minutes of polling - a cold boot or busy queue on Replicate (the `starting` state) exceeds that routinely for non-official or large models (hunyuan-image-3, imagen-4-ultra, gpt-image at high quality); the library runs 8 of these in parallel.
- Impact: the customer pays for an image the product throws away; library_gen flags the item as a billed failure and never retries it (correctly - it IS billed).
- Fix (snippets 1-2): a module poll budget of 900 s; on exhaustion POST the prediction's `urls.cancel` (host-checked, best-effort) and raise a BilledFailure naming the id, the status and whether the cancel went through.
- Verification: CONFIRMED by the code contract (deterministic on the 240 s clock) - probe `RF_stuck_prediction_cancelled_and_named` RED (message names no id, no cancel POST) and `RF_poll_budget_survives_a_6_minute_prediction` RED (a 400 s prediction written off) → both GREEN. How often real predictions exceed 240 s is unmeasured here; Replicate's own docs describe multi-minute cold boots.

**[LOW] Four of the six BilledFailure sites omit the prediction id** - `line 354` (poll), `358` (terminal status), `364` (CDN refusal), `374` (download)
- What: bundle.py's abort receipt and library_gen's flagged records carry the BilledFailure MESSAGE as the only trace of the tripping item's spend; without the id the customer cannot reconcile it on replicate.com.
- Fix (snippets 3-6): every BilledFailure names `pred["id"]`.
- Verification: CONFIRMED - probes `RF_terminal_failure_names_prediction`, `RF_download_failure_names_prediction` RED → GREEN.

**[PLAUSIBLE, LOW] An output that is neither a str nor a list of str is refused as "off the Replicate CDN"** - `line 362-364`
- What: `out[0] if isinstance(out, list) else out` then `_host_ok(non_str)` → False → BilledFailure with a misleading message. Unverified because none of the MODELS entries is known to return a dict output; noted for the day one does.

## Missing safeguards (not fixed)
- No stop/cancel hook inside `_wait`: a run aborted by library_gen/bundle keeps every in-flight worker polling to completion (they are billed on creation, so nothing is saved by stopping - noted for clarity, not a defect).
- `MODELS.get(model, model)` passes any `owner/name` slug through; the price gate that refuses unpriced models lives in app.py/library_gen (their units), not here.

## Adversarial verification pass (refuted claims)
- "`_download` follows redirects across hosts" - refuted: every hop is re-validated against `_FETCH_HOSTS` and the request carries no Authorization header.
- "the AF-SDXL-404 `continue` consumes a retry, so the version-pinned request gets one fewer attempt" - true but harmless: a 404 creates nothing, and the last-attempt `continue` is handled by the `pred is None` branch (plain, retryable, explicitly unbilled).
- "`build_inputs` passes `extra` unfiltered when the schema is missing" - refuted: RESERVED_PROPS are dropped before the schema check.
- "retrying a 429 on the create POST can double-bill" - refuted: 429 is rejected before creation (server-side rate limit).
- "a 401 mid-poll should be retried, not BilledFailure" - refuted: the prediction exists and was billed; failing the item once is the documented contract.
- "the poll sends the token wherever `urls.get` points" - refuted: `_host_ok(get_url, (_API_HOST,))` refuses any other host before the request.
- "`_wait` re-captures `get_url` only once" - refuted: refreshed from every poll response (line 393).

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `790e880c2d0459f351b9d5df22bb9cdcd4bc1c850a69a7ea27eed03c5f7b92c5`. Rows AF-RF-WAIT-BUDGET-CANCEL, AF-RF-BILLED-IDS in `docs/remediation_manifest.json`, same commit.

