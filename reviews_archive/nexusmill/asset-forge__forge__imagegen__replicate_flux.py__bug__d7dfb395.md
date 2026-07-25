# colibri-review — asset-forge/forge/imagegen/replicate_flux.py — bug (hunt round 1, effort=mid) [+ twin]

- **Source:** asset-forge/forge/imagegen/replicate_flux.py (byte-identical twin, G23) · **Scanner:**
  general-purpose subagent @ claude-sonnet (mid) · **Verification + fix:** claude-opus-4-8[1m]
  (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** d7dfb395664005f3d3228f35b4851bdbb9530eacc1411e461e5837128adf52da
- **Date:** 2026-07-24 · **Mode:** bug · round 1. (Scanner ran under the pre-priming subagent regime;
  every finding below was independently re-verified in-session against current bytes before fixing.)

## Verdict
Two HIGH money-safety defects — both confirmed and fixed with pre/post tests. The Replicate spend
path had the same double-bill class as the sibling `replicate_client` (already fixed) **plus** a
cross-file re-bill where `library_gen`'s retry ladder re-spent on post-creation failures.

## Bugs & vulnerabilities (CONFIRMED, fixed)

**[HIGH] Create-POST retry on 5xx/timeout double-bills** - `_transient:108` + `generate` create loop
- The create POST sends `Prefer: wait`, but the loop retried via the broad `_transient` (5xx +
  timeout). A 5xx/read-timeout there may mean the prediction was already created and billed →
  re-POST double-bills. **Fixed** with a narrow `_transient_create` policy (429 + pure connection
  failures only; 5xx/timeout raise a `BilledFailure` instead of re-POSTing). Poll/download keep the
  broad `_transient` (free re-fetches). **Verified:** pre-fix a single 504/timeout issued **3** create
  POSTs; post-fix **1** (junk/_flux_test.py 6/6, pre-fix 2/6). Committed 8d4c97c, refined below.

**[HIGH] Post-creation (billed) failure re-spent by `library_gen`'s retry ladder** - `replicate_flux.generate` post-creation raises × `library_gen._run_job_locked:334-361`
- Once a prediction is created it is billed, but a terminal non-succeeded status (moderation reject /
  cancel), no-output, refused-output — and the create-5xx/timeout case above — raised a plain
  `RuntimeError`. `_run_job_locked` matches only credit/402, auth/401-403, 429; everything else is
  "other transient" and retries `provider.generate()` up to 3× → re-creates + re-bills (**4
  create/billing events for one moderation-failed image**).
- **Fix (cross-file, both twins):** a `BilledFailure(RuntimeError)` type raised at every billed point
  in `generate` (the 5 raises); `library_gen` catches `BilledFailure` **before** the generic `except`
  and fails the item **once** (no retry, mirroring the `CreditError` branch).
- **Verified:** junk/_billedfailure_test.py **8/8** — a moderation reject and create-504/timeout raise
  `BilledFailure` (moderation = 1 create POST); the ladder calls `generate` **exactly once** for a
  `BilledFailure` and marks the item failed (`job.failed==1`); and a genuine transient `RuntimeError`
  is **still retried 4×** — proving the fix is targeted and showing the exact pre-fix re-bill count.

## Deferred
- **RF-2:** the poll/download-exhaustion raises are not yet `BilledFailure` (persistent poll/download
  failure on an existing prediction can still re-bill), and `_download` leaves a partial file on
  failure. Rarer than the moderation case; wants a small `generate()` restructure + its own test.
- **LG-1 (already recorded):** the MEDIUM `flux-1.1-pro-ultra` priced-but-unmapped model is the same
  finding deferred from unit 14 — needs the verified Replicate slug or a product decision.

## Refuted during verification (scanner self-refuted; recorded in `_refuted_ledger.json`)
- SSRF via slug injection / redirect token leak — `_host_ok` + `_NoRedirect` + `_MODEL_RE` gate the
  create/poll/download URLs (row 531f059, verified still in place).
- Non-standard-port host bypass (needs DNS/TLS control); `extra` body-key injection (no caller passes
  it); `_wait` timeout reset (latency nit); permissive schema fallback (intended); `int(seed)` raw
  ValueError (pre-POST, no caller passes non-numeric).
