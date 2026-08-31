Source: Spector/index.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 499b337968fb03ad2554af8e759f46c7351ed48dea90636d4f0d67f1d4a2b1d1
Date: 2026-08-07
Mode: bug (FIRST review - never in .colibri_reviews/_manifest.json; Spector as a whole was
missing from _hunt_plan.json entirely, carrying a stale "design-stage, below the line" doc-note
that predates the product actually shipping - see the hunt-plan _rule fix in this same sweep)
Context pack: full 55-line file read; find_importers=0 (dynamic `import index as _index`/`from
. import index`, not statically resolved) so cross-referenced via search_text: SearchIndex is
called from Spector/warehouse.py (already-reviewed unit) at 3 sites - the ingest-path dedup
check, inspect()'s dry-run nearest lookup, and _find_locked()'s similarity search - plus
Spector/tests/test_regressions_0701.py. Traced all 3 warehouse.py call sites in full to check
how each constructs the matrix/query width relative to SearchIndex.query()'s own pad-or-
truncate contract.

## Verdict
Shippable. No confirmed defect in this file itself. Its query() method's "pad if shorter,
truncate if longer" contract is a genuine sharp edge that already caused a real bug in one of
its three callers (see below) - not a defect in index.py, but worth hardening here since every
future caller inherits the same trap.

## Bugs & vulnerabilities
None confirmed in this file.

## Missing safeguards
- query()'s `q = q[:self.d]` silently truncates an over-long query to the index's width instead
  of raising. Traced impact: this is exactly the failure mode _find_locked() in warehouse.py
  documents fixing with an explicit comment ("a mixed-k library ... made ... the index query
  raise ValueError"), and the ingest-path dedup check (warehouse.py's other caller) still had
  the unfixed version until this same review sweep found and fixed it (see
  docs/remediation_manifest.json, 2026-08-07, Spector/warehouse.py entry) - a proven, not
  theoretical, cost of leaving this contract implicit. A caller-facing improvement: raise
  ValueError when len(q) > self.d and the caller hasn't opted into truncation, so a future
  fourth call site fails loudly in testing instead of silently discarding shape information.
  Not fixed in this pass (would require auditing every call site's tolerance for the new
  exception; flagged for a follow-up rather than a same-session behavior change to a shared
  primitive with 3 live callers).
- `top` is trusted as already-sane by every current caller (warehouse.py always passes an
  int; app.py's public API clamps ?top= to [1,100] via _clamped_top() before it ever reaches
  Warehouse.find()). No live path was found that could pass zero/negative top into query(),
  so not reported as a bug - noted only because query() itself does not defend against it
  (int(min(top, self.n)) with a negative top passes a negative k to faiss.search, which was not
  exercised).
