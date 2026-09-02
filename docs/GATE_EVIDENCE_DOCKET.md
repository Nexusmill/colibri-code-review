# GATE_EVIDENCE_DOCKET.md - what the gate has caught (the running case)

> Owner order 2026-08-31: *"keep a manifest of everything the adversary catches and
> forces you to remediate as an evidence docket to further bolster the case for this
> gate and layered structure."* Machine-readable twin: `gate_evidence.json` (the row of
> record - this page is the readable summary). **Covenant: every catch that forces a
> remediation gets a row in the same working session as the catch. Rows are never
> deleted.** False rebuttals are the strongest evidence in the file: they prove the
> founding thesis - authors, AI agents included, defend invented claims about code
> they have not read.

## The scoreboard (as of 2026-09-01)

- **19 evidence rows** across 3 days of the gate's existence.
- **A false-green test-coverage construction caught before it landed** (EV-019): the
  new PS-LIB battery's run-integrity guards each failed only one of its two rows, so
  a missing Blender, a pre-check crash, or the packaged add-on failing to enable -
  the exact regression class the battery exists to catch - left the other row PASS
  with zero checks executed. The reviewer traced all four trigger paths from the
  staged bytes; the fix (both-row LIBRUN_ guards + own-evidence-required grading)
  was verified by trace in the re-review.
- **The gate blocked its own model promotion, three times** (EV-018): the change that
  made deepseek the primary reviewer was BLOCKed by deepseek itself on its first
  official runs (two findings BLOCKs plus one fail-closed BLOCK on its own empty
  response) - a reachable crash behind a false 'unreachable' comment, a dead
  fallback on the canonical transport failure, and a security comment
  contradicting the code; the final CLEAR arrived through the new fallback path
  exercising itself live.
- **An incomplete truth-pass caught inside a CLEAR** (EV-017): a registry
  correction fixed one occurrence of a stale count and declared victory; the
  reviewer's clearance notes pointed at the second occurrence three rows away,
  and the re-edit invalidated the clearance exactly as designed.
- **A remediation itself caught destroying data** (EV-016): the fix for the archive
  schema drift silently discarded two real review records on a mode collision; the
  reviewer traced the deletion out of the staged diff and the BLOCK stopped it from
  landing - the corpora were restored and re-normalized loss-free. Remediations get
  reviewed like any change; that is why.
- **~24 covenant violations by past sessions surfaced in one sweep** the first time the
  post-gate audit ran the features critic (EV-015): stale testers masking stronger code,
  an overruled design still asserted as the contract, thirteen orphaned green batteries,
  nine never-tested rows - the harness's verdicts had quietly stopped meaning anything
  for a fifth of the registry until a detection layer was made to look.
- **3 false rebuttals by the authoring agent, caught by the reviewer reading the actual
  bytes** (EV-001, EV-002, EV-010) - including one made the same day the author wrote
  the docket row about the previous two.
- **1 CRITICAL total-disarm caught before it shipped anywhere POSIX** (EV-003: mode
  100644 = the entire gate a silent no-op on Linux/macOS clones, present in all three
  originally-armed repos).
- **1 CRITICAL silent-bypass class caught at design time** (EV-005: forging
  clearance.json - invisible to every other layer; now denied machine-wide).
- **1 layer that caught its own production bug on first live use** (EV-006: the push
  guard's --not toggle) and **1 fail-closed design that proved itself live** (EV-004:
  a 50-minute empty model response BLOCKed instead of clearing).
- **3 real defects found in code that had ALREADY passed review** when it was re-read
  in a new context (EV-008: the distributed plugin bundle) - "reviewed" is a property
  of a diff in a repo, not of bytes.
- **2 governance-data diseases surfaced only because the gate forces manifest reads**
  (EV-011 duplicate keys, EV-014 misfiled dockets making open work invisible).
- **1 backwards security decision reversed** (EV-009: the rebase-only merge fallback
  that would have let unaudited shas onto protected branches), with the follow-up
  round also catching the overstated docstring.
- **The guard held against its own author twice within an hour of going live**
  (EV-012) - reworded, never weakened.

## Why this docket exists

Every row is a defect, bypass, or false claim that the ordinary workflow - the same
agent writing, reviewing, and committing - had already missed or would have shipped.
The layered gate did not make the authors better; it made their errors LOUD before
they landed. That is the whole argument, and it is also the argument for a
harness-native version of the same mechanism
([anthropics/claude-code#90887](https://github.com/anthropics/claude-code/issues/90887)):
the rows in the `advisor`/`design` layers and the accepted-false-positive frictions
show what userland cannot close cleanly.

## Reading the rows

See `gate_evidence.json`. Fields: `layer` names which enforcement layer made the
catch (gate-review BLOCK, pre-commit wall, post-commit notary, push guard, auditor,
harness guard, CI, advisor second-reviewer); `author_initially` records whether the
author disputed the finding - the false-rebuttal rows quote what was claimed and how
it was disproven; `resolution` links the fix and its regression coverage.
