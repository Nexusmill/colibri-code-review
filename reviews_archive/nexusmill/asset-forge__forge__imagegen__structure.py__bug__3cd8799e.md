# Bug review: `asset-forge/forge/imagegen/structure.py`

- **Source path:** `asset-forge/forge/imagegen/structure.py` (creator edition, canonical)
- **Reviewer:** claude-sonnet-5 (in-session), Colibri G37 protocol
- **sha256:** `3cd8799ece48a1fc320239a53c7e2979ae7bf610032db63fa31fad981d8c8cb0` (sha8 `3cd8799e`)
- **Date:** 2026-09-11 · **Mode:** bug, FULL review (owner ruling: the only prior record,
  grok round 6 at sha `75c4c096` dated 2026-08-22, predates the adversarial gate born
  2026-08-30 and is untrusted as a baseline; current bytes also differ from that sha — a
  GROK-STRUCT6 fix landed 2026-08-23, itself pre-gate — so this is a full re-read, not a
  delta)
- **Twin parity:** `asset-forge-user/forge/imagegen/structure.py` verified byte-identical at
  the same sha256 this pass (G23) — findings apply to the end-user build unchanged.
- **Context pack:** `get_file_outline` (14 symbols, 724 lines); sole importer is
  `forge/library_gen.py` (confirmed via the `prompts.py` review's cross-file check —
  `library_gen.py:194-258` calls `structure.allocate` and threads `structures=` into
  `expand_theme`); the module's own extensive docstring (the design rationale: distance-2
  code by construction, the V4 catalog-`variants` dead-data precedent this replaces); the
  `TYPE_FAMILY`/`TYPE_FORMS`/`FAMILY_FORMS` tables read in full; every one of the 724 lines
  read end to end.

## Verdict

Shippable. The core guarantee (`allocate()`'s distance-2 code — every pair of slots differs
in >= 2 of {form, massing, edge, incident}) is mathematically sound and I traced it by hand,
not just by reading the comment: the CRT-injectivity argument for `lap -> (lap mod 8, 3*lap
mod 7)` holds (`gcd(3,7)=1` makes `3*lap mod 7` a bijection of `lap mod 7`, so the pair is
injective for `lap < 56` by CRT since `gcd(8,7)=1`), the `_CHECKSUM_INVARIANT` assert and the
`_EDGE_STRIDE`/`len(EDGE)` coprimality assert both fire at import (loud failure, not silent),
and `allocate()` raises `ValueError` rather than wrapping when `n` exceeds capacity. One
real documentation/behavior mismatch found; one design fragility flagged PLAUSIBLE without a
confirmed trigger.

## Bugs & vulnerabilities

**[LOW-MEDIUM] The module docstring's CENSUS claim does not match `allocate()`'s actual
selection logic** — module docstring vs `structure.py:671-724`
- What: the docstring states *"CENSUS. Selection tracks how often each axis value has been
  used and prefers the least-used."* The actual code does not do this: `fi`, `mi`, `ei` are
  computed by a purely deterministic formula (`(off_f + i) % len(forms)`,
  `(off_m + lap) % len(MASSING)`, `(off_e + _EDGE_STRIDE * lap) % len(EDGE)`) seeded once
  from a hash of `(type_id, seed)` — there is no runtime frequency tracking that feeds back
  into which axis value gets picked next. The `census` dict is populated strictly AFTER each
  slot is chosen (`census[axis][val] = census[axis].get(val, 0) + 1`), as a passive report
  for callers/tests to inspect balance, never as an input to the selection itself.
- Trigger: none needed to reproduce — this is a static claim-vs-code mismatch, confirmed by
  reading `allocate()`'s body; no runtime condition changes the outcome.
- Impact: no functional bug (the round-robin/lap scheme it actually uses is a STRONGER
  guarantee than "prefers least-used" — it's a proven-by-construction distance-2 code, not a
  greedy heuristic). The risk is purely to future maintainers: the docstring invites the
  belief that `allocate()` adapts to census data, which could lead someone to "wire in" the
  census as a feedback input (defeating the deterministic reproducibility the module's own
  headline requirement demands — "Deterministic in (type_id, n, seed)"), or to treat the
  census as evidence of adaptive balancing it does not provide.
- Fix: reword the docstring's CENSUS bullet to describe what the code does — a passive
  per-slot record for callers/tests to assert balance against the round-robin/CRT
  guarantee, not a selection input. No code change needed.
- Verification: CONFIRMED (read `allocate()`'s full body; no branch reads from `census`
  before writing to it).

