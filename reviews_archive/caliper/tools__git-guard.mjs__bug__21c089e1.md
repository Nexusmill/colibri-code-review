# colibri bug review - tools/git-guard.mjs (delta)

source: tools/git-guard.mjs · reviewer: ZCode GLM-5.3 in-session · sha256 21c089e1 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 1c33320b @ 6d44839 2026-08-30)
context: diff 126+38; prior review 1c33320b (2026-09-03) carried; the Tools-twin gate reviews (gate_20260904-152036/-154627/-161013, rounds 2-6) already adversarially verified these exact rules; tools/git-guard.test.ts battery green.

## Verdict

Shippable - the decide() extraction (pure core + thin process entry) and the token-aware rules closing the four live-tested bypasses and the EV-028 path-segment family.

## Bugs & vulnerabilities

None new. Verified in this pass: the -n bundle logic (letters before n must all be flag-taking; -mn allows, -nm denies); the disjoint triple-alternative regex (no exponential backtrack on ./-runs - measured in the Tools twin round 5); the ambiguous-segment enumeration (cap 8 -> deny; both-ways reading catches mixed x/.../../hooks); the .githooks/ non-match; script-entry guard via pathToFileURL (import for tests does not write stdout).

## Missing safeguards

- (documented residual, unchanged) full variable/eval indirection of the FLAG itself stays beyond regex reach - the inner git hook is the real gate.

## Fixed since last review

- the four bypasses (separate-token -n, env-var hooksPath injection, comm\it escaping, verb-gap .git/hooks writes) - FIXED and battery-covered; the -mn live false positive - FIXED (bundle direction check).

## Verified-correct

- Rule 3's GIT_CONFIG_KEY_N trigger fires before any git word (env injection shape); read-verb list deliberately excludes a bare `git` word-match (the .git-in-path self-match trap, documented); deny-on-doubt default for unknown verbs.
