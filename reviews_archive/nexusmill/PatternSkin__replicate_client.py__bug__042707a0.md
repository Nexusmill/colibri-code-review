# BUG review: PatternSkin\replicate_client.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\replicate_client.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:15
- tokens: in 2103 / out 2234
- est cost: $0.0398

---

## Verdict
Not quite safe to ship as-is. The core retry/poll flow is sound, but the single biggest risk is **double-billing**: the code retries the prediction-creation POST on 500/502/503/504, and a server-side failure can occur *after* Replicate has already created (and charged for) the prediction — each retry silently spends money again with no idempotency protection.

## Bugs & vulnerabilities

**[HIGH] Retrying the prediction-creation POST on 5xx can create duplicate paid predictions** - `line 90-92`
- What: On HTTP 500/502/503/504 the code sleeps and re-POSTs the creation request up to 4 more times. A 5xx from Replicate does not guarantee the prediction wasn't created server-side (e.g., gateway timeout after the backend accepted it).
- Trigger: Any transient 5xx/gateway error on the initial POST to `/v1/models/.../predictions`.
- Impact: Multiple billed generations for one user click; user is charged 2–5× for a single request, silently.
- Fix: Don't blindly retry the create call. On 5xx, either query `GET /v1/predictions` filtered by recent creations to check for a duplicate before re-posting, or use an idempotency/cancel-on-retry strategy (e.g., retry, then cancel all but one). At minimum, only auto-retry 429 and network-layer failures, and surface 5xx to the user.

**[MEDIUM] `int(seed)` raises uncaught `ValueError` on non-numeric input** - `line 77`
- What: If `seed` is a string that isn't a valid integer (e.g. `""`, `"abc"`, `"1.5"`, or a value from a Blender text property), `int(seed)` throws before any try/except exists in this function.
- Trigger: User types a non-integer or empty-but-not-None seed in the UI.
- Impact: Raw traceback instead of a graceful error; generation aborts.
- Fix: Wrap in try/except: `try: inp["seed"] = int(seed) except (TypeError, ValueError): raise RuntimeError("invalid seed: %r" % seed)`.

**[MEDIUM] Poll loop has no error handling — transient GET failures abort a paid generation** - `line 105-110`
- What: The initial POST is carefully retried, but the status-poll `urlopen`/`json.loads` inside the `while` loop is naked. A single `URLError`, timeout, or malformed JSON body mid-poll raises an unhandled exception and abandons the (already created and billed) prediction instead of resuming polling.
- Trigger: Any network blip, TLS reset, or non-JSON 5xx body from `get_url` during polling.
- Impact: User loses the generation and the money despite the prediction likely succeeding seconds later.
- Fix: Wrap the poll request in try/except with the same bounded retry/backoff used for the POST, and keep polling until `timeout` expires.

**[MEDIUM] Unvalidated scheme/host on output download enables SSRF / local file read** - `line 114-117`
- What: `out_url` comes from the API response and is passed straight to `urllib.request.urlopen`. `urllib` happily handles `file://` and arbitrary internal hosts. Trust in api.replicate.com's TLS is the only control; a compromised/mitm'd response or a future provider added to `_PROVIDERS` pointing at an HTTP or attacker-controlled endpoint turns this into file read (`file:///etc/passwd` gets written to `out_path`) or SSRF.
- Trigger: Malicious or buggy prediction response whose `output` URL is a `file://` or internal-network URL.
- Impact: Local file exfiltration into the output texture path; internal network probing.
- Fix: Validate `out_url` before fetching: require `urlparse(out_url).scheme == "https"` and (ideally) an allowlisted host suffix (e.g. `replicate.delivery`).

**[LOW] `pred["output"]` KeyError / malformed output shape not handled** - `line 113-114`
- What: If status is `"succeeded"` but `output` is missing or an empty list, line 113 raises `KeyError` and line 114 raises `IndexError` — neither is a `RuntimeError`, so callers expecting the documented error type get a bare traceback.
- Trigger: Schema change or edge-case model response.
- Fix: `out = pred.get("output"); if not out: raise RuntimeError("generation succeeded but returned no output")`.

**[LOW] Error-body read on retryable HTTPError leaks the connection** - `line 89-92`
- What: On the 429/5xx retry path, `e.read()` is never called and `e.close()` is never invoked; the HTTPError's socket isn't deterministically released before the next attempt (relies on GC).
- Fix: `e.close()` (or read-and-discard) before `continue`.

**[LOW] Unknown model silently falls back to using `model` as the slug with price 0** - `line 72`
- What: `_REPLICATE_MODELS.get(model, (model, 0))` means a typo'd or injected model name is sent to the API as-is, and any UI showing cost displays 0 for it — the "price shown in every UI that spends money" guarantee in the docstring is broken for that path.
- Fix: Reject unknown models explicitly: `if model not in _REPLICATE_MODELS: raise RuntimeError("unknown model %r" % model)`.

## Missing safeguards
- No validation of `token`/`key` for control characters before embedding in the `Authorization` header (lines 46, 78, 107) — a key containing `\r\n` currently just produces a confusing "network error"; validate format explicitly.
- No unit tests for: retry-exhaustion path, poll-loop transient failure, `seed=""`, unknown model, and missing/empty `output` — all currently raise undocumented exception types.
- The `timeout=180` poll budget vs. the 150s `Prefer: wait` POST timeout is untested; a slow generation can be abandoned client-side with no cancel call to Replicate (leaving a paid prediction running). Consider issuing a `cancel` on timeout.
- `out_path` is never validated (parent dir existence, no write to unexpected locations); a failure in `open()` surfaces as a raw `OSError` after the user has already been billed.