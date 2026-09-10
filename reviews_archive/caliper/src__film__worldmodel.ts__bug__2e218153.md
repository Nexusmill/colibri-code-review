# colibri bug review - src/film/worldmodel.ts (delta)

source: src/film/worldmodel.ts · reviewer: ZCode GLM-5.3 in-session · sha256 2e218153 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 80b059a3 @ 7c3ad72 2026-08-31)
context: diff 31+2; prior review 80b059a3 (2026-09-03 fresh-context) carried; consumers: vite.film world-build loop + withWorldAnchor + carriesAnchor (new).

## Verdict

Shippable - the delta is hardening: duplicate-name refusal, single materials validation, and a checkable anchor-carried helper.

## Bugs & vulnerabilities

None new. refuseDuplicates throws (strict, re-ask pattern) on same-named characters/sets - names are the selection key (ruling 42) and ambiguity there defeats every downstream gate; materials strList now evaluated once; carriesAnchor uses token coverage with an explicit multi-character rationale (relevant-sheet embedding, not the whole block) and a 0.6 floor - an empty anchor set returns true (nothing to carry).

## Missing safeguards

- carriesAnchor's stop-word-less token space counts "the/and"-class words as coverage if the anchor contains them (length>2 filter removes most) - acceptable for its test/gate role.

## Fixed since last review

- (prior findings from 80b059a3 were addressed in this delta per the 2026-09-03 hunt; duplicate-name refusal + single-validation verified present.)

## Verified-correct

- compileAnchor/withWorldAnchor unchanged in shape (spread + typed generic); the helper's coverage loop counts distinct anchor tokens present in the prompt.
