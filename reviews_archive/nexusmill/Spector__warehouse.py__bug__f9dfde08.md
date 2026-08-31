Source: Spector/warehouse.py
Reviewer: claude-sonnet-5 (in-session)
sha256: f9dfde08330b384cb6e3cc0156f7b47c34cc86ae2b3fe529af46b1b79fc1ea12
Date: 2026-08-07
Mode: bug (TARGETED DELTA - not a full re-review; see scope note below)
Context pack: this file's only prior review is .colibri_reviews/Spector__warehouse.py__bug__
deb602d6.md, a K3 (moonshotai/kimi-k3) pass from 2026-07-19 21:13, ~3 weeks before Spector's
actual product launch per CLAUDE.md's product history, cached with only a partial (8-char) sha.
This session was scoped to Spector's never-scanned files (index.py/build.py/templates/
index.html/__init__.py); warehouse.py was pulled in only because reviewing index.py required
tracing all of its callers, and that cross-file trace of the 3 SearchIndex call sites
(_ingest_locked's dedup check, inspect(), _find_locked()) surfaced a real, confirmed defect in
the FIRST of those three (see Bugs below). This is NOT a fresh full-file review - the rest of
the file's ~1122 lines were not re-audited this session.

## Verdict
The one code path actually traced end to end (the dedup dmax computation) had a real,
proveable defect, now fixed. Scope note: the cached 2026-07-19 K3 review's HIGH findings
(mixed-DNA-dimension crash in find(), scipy-absent dedup silent-pass) both appear, from what
was incidentally read while tracing the SearchIndex call sites this session, to already be
fixed by later commits - _find_locked() now has explicit dmax-padding with a comment describing
exactly the old crash, and dedup relies on `_chamfer` which is worth a fresh look - but neither
was independently re-verified against its own reproducer this session, so they are NOT marked
resolved here. Recommend a proper full re-review of this file as a follow-up: its only review
predates the product's actual launch and several referenced line numbers no longer match current
structure.

## Bugs & vulnerabilities

**[MEDIUM] Ingest-path dedup check omitted the query's own length from its padding width**
- `_ingest_locked`, was line ~371 (now ~376 after the fix's own comment)
- What: unlike its two siblings in the same file - `inspect()` and `_find_locked()`, the latter
  carrying an explicit comment ("a mixed-k library ... made ... the index query raise
  ValueError") documenting a prior fix for this exact class - the dedup check computed
  `dmax = max(len(m) for m in mats)` from the EXISTING library only, never including the
  freshly-computed `dna`'s own length, and passed `dna` unpadded into `SearchIndex.query()`.
- Trigger: the warehouse holds DNA narrower than the part currently being ingested - reachable
  today via importing a `.spectorpack` built with an older/different `k` default, a shipped,
  documented sharing feature (`import_pack`/`_clean_row`) with no k-consistency enforcement.
- Impact: `SearchIndex.query()`'s `q = q[:self.d]` silently truncated the new part's high-order
  shape modes down to the library's narrower width instead of padding the library up to match -
  discarding real discriminating information from the dedup comparison.
- Fix: `dmax` now includes `len(dna)` and the query is explicitly padded when shorter, mirroring
  `inspect()`/`_find_locked()` exactly. Behavioural proof (junk/hunt_verify_ingest_dmax.py): a
  synthetic 30-wide library vs. a 50-wide incoming DNA gave dist=0.000200 (falsely under the
  dedup threshold - would have discarded the new part's own blob and silently aliased it onto an
  unrelated existing part) pre-fix, vs. the correct dist=2.630321 post-fix. Logged in
  docs/remediation_manifest.json (2026-08-07).

## Missing safeguards
- Carried forward, unverified this session: every item in the 2026-07-19 K3 review
  (.colibri_reviews/Spector__warehouse.py__bug__deb602d6.md) not explicitly addressed above.
  A fresh full-file pass is owed - it has never been re-scanned since before Spector's launch.
