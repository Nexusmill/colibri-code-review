<!-- source: src/api/queueNodes.ts | reviewer: glm-5.3-zai-in-session | sha256: 29c6863ae671cf3727a8584abb79d45bc450389d3e6cfb9a00d80948f1cb98f0 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the NEXT top ten files by import PageRank (the board past the hunted ten); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop). -->

## Verdict
Shippable. The delta since the prior review (sha256 7d97c642 → 29c6863a) is a documentation-comment change only — zero executable-code change (verified by recovering the prior blob from git dangling objects, `ffdf2ba3`, and diffing against the working tree: a single hunk at lines 17-19). The comment edit is itself a truthfulness fix: the old comment claimed the spoken count was "de-duplicated", which was false — the code has always spoken the raw `nodes.length`. The new comment now matches the code exactly (`nodes.length` raw total; `unique` distinct classes in graph order, capped at 6 with `+N more`), aligning with the repo's truthful-status doctrine. Pinned tests pass fresh: 5/5 in `src/api/queueNodes.test.ts`.

## Fixed since last review
- Prior review (2026-09-06, sha 7d97c642) recorded zero findings; verdict was "Shippable. Pure decode ... malformed shapes return [] never throw (pinned)." — **verified still true**: `queueNodeClasses` (lines 6-15) unchanged byte-for-byte; the malformed-shape behavior (`null`, `undefined`, `"string"`, non-node values → `[]`) is pinned at `src/api/queueNodes.test.ts:16-19` and passed in today's fresh run.
- The old comment's implicit misdescription ("de-duplicated for the count") — a latent doc-vs-code falsehood present at the prior sha — **fixed** by this delta (lines 17-19 now accurately say "total node count (raw, duplicates included)"). It was never file-internal risk (no behavior read the comment), but it violated the truthfulness doctrine; corrected.

## Bugs & vulnerabilities
None new. The changed lines are comment-only; re-opened per Phase 3 and traced:
- The new comment's three claims were each checked against the code: raw count = `nodes.length` (line 23, template head); distinct list = `[...new Set(nodes)]` (line 22) — `Set` preserves insertion order, which for `Object.values` iteration in `queueNodeClasses` is graph order; `+N more` derived from `unique.length - 6`, consistent with the capped list (line 23). No mismatch survives.
- Consumer contracts re-verified at both sites, unchanged since the prior review: `src/api/client.ts:88` passes the untyped prompt blob `entry[2]` into `queueNodeClasses(prompt: unknown)` (guard at line 7 absorbs any shape); `src/surfaces/QueueSurface.tsx:114` passes `e.nodes` (typed `string[]`, declared `src/api/client.ts:74-75`) into `describeQueueNodes`. No drift, no break.

## Missing safeguards
- (Carried observation, unchanged code, not a new finding) `describeQueueNodes` trusts its `nodes: string[]` annotation; the only production caller feeds it the output of `queueNodeClasses`, which pushes only verified `typeof ct === "string" && ct` values — so no coercion path exists today. No action needed.
- (Out-of-file, cosmetic) `QueueSurface.tsx:114` renders "runs the entry carries no readable graph" for an empty decode — grammatically awkward seam of the two strings, but that wording lives in QueueSurface and is unchanged; noted only so the next QueueSurface pass can see it.

context-pack: jcodemunch `local/Caliper` (find_importers → client.ts, QueueSurface.tsx, queueNodes.test.ts; usages traced), git dangling-blob recovery of prior sha, fresh vitest run.
new-findings: 0
