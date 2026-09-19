# Synthesis — prompt-curation post-gate re-audit (prompts.py, structure.py, colour_forms.py, catalog.json)

- **Reviewer:** claude-sonnet-5 (in-session), Colibri G37 protocol
- **Date:** 2026-09-11
- **Scope:** `asset-forge/forge/imagegen/{prompts.py,structure.py,colour_forms.py}` +
  `asset-forge/forge/catalog.json` (all four verified byte-identical against their
  `asset-forge-user` twins, G23) — the files implementing the anti-duplication/curation
  philosophy Damien described as pre-gate work: "the library generation became curated...
  some classes are special and require specialized prompt curation because forcing non
  duplicates becomes less about language and more about the knowledge of the subject
  matter."

## Bottom line

**No crash-class or shipped defect across any of the four units.** The doctrine machinery
is real, well-engineered, and (where I could test it against live data — every one of the
46 colour-curated types, every one of the 153 catalog types' structural classification)
empirically holds. The concrete gap is exactly what Damien suspected but hadn't pinned
down: **Tranche 1's per-type structural curation (47 of 153 types, 2026-08-12) was never
extended to Tranche 2**, and 51.6% of catalog types run on a keyword-inference fallback
that a documented, verifiable pattern — masonry/fibrous material words absorbing types
whose actual form belongs to `formal` — misclassifies for at least 9 confirmed cases
(aztec, greek_key, islamic, sacred_geo, penrose, gothic, mandala, barn_quilt, shibori).

## Findings ranked

1. **[MEDIUM] Tranche 2 catalog coverage gap, quantified** (catalog.json review) — 79/153
   types uncovered, 9 confirmed misclassifications. 8 share one root cause (`"formal"` has
   no active hint entries in `_FAMILY_HINTS`); the 9th (shibori) is a related but distinct
   mechanism - its better fit (cellular) DOES have active hints, they just do not appear
   in shibori's own prompt text, so an earlier-checked family wins by iteration order
   (corrected per the adversary gate's factual catch, 2026-09-11). This is
   content/scoping work, not a code fix.
2. **[LOW-MEDIUM] structure.py docstring/behavior mismatch** — CENSUS claims adaptive
   least-used selection; the code is deterministic round-robin. Doc-only fix.
3. **[LOW, PLAUSIBLE] Two independent substring-matching fragilities** (`structure.py`'s
   `_FAMILY_HINTS`, `colour_forms.py`'s `is_achromatic`) — same defect CLASS already
   confirmed and fixed elsewhere in this exact file family (`prompts.py`'s
   AF-PROMPT-TEXTURE-WORDS/STRIP-WORDS), neither has a live trigger in current data, both
   tested empirically before being downgraded from a first-draft "confirmed" guess.
4. **[LOW] subject_class() geometric-branch asymmetry** — considered, then REFUTED against
   this file's own remediation history (it IS the fix for a previously-confirmed bug, not a
   new one) before being reported. Documented as a process note, not a finding.

## Process note (for the manifest/campaign record)

This review caught its own near-miss: a first-draft finding on `prompts.py` would have
recommended re-introducing a bug (AF-PROMPT-CLASS-SUFFIX) that a 2026-09-10 post-gate pass
had already fixed, because the manifest cache-check (colibri Phase 0) was run AFTER
drafting findings instead of before. Corrected before publishing by checking
`docs/remediation_manifest.json` and the file's own review postscript. Lesson recorded in
`docs/AGENT_STATE.md` round 42 for future sessions: **run Phase 0 before Phase 1, always.**

Every finding in this synthesis and its four component reviews was checked against real
data where the tooling allowed it (running `colour_forms.allocate()`/`capacity()` against
all 46 live catalog entries; running `structure.classify()` against all 153 live catalog
types; searching for real substring collisions across all 72 colour terms and 77 curated
clauses) rather than left as theoretical — three initially-plausible concerns were tested
and came back clean, and are reported as PLAUSIBLE/forward-looking rather than shipped as
confirmed defects.

## Recommended next action

Owner-scoped, not code work: extend Tranche 1's method to the 9 confirmed cases (cheap —
`TYPE_FAMILY` corrections only, no new authored pools needed) and spot-check the remaining
~51 uncovered-but-plausible types at leisure. A permanent lint/harness row flagging any
catalog type resolving via the hint fallback (rather than an explicit table entry) would
close this class of gap going forward without requiring another manual audit pass.
