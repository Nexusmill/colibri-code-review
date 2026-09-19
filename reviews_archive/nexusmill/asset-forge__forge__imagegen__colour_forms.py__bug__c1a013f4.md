# Bug review: `asset-forge/forge/imagegen/colour_forms.py`

- **Source path:** `asset-forge/forge/imagegen/colour_forms.py` (creator edition, canonical)
- **Reviewer:** claude-sonnet-5 (in-session), Colibri G37 protocol
- **sha256:** `c1a013f47340a49f59e36e6faa3c68ea037f1b3cc7f2f25de8fb1129e4ed8812` (sha8 `c1a013f4`)
- **Date:** 2026-09-11 · **Mode:** bug, FULL review (owner ruling: the only prior record,
  grok round 5 at sha `ad2e8ae7` dated 2026-08-22, predates the adversarial gate born
  2026-08-30 and is untrusted; current bytes also differ from that sha (a GROK-CF5 fix
  landed the same day, pre-gate) — full re-read, not a delta)
- **Twin parity:** `asset-forge-user/forge/imagegen/colour_forms.py` verified byte-identical
  at the same sha256 this pass (G23).
- **Context pack:** `get_file_outline` (26 symbols, 284 lines); sole importer is
  `forge/library_gen.py` (confirmed via direct search — two call sites, line 204 for
  allocation, line 298 for the quality-floor's `is_achromatic` check); both call sites read
  in full to verify the cross-file contract; the module's own design docstring (COLOUR-FORMS,
  2026-08-14 — Damien's own escalation from "6 variations" to "n300 variations... for every
  type"); `catalog.json` (both twins byte-identical, sha `7b04f1f2`) loaded to test every
  real catalog entry against the live module, not just read as prose.

## Verdict

Shippable. **Empirically verified against every real catalog type, not just traced by
eye:** ran `colour_forms.allocate()` and `capacity()` against all 46 catalog types that
actually declare `colour_variants`/`colour_axes` — zero exceptions, and every one clears
the module's own stated n300 capacity target (the docstring's "756-1008" / "504-756"
capacity claims hold in practice, not just in the comment). No crash-class defect found.

## Bugs & vulnerabilities

**No CRITICAL/HIGH/MEDIUM found.** Traced and empirically confirmed safe:
- **The 107-of-153 catalog types with NEITHER `colour_variants` NOR `colour_axes` do NOT
  crash.** `colour_forms.allocate()` on such a type would hit `capacity()==0` and raise
  `ValueError` for any `n>0` — but `library_gen.py:204` and `:298` both gate the call behind
  `if _variants or _t.get("colour_axes"):`, so the 107 uncovered types never reach this
  module at all; they use the generic hint-cycling path (`prompts.py`'s `avoid_hints`)
  instead. Verified by reading both call sites, not inferred from the guard's presence alone.
  `library_gen.py:204-211` also wraps the call in try/except with a graceful fallback to the
  static `colour_variants` list on any `colour_forms` exception — a capacity failure on the
  46 covered types degrades, it does not crash the batch.
- **Zero-division/empty-pool risk across every indexing site** (`_pool`, `_combo_clause`,
  `allocate`'s `tail`/`head` slicing) — traced and confirmed no path divides or indexes by a
  possibly-zero length without a prior guard; `allocate()` returns `[]` immediately for
  `n<=0` before any pool access.
- **The internal collapse guard held for every real template**:
  `assert len(set(combos)) == len(combos)` in `_pool()` — this assert runs at CALL time
  (not just import time), so a future catalog edit that adds a `colour_axes.templates` entry
  missing the `{c}` placeholder would still be caught loudly the first time that type is
  generated, not silently. Confirmed by running `_pool()`/`capacity()` against all 46 live
  entries — no collapse in the current catalog.

**[LOW, PLAUSIBLE — tested empirically, not triggered by current data]
`is_achromatic()`'s specials-matching and achromatic/chromatic set checks are both
substring-based, the same class of fragility flagged in the `structure.py` review of the
same session** — `colour_forms.py:255-263`
- What: `if c and c in cl` (does a curated special's clause text appear as a substring of
  the passed clause) and `has_ach = any(t in cl for t in _ACH_SET)` /
  `has_chrom = any(t in cl for t in _CHROM_SET)` are all substring containment tests.
- What I actually checked (not just theorized): (1) whether any `_ACH_SET` entry is a
  substring of any `_CHROM_SET` entry or vice versa — **zero cross-hits across all 72
  colour/metal/wood/stone terms**; (2) whether any catalog type's curated special clause is
  a substring of another type's special clause — **zero collisions across all 77 curated
  clauses in the live catalog**. Both checks came back clean against real data, so this is
  NOT a live defect today.
- Why flagged anyway: there is no assert or test enforcing either invariant going forward —
  a future colour/wood/stone entry or a new curated special could introduce a substring
  collision with nothing catching it before a quality-floor judgement silently flips
  (an achromatic-intended image judged chromatic, or vice versa). Recommend an assert
  alongside `_ACH_SET`/`_CHROM_SET`'s definition (no chromatic term is a substring of an
  achromatic one or vice versa) mirroring the collapse-guard pattern already used in `_pool()`
  — cheap insurance for a check that currently has none.
- Verification: **tested against live data, found no trigger; PLAUSIBLE only as a
  forward-looking gap**, not a confirmed present-day defect.

## Missing safeguards
- `library_gen.py`'s fallback path (on a `colour_forms` exception) returns the RAW curated
  `colour_variants` list without truncating or cycling it to match the requested `n` — for a
  type with fewer curated variants than `n` requested, the fallback under-supplies rather
  than raising or cycling. This is `library_gen.py`'s fallback logic, not a defect in this
  file, but worth noting since it's the direct consequence of this module's fail-loud
  design meeting a caller that doesn't fully honour the same contract on the fallback path.
  Not independently verified this pass (`library_gen.py` is out of this session's scope,
  already reviewed separately in round 39).
- No harness/lint check enforces the doctrine's own stated target ("all clear n=300 with
  headroom") against catalog edits — a new type could be added with `colour_axes.templates`
  supplying too little capacity and nothing would flag it until a generation run hit the
  `ValueError` live. The runtime check exists (fail-loud, confirmed above); a pre-flight
  lint over `catalog.json` would catch it before spend rather than during it.

## Cross-file note
This module and `structure.py` (reviewed earlier this session) are deliberately parallel
in design (per-type capacity contract, specials-pinned-at-slot-0, capacity-refused-never-
wrapped) and share the SAME substring-matching fragility class in their respective
"does this text describe that category" checks (`_FAMILY_HINTS` there, `is_achromatic`
here). Neither has a live trigger today; both would benefit from the same hardening
pattern if one is applied.

## Adversarial verification (Phase 3)
- Ran `capacity()`/`allocate(n=6)` against every one of the 46 real catalog types with
  `colour_variants`/`colour_axes` — zero exceptions. CONFIRMED the doctrine's capacity claim
  holds in practice.
- Re-read both `library_gen.py` call sites verbatim to confirm the `if _variants or
  colour_axes:` guard actually gates BOTH the allocation call (line 204) and the
  `is_achromatic` quality-floor call (line 298) — CONFIRMED, not assumed from one site.
- Tested the achromatic/chromatic cross-substring theory against all 72 real terms and all
  77 real curated clauses — CONFIRMED clean (zero hits), so the finding above is reported as
  PLAUSIBLE/forward-looking, not shipped as a confirmed defect.
