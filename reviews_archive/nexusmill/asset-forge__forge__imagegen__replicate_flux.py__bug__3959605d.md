# Bug review: `asset-forge/forge/imagegen/replicate_flux.py`

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/imagegen/replicate_flux.py` (creator edition, canonical)
- sha256: `3959605d59bbaf4c76a6f9f21fd28a42ec0ef0a44f7dd6cb8bed8a401adeb956`
- Twin parity: `asset-forge-user/forge/imagegen/replicate_flux.py` byte-identical at the same
  sha (G23 verified this pass) — verdicts apply to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- Context pack: `get_file_outline`; `find_importers` → 4 importers (`forge/imagegen/__init__.py`,
  `library_gen.py`, `tests/harness/run_assetforge.py`, `tools/curated_run.py`); the `extra=`
  call chain traced end to end (`app.py:1103/1286` `_clean_schema_extra` → `bundle.py:51/88/175`
  → `build_inputs`), including `RESERVED_PROPS` at `schema.py:220`; `catalog.json` declared
  `avg_seconds` per model (to size the poll timeout against reality);
  `docs/remediation_manifest.json` rows for this file — 2026-07-20 `531f059` (path-injection /
  token-leak redirects / output guard), `glm20-7` (create+poll in one retry loop),
  2026-07-24 `af-flux-no-double-bill` and `af-billedfailure-no-respend`, `flux-r2-reset-rf2`
  (reset-class → BilledFailure), `tranche1-deferrals` LG-1, 2026-07-30 `concurrency1` /
  `composition1` (`_FETCH_HOSTS`); commit fb01a35 (nano-banana-2-lite, the in-window change).
- **Round 3 — DELTA against r1 `…__bug__d7dfb395.md` and r2 `…__bug__ab57fa34_r2.md`**
  (both 2026-07-24; r2 reviewed a 231-line file, this one is 387 lines). Both are **on disk but
  absent from `.colibri_reviews/_manifest.json`**, so a Phase-0 check driven by the manifest
  alone would have wrongly reported this as a first review. Found by listing the review
  directory directly — the manifest has drifted; see the cross-file synthesis.

## Verdict

Shippable, with two narrow money-accounting defects on failure paths. The money-safety
architecture here is genuinely strong — the create/poll split, the `BilledFailure` contract, and
the deliberately narrow `_transient_create` policy all hold up under trace, and the in-window
change (fb01a35) is a pure slug addition that introduces nothing. Both findings are cases where
a *non*-billed or *recoverable* event is reported to the caller as an unrecoverable billed one,
so the customer is told they spent money they either did not spend or could still recover.

## Bugs & vulnerabilities

**[MEDIUM] A 404 on the final create attempt exits with `pred is None` and is reported as a billed failure, though nothing was created** — `replicate_flux.py:280-289`, surfacing at `:316` and `:324`
- **What:** The AF-SDXL-404 branch resolves a pinned version and `continue`s to the next create
  attempt. On the **last** iteration of `for attempt in range(retries)`, `continue` ends the loop
  without assigning `pred` and without raising. Execution falls through to the poll loop, where
  `self._wait(pred)` runs on `None`.
- **Trigger:** Two transient create failures (429, or connection-refused) followed by a 404 on
  the third attempt, for a model Replicate has not designated "official" (`stability-ai/sdxl`
  and friends — exactly the class the 404 branch exists for). `retries` is always 3: jCodemunch
  confirms `retries=` appears at the definition only, no caller overrides it.
- **Impact:** `None.get` raises `AttributeError`, which `_transient` correctly classifies as
  non-retryable, so line 324 converts it into
  `BilledFailure("polling the created (billed) prediction failed: 'NoneType' object has no
  attribute 'get'")`. Three things are then wrong at once. (1) The message is false — this
  file's own comment at line 276 states a 404 is "a routing rejection, not a compute run —
  Replicate never created anything". Nothing was billed. (2) `BilledFailure` is a **contract**
  (lines 160-164): callers with a retry ladder MUST NOT re-call `generate()`. So a free,
  provably-safe-to-retry routing rejection permanently kills the item instead of retrying it.
  (3) The money meter over-reports: per the 2026-08-04 `hunt-af-0804` remediation row,
  `library_gen`'s `spent_est` deliberately counts `BilledFailure` items as billed, so the
  customer is shown spend that never occurred (G19 honesty, in the wrong direction).
- **Fix:** Guard after the create loop — `if pred is None: raise RuntimeError(...)` (a plain,
  *unbilled* error the ladder may retry). Better still, don't let the 404 branch consume the
  final attempt: resolve the version and retry outside the attempt budget, since it is a
  routing correction rather than a transient failure.
- **Verification: CONFIRMED.** Traced statement by statement. `AttributeError` is not an
  `HTTPError`/`URLError`/`socket.timeout`/`ConnectionError`, so `_transient(e)` is `False`;
  `attempt == retries - 1` is `0 == 2` → `False`; therefore line 319's condition is `True`,
  `isinstance(e, BilledFailure)` is `False`, and line 324 raises. The one escape I looked for —
  a `pred is None` guard between the loops — does not exist.

**[MEDIUM] A poll timeout throws away a paid prediction without spending the free retry budget, and reports it without the prediction id** — `replicate_flux.py:351-364`, surfacing at `:327-328`
- **What:** `_wait` breaks out of its polling loop on timeout (line 355-356) and **returns** the
  prediction rather than raising. The caller's poll loop (lines 314-326) therefore sees no
  exception, `break`s on its first pass, and line 327 raises `BilledFailure` because the status
  is still `processing`. The `for attempt in range(retries)` budget on the poll — which the
  comment at lines 312-313 correctly notes is **free** ("re-fetches the SAME prediction's get
  URL") — is unreachable for the one failure mode it would most help.
- **Trigger:** Any prediction that has not reached a terminal status within the hard-coded
  `timeout=240` seconds: Replicate cold start, queue backlog, or a genuinely slow model.
- **Impact:** The prediction is created, billed, and very likely completes moments later — but
  Asset Forge abandons it after a single 240 s window instead of the ~12 minutes the existing
  budget would allow at zero additional cost. The customer pays and receives nothing. This is
  the same "billed but lost image" class the team already judged severe enough to widen a
  security control for (`_FETCH_HOSTS`, lines 106-112, where a 7% loss beat the SSRF risk).
  Compounding it, the message is `f"generation {pred.get('status')}: {pred.get('error')}"` →
  literally **`generation processing: None`** — it carries no `prediction_id`, unlike every
  other `BilledFailure` in this file, all of which end "check replicate.com before retrying".
  The customer is told to check a dashboard with no identifier to look for.
- **Fix:** Raise a distinct timeout error from `_wait` instead of breaking, so the existing free
  poll-retry loop re-polls the same prediction; and include `pred.get("id")` in the terminal
  message so a billed-but-undelivered prediction is recoverable by hand. Optionally scale
  `timeout` from the model's `avg_seconds` rather than a single constant.
- **Verification: CONFIRMED** for the mechanism; **frequency is honestly low.** The control
  flow is certain (the `break` at line 356 cannot produce an exception, so line 317's `break`
  always fires on the first pass). But sized against the data: the slowest declared
  `avg_seconds` in `catalog.json` is 25 s (`flux-2-max`), so 240 s is roughly 10× headroom and
  this will not fire in normal operation. It fires precisely in the cold-start/backlog
  conditions the retry ladder exists for — which is why the unreachable free budget matters
  rather than the timeout value itself.

## Missing safeguards

- **`build_inputs` trusts `extra` completely — the reserved-prop guard lives only in the HTTP
  layer.** Lines 213-217 copy every `extra` key the schema accepts straight into the request.
  The protection against a caller overriding `prompt`/`seed`/`num_outputs` is
  `app.py:_clean_schema_extra` + `RESERVED_PROPS` (`schema.py:220`), which I verified does
  contain `prompt, seed, aspect_ratio, output_format, num_outputs, prompt_strength` plus the
  reference names — so the **HTTP path is correctly guarded and that candidate finding is
  refuted.** But `bundle.py:88` re-reads `model_extra` from a recipe file *without* that
  sanitizer, and `tools/curated_run.py` / `gen_bundle.py` construct providers directly. A
  `num_outputs` arriving by either route multiplies paid spend while the price shown on the
  control still says one image (G19). Cheapest durable fix: drop `RESERVED_PROPS` keys inside
  `build_inputs` too, so the invariant holds wherever the provider is constructed. Reported as
  a finding against `bundle.py` (Unit 4), where the unsanitized merge actually happens.
- **`_supports` fails open when the schema fetch fails** (lines 186-189, and `or not self.schema`
  at line 216). Deliberate and documented, and the failure mode is a clean unbilled 422 on the
  create POST — but it means a token/network problem silently changes request-building policy.
- **`_download` may exceed `max_bytes` by up to one 64 KiB chunk** before raising (lines 374-379).
  Cosmetic; the partial file is correctly unlinked.

## Fixed since last review (delta vs r1 `d7dfb395` / r2 `ab57fa34`, both 2026-07-24)

- **Every r1/r2 fix is present and intact** in the current 387-line source; none re-opened.
  Re-confirmed by direct read: the create and poll loops are separate (r1); `_transient_create`
  retries only `ConnectionRefusedError`/`socket.gaierror` and the reset-class is converted to
  `BilledFailure` at lines 302-309 (r2's HIGH); poll and download exhaustion both raise
  `BilledFailure` at lines 324 and 344 and `_download` unlinks the partial file at lines
  381-386 (r2's MEDIUM, closing RF-2). All `verified-stale`, **not** re-fixed.
- **Both findings in this round are genuinely new, not re-charges.** The `pred is None` defect
  lives in the AF-SDXL-404 branch, which did not exist when r1/r2 ran — it was added
  **2026-08-03 in commit 7a1efad** (`git log -S "AF-SDXL-404"`), ten days after those reviews.
  This branch has never been reviewed.
- **r1's `_wait` timeout refutation is adjacent but not the same defect.** r1 listed
  *"`_wait` timeout reset (latency nit)"* among its refutations and r2 re-confirmed it. That
  dismissal concerns the timeout's *duration/reset* behaviour — a latency question, and I agree
  with it: 240 s against a 25 s worst declared `avg_seconds` is ample. The MEDIUM above is a
  different defect in the same method: that `_wait` **returns instead of raising** on timeout,
  which makes the caller's *free* retry budget unreachable and produces a terminal message with
  no `prediction_id`. That is a money-recovery defect, not a latency one, and neither prior
  round examined it.
- **STALE REFUTATION FLAGGED — r1's `extra` dismissal no longer holds.** r1 refuted "`extra`
  body-key injection" on the explicit basis *"(no caller passes it)"*, and r2 re-confirmed it.
  That premise was true in July and is **false now**: AF-SCHEMA-UI (2026-08-05) wired the
  dynamic options panel through to this parameter, and `bundle.py:175` passes
  `extra=(model_extra or None)` on every generation. The HTTP path acquired a matching guard in
  the same change (`_clean_schema_extra` + `RESERVED_PROPS`), so the product is still safe —
  but the *reason* r1 gave has expired, and the recipe path (`bundle.py:88`) picked up no such
  guard. Recorded so a future round does not lean on the dead premise; see the missing-safeguard
  bullet above and the Unit 4 finding.

## Explicitly NOT re-opened (G35 / G1)

- **`_FETCH_HOSTS` allowing all of `r2.cloudflarestorage.com`** (line 139) is a **decided,
  documented, accepted risk** — Damien's explicit call, 2026-08-04, option 1 of 3, recorded at
  lines 106-138 together with the three conditions that would reopen it. None of those
  conditions has changed. Recorded here as `verified-stale` so the next reviewer does not
  re-litigate it or "fix" it by narrowing the host, which would silently reintroduce the
  measured 7% billed-but-lost-image failure. **No finding.**
- Prior remediation rows for this file (create/poll loop separation `glm20-7`; reset-class →
  `BilledFailure` `flux-r2-reset-rf2`; no-double-bill `af-flux-no-double-bill`; model
  path-injection and redirect token-leak `531f059`) were each checked against current source and
  are **present and intact**: `_MODEL_RE.fullmatch` + `".." not in` at lines 174-175, `_NoRedirect`
  at 143-148, no `Authorization` header on the download request at line 370, and the create and
  poll loops are separate. `verified-stale`, no re-fix.
