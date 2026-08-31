# Bug review: `asset-forge/forge/library_gen.py` — full-file redo (r4)

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/library_gen.py` (creator edition, canonical)
- sha256: `4e7bd2f68318db3b955e1a2c59fc3d386fd1051faae866c871066c63442dfac1`
- Twin parity: `asset-forge-user/forge/library_gen.py` byte-identical at the same sha (G23
  verified this pass) — verdicts apply to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- **Forced full-file redo at an already-reviewed sha.** `_manifest.json` holds this sha from
  2026-08-10, but that review (`…__bug__4e7bd2f6.md`) is scoped *"(LIB-FLAGGED-1 additions)"* —
  a same-session self-review of the flagged-relocation block, not a full-file verdict.
  Prior rounds on disk: `ca942a8c` (r1), `95c8603e_r2`, `0d017eb5_r3`, `4e7bd2f6`
  (LIB-FLAGGED-1), plus `debug__f14c435e` (klein diversity collapse, 2026-08-09).
- Context pack: `get_file_outline` (996 lines, 30 symbols); `forge/quality.py` (Unit 1 this
  pass) and `forge/bundle.py` (Unit 4) for the shared quality-floor contract;
  `forge/output_opts` usage via `_oo.normalize`/`prompt_fragment`/`wants_dual_render`;
  `_cc.imap_bounded` single-writer semantics; ~20 `docs/remediation_manifest.json` rows naming
  this file (`bb2e047` run-lock, `0b45c35` retry budgets, `af-libgen-money-clamp`,
  `af-libgen-count-validation`, `unit10-libgen-authfail`, `libgen-r2-money-types`,
  `tranche1-deferrals` LG-1/LG-3, `lg2-pe1-receipts` LG-2, `ckpt-stream`, `model-sweep`,
  `hunt-af-0804` spent_est, `forgehunt1` LIB-SEAM/MODEL-SEED, `default-library-animal-skins`).
- **Depth disclosure (G11):** traced in full — `_finish_prompt`, `build_plan`, `build_wildcard`,
  `_RunLock`, `_plan_paths`, `_work`, `_attempt`, the `imap_bounded` consumption loop, `_bills`,
  `_write_manifest`, `_write_quality_report`. Read but not exhaustively re-derived —
  `estimate`, `prepare_job`, `_height_map`, `_expand_prompts`, whose prior-round findings were
  checked against current source and confirmed closed (listed under *Fixed since last review*).

## Verdict

Shippable with reservations. The money-safety machinery — run lock, split 429/error budgets,
BilledFailure handling, per-item checkpointing, `_bills()` — is the strongest code in this
subsystem and every prior fix survives intact. Two real defects remain: the **wildcard path
never received the output-mode and background wiring the catalog path has**, so wildcard items
silently regress two separately-fixed behaviours; and the durable customer-facing manifest
omits the very per-item facts that make its spend figure reconcilable.

## Bugs & vulnerabilities

**[MEDIUM] `build_wildcard` ignores output mode and background options — wildcard items regress LIB-SEAM(b) and cannot produce transparent output** — `library_gen.py:335` vs `:259-274`
- **What:** `build_plan` threads the normalized output options into every item it builds:
  it calls `_finish_prompt(core_i, cat, opts["mode"])` and appends `bg_fragment`
  (`_oo.prompt_fragment(opts)`) to the prompt, and it stamps `"mode": opts["mode"]` on the item
  (lines 264-274). `build_wildcard` does none of these. Line 335 is
  `"prompt": _finish_prompt(core, cat)` — **no mode argument, no `bg_fragment`** — and the item
  dict it returns (332-337) carries `pack/type/name/prompt/seed` with **no `mode` key**.
  `build_plan` appends these items to the same plan at line 278.
- **Trigger:** Any job with the wildcard enabled. Two distinct consequences:
  1. **Emblem mode.** `_finish_prompt` with `mode=None` falls through to line 107 and appends
     `cat['prompt_suffix']` + `cat['height_hint']` — the height-map treatment. Its own docstring
     (90-100) records why that is wrong: LIB-SEAM(b) fixed exactly this, because
     `prompt_suffix` says "seamless tileable repeating pattern" and "emblems, which are centered
     motifs and must NOT tile, were instructed to tile anyway", while `height_hint` is
     "actively wrong for an EMBLEM, where colour is the point". The fix landed in `build_plan`
     and never reached `build_wildcard`. Worse, `_plan_paths` (line 681) resolves
     `it.get("mode") or job.get("mode") or "heightmap"` — with no per-item mode, wildcard items
     inherit the job's mode and are **filed into `emblem/`** while carrying tiling-and-height
     prompt language.
  2. **Transparent background.** With no `bg_fragment`, the prompt contains no keyable backdrop
     clause. In `_attempt`, `_alt = it["prompt"].replace(_wf, _bf) if _wf and _wf in
     it["prompt"] else None` (line 795) therefore evaluates to `None`, and line 814 sets
     `it["alpha_error"] = "no keyable backdrop clause in the prompt"`. The dual-pass alpha solve
     never runs, and the item ships opaque.
- **Impact:** Paid output that does not match the options the customer selected. **This is an
  incomplete closure of docket `AF-OUTPUT-KNOBS`, not a new idea** — that docket
  (`deferred_manifest.json`, status `done`, 2026-08-04) lists `forge/library_gen.py` among the
  files it wired, but the wiring reached `build_plan` only. The transparent-background case is
  precisely the failure class its own comment (784-787) calls a "silent product-contract no-op" — "the UI offered it, and nothing ever
  performed the second render… every 'transparent' emblem shipped opaque" — remediated for the
  catalog path on 2026-08-04 and still live for wildcard items. It does at least record
  `alpha_error` rather than failing silently, which is why this is MEDIUM and not HIGH.
- **Fix:** Give `build_wildcard` the same `opts` treatment `build_plan` has: accept `opts`, call
  `_finish_prompt(core, cat, opts["mode"])`, join `bg_fragment` onto the prompt, and stamp
  `"mode": opts["mode"]` on each item. `build_plan` already holds a normalized `opts` at line
  232 and passes `cat` at line 278, so it is a one-argument change at the call site.
- **Verification: CONFIRMED.** Every step read directly: the `build_plan` item construction
  (259-274) against the `build_wildcard` item construction (332-337); `_finish_prompt`'s
  `mode == "emblem"` branch versus its `mode=None` fall-through (101-108); the `_plan_paths`
  mode fallback (681); and the `_alt`/`alpha_error` path (795, 813-814). Refutation attempted:
  I checked whether `prepare_job` re-stamps `mode` onto wildcard items after `build_plan`
  returns — it does not; the `it.get("mode")` fallback at line 681 exists precisely because
  some items lack the key, and it silently resolves the *filing* question while leaving the
  *prompt* wrong.

**[MEDIUM] `LIBRARY.manifest.json` omits the per-item facts that make its own spend figure reconcilable** — `library_gen.py:962-967`
- **What:** `_bills()` (857-866) correctly counts every billed generation per item — the base
  image, a `billed_failure`, a `_qc_retry`, and a `dual_pass` second render — and feeds
  `job["spent_est"]`. But `_write_manifest` copies only `pack, type, name, seed, prompt, file,
  height_file, status, quality_warning, quality_metrics` into the durable record. **None of
  `_qc_retry`, `billed_failure` or `dual_pass` is carried through**, and `spent_est` itself is
  not written to the manifest either.
- **Trigger:** Any run containing a quality-floor retry, a billed failure, or a dual-pass
  transparent render — i.e. most non-trivial runs. Per Unit 1, the retry rate is inflated by
  ~2.9% of items being rejected for legitimately-requested monochrome.
- **Impact:** The manifest is the durable, customer-facing receipt (`job.json` is internal and
  lives in the job directory). From it, a customer counting `status == "done"` items concludes
  they were billed N generations when they were billed N + retries + billed-failures +
  dual-passes. An item retried once and then *passing* leaves **no trace at all** — its
  `quality_warning` is `None` because it succeeded — so a doubled charge is invisible. This
  contradicts the block's own comment (957-961), which states the change was made so
  "LIBRARY.manifest.json is a complete record of what happened to every paid image". Under G19
  the money story must be honest at the point the customer reads it; the data already exists in
  `job["items"]` and is simply not copied. A failed-but-billed item is likewise
  indistinguishable from a free failure in the receipt.
- **Fix:** Copy `_qc_retry` (or a derived `billed_generations: _bills(it)`), `billed_failure`
  and `dual_pass` into the manifest item, and write `spent_est` at the top level beside
  `count`/`failed`. `_bills` is already the single source of truth — reuse it rather than
  recomputing.
- **Verification: CONFIRMED** by reading `_bills` and the `_write_manifest` item comprehension
  side by side; the three keys are absent from the output dict. `QUALITY_REPORT.txt` partly
  compensates — it prints an aggregate `%d quality-floor retries taken` (line 987-988) — but it
  names only the *flagged* items (991-994), never which items were retried, so per-item
  reconciliation is impossible from either artifact.

## Missing safeguards

- **`_write_quality_report`'s docstring overstates when it is written** — and docket `LG-2`
  (status `done`) closed only half of this. It claims the report is
  "Written alongside the manifest at every checkpoint, so it's always current, never a separate
  stale artifact" (975-977). In fact `_write_manifest` — its only caller — runs at lines 942 and
  948 only, i.e. at terminal and early-return points. The per-item checkpoint inside the
  consumption loop calls `_write_job` alone (877, 933). So after a hard crash mid-run, `job.json`
  is current (that is exactly what `AF-CKPT-STREAM` bought, 843-852) while
  `LIBRARY.manifest.json` and `QUALITY_REPORT.txt` are stale or absent. `LG-2` closed the
  *graceful* early-return gap and is correctly closed for that scope; the hard-crash gap remains,
  and the docstring asserts otherwise.
- **The quality-floor retry's seed is not recorded** — same class as the Unit 4 finding against
  `bundle.py:196`, but **materially better handled here**: `_attempt` writes the retry to a
  distinct filename encoding the alt seed (`{base}_r{seed & 0xFFFF:04x}.png`, line 701) with an
  explicit comment that the rejected image must survive for inspection. So the evidence exists
  on disk and `it["file"]` points at it. What remains is only that `_write_manifest` still
  records `"seed": it["seed"]` (963) for an image generated at `it["seed"] ^ 0x5F5F5F`, leaving
  the manifest internally inconsistent (a `_r…` filename beside a base seed). Derivable, low
  impact, worth fixing alongside the manifest change above.
- **`build_wildcard` does not clamp `n` against `MAX_COUNT_PER_TYPE` directly** — it clamps to
  the catalog's `wildcard.tunables.count.max`, defaulting to `MAX_COUNT_PER_TYPE` only when that
  key is missing (292-293). A hand-edited catalog with a large `max` raises the ceiling on a
  paid path. The `af-libgen-money-clamp` remediation clamped the client input; the catalog is
  trusted local data, so this is a note rather than a finding.

## Fixed since last review (delta vs r1-r3 and the LIB-FLAGGED-1 round)

All prior findings re-checked against current source; **none re-opened, none re-fixed**:
- **LIB-FLAGGED-1's silent skip-on-collision — FIXED.** `_unique_flagged_dest` (901-909) is
  present with the numeric-suffix convention and correct `.height.png` double-extension
  handling; the move now always succeeds and `png`/`hp`/`vector_file` are all reassigned.
  I additionally traced the partial-failure path: if the PNG rename succeeds and the height
  rename then raises, the `except OSError` (925) leaves each variable pointing at whatever is
  actually on disk, so the manifest stays consistent with the filesystem. Correct.
- **Exclusive run lock (`bb2e047`)** — `_RunLock` intact (575-610), non-blocking, with the
  Windows `msvcrt` / POSIX `fcntl` split and release in a `finally`.
- **Split 429 / error retry budgets (`0b45c35`)** — intact (702, 734-745).
- **Auth-failure fast stop (`unit10-libgen-authfail`)** — intact (727-732).
- **BilledFailure never re-generated (`af-billedfailure-no-respend`)** — intact (717-721).
- **Count validation (`af-libgen-count-validation`) and money clamp (`af-libgen-money-clamp`)** —
  intact (253-257, 292-293), plus the malformed-`types` and non-dict-`selection` guards
  (240-252).
- **LG-3 lock_palette gating on the flag** — intact (320-322).
- **Deferred dockets consulted (G35):** 15 deferred rows name a file in this hunt; the only two
  still open (`LIB-KLEIN-WARN`, `LIB-RESHIP-NB2`) are unrelated to the findings above.
- **Wildcard empty-pool guard (`glm20-3`)** — intact (314-315).
- **CKPT-STREAM per-item checkpointing** — intact (870-935).
- **`spent_est` honesty (`hunt-af-0804`)** — `_bills()` intact and correct under every
  combination I enumerated (done / billed-failure / retry / dual-pass, including overlaps).
- **LIB-SEAM edge blending (`forgehunt1`)** — intact (775-782), correctly skipped for emblems.