**[LOW, PLAUSIBLE — no confirmed trigger found] `classify()`'s `_FAMILY_HINTS` scan matches
hint words as raw substrings, the same defect class already found and fixed elsewhere in
this codebase's sibling file** — `structure.py:597-613, 643-656`
- What: `any(h in blob for h in hints)` tests substring containment, not whole-word matching.
  This is the exact pattern `prompts.py`'s `is_texture_intent`/`_strip_concept` used to use
  before the 2026-09-10 full re-audit replaced both with compiled whole-word regexes
  (AF-PROMPT-TEXTURE-WORDS/STRIP-WORDS, confirmed in this session's delta review of that
  file) — this file was never given the equivalent hardening.
- Trigger sought but not found: I tried to construct a realistic catalog-type or bundle-theme
  string that would misclassify via an unintended substring hit (e.g. "rib" inside "fiber",
  "tile" inside "reptile", "grit" inside "integrity") and in every pattern-relevant case I
  could construct, either (a) an earlier, more specific hint in an earlier-checked family
  matches first by design (e.g. "reptil" is an explicit `overlapping`-family hint, checked
  before `masonry`'s "tile" could hijack "reptile"), or (b) my candidate word did not
  actually contain the substring on closer inspection. I could not produce a clean,
  real-world trigger in this pass.
- Impact if a trigger exists: cosmetic, not a crash — a misclassified type gets a
  structurally-plausible-but-wrong 10-phrase pool (the `"formal"` fallback still applies if
  nothing matches at all, so there is no crash path either way).
- Verification: **PLAUSIBLE, not CONFIRMED** — flagging per Phase 3's rule (unverified
  claims are kept only with an explicit note, never presented as confirmed). Recommend
  hardening to whole-word matching as defense-in-depth given the established precedent in
  this exact file family (three confirmed substring bugs already fixed in `prompts.py`), not
  because a live failure was reproduced here.

## Missing safeguards
- No harness/lint check flags a catalog type that resolves via the `_FAMILY_HINTS` fallback
  (as opposed to an explicit `TYPE_FAMILY`/`TYPE_FORMS` entry) — see the cross-file finding
  below, carried from the `prompts.py` delta review of the same session.
- `capacity()`/`allocate()`'s raise-on-overflow is the correct choice (a caller asking for
  more than the pool can distinctly supply gets a loud `ValueError`, not silent duplication)
  but nothing in this file or its sole caller (`library_gen.py`, already reviewed separately)
  pre-flights that check before spending on a batch — not re-verified in this pass since
  `library_gen.py` is out of this session's scope.

## Cross-file note (already reported once, cross-referenced here rather than duplicated)
The `TYPE_FORMS`/`TYPE_FAMILY` "Tranche 1" coverage (47 authored types) is explicitly
documented as incomplete — see the `docs/CURATED_DEFAULT_PROMPTS.md`-referenced "tranche 2"
note in `TYPE_FAMILY`'s own comment. Full finding recorded in this session's
`asset-forge__forge__imagegen__prompts.py__bug__19c0084e.md` delta section (2026-09-11) to
avoid duplicating it in two files; carried forward to the `catalog.json` unit.

## Adversarial verification (Phase 3)
- Re-derived the CRT injectivity argument independently rather than trusting the comment's
  assertion — CONFIRMED correct for `lap < 56` given `len(MASSING)=8`, `len(EDGE)=7`,
  `_EDGE_STRIDE=3` (coprime to 7, verified by the module's own `_gcd` assert at import).
- Attempted to falsify the distance-2 guarantee by hand-picking two slot indices `i1, i2`
  within one lap (same massing/edge) and confirming their `incident` values differ whenever
  `form` differs (since `incident = (form+massing+edge) % len(INCIDENT)` and
  `len(INCIDENT) >= max pool size` by the asserted invariant) — CONFIRMED holds.
- Traced every `%` (modulo) site for a zero-divisor risk (`len(forms)`, `len(MASSING)`,
  `len(EDGE)`, `len(INCIDENT)`) — all are non-empty module-level constants or the result of
  `forms_for()`, which always returns a non-empty list (either a `TYPE_FORMS` entry or a
  `FAMILY_FORMS` entry, both authored as non-empty pools) — CONFIRMED no ZeroDivisionError
  path.
- The census/docstring mismatch was verified by reading `allocate()`'s control flow twice,
  confirming no code path reads `census` before the loop that writes to it — CONFIRMED.
