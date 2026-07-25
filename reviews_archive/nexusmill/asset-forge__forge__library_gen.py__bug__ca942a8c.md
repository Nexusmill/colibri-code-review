# colibri-review — asset-forge/forge/library_gen.py  (bug)
- source: asset-forge/forge/library_gen.py  (+ twin asset-forge-user/forge/library_gen.py)
- model: claude-fable-5 (in-session, max)  · sha256: ca942a8c64d5b85f1c1444a34ac16749a6e4d48a4670ccdde043fe1165f7629d  · date: 2026-07-22  · mode: bug
- context pack: grep importers (app.py libgen_start/estimate) · remediation_manifest (3 prior
  library_gen fixes: run_job double-charge lock bb2e047, retry budgets 0b45c35, wildcard
  empty-pool guard glm20-3) · catalog.json tunables (wildcard count.max=200; 12 packs/153 types) ·
  sync_builds.py WHITELIST (library_gen.py is a SHARED byte-identical file — NOT whitelisted)

## Verdict
Shippable AFTER this fix. Single biggest risk was unbounded paid-generation count.

## Bugs & vulnerabilities
**[HIGH] Unclamped paid-generation count — money-safety** - `build_plan` count (line ~86), `build_wildcard` n (line ~108)
- What: per-type `count` and wildcard `n` were taken from user input with NO upper bound.
- Trigger: POST /api/library_gen/start (or /estimate) with selection count=100000 (fat-finger or malformed client).
- Impact: prepare_job/libgen_start launch a paid Replicate run of arbitrary size. Proven by execution:
  count=100000 -> 200,000-image plan, estimate $600, unbounded upward (spends real money on the
  user's own Replicate account up to their balance; run pauses only on 402/insufficient-credit).
- Fix: clamp per-type count and wildcard n to the catalog's OWN documented ceiling
  (wildcard count.max = 200) via MAX_COUNT_PER_TYPE at the shared build_plan/build_wildcard choke
  point. Clamps DOWN (fail-safe); the /estimate endpoint builds via build_plan so it now reflects
  the true capped image count + cost before the user pays. VERIFIED: count=100000 -> 200 on both
  editions; legit count=6 -> 6 unchanged.

**[MEDIUM] Twin-build drift (G23) — user edition missing empty-pool guard** - user `build_wildcard`
- What: the wildcard empty-pool guard (creator commit glm20-3) was never propagated to
  asset-forge-user/forge/library_gen.py (a SHARED, non-whitelisted file that must be byte-identical).
- Trigger: user edition wildcard with wildness low enough to empty a pool -> rng.choice([]) IndexError.
- Impact: crash in the shipped user build; sync_builds.py drift guard would flag it.
- Fix: reconciled user==creator (byte-identical), which restores the guard AND lands the count clamp.
  VERIFIED: files now IDENTICAL; guard present in user edition.

## Missing safeguards (noted, lower priority — not fixed here)
- No TOTAL-plan backstop cap: selecting all 12 packs x 153 types x 200 still theoretically = ~30.8k
  images. Per-field clamp closes the fat-finger vector; /estimate discloses cost (G19). A total cap
  would need a raising path + app.py handling in both editions — deferred as a follow-up.
