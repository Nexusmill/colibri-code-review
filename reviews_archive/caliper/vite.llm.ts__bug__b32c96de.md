# colibri bug review - vite.llm.ts (delta)

source: vite.llm.ts · reviewer: ZCode GLM-5.3 in-session · sha256 b32c96de (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 96752e82 @ 1fbf0ed 2026-08-23; unchanged regions byte-identical to prior sha)
context: diff 38+11; prior review 96752e82 carried; cross-file: brain.json pick vs BRAIN_OPTIONS/BRAIN_ENDPOINTS, readServiceKey, the wizard/agent turnOnCloudBrain consumers; Node Dirent.parentPath availability (Node 25).

## Verdict

Shippable - no new defects. The delta is the persisted brain pick (owner ruling 26) done honestly (never persists "local", key-gated on read) and a traversal-surface-free extract rewrite.

## Bugs & vulnerabilities

None new. readBrainPick validates provider against isBrainId and rejects "local"; keyedBrainPick nulls when the pick's key is gone (falls back to the registry default, never a broken brain); every cloud start re-persists the chosen model. The extractServer recursive-readdir rewrite builds paths only from parentPath+name (already-joined by Node) - no zip-controlled name reaches a path constructor.

## Missing safeguards (unchanged)

- Download redirect boundary checked on the original URL only (prior note).
- OPTIMIZE double-click double-spawn window (prior note).

## Fixed since last review

- (no open confirmed findings at 96752e82)

## Verified-correct (adversarial passes, findings deleted)

- cloudModels[brainKind] fallback chain (pick.model only when the pick matches the resolved provider; BRAIN_OPTIONS registry otherwise); writeBrainPick's no-op guards (local/empty) prevent junk persistence; readdir failure degrades to [] then the not-in-zip error.
