# GATE_EVIDENCE_DOCKET.md - what the gate has caught (the running case)

> Owner order 2026-08-31: *"keep a manifest of everything the adversary catches and
> forces you to remediate as an evidence docket to further bolster the case for this
> gate and layered structure."* Machine-readable twin: `gate_evidence.json` (the row of
> record - this page is the readable summary). **Covenant: every catch that forces a
> remediation gets a row in the same working session as the catch. Rows are never
> deleted.** False rebuttals are the strongest evidence in the file: they prove the
> founding thesis - authors, AI agents included, defend invented claims about code
> they have not read.

## The scoreboard (as of 2026-09-04)

- **31 evidence rows**, one line each (the running summary; the full rows are in `gate_evidence.json`):
  - EV-020: a phase-2-sweep gate BLOCK caught two confident-wrong claims in the agent's OWN gated review deliverables — a dropped finding + a false "ten locations" count.
  - EV-021: while gating the sweep's OWN remediation, the gate CRASHED on a malformed-200 from OpenRouter — a documented-but-deferred MEDIUM in the gate's own `_call_one_model` — blocking its own commit until fixed; the fail-closed crash is what surfaced it.
  - EV-022: hardening the harness_guard residuals took **eight gate rounds** — a real agent-reachable forgery route into gate state (write-denylist gaps, first-word read-allowlist, process substitution, function-shadowing, PATH hijack) or an integrity defect (author overclaims, a staging mismatch) caught nearly every round; the final secure design blocks the whole state dir from Bash with no read exemption; round 8 was a gate regex-misread settled by a byte-cited rebuttal.
  - EV-023: the gate BLOCKed a commit that would have written **live plaintext network credentials** (two device admin credentials pasted into a tracked memory-archive file) into permanent git history; content review, not path/extension filtering, is what caught it.
  - EV-024: amending EV-023, the gate BLOCKed the author's confident-wrong claim that the creds “never left the machine” — false, since the gate's own review transmits the staged diff to a remote model, so the EV-023 catch itself sent them off-machine; accepted not rebutted, the owner reaffirmed no-rotation on a no-financial-exposure basis, and the exposed enforcement gap (the gate skipped docs-only commits AND transmitted secrets to review them) was addressed by a LOCAL secret pre-scan in the gate (Tools 89df736) that catches pattern-detectable secrets on every staged file without transmitting them (residual: a bare dictionary-word password in a docs-only prose commit is caught by neither the pattern scan nor the LLM, which only reviews code — documented, a separate owner call) — which the gate then reviewed across three rounds, BLOCKing itself twice first (incl. the removed-content exfiltration flow, and an escaping bug the author introduced fixing round 1) before CLEAR).
  - EV-025: committing the HOOK-JSON-CODEPAGE fix in Nexusmill (the SessionStart grounding hook emitted cp437-corrupted JSON that Claude Code 2.1.258 rejects, silently dropping the whole grounding context), the local secret pre-scan BLOCKed on a weeks-old AGENT_STATE line whose 'token = ...' value is a 21-character all-uppercase env-var NAME (no digits, no lowercase) - a `_looks_secret` false positive on the '20+ chars, two classes' branch. Accepted, not loosened: the doc line was reworded to what it is, the floor left untouched pending an owner ruling on rejecting identifier-shaped values (which would also exempt all-caps digit-free passphrases) and on full-blob vs added-lines scanning of large historical docs). RULED the same day: the floor now requires a digit class on the long two-class branch (Tools ad641bb, TDD 51->54), and the fixtures exposed a pre-existing fail-open (unquoted letter-led hex swallowed by the bare-identifier exemption), fixed in the same commit; the gate's first review of that fix BLOCKed on a claimed docstring self-trip that the bytes refuted. Second ruling the same session: the floor scans ADDED lines only, at new-file line numbers (Tools 623bb1a, 54->56); history is the auditor's problem, not the floor's. Honest limits recorded: binary and >25 MB blobs were never scanned by the floor and still are not (the guard predates the ruling and is retained); the gate's own review of the change caught a real `.gitattributes -diff` blind spot (fixed with --text, fixture 24c) and made a mid-merge combined-diff claim that the bytes refuted (fixture 24d).
  - EV-026: wiring the new G38 skill gate at repo level (so Cowork, which executes only repo-level hooks, is gated), the gate BLOCKed with three real findings, the first MEDIUM: the project-level instance decided whether to step aside for the user-level instance by a SUBSTRING test on ~/.claude/settings.json, so a user file carrying only a PreToolUse row - exactly the shape of the change's own selftest fixture - made it skip post/stop too, nothing was ever recorded, and G-POSTURE would have denied the first source edit forever in every CLI/VS Code session with partial wiring (the gate's own "a hook bug must never brick work" invariant, violated by its own wiring); plus the installer crashing (exit 1, indistinguishable from "rows missing") on structurally wrong settings instead of REFUSING, and a mixed foreign+gate row being clobbered. All three reproduced RED then fixed GREEN (per-event, per-subcommand row detection with any-doubt-runs; one REFUSED/exit-2 path; gate-owned = every hook in the row), selftests 63->66 and 19->25, round 2 CLEAR (Tools eb86adb). Then the per-repo reviews of the generated settings files (all eight BLOCKed) caught one more real gap - 3DPrinting registers desktop-commander as `desktop-commander-local`, which the exact-name matchers could never see - fixed test-first by prefix canonicalisation + regex matchers (Tools c2b1781, selftest 70/70); their other claims (`args` "not in the schema", absolute paths, Skill post-only, fail-open) were rebutted with the documented schema, the live G39-guard evidence and the design spec - and then 3DPrinting's round 2 turned the rebuttal's own "never a block" claim against it: bare `python.exe <path>` exits CPython status 2 when the script is missing, which IS the hook protocol's block code, so a moved Tools checkout would have hard-blocked every tool and the Stop hook in every repo with no in-agent recovery. Accepted over the author's rebuttal, fixed test-first with an inline bootstrap that exits 0 on a missing script - and the review of THAT fix caught the next one: plain `python -c` puts the hooked repo's directory first on sys.path, so a repo shipping `json.py` would have run inside the gate process; fixed with `-I` isolated mode + an explicit path insert + tracebacks to stderr, proven by a poisoned-cwd process test (installer selftest 30/30, user-level rows rewired too, Tools 512d35a); the same latent brick in the G39 harness_guard rows is flagged to the owner.
  - EV-027: gating the new G38 skill-census tool (Nexusmill ff4de0d0), round 1 BLOCKed on a MEDIUM that was a scope false positive - the reviewer, which is sent code-class files only, declared the staged census record "not staged" and the manifest row a same-commit contract break; rebutted with the staged name-status bytes and accepted - plus two real LOWs fixed test-first (output directories never created, so the docstring's own example crashed after the full walk; an absent store root silently produced a confident zero for the very metric G38 polices, now a stderr warning) and one speculative LOW declined on a full two-store walk + shape probe (the reviewer weighed the decline and accepted it: unguarded shapes fail loud, the safe direction). Same session, flagged not fixed: the skill gate itself mis-denied a mid-session edit as "first source edit" after a verification-before-completion run.
  - EV-028: closing the GUARD_PORTABILITY backlog in the G39 harness guard (`.git/hooks` protection, the `-mn` false positive, `$VAR commit -n`; Tools b4f5081), the gate BLOCKed the first cut on two HIGHs - `.git/./hooks`, `.git//hooks`, `.git./hooks` and `.git/info/../hooks` all resolve to the live hook dir and all passed both the Bash regex and the file-tool adjacency test, while the author's selftest comment claimed "any case, any separator" over a battery with no such row (the exact redundant-component class EV-022 closed for `.adversary`) - then BLOCKed the fix on a third HIGH: `\.?` tolerated one trailing dot where Windows trims any run, so `.git../hooks` still passed the Bash side while the file-tool side already denied it. Every finding reproduced by probe on the pre-fix bytes and fixed test-first (deny-on-doubt regex, canonicalised segments, drive-letter strip; guard_selftest 91 -> 128); the 8.3 short-name residual was declined with rationale and settled in round 3. A security control that would have shipped trivially evasible, twice, behind a green battery.
  - EV-029: gating the Caliper twin of that fix (tools/git-guard.mjs), the gate returned CLEAR having reviewed only the test file - `.mjs`/`.cjs`/`.mts`/`.cts` were not in the code-extension set, so an ES-module security guard was routed to the docs layer and would have landed with a clearance covering only its test; Caliper's two earlier git-guard commits were never notarized as code for the same reason. The reviewer said so in its own scope sentence; the author counted the files instead of trusting the verdict. Fixed test-first in both the gate and the vendored auditor (Tools c8262b8, gate_selftest 59 -> 61); the per-repo re-vendoring and the notes it will demand for old `.mjs` commits are the owner's sweep.
  - EV-030: with the `.mjs` finally in the payload, Caliper's reviewer found a one-line ordering bug in the EV-028 canonicaliser - the `..` test ran before the trailing dot/space strip, so a Windows-trimmed `.. ` parent segment later in the path was pushed as a literal name (and, in the harness_guard twin, silently dropped), and the quoted `.git\z\.. \hooks` also slipped the Bash token class; the harness guard had CLEARed its own round 3 with the identical order an hour earlier, and the docket review of the EV-028 row then named two more members of the class from the transcribed rule alone. All fixed test-first in both guards (strip first, then pop; a dot/space run admitted before a separator). The fix's own review then caught that a "starts with .." pop threw `.git` away on `.git/.../hooks` (final shape: every all-dot segment read both ways, either adjacency denies), and the review of THAT caught two more - the widened pop reading could delete the `.adversary`/`skill_gate` segment while membership checked only that reading (a forgery path flipped to allow), and the regex's overlapping alternatives backtracked exponentially on `./` x 40, which the author's first timing rows did not reproduce and the `./` construction did. Five rounds on one rule family: canonicalise before you compare, test every check against every reading, and a second reviewer reading a port catches what three rounds on the original did not.
  - EV-031: syncing the two-weeks-stale plugin copy of the gate into the marketplace put the WHOLE gate file in front of a reviewer, which found that the docs feed (the layer built after EV-024 to scan docs-only commits locally) lacked the `--no-color --no-ext-diff` its code-feed sibling carries - `color.diff=always` paints escapes so no line starts with `+` and the docs scan receives nothing and passes silently; an external diff driver crashes the gate. Reproduced RED in the gate selftest for both triggers, fixed with the two flags, plugin re-synced. EV-008's lesson again: a full-file re-read in a new context finds what diff-scoped reviews cannot.
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
