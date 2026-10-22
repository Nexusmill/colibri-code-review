# GATE_EVIDENCE_DOCKET.md - what the gate has caught (the running case)

> Owner order 2026-08-31: *"keep a manifest of everything the adversary catches and
> forces you to remediate as an evidence docket to further bolster the case for this
> gate and layered structure."* Machine-readable twin: `gate_evidence.json` (the row of
> record - this page is the readable summary). **Covenant: every catch that forces a
> remediation gets a row in the same working session as the catch. Rows are never
> deleted.** False rebuttals are the strongest evidence in the file: they prove the
> founding thesis - authors, AI agents included, defend invented claims about code
> they have not read.

## The scoreboard (as of 2026-09-16)

- **95 evidence rows**, one line each (the running summary from EV-020; the full rows, including
  EV-001 through EV-019, are in `gate_evidence.json`):
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
  - EV-032: arming the gate on a fresh repo (Blink) put the arming commit in front of a reviewer, which BLOCKed with three findings against the vendored auditor itself: HIGH - the tripwire's baseline anchor is attacker-writable repo content (a bypassing committer moves `.githooks/adversary_baseline` onto their dirty commit, the walk goes empty, false 'clean'; layer-4 CI reads the pushed baseline so it does not close the hole), proving the auditor's 'no local trick escapes' docstring overclaims the playbook's own detection-not-prevention contract; LOW x2 - malformed-but-valid-JSON notes and a non-UTF-8 filename both crash the audit at exit 1, colliding with the violations code (loud, never silent). Owner ruled rebuttal-only: the arming cleared via a factual `--context` (byte-identical vendoring contract; canonical fixes belong in Tools), with all items logged flagged-not-fixed for a Tools-side test-first pass, plus a reviewer-raised gate-side question (does `record` bind clearances to the commit tree across rebase/cherry-pick?).
  - EV-033: moving the netdiag toolkit byte-identical into Tools, the gate BLOCKed on the ARRIVING bytes: four of eight diagnostics never import `os` (dead on arrival since 2026-08-09, in the origin repo too) and the toolkit's own self-check hardcoded the old path - "byte-identical, no behaviour change" was true of the diff and no defence of the code; fixed test-first (static probe RED 4 -> GREEN 0, verify.py ALL CLEAN), CLEAR round 2; the docket gate then caught this row's own drafts twice (034227: an uncited CLEAR; 035628: that catch itself unrecorded), which pushed the probe into `Tools/netdiag/verify.py` for good (654588e).
  - EV-034: the paired 3DPrinting deletion commit BLOCKed round 1 on two scope false positives (the staged README pointer and the deleted `_reports/.gitignore` are non-code, so the reviewer never saw them) - the SECOND occurrence of the EV-027 class; rebutted with `git diff --cached --name-status`, CLEAR round 2 with the reviewer independently corroborating EV-033's missing-import defect in the deleted bytes. This row's own first draft then claimed a THIRD occurrence citing EV-023 (the credentials catch) - the docket gate BLOCKed that invented prior instance; corrected.
  - EV-035: the FIRST history rewrite of an armed repo (3DPrinting's owner-run purge) hit the push guard: main audited clean, but the guard's non-forced notes push was non-fast-forward against the remote's pre-rewrite notes, so the whole push was refused - correct - while its printed recovery (`notes merge -s cat_sort_uniq`) was WRONG for a rewrite (it re-imports notes naming commits that no longer exist); recovered live by force-pushing the rebuilt notes ref FIRST, hint fixed in Tools 491235d. The same CLEARed runbook showed FOUR live-only defects that day (dirty gitlink at preflight; a filter-repo stdin prompt hidden behind captured stdout for 2h47m; the gated-prefix baseline commit, cleared by an agent gate run before the owner reached it; this push order) - a fresh-clone rehearsal was the wrong test double for all four; runbook fixed in 3DPrinting 0bf78c9. This row's own first draft was then BLOCKed by the docket gate (124456) for claiming CLEARs it did not cite - the EV-033 class, repeated by the same author the same day.
  - EV-036: the two commits that landed the post-gate audit's 24 Phase-3-gated review records (jcodemunch-mcp e6d8eb0, deepagents-quickstarts 407cab3) each BLOCKed round 1 on the SAME scope false positive - "only the manifest is staged, every review record it indexes is missing" - while `git diff --cached --name-only` listed 39 and 11 staged paths; the reviewer receives code-class files only, so the .md records were invisible to it. THIRD occurrence of the EV-027 class (after EV-034), twice in seven minutes; rebutted with the verbatim staged list, CLEAR round 2 on identical bytes (220915, 220944). The class is now predictable enough that the author front-loads the staged path list into round 1's --context for any index-shaped commit; the EV-034 observation (feed the reviewer the staged NAME LIST of non-code paths) now has three data points.
  - EV-037: remediation item 3 in jcodemunch-mcp (index_folder branch-delta mode had never been reachable) BLOCKed twice on the author's fix being INCOMPLETE - round 1 found the warm-cache rebuild (`_patch_index_from_delta`) dropped the freshly persisted branch, so the fix held only until the first watcher event; round 2 audited the machinery the fix switched ON and found the deferred-summarizer thread and `_record_coverage` still writing branch state into the base, plus a branch-blind content dir (MEDIUM, confirmed, left open and documented). All accepted, none rebutted, three fixed RED-first, CLEAR round 3 (fe2afe5). Lesson: a fix that activates dormant code makes that code the review unit.
  - EV-038: remediation item 8 in repo-memory BLOCKed round 1 on the author's stale-row fix purging an UNCHANGED sibling's rows through a stem-keyed source (`README.md` and `docs/README.md` share `docs/README/section`); reproducing it RED showed the collision predated the fix (`replace_all` purges the whole shared source on any rebuild or delete of one file of the pair), so the repair became a stem-group rebuild; CLEAR round 2 (28846a2, local-only repo). Lesson: when a fix touches a keyed store, test the KEY's collisions - the feature fixture used distinct keys and could not see the purge.
  - EV-039: remediation item 9 in Tools BLOCKed round 1 because the author's new owner_setup selftest was VACUOUS - every Part B scenario used a missing GITEXE and died at the fix's own up-front guard, so the gh-missing / scope re-verify / per-repo-row paths it claimed to lock never ran, and one check matched the section header's word `workflow`; the reviewer also caught `http.client.HTTPException` still escaping the 'never traceback after billing' handler. All accepted; selftest rewritten to drive each path (12/12, every scenario traced by the round-2 reviewer), CLEAR round 2 (5a372a0). Lesson: when a fix adds an early return, prove every test scenario gets past it - a green count is not evidence the new code ran.
  - EV-040: the jcodemunch-mcp branch-scoped content tranche (0fe7c3a + 505d365) BLOCKed round 1 on BOTH commits - the second on two MEDIUMs in the author's own DESIGN, which the author, the advisor and the owner's ruling had all approved: the spec's "rmtree the branch dir before the walk" made a mid-walk failure STICKY (the delta rows are only replaced at the end of the walk, so the surviving rows pointed at deleted bodies and the next incremental run, seeing matching hashes, never rewrote them), and a subdirectory walk on a branch would have dropped the branch's delta rows outside the walked prefix; the wipe was deleted (the store's own `replace_all` dropped-bodies pass, required by the same reviewer in the store commit's round 1, already covered stale bodies) and the subdir case is refused explicitly - both RED-first; the store round also caught two real LOWs (stale bodies after `replace_all`, an unlocked rmtree racing the locked save) and raised one HIGH (legacy-delta migration) that the author refuted with a live probe (33 indexes, 0 branch_meta rows) and the reviewer accepted as proof. Lesson: failure ORDERING is its own review unit - write the crash-between-steps test before choosing the order.
  - EV-041: the OWNER caught a residual accepted on a false premise - 'per-clone arming is a git limitation' - while provisioning Codex checkouts; a machine-global hook path arms fresh init/clone/worktree with no per-clone action (probed), and worse, worktrees of ARMED repos on pre-vendoring branches were committing ungated (a dangling relative value: two live cases). The fix (Tools 1332bff + cde796d: dispatcher hook dir, absolute pin, rules epoch, census, guard covenant, Codex adapter) went through FIFTEEN blocked rounds - six on commit A, nine on commit B - every one a real defect of the author's, every one fixed RED-first with the reviewer's own trigger as the row: the tree that could not pass its own selftest, reclassified history, an absolute pin to a missing dir printing ARMED, partial dispatcher loss, unverified dispatcher content, unisolated fixture commits, tab/NBSP and quote-adjacent and quote-glued suffixes, agent-writable dispatchers, substitution and redirection riding inside the arming exemption, 8.3 aliases, literal-free global config writes, adapter shapes that fell open, a warn-only verify, a quadratic scan, quote-pair token splitting. Lesson: a text guard's allowlist is judged by what the SHELL hands git, not by what the regex sees - every spelling class the live-hook-dir rule had ever pinned applied to the new covenant, and the reviewer walked them one per round.
  - EV-042: the canonical shims (Tools/adversary-gate/pre-commit etc., the single source of every vendored shim) had NEVER been gated code - the classifier knew only .githooks/ and extensions - found from the gate's own status line in round 1 of the same tranche; HOOK_NAMES closed it and the per-repo rules epoch keeps the two historical un-reviewed shim commits from becoming permanent violations (verified: violations before the epoch, clean after).
  - EV-043: the machine-wide dispatcher self-check false-fired "dispatcher MODIFIED ... failing CLOSED" on a byte-clean dispatcher for EVERY partial commit (`git commit -- <paths>`) from an armed repo - a partial commit exports an absolute GIT_INDEX_FILE that re-targeted the self-check's `git -C "$SUITE"` onto the committing repo's index; found landing these gate docs under the stage-explicit-paths discipline. The fix (a clean-git-context helper; the in-band SELF exception REMOVED as strictly fail-closed) was itself BLOCKed by the gate TWICE - the reviewer caught that round 1 let an untracked dispatcher pass and round 2 let a staged edit ride a partial commit of other paths while the modified hook executed and was notarized clean - before CLEAR on round 3 (Tools 7ba0e3b). The author believed each of the first two fixes was complete and was wrong both times.
  - EV-044: migrating seven jcodemunch-mcp retrieval tools to the new `content_path` resolver deleted a local `content_dir` but left one bare-name read alive in get_symbol.py's `content_cache_missing` error message - a NameError on exactly the path meant to explain a missing body; 127 targeted tests were green because nothing exercises that path. Caught by the reviewer's per-variable trace in round 1; the author's own scan had matched the call spelling and missed the bare name. Round 2 BLOCKed again on a FALSE CLAIM: the author's context asserted every getsize/exists caller was guarded, but the same file's token-savings `getsize(file_full_path)` was not - the variable had become Optional and the old `except OSError` no longer covered it, so one missing body killed the whole batch response. Fixed round 3.
  - EV-045 (CLOSED the same day - see the row's tail): the machine-wide `core.hooksPath` arming gates EVERY `git commit` on the machine, including throwaway pytest fixture repos under %TEMP% - a probe showed a .txt commit running the docscan model (3.9 s) and a two-line .py commit running a PAID external review to CLEAR (18.9 s) inside a temp repo. jcodemunch-mcp alone has 327 git-fixture tests in 21 files; an acceptance run took 15 min with 11/12 failing in the fixture (false RED), and a full suite ran 35+ min spending a review per fixture commit before it was killed. No temp-dir or unarmed-repo exemption exists. The author's first proposal (dispatcher skips repos under the OS temp dir, "narrow, push-side still catches it") was REFUTED by the docket gate reviewing this very row: pre-push is the same dispatcher, so the skip exempts the push guard too, and every temp locator reads committer-controlled environment (`TMPDIR=<parent of a real repo>` reclassifies a real checkout) - the env-override class EV-041 just hardened against. Withdrawn; candidates with their holes stated are in the JSON row (A' env-free temp path, pre-commit only; H conftest-scoped empty GIT_CONFIG_GLOBAL as gated repo code; I accept the cost). Owner ruling pending.
  - EV-046 (CLOSED the same day - see the row's tail): the local secret pre-scan blocked jcm B2 part 2 on a pre-existing docstring in assemble_task_context.py:178 - a hyphenated Capitalised phrase after a parameter-name colon scores three classes and trips the 12-char password rule (the literal is not reproduced here; quoting it trips the floor in every doc). Lower-casing clears the blob, but the transmit payload includes the diff's REMOVED lines by design, so the old line trips it again: a floor false positive can never be remediated by edit through the gate. Options in the row (owner OVERRIDE for the commit; a floor refinement for hyphenated alpha-only phrases with a selftest pin; removed-line exclusion rejected). CLOSED the same day by the owner's third way: warn at commit, scrub the payload, refuse at push (Tools 8245433 + ad484fa). EV-045 likewise CLOSED the same day (Tools 1f287bb: fixture repos under the profile Temp skip the review, never the push guard; cause amended - the paid review per fixture commit needed the same morning's auto-review commit 9597241 as well).
  - EV-047: the gate reviewing its OWN scrub and push guard BLOCKed eight of ten rounds (six on the scrub, two on the push guard), every finding real except one reviewer sub-claim refuted by probe: six exfiltration paths in the scrub (second value on a line, private-key body, the 32-match cap, an unterminated BEGIN gutting the payload fail-open, key material on the header line, exotic separators hiding a value behind the 4096 gate), a silent no-scan at push under diff.noprefix, a header desync, replace-ref probes, tutorial-idiom false refusals, shallow/new-remote mis-scans, an OVERRIDE dead-end - plus three honesty catches (a message promising code not yet written; the suite's own fixture literals tripping the floor and voiding the no-self-trip row; a scrubbed fixture reading as a broken test). Two author claims were confidently wrong; one reviewer claim was refuted by probe. All landed with pinned rows; gate selftest 66 -> 89.
  - EV-048: the push guard's docs re-run refused three evaluation REPORTS on its first docs-heavy push - the local docs model read security INVENTORIES as secrets and, after a first calibration, quoted env-var NAMES as the 'value'; fixed by prompt (Tools 724d095: inventories, shapes and names are not values; 0 FN kept), with the honest note that the block was whole-chunk emergent and the selftest cannot carry it.
  - EV-049: B2 part 2 (retrieval follows the checkout) BLOCKed twice - the composed view was HALF-WIRED (17 internal content reads still served BASE bytes on a branch checkout), the default git-diff baseline became branch_head..HEAD = EMPTY (get_pr_risk_profile answered 0.0 silently), and result caches served feature-branch results after `git checkout main`; round 2 caught the cache fix's missing guard, a stashed transient failure and the new baseline helper's own error path. Round 4 then caught a reader hiding behind the _utils allowlist (resolve_fqn) and summarize_repo PERSISTING branch symbols into the base index (reproduced on the fixture). All eight confirmed; five rounds to CLEAR (jcm 78a76ed).
  - EV-050: landing the state branch on main, the push guard's docs re-run caught a REAL quoted value (the GCP project id + Hub handle in a report); after the commit was rewritten the model quoted NAMES as values on two more chunks; the fix - a deterministic evidence gate on the model's own REASON line - was itself BLOCKed by the gate for accepting all-caps values (an AWS key id) as names; fixed with fixtures (Tools f2fdfd4). Both PRs then landed by fast-forward (owner_ff_merge.py).
  - EV-051: carrying the DeepAgents runtime into the new fleet repo (A1 core, round 1) the reviewer found a Postgres password FALLBACK default in the carried settings - scrubbed to env-only at carry; the verbatim-carry contract clears secrets and tenant ids, nothing else.
  - EV-052: the fleet's A2 carry (round 1) held the real GCP project id as a code default - scrubbed to env-only; the same id in the carried AGENT_PROTOCOL.md was scrubbed by hand (the reviewer never sees .md), and the attic's INDEX now lists every remaining occurrence (59 files) for the owner's Phase 1 scrub.
  - EV-053: the attic's first chain (21 commits) was REFUSED by a probe push for five floor literals in history and rebuilt from birth; the second build was reset when the F5b review READ a live Postgres password in keyword arguments (the assignment heuristic never sees kwargs), a widened scan then FALSE-POSITIVED on the env-var name Q2_SSH_PASSWORD and the E1b re-review caught the author's wrong scrub; a digit-free DSN default forced a third build. Owner ruling 2026-09-08: no rotation (Moltbook service gone; Postgres local, no external face).
  - EV-054: the fleet's probe push was refused three times on PLACEHOLDERS the local docs model quoted as values - 'yourpassword', then the DSN role word 'pw', then the elided prefix 'lsv2_sk_...' (the two docs-only close-out commits shifted the chunk boundaries and re-opened refusals on unchanged text); fixed at the root in Tools 14d1f09 / fb0d9a6 / d9876ff, and the gate BLOCKed the author's first cut of the third fix as a fail-open ('makerbase...' would have been withdrawn). Probe after EVERY commit.
  - EV-055: the ARMED-AT-BIRTH change BLOCKed three rounds running, each on the author's previous fix - an unborn-HEAD crash, then a fix that let a BROKEN clone audit clean (any rev-list failure read as 'no commits yet'), then a corrupt ref file fooling the rev-parse discriminator - and both re-anchor commits BLOCKed until the epoch flip was proven by enumerating history rather than by an audit run under the old epoch (Tools 9e46976, four rounds; fleet 203e843 / attic 428eeb5).
  - EV-056: the arm_repo cp1252 fix pinned the child's stdio and left the PARENT decoding the same pipe with the console codepage (mojibake by construction, a crash under a stricter console) - and the selftest harness carried the identical bug, so the round-trip row failed on the harness first (Tools a0683c3, two rounds).
  - EV-057: the commit that added EV-055/056 and made the owner script derive its ids from the rows LEFT three strings still saying 'five rows' / EV-054 - including the gate context the owner's step-4 review would read - and round 2 named the `--skip-docket` fail-open that deletes the evidence file on a false premise (Nexusmill c30db949 + follow-up).
  - EV-058: the docket append ITSELF was BLOCKed for the docket's own class - rounds claimed without artifacts (EV-054 amendments, EV-055/056 'round 2 CLEAR') and a '-era' filename that exists nowhere: the author had typed review filenames from memory; every ref re-read from the review directories (colibri worktree gate_20260909-073612, r1).
  - EV-059: the docket append was BLOCKed AGAIN, this time on the author context: it claimed the scoreboard .md edit while the reviewer's payload (code-class files only) held just the JSON - the .md was staged, the context never said it was outside the payload; the script now builds its context from git diff --cached --numstat and names what the reviewer cannot see (colibri worktree gate_20260909-075333, r1).
  - EV-060: the OWNER found that Tools 8245433 (09-07) removed _scan_text_secrets while the Codex reviewed-write broker still called it - the gate had CLEARed it because the caller was not staged (a reviewer cannot see an unstaged caller); every reviewed write since had crashed; fixed with the wrapper restored AND a deterministic in-gate refusal of any symbol removal with a live caller in the frozen index, whose own round 1 BLOCKed on a cwd-scoped listing that would have left the guard inert from a subdirectory (Tools de3f953, two rounds; this row's own append round 1 caught its selftest arithmetic).
  - EV-061: the push guard REFUSED a four-commit Nexusmill docs branch on a doc published two days earlier: a NEW ref excluded only the baseline and re-fed 124 published commits to the docs model, whose REASON glued an elided `AIza` prefix to the next word so the classifier held it; fixed in FIVE rounds, each on the author's own cut - unvalidated tips, a sha list on argv, then the exclusion narrowing the security barrier itself (restructured to the docs feed only), then a context claiming 113/113 against a log saying 111/112 (Tools 6d24c55).
  - EV-062: the archive-mirror commit of three scanned repos' review records was BLOCKed on three caliper rows whose recorded sha was the post-fix bytes while the review file hashed the pre-fix bytes, with no note (every other such row had one); the author's first bytes check read the archive schema one level too shallow and reported zero mismatches; fixed at the source (Caliper 874b2ea) and re-mirrored, colibri 0ea3f50
  - EV-065: the sweep's own fix for a stuck paid-button guard registered its release timer non-persistent - Blender purges it on the very file load that triggers the defect; caught in round 1, persistent=True + a battery assertion, the battery had been green on a fix that did not work for its headline path
  - EV-066: the full re-audit batch's own busy-guard fix dropped the old `finally`, so a Ctrl+C mid-bake re-opened the stuck-busy class on a narrower path, and two of its nineteen new batteries were bound to the author's machine (PowerShell, a ROCm venv) with no SKIP; caught in round 1 on a 73-file tranche whose 26 fixes all held
  - EV-067: the style-reference relocation took THREE gate rounds: round 1 caught the missed picker enumerator, the orphaned default-path installs and eight double-amended registry rows; round 2 caught the author's own adoption fix (it required the new folder to be absent, which the app's own mkdir makes false) plus a stale count and a machine-dependent probe check; all six real, none rebutted
  - EV-068: a website copy scrub (owner order: no visible dollar figures) replaced '$0.30 per 100 textures' with 'a small fraction of a cent' - false by 30x against the per-texture rate the same change was deleting - and left the in-app guide contradicting the privacy page on where the API key lives, though the guide was in the same staged set; both caught in round 1, both accepted
  - EV-069: a review-manifest row carried a 12-char sha because the persist script trusted a truncated digest in the sub-agent's audit summary and only checked the prefix; caught in round 1 against the 27 full-length sibling rows; the full digest was reconstructed from the HEAD blob with the file's CRLF newlines and verified against the prefix, and the writers now assert the length
  - EV-070: the docket commit carrying EV-068/069 was itself BLOCKed - as first staged both rows claimed a round-2 CLEAR while citing only their round-1 files (the EV-058 class, re-introduced beside EV-058's lesson); corrected before landing, so 10772dd carries the fixed rows and the catch survives only in the round-1 artifact - which is why this row exists; its own first draft was BLOCKed for narrating the pre-correction bytes as committed
  - EV-071: a char-to-byte offset sweep in jcodemunch-mcp's AL extractor retyped the function's line table to character units and converted Passes 1-13, leaving Pass 14 (~800 lines below the last hunk, unseen by the reviewer) storing the raw character index as byte_offset - the very defect class the commit claimed to close; the reviewer reasoned it from the retyped shared state, the author had counted hunks; fixed at the root with a RED-first test, round 2 CLEAR (gate_20260913-141605.md), landed 857a4d5
  - EV-072: the redact tranche in jcodemunch-mcp taught redact_dict to walk tuples while the depth-cap guard three branches above still enumerated (str, dict, list) - a tuple past depth 20 was returned raw with its strings unscanned, against the cap's own 'never return raw data past the cap' invariant (F10); accepted, one-token fix, and the first regression test written for it passed on the broken bytes (tuple nested in lists) before being corrected to reach the named branch; settled in round 2 (gate_20260913-143014.md), tranche CLEAR in round 3 (gate_20260913-144119.md), landed fd1069c
  - EV-073: the same tranche's whole-block private-key rule (`.*?` to the END banner) had been cleared by the author's own refuted-list as 'linear, no nested repetition' - the gate pointed out linear per ATTEMPT is not linear per sub(): every unterminated BEGIN banner walked to end of text (5.4 s for 224 KB of banners, minutes for 1 MB, per tool call) and a banner quoted in prose swallowed 200 legitimate lines up to the next real key; accepted on measurement, fixed with a tempered span that stops at the next `-----` (1 MB in 0.09 s, large real keys still redacted whole; a size cap was rejected because exceeding it would leak the key), the refuted-list amended in place; round 3 CLEAR (gate_20260913-144119.md), landed fd1069c
  - EV-074: the assemble_task_context tranche in jcodemunch-mcp closed 'a stage listed in stages_run with no entry and no flag' for the dispatch loop, and the same diff touched the cross-repo layer that runs after the loop without holding it to the new contract - with cross_repo=True and the budget spent it was listed unflagged, breaking the invariant the staged battery encoded but never drove through that branch; accepted, fixed, RED-first test at the invariant assertion; round 2 CLEAR (gate_20260913-145957.md), landed c5a6f7e
  - EV-075: the credentials tranche's new test battery left credentials._resolution_source populated (the keyring-diagnostics global, written outside monkeypatch's reach) with no isolation fixture - green only by collection order; on reading the sibling test file that DOES isolate it, the author found it guards a second copy of the module (`src.jcodemunch_mcp` import), so nothing had ever isolated the real one; accepted, fixture added on the right module; round 2 CLEAR (gate_20260913-165331.md), landed 1aefece
  - EV-076: the get_file_tree tranche in jcodemunch-mcp normalised the path prefix for the filter and left _build_tree slicing by the raw prefix - 'src//' cut one character too many off every relative path and silently merged colliding files where the old bytes returned an empty tree; the author's pins missed the very shape the normalisation exists for; accepted, the helper normalises too, RED-first collision test; round 2 CLEAR (gate_20260913-173408.md), landed ad9f01c
  - EV-077: the import-scip tranche in jcodemunch-mcp moved _bounded_gunzip to security.py and kept the old name bound (an import alias, then a module-level assignment) - the removed-symbol pre-check REFUSED both rounds before any review because it compares definitions and saw unstaged callers; a false refusal recorded as data about the layer, resolved by staging the caller re-pointed; round 4 CLEAR (gate_20260913-201642.md), landed d9f2521
  - EV-078: the same tranche's context claimed the review ledger gained two rows while the staged manifest carried four - two belonged to an uncommitted later tranche the driver re-staged by accident; the reviewer counted the staged blob; manifest rebuilt from HEAD; round 4 CLEAR (gate_20260913-201642.md), landed d9f2521
  - EV-079: the same tranche's corrupt-gzip test sliced a few-hundred-byte blob at byte 2000, never truncating it, and passed through the wrong ValueError; the fixture now halves the blob and asserts the wrapper's message; round 4 CLEAR (gate_20260913-201642.md), landed d9f2521
  - EV-080: the EV-077..079 docket commit itself cited Tools 8245433 as the commit that closed the unstaged-caller hole - per EV-060 it is the incident and de3f953 the fix; the reviewer reconciled the new row against EV-060 in the same file; corrected in place; round 2 CLEAR (gate_20260913-210200.md), landed 7b86439
  - EV-081: the refresh slice lock (tail batch 5) heartbeated only between batches, so one long batch went silent past budget + grace and a second run broke a LIVE lock; and release unlinked without an owner check, deleting the next run's lock (ABA) - a token, an in-batch heartbeat thread, owner-only touch/release and a lock-lost refusal that never writes the cursor; three tests RED on the round-1 bytes; round 2 CLEAR (gate_20260913-234116.md), landed 17e5a44
  - EV-082: get_changed_symbols' sibling pair-off (tail batch 5) keyed on (name, kind, body) and hid a byte-identical A.f -> B.f move, and caught only boundary renumbering so deleting the first of three read as 1 removed + 2 spurious modified - the author's 'exactly one removal' claim tested at N=2 only; group alignment on the ordinal-stripped id; four tests RED on the round-1 bytes; round 2 CLEAR (gate_20260913-234116.md), landed 17e5a44
  - EV-083: pushing the marketplace 0.3.0 re-vendor, the push guard's docs lane (the local docscan model) refused the branch because the README named the default reviewer by its OpenRouter model id and the 4B model quoted that id as 'the secret value' (3/3 on-machine, captured); _evidence_is_name holds any slash/digit/dot token as a value, so a FALSE POSITIVE stood. Owner ruling: reword (models named in prose, ids left to DEFAULT_MODEL) + docket; the reworded text was pre-tested with docscan before re-gating; the two unpushed commits were rebuilt, re-gated CLEAR (gate_20260914-171625 / -173319) and re-notarized. OWED in Tools: teach the heuristic that a provider-slash-model slug names no value (TDD, gated), then re-vendor docscan.py.
  - EV-084: the first EV-083 row claimed the rebuilt commits' CLEARs while citing the superseded branch's review artifacts, and its run claims (3/3 repro, bisect, pre-test, refusal) had no captures - the docket's own gate reconciled verdicts against refs (EV-058/EV-070 class) and BLOCKed; refs re-derived per sha, every claim pointed at its capture. Lesson: placeholder-sha rows must have their refs re-derived when filled.
  - EV-085: the Tools docs-release commit (install_gate.py's printed NEXT steps rewritten to the auto-review contract) BLOCKed round 1: the file's own module docstring still taught 'attempt the commit (EXPECT refusal)' - REAL, fixed in the tranche (a selftest checks flags, not prose); and the deleted 'ALSO push the notes' step was called the file's 'own prior testimony' that the shim does not push refs/notes/adversary - FALSE by scope (the mechanism lives in pre-push + cmd_check_push, outside the staged set), rebutted with the lines and the same-day live notes ref; round 2 CLEAR. The reviewer-scope class again (EV-027/034/036/059 and the marketplace 0.3.0 round 1 under EV-083): cite the out-of-set mechanism in the FIRST --context.
  - EV-086: the OWNER's fast-forward of this PR (14 commits to main) was refused by the push guard's docs lane - chunk 3 of the 14-commit feed (the 4fbab93 docs release) drew 'needs `OPENROUTER_API_KEY`' 3/3, and the verb 'needs' was not in the vocabulary, so the name-only withdrawal never fired; the same lines had passed when pushed to the branch in smaller pieces (chunk boundaries elsewhere), and a known remote tip re-feeds even published, already-scanned commits. Root cause fixed in Tools 51ba4b3 (TDD 13/14 -> 14/14; the EV-083 slug rule landed in the same tranche, bounded to known providers and model-id shapes); the exact refused feed re-run 3/3 clear; the owner re-runs the same command. Follow-up: extend the tracking-ref exclusion to the known-remote path.
  - EV-087: the gate CRASHED on its own transport while gating fleet unit 2 - the primary model's chunked body broke mid-stream, `r.read()` raised `http.client.IncompleteRead`, and both transport handlers caught `OSError` only (IncompleteRead is an HTTPException), so the exception escaped the chain handler: raw traceback, no failover, no verdict. The retry cleared through the KNOWN empty-response path, which proved nothing about the unknown family. Fixed in Tools 26280c7 (TDD: two new CHECKS, 4/6 -> 6/6; gate CLEAR r1): both handlers catch `(OSError, http.client.HTTPException)` - the OpenRouter side advances the chain, the xAI backup fails closed cleanly. Third transport family found live (EV-018 empty, EV-021 non-JSON 200, now a truncated 200). Tools main is local-only on this fix; the hooks run the working tree, so it is live.
  - EV-088: the gate's deterministic removed-symbol guard REFUSED the fleet's whole-package deletion (atlas/, 73 files) - sixteen 'callers' were modules' own `def main`, a `from fleet.cli import main`, and one dead import of an uninstalled package; names were matched unqualified and the documented escape cannot apply to a module's own definition. The fix took SIX review rounds in Tools: five successive drafts each kept one fail-open branch ('source not found -> external -> vouch') and the reviewer caught TWO false verification claims by the agent (r1: RED/GREEN numbers the chain never produced - its commit had died in the armed fixture; r4: '119/119' while check 47 measured RED). Landed as Tools ca686ed: a bystander's own def/class shadows, `from X import name` shadows only on index-proven, unique, root-file evidence, a plain import never shadows, everything unprovable refuses (checks 43-51, 121/123 -> 123/123 measured). The deletion then cleared on its first run (fleet 8767694); the dead import was deleted with the package, not excused.
  - EV-089: the docs lane refused the fleet repository's first push (19 commits, 35 chunks) on chunk 11, 3/3, REASON `"k"` - the implementation plan's embedded test code sets the provider key to a one-letter fake, and _evidence_is_name held a single character as a value. Fixed in Tools c33a704 (TDD 13/14 -> 14/14): a one-character alphanumeric literal names no value; two characters and up hold. The identical push then passed with the withdrawal line printed. Third precision gap in that function in two days (EV-083, EV-086).
  - EV-090: re-vendoring the six-round-reviewed guard fix (ca686ed) byte-for-byte into the marketplace plugin put the SAME bytes in front of a second repository's gate, which found three holes in three rounds: a def the vouch target later re-binds still vouched (an under-report; Tools 7935480), `def keep` + `from lib import *` vouched with nobody named (a genuine fail-open; Tools 8b4e40c), and a `global keep` inside a class body re-bound at import unseen (Tools b0de7ab). Tools' own gate took two more rounds on the fix (`case {**rest}`, default-argument walruses; class bases/keywords, return annotations, the `ast.Match*` floor). Check 54 pins twenty-three module-scope binding shapes; gate_selftest 126. Marketplace 0.3.3 cleared on the fourth round as 6621ab2 (PR #5; main is protected there now). The mechanism is the lesson: a second armed repo reviewing identical code is a second independent reviewer for one gate call.
  - EV-091: the round-table build's Task 1 was committed with '1 failed' in its own suite line - the gate read the new isolation test against the staged bytes and named the failure (TableConfig's default_factory shared the SAME Seat instances across tables; fleet gate_20260916-001703); fixed as fresh Seats per table (ad002e5), and the build chain was rewritten that hour to stage only on an all-pass line - every later commit of the build went through it.
  - EV-092: eight BLOCK rounds on Tasks 0-9 of the round-table build (doctor, protocol, voices, knowledge, genesis): a dead-table lottery that told an excused seat to speak, two non-terminating genesis loops, a queue-jump the author's own test had canonised, an interrupted knowledge write left permanently 'done', the ScrapingDog api key re-raised inside httpx error text (secret hygiene), CRT '100' graded as '10', a duplicate persona name silently clobbering another seat's Hub prompt - all real, all fixed test-first (fleet e820041, 388f70c, a4bfc16, 058c7f9, 16b8661).
  - EV-093: seven BLOCK rounds on Tasks 10-13 (skeptic, avatars, render): a 'docs.' host PREFIX that made any attacker domain a tier-1 source, follow_redirects past the provider allowlist, a REFUND after a paid image generation that the author's own test asserted, a blocklist that admitted plurals and hyphen compounds, a frame test that compared different tiles so a disabled pulse still passed, and an ffmpeg pipe that masked its exit code - all real, all fixed test-first (fleet e8e058b, 651b487, c878861).
  - EV-094: the session runner (Task 14) took nine rounds: a pass re-entered the unconditional speaker fork and DOUBLED credibility deltas; the contest guessed its ruling by position; a shared usage drain billed tokens to the wrong seat; a silent (TTS-failed) turn had its unspoken claims REVIEWED and remembered; a pass handed the floor straight back to the last speaker. GLM returned no content on three rounds and the gate's fallback reviewer (xai:grok-4.6) found three of the defects; two author rebuttals with bytes were verified and accepted. Commit eed13a4; the CLI that wires the per-model usage handler is d8d8ea0.
  - EV-095: the CLI round (Task 15) - genesis build would have sent a SILENT placeholder turn ('[<seat> silent: SpeechError]') to the image model as the avatar prompt (two billed generations, the 'no prompt spoken' guidance never firing in the case it was written for), and the battery demanded the search key and built the TTS pipeline it never uses; round 2 claimed render_video's `store` keyword hallucinated - FALSE on render.py 240-249 (committed in c878861), rebutted with the lines, while its coverage half was real and got the missing re-render test. Commit d8d8ea0.
  - EV-096: the round-table follow-ups after the owner's first live meeting took one BLOCK round each: record.json attributed a seat's FAILED intro/speak to the next seat's turn (a pass appends no turn) and recorded three failure paths as 'ok' (9ecfd39); the deepseek fallback order contradicted the owner's own reliability-first rule in the same comment (2566b83); the generation-record lookup let one malformed 200 void a session's provider attribution, ran unbounded between notes.txt and state.json, and lost its failure note (18093fb). All real, all fixed test-first, second rounds CLEAR.
  - EV-097: the ADVISOR layer caught the reviewer benchmark behind the gate's own chain recommendation counting MENTIONS as catches - the doc said 'read against the text', the script had a regex; re-read, GLM's '4/4 in 5/5' was 3/3 of the unambiguous plants, V4.1 Flash's '4/4 in 3/5' was 2/3, and the fourth plant was weak. The recommendation survived; the table, the state entry and the memory were corrected (fleet 6cf24ee) and the honest scorer shipped with the probes (Tools 3165db8).
  - EV-098: the Tools gate, reviewing the probes' move into Tools with their evidence JSONs, proved from the evidence that probe_endpoints read a `stats` field no endpoint carries - the step-1 table had printed 0 in its throughput and latency columns on every run (real, fixed test-first). Round 2 then claimed, as HIGH, that the usage handler's field is a list in every langchain-core release, so the pins probe would crash after paying for its calls - FALSE: the installed 1.6.3 declares a dict at usage.py line 40, the fleet CLI reads it the same way, and the committed rows carry the token counts; rebutted with the line via --context and pinned by a selftest check against the installed handler. Round 3 CLEAR; selftest 17/17 (Tools 3165db8).
  - EV-099: pre-testing the FULL Tools main-push docs feed (EV-086 discipline) drew a BLOCK 3/3 on a reviewer response quoting a fixture's `timeout_s: float = 30.0` - REASON `30.0`, which _evidence_is_name held as a value; the same chunk cleared alone. A decimal float is a quantity, never a credential: rule bounded to digits.digits (six each side, optional sign), integers/PINs and glued forms still hold; 13/14 -> 14/14, the identical feed 3/3 clear, the push went through (Tools c003d06). Fourth precision gap in that function in three days (EV-083, EV-086, EV-089).
  - EV-100: the AUDITOR caught a rebase of PR #21 gluing two notarization notes into one - the installer set notes.rewriteRef but never notes.rewriteMode, so git's default CONCATENATE copied the original note onto a replayed commit the post-commit notary had just notarized afresh ('note is not valid JSON'). Fixed test-first in Tools dcbacaa (the installer pins `ignore` - its own gate round showed overwrite would destroy a fresh notarization of rewritten content - verifies it, the census counts its absence as stale; install 77/77 with a rebase-replay proof; all 23 checkouts re-armed); the branch was rebased again from its original commits under the pinned mode and audited clean - no note hand-edited.
  - EV-101: the gate's round one on the fleet names tranche (the first live genesis build's crash fix) caught two real LOWs in an otherwise-passed diff - a genesis introduction whose name was refused was accounted 'ok' and so attributed to whoever spoke next (the reconstruction record wrong, money and state untouched), and the new `rt genesis rename` recovery command died with a raw traceback and unbilled calls on the very provider outage it exists for. Both fixed in the hour (outcome 'refused' stays unattributed; billing in a finally; every exception reported with exit 2), tested, round two CLEAR; landed as fleet 76dc7e8.
  - EV-102: the gate's round one on the fleet thrones tranche caught the one paid generation the renderer opened unguarded - the new backdrop image was written and billed without a decode check while every render opened it with none, so one bad provider payload would brick the table's video until a hand-delete; the author had hit the same failure that hour through a test fake and closed only that door. Fixed: decode before write (written off, nothing written), guarded open (warn, token ground); thrones reports counts and never claims a replacement that did not happen. Round two CLEAR, landed as fleet 62140a3.
  - EV-103: the push guard's docs lane refused a one-PNG brand commit as 'secret material in outgoing documentation' - `--text` (pinned so a -diff attribute cannot blind the scan) forces a diff of a binary, only NUL-carrying lines were dropped, and 28,881 NUL-free deflate lines went to the docs model; chunk-boundary roulette had let a sibling PNG through minutes earlier. Fixed test-first in Tools e51909c (the push audit applies the staged scanner's 8 KB NUL rule per path; selftest 130/130); the push then went through.
  - EV-104: two round-one catches on the fleet scale-and-clipping tranches, both retry paths that would have rebuilt the same failure - a throne choice recorded before its brief was screened would have cached a refusal for every retry (6eb2b83), and a candidate that recorded its prompt but not its canvas sent the operator to a regen that would have redrawn the throne square, reproducing the cut-off and replacing the good tall batch (ede2f7e). Both fixed in the hour with tests; round two CLEAR on each.
  - EV-105: the owner's local avatar review page - the gate caught that its API parsed any POST as JSON with no Host or content-type check, so any other open tab could fire a cross-origin text/plain POST at 127.0.0.1 and run a paid generation or rewrite the review state (MEDIUM), plus two traceback exits on the owner's likeliest mistakes (a busy port, a port out of range); then a reload that would have re-billed the old prompt, a rebound read past the POST-only Host check, and a Regenerate on the wrong canvas. Fixed with tests across five rounds; the busy-port test itself exposed HTTPServer's address reuse sharing the port on Windows. Landed as fleet 20c7137.
  - EV-106: the parallel knowledge backfill - the gate caught that a pool exit would have swallowed the owner's Ctrl+C for a whole seat (~2 h of paid searches behind a frozen terminal, MEDIUM); the fix's own GREEN run then showed that on Windows a main thread blocked in Future.result() sees no SIGINT until the wait returns, so the main thread polls. Real-signal test. Landed as fleet 7aa1053.
  - EV-107: the Store's first vacuum (a Lance table of 21,782 versions and 17 GB behind 14,781 rows) - the gate caught that its periodic prune was ungated while LanceDB's default read consistency leaves every other process on the version it opened: the review page or the Agent Server would have failed after ten idle minutes, a paid run would have aborted on the row-count guard, and the first optimize on the bloated store would have frozen a live run for ten minutes (HIGH). Fixed with strong read consistency (a two-connection test), a strict guard on the offline command only, and a bloated-store refusal in `rt backfill`. Landed as fleet d8fb038.
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
  - EV-108: the PatternSkin test-surface tranche - the gate caught that the runner rebuilt to never exit 0 on failure still exited 0 on a signal-killed child (max() over a negative code), that the harness tester's stale-results clear sat after the add-on import it was meant to guard, that a scipy-less 'skip' still failed, and that five manifest rows cited 23 checks for a 22-check battery; all four fixed before round two (Nexusmill 23f9598c, rebuilt on main from 7c490e8f).
  - EV-109: the harness run-artifacts tranche - the gate caught that the new mtime freshness gate could be defeated by the runner's own run_download.py merge (a stale results file re-stamped fresh on the very no-Blender profile the fix targeted) and a locked-file crash in the runner; two of its four rounds were a lane-filter false positive (the reviewer never sees .gitignore/.txt/.stl hunks), rebutted with the staged name-status list both times - an OPEN Tools observation (Nexusmill 0435eaef, PR #24).
  - EV-110: a stash pop left four conflict blocks inside the Caliper review-manifest mirror and the agent staged it blind; the gate caught an unparseable ledger, resolved to the live store's bytes (sha256-identical) with the known source-side token mismatches recorded, not edited (colibri abe8045, PR #22).
  - EV-111: the Blink song-archive tranche - the gate caught that a best-effort archive guarded only its copy step (plan.json/index.html write failures would abort enrichment after the songs were paid for), that corrupt hand-edited plan.json rows crashed the page build, and that a same-name re-run silently overwrote a previously archived paid mp3; all fixed with tests before the CLEAR (Blink 67240b6).
  - EV-112: the Blink online-songs tranche - the gate caught that http.client.IncompleteRead (an HTTPException) escaped the publish path's (EnrichError, OSError, ValueError) funnel, bypassing the retry and failing the whole enrichment after the paid songs existed, leaving uploads orphaned from a stale manifest; the caught class joined the tuple with a regression test before the CLEAR (Blink acf8d3d). [EV-111 lands via the feat/agent-error-rates branch - the repo switched to main mid-session 2026-09-21.]
  - EV-113: the KokoroBookReader adoption tranche - the gate caught the data-migration call sitting outside app.py's try (its authored failure message unreachable as a dialog), suspend_for_analysis raising analysis_busy before a confirmed kill (permanent narration wedge on a kill timeout), and style_scan wedging forever on one corrupt cache file; all three fixed before the CLEAR, and a fourth finding claiming setup.ps1 was unrunnable for missing staged files was factually rebutted via --context (the reviewer payload scrubs to code files; requirements.lock and launch.cmd were staged all along) and upheld on re-verification (Nexusmill 1a713344).
  - EV-114: the scan_queue first-LIVE-drain tranche - the autoland plan's queued verification step finally ran and caught the batch transport dead twice over (a raw dict as POST data crashing http.client's chunked encoder, and an OpenAI file-upload shape OpenRouter rejects in favor of an inline requests array), with the live API's own validation errors dictating the real contract; the round-1 review also hallucinated a dispositive SyntaxError that fell to byte evidence (staged==disk, py_compile clean on both, module had executed live) - the strongest false-finding class the docket tracks (Tools 3567c91; the M2 unit then submitted first-try on z-ai/glm-5.3:batch).
  - EV-115: the scan_queue manifest trilogy - three gate rounds on one defect class: the writer shipping a wrapper-array + string-mode shape into the canonical colibri flat manifest (caught in the Nexusmill gate), then a fix that never healed the damaged data, then a self-heal loop that shadowed its own parameter and re-injected the broken shape while dropping the caller's paid row - the author's own new selftest check failing 11/12 predicted round 3's catch; final shape flat/canonical/self-healing (Tools 2fb3128).
  - EV-116: gating the KokoroBookReader voice-path self-heal (Nexusmill 6e886b7a), round 1 BLOCKed on the loop's own safety claim - unguarded Path(recorded).is_file() in the constructor meant a corrupt voices value (TypeError) or a non-ENOENT OSError (deny-ACL / quarantined file / disconnected volume, which Path.is_file propagates) aborted the ENTIRE library load, while the remediation row claimed 'an OSError never aborts startup' around save() only; fixed test-first with an isinstance(str) guard + per-entry except (OSError, ValueError), the PermissionError case proven via a Path subclass, suite 151/151.
  - EV-117: the PR-25 replay rounds - the gate caught worktree double-counting in the error-rate ledger (directory-name identity vs shared notary refs), the EV-116 row's missing refs, a 4-row dangling blink mirror, the archive-name fallback double-count, unguarded git probes, and the silent loss of v2's dangling-manifest surfacing; plus a stale-number rebuttal from the author - all fixed across three rounds (colibri 127f155+).
  - EV-118: strengthening a false-coverage test (itself batch-scan remediation), the edit deleted the identical-content rerun that was the only proof of cache reuse - leaving a trivial cold-call count annotated as cache reuse, while the remediation row claimed reuse was asserted; the gate BLOCKed the fix for reintroducing the exact defect class it was fixing. One line restored (identical rerun before the changed run); suite 156/156, CLEAR round 2 (Nexusmill 4533b887).
  - EV-119: the displaced-ids style-scan fix (owner's stuck-at-168) - the gate caught the new recovery recursion sitting OUTSIDE the ValueError fallback (a failing displaced re-ask aborted the whole section, discarding collected answers, where the old code half-split and recovered) and burning the shared _depth<3 split budget; fixed with except ValueError -> retry_split and budget-free same-depth recursion whose termination is structural. Round 2 then caught the amended manifest row keeping both the pre-gate 168/168 and post-gate 169/169 claims in one verification field; rewritten as one sequence, round 3 CLEAR (Nexusmill 614ce62d; reviews gate_20260922-232504/-234844/-235936).
  - EV-120: the autoland T1.2 wiring rounds - eleven gate rounds caught dead-on-arrival claim argv on the production path, un-sandboxed tests writing the owner's live front, a self-lockout occupied verdict for compacted sessions, payload-budget and surrogate-split hazards, and interpreter drift; one round's findings were all false and rebutted with live evidence, its follow-up real (Nexusmill 115e5ac1).

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


## 2026-09-09 ROOT history audit catches (EV-063 / EV-064)

- **EV-063 (HIGH):** Deleting the current branch ref made a ROOT-baseline repository with remaining commits read clean. Tools 3c1243aff8de now requires successful object enumeration with no commits; four regressions caught the old behavior,47/47 passed after repair. Independent prewrite and automatic Git CLEAR; notarized blobs verified.
- **EV-064 (MEDIUM):** Blink gate_20260909-212210 caught the ROOT epoch shortcut skipping the shallow-history probe. A real shallow clone with valid notes returned clean. The shortcut now follows the probe; three failing-first regressions pass and the full suite is50/50. Tools/Blink copies match, Blink is ARMED. Automatic Git CLEAR and committed: Tools 70835b6448da (gate_20260909-224351), Blink a9f9fe6ee214 (gate_20260909-224734).

## 2026-09-23 mimosa L3 false BLOCK (EV-124)

- **EV-124 (false BLOCK, EV-109 class):** The mimosa ZCode plugin's git-gate (PreToolUse on Bash, project-wide scan of the session repo on any `git commit`) pinned EVERY commit from ZCode sessions in this repo on 12 HIGH findings. All 12 adjudicated refuted or verified-stale on current bytes under the colibri-review skill's Phase 3: `store.py:116` is the path sanitizer itself (`_safe_name` flattens both separators to `__` before any join), `store.py:72/165` write fixed filenames under the operator-chosen base, `agent_error_rates.py:569/658` cite lines past the 555-line EOF (the scan snapshotted a mid-edit file), `analyzer.py:93` and `app.py:21` are the designed OpenRouter catalogue lookups (operator-configured / hardcoded-literal URL - no steerable input), `static_context.py:148` writes `os.path.basename(rel)` into a fresh `mkdtemp`, and the four test hits are mkdtemp + literal-name fixtures. Zero CONFIRMED, zero PLAUSIBLE; no code changed. The plugin ships no acknowledgment path (sealed hook, no allowlist in its contracts), so the release is an owner ruling on its scope - recorded here so the adjudication does not have to be re-derived while it stands. Owner-requested deep scan 2026-09-24 (seal sha256:cd19ef4e): 11 findings = the same seven + the two past-EOF staleness repeats + three `legacy/` flattening-pattern hits, all refuted identically - and a fifth commit denial immediately after the scan proves the git-gate does not read the deep-scan artifacts (its finding set still carried the four test-file hits the scan never made): the plugin's fix-and-rescan remedy loop cannot release itself. Denials 6-7 (2026-09-24): the owner's mid-session Settings disable changed nothing - hooks register at session start, so a disable can only apply to a NEXT session. Denial 8 (2026-09-24, fresh session after the owner's mandated restart) exposed the root cause: the Settings disable never persisted - `~/.zcode/cli/config.json` still read `mimosa@zcode-plugins-official: true`, so the restart dutifully re-loaded the plugin and its gate and fired byte-identically again. Enacting the owner's standing disable + landing order, the agent flipped the persisted flag to false (user settings, not repo code); one more restart yields a gate-free session for the landing.


## 2026-09-25 perfection-R2 plan-gate catch (EV-127)

- **EV-127 (plan-gate BLOCK, real catch):** gate_20260925-193002 on the Nexusmill perfection-R2 wave (PatternSkin/ai_parts.py paid-cache mirror fallback) refuted the Fix-Contract's mirror-byte-identity invariant - the mirror refresh is best-effort (the 2026-09-10 ALWAYS-REFRESHED fix exists because mirrors go stale), so a valid-but-refused lineage primary can coexist with a resumable signature mirror. Amended per the verdict: every candidate judged independently (refusals continue) across the five readers; verdict-named test RED->GREEN (overrun done=99 primary -> mirror done=1 quoted; wrong-count primary -> mirror hit). Re-gate CLEAR gate_20260925-194717 - mimo-v2.6-pro@xiaomi delivered the verdict after a deepseek incomplete response, the pinned-chain fallthrough working as designed. The wave's staged blobs were swept into the parallel session's docs-titled commit daad6682 by the shared-checkout index race (fbb02cd1 class); HEAD bytes verified identical to the gated working tree.

## 2026-09-26 KBR duplicate-guard input-space catch (EV-134)

- **EV-134 (gate-review BLOCK, real catch):** gate_20260926-023019 (mimo-v2.6-pro, after a deepseek 402) on the KBR Kindle duplicate-import guard flagged that (title, author) equality alone merges distinct books - read_epub defaults missing OPF title to path.stem and missing creator to '' - so a second metadata-less/same-stem import would silently return a foreign id before the source copy; and the new per-row json.loads(payload) was unguarded, letting one corrupt row block all imports. Both confirmed at the bytes and fixed: identity now requires non-empty title AND author plus identical sentence-text sequences (revised editions import separately; the re-conversion test reworked to two same-text/different-timestamp EPUBs with asserted-different ids) and per-row try/except skips corrupt rows. RED->GREEN both boundary tests; suite 195/195.

## 2026-09-26 governance-JSON encoding catch (EV-135)

- **EV-135 (gate-review BLOCK, split verdict):** gate_20260926-023803 on the EV-134 docket commit. CONFIRMED and fixed: the docket JSON was rewritten with a BOM it never had plus LF/no-trailing-newline on a CRLF file (per-file governance-JSON conventions, the round-55 lesson). REFUTED with byte evidence: the same verdict's HIGH claim that reviews_archive/nexusmill/_manifest.json was corrupted/invalid JSON - json.loads succeeds, schema intact; the whole-file diff was background-daemon re-serialization, restored and left unstaged. Landed as b6d0b7b (after a stale-_commit_msg.txt amend - the printf for the correct message died inside a gate-denied Bash chain, the pre-execution-deny pattern).
## 2026-09-26 perfection wave-4 retry guard-class catch (EV-136)

- **EV-136 (gate-review BLOCK, real catch + rebutted edges):** gate_20260926-092200 (deepseek-v4-pro-0813, 20 findings) on the bounded-transient-retry commit in the perfection(analyzer.py) run. CONFIRMED and remediated same session: _transient assumed APIStatusError.status_code always exists (an attribute-less instance would raise AttributeError inside the retry's except-handler, defeating the retry); _call_retry with retry_max_attempts<=0 returned None via an empty range (cryptic AttributeError at resp.choices[0]); retry_backoff_base unguarded against negative (ValueError in sleep) and huge (hours-long hang) values; no direct _transient unit tests. Fixes: getattr + None-guard predicate, max_attempts clamped >=1 at both call sites, base clamped >=0 with per-sleep cap 60s, direct unit tests including the attribute-less subclass. REBUTTED with reasons via run --context: string status_code (#4, SDK types it int), backoff jitter (#10, deliberate determinism - the net pins the sleep shape), excluding 501/505 from the 5xx class (#19/#20, blanket-5xx is standard and the attempt budget bounds cost). Escape-rate: 20 findings / 6 accepted / all in prior-round (wave-4-touched) code / catch stage: commit-gate - the plan gates (3 grok rounds) had cleared the design but never the zero/negative config partition.
## 2026-09-26 perfection wave-8 finish-signal dispute catch (EV-137)

- **EV-137 (gate-review BLOCK, additive resolution):** gate_20260926-102147 (deepseek-v4-pro) on the cold-pass remediation commit. The wave-8 fix that updated usage[finish] to the corrective retry's finish_reason unconditionally discarded the first attempt's truncation signal - and the wave-8 test pinned that loss (finding 3, correctly). A genuine semantic dispute with the COLD-pass finding that motivated the change (stale finish misread complete reviews as truncated). RESOLVED ADDITIVELY same session: finish tracks the response whose content shipped; the first attempt's finish is preserved as usage[first_finish] when a retry ships; test asserts both. The gate's F2 (plan-prior wording nuance) was judged cosmetic/not-blocking by the gate itself. Also this round: the commit message's shell quoting mangled a code span (backticks inside double quotes executed) - message-only defect, the gate had already reviewed the staged bytes; re-commit uses single-quoted messages.

## 2026-09-27 remediation and alignment supplement

[EV-138 through EV-145](gate_evidence_20260927.json) record the upheld semantic-refusal rebuttal, corrected queue-estimate regression, pre-write adjudication for remediation commit 73313cf, and the staged-blob memory regression caught during Tools-to-marketplace synchronization. The machine-readable supplement preserves the original docket while keeping each new reviewed document within the broker size limit.

The alignment supplement also records fail-closed evidence persistence, bounded large-document review, array-shaped references, routing-fixture isolation, and factual rebuttals.

All entries through EV-151 are now included in [the canonical machine-readable docket](gate_evidence.json). The bounded broker repair permits the full central document to be reviewed again. EV-146 records forced text diffs for oversized source marked binary; EV-147 records production parser regression coverage. The earlier supplement is retained as a historical snapshot.

EV-148 records preservation of corrupt append-only evidence across all three metadata writers. EV-149 records numeric same-second artifact selection in the test helper. Both were reproduced before repair and their targeted regressions passed afterward; details and individual artifact references are in the canonical JSON docket.

EV-150 records the age-only lock stealing catch: existing locks are no longer removed based on age. Two new regressions and the full 203-case gate suite pass; operator verification and cleanup are required for abandoned locks.

EV-151 records reversible explicit caller encoding after a multiword name corrupted per-file attribution. The integrated production header/adjudication regression reproduces the old failure and passes after repair.


EV-152 (Blink, 2026-09-27) records the nine-round BLOCK of the first birdcam/cards.py commit - a paid 920-image title-card generator whose initial version carried 14 distinct latent failure-path defects (16 raw findings; two round-2 reports were stale re-reports of already-fixed code) (paid-range misflags, non-atomic writes accepting partial cards/fonts, force-regeneration destroying archived cards, billed-retry undercounting, overlapping-run manifest clobber, timestamp-lock races, lockless index overwrites, date.max overflow, malformed-manifest crash). Every finding was reproduced RED-first (test file grew 14 to 33 cases; full suite 217 OK) before commit c2ae400 earned CLEAR. Structural remedies: atomic temp+validate+replace chokepoints, an OS-level msvcrt/fcntl lock, merge-on-write manifest saves, and honest billed-versus-archived cost reporting.


EV-153 (Blink, 2026-09-27) records the static title-card-video wiring catch: the pre-commit proving run showed an UNCAPPED video-concat encode running to 7215s because Blink containers carry lying stream timestamps (80s stream inside a 1191s container) - the stills path's -t cap is load-bearing; and the gate's P2 showed container-duration audio padding outrunning a card's visual track. Fixed with the -t cap restored, a stream-vs-container honesty check on card MP4s, and a painted fallback; six new tests (suite 223 OK) plus a real-file 1199.2s 1080p30 assembly verified before commit c1eb108 earned CLEAR.

EV-154 (fleet, 2026-09-27) records the 41-round BLOCK arc of the round-table config page commit: stored XSS via insertAdjacentHTML, a backfill --yes that pre-authorized spend before the owner read the CLI estimate, store_optimize violating the EV-107 offline vacuum contract, resume clearing the halt under a live job or crashed-page orphan, shutdown leaving paid children, the review page's paid generation unserialized with pipeline jobs, Windows LockFile side-handle blindness (twice), and a string of orphan-detection holes. The lock schemes the author proposed first (Store write-then-reread, O_EXCL file, replace+grace) each admitted two winners and were rejected before the OS byte-lock design landed. All fixed with verdict-named tests (suite 412 to 466) before commit a9c4f2c earned CLEAR; one rebuttal accepted - the owner-self-spoof residual is the honesty clause's own class.

EV-155 (fleet, 2026-09-27) records the 22-round arc behind the owner's live Draft-topics failure: EV-154's "proven" parent delegation could never work in a real child because os.getppid() on Windows is not the spawner's pid (the in-process test rig shared one pid and masked it), and separately seats.slugify() validates 2-24 chars so a real 68-character search title killed the topics draw with BadTable. Withdrawn in favor of child-claims-itself (page holds the slot only for the spawn instant; children retry-claim), a full orphan/leftover lifecycle with the owner's Resume as the all-clear, an unvalidated slugify_name plus stem+index topic ids, and the page-UX fixes (dismissible log, every finish spoken with its exit code). Verified live on the owner's own field: 4 topics drafted, exit 0, visible in the topics box (suite 466 to 470; commits 6fb629c7 + b17db828).
## 2026-09-28 laser generator input-space saga (EV-163..EV-167)

- **EV-163 (validate-before-build):** gate_20260928-223907 (gpt-6-luna-pro) on the first staging of the new laser/generate_baroque_cover.py - no commit existed at BLOCK time; the fully remediated wave landed later as Nexusmill b79dfd38. build() ran before validate(), so --holes 1 divided by zero in hole_ys() and --holes 0 indexed an empty list - the advertised n_holes>=4 check was bypassed with a traceback. RED proven on both inputs; validate_config() now runs before build(), validate_bounds() stays post-build. The G38 skill gate also forced systematic-debugging before the fix edit - the process layered correctly.
- **EV-164 (input-space guard family, 3x P2 in one review):** gate_20260928-224357. (a) --spine 60 --hole-d 40 passed the spine-gap check while 20mm-radius holes overshoot the insets; (b) --cover-height 20 put hole rows outside the cover; (c) --hole-d nan defeats '<=' comparisons (NaN compares False) and wrote nan path coordinates. All three reproduced RED; guards: hole_d within 2*(min_inset-2), 2*hole_end_margin+hole_d within cover_h, and 'not (v>0) or not isfinite(v)' per dimension key.
- **EV-165 (engrave-piece containment):** gate_20260928-224817. --cover-height 100 passed every check because validate_bounds() only proved drawings stay on the 300mm SHEET; the fixed-size cartouche engraved ~6mm past the cover edge. Fixed structurally, not with a size constant: each piece draws into its own Canvas with engrave-only bounds; validate_pieces() proves engraving stays inside its piece rectangle at ANY parameter combination.
- **EV-166 (hole pitch vs hole diameter):** gate_20260928-225553. --holes 100 passed count/margin/containment checks - no check related pitch (~1.9mm) to hole diameter (4mm); adjacent holes merge into slots. Guard: pitch >= hole_d + 2mm. The first guard version itself divided by zero at --holes 1 and was caught by the agent's own regression battery before the next commit - the guard needed a guard; that near-miss is the strongest row of the batch.
- **EV-167 (inner-first cut order in the file):** gate_20260928-225921 (BLOCK) -> gate_20260928-230255 (CLEAR, sha 7330d7fb). Every red cut path emitted the outer rectangle BEFORE its lace holes; Bambu Studio's Inner Shape First defaults on, but the FILE ordered outer-first, so any subpath-order-honoring tool releases the piece before its holes are cut. cover() and spine() now emit all hole ellipses first, rectangle last - verified on the emitted SVGs (cover cut path = 7 M-subpaths, holes first, 3-L rect last). Notarized on Nexusmill b79dfd38.

All five rounds: same file, one landing commit (Nexusmill b79dfd38), every finding reproduced RED before its fix and every fix regression-batteried (10 adversarial inputs exit 2, default + variants exit 0). The saga is a clean demonstration of the input-space guard-class: four of five catches were parameter combinations no single check covered.

## 2026-09-30 .lac packager tranche (EV-175)

**EV-175 (Nexusmill, 2026-09-30)** records the 21-round arc behind the
Bambu .lac packager commit d1f74dd6 (media/laser/chest.lac - the owner-
ordered deliverable): a broken path anchor from the junk->laser source
move; the fa.generate (url, metrics) contract violated twice (heightmap
branch, then the --look branch the round after); rotated-part rasters
axis-aligned (transposed art on assembled faces) and bbox rasters
burning wood the cut removes (now masked even-odd to the part outline);
the input-space family (px_per_mm 0/neg/inf/overflow -> band [1,32],
NaN map coordinates -> load-time refusal); the truth-in-the-map family
(duplicate rows, truncated maps, swapped art assignments - all now
refused against the generator's mirrored part->art mapping); and the
doc-drift family (the plan sheet's corner detail redrawn twice - the
crossed-slot fiction, then parallel strips - before the true
perpendicular L; budget arithmetic 3-vs-4 sheets). Round 20 is the
transport-artifact lesson: the payload masker rewrites dotted-quad
version strings as IP literals, so the FileVersion rebuttal could never
stick across dispatches - resolved by building the value at runtime from
parts, bytes identical. The commit-time large-file guard also forced the
7.7 MB .lac out of laser/output/ into media/ without touching
--no-verify. Same session, systematic-debugging (read-only-file probe)
caught a pre-existing battery bug outside the gate's sight:
test_two_drawer_config_builds ran the generator CLI without --outdir,
so every full-suite run silently overwrote the committed 3-drawer
map/SVGs with a 2-drawer layout - the .lac work surfaced it as
mysterious map drift. Suite 77 -> 95, all verdict-named.

## 2026-09-30 Local-rung replay harness landing (EV-176, EV-177)

**EV-176 (Tools, 2026-09-30)** — three BLOCK rounds on `replay_local.py` (landing
`5a9a30d`) alleged: `_call_model` does not exist (with a proposed fix that would have
404'd on double prefix-handling), an `invert_guard` regex that "corrupts diffs", and a
dict-entry API cited to lines that do not exist in the file. All three disproven with
byte-level evidence (5-case execution transcript for the regex; live round-trip for the
call path); root cause: the reviewer audits calls into UNSTAGED `adversary_gate.py` and
invents its API. Kernels adopted: four new battery rows (run_round end-to-end behind a
fake transport; invert_guard coverage) and the upstream contract now documented in the
staged docstring. Mitigation for reviewers: when the call target is unstaged, treat
`--context` verbatim quotes as ground truth; never fabricate the hidden signature.

**EV-177 (Tools, 2026-09-30)** — the strongest row of the saga: round 4 caught a REAL
defect in the AUTHOR'S REBUTTAL EVIDENCE. The round-4 context quoted `_call_model` as a
bare 4-tuple passthrough while the code 3-unpacks it; the live file reads
`return _call_model_ex(model, user_content, timeout, attempts=attempts)[:3]` — the slice
was dropped because the quote came from the jCodemunch index cache, not the file. The
code was right; the "verbatim" quote was not. Lesson banked (G36-adjacent): byte-exact
quotes used as review evidence are re-read from the live file at dispatch time. An index
cache is not a source of record.

## 2026-09-30 Replay cap-fix saga (EV-178)

**EV-178 (Tools, 2026-09-30)** — kimi-k2.7-code went 3-for-3 on REAL measurement-integrity
defects in `replay_local.py` (landing `6fe0161`): byte-identical no-op "buggy" rounds
deflating the catch rate; never-sent pseudo-rows polluting rounds/malformed-rate/median;
and the author's first fix counting the skip bucket after filtering it (caught by the
author's own battery before review). All adopted with pinning rows. Fleet signal: kimi
clean single-verdict formats throughout, while coder-next rolls on the same payloads
produced one degenerate repetition loop and two duplicate-verdict markers — live evidence
for kimi as the rebuttal tier.

## 2026-09-30 Chain-reorder saga (EV-178)

**EV-178 (Tools, 2026-09-30)** — two BLOCK rounds on the reliability-tilted chain
reorder (`019b890`). r1 alleged the bare-ladder/pinned-chain split was newly introduced
(disproven: documented design, prior ladder equally bare, parity row strips pins by
intent). r2 was a new failure class: a SELF-REFUTING BLOCK — the artifact's body
concluded "The finding is wrong. The change is correct." and still emitted
`VERDICT: BLOCK`. Kernel adopted: ladder comments now say "endpoint pins live in
DEFAULT_CHAIN" instead of "(reliability-pinned)" on bare entries. Lesson: when the body
agrees with the rebuttal but the verdict line contradicts it, address any surviving
kernel and re-run with an addendum — never argue the verdict line.

## 2026-10-03 Prospective text activation (EV-187)

**EV-187 (Tools)** — the xAI backup gate caught a real retroactive `.txt`
classification error: commit `3165db811249` legitimately lacked two text
evidence keys under the old rule. The owner selected an anchored prospective
boundary. Commit `625d4c586456` adds a separate immutable text marker,
preserves existing baselines and notes, and keeps all staged text reviewed.
The final Tools audit walks 142 commits with no violations or overrides.
All three destination migrations passed their own exact-byte xAI gates.
Missing, malformed, moved and shallow markers apply the rule everywhere;
nine disposable Git regressions cover the boundary. Installation and fresh
source isolation passed; the running native Codex binding needs quit/reopen.
## 2026-10-10 Experiment-10 transfer landing (EV-195)

The semantic-delta payload + BLOCK-finding adjudication tranche (owner order
2026-10-10, local-gate experiment #10) drew one BLOCK on its first round:
hy4-preview flagged that finding_adjudicator.py was missing from
runtime_loader.CATALOG, so the certified enforcement runtime would not
ship it and the gate's deferred import would fail silently in production
while every working-tree test stayed green. Remediated in-session with
the CATALOG entry plus an AST-based catalog guard test. The finding is
itself the transfer's thesis: verbatim anchor, concrete trigger, producing
caller, broken behavior - the anchor quad the layer now enforces.
## 2026-10-10 Experiment-10 transfer deployment (EV-196)

A second BLOCK caught a real deadlock: the CATALOG addition makes the
immutable active installer emit old-catalog manifests the new loader
rejects. The bootstrap activation escaped it - and then exposed a deeper
collision (write_generation validates a new-catalog manifest against a
generation directory the failed attempt wrote under the old catalog).
Unblocked by removing the poisoned derived generation dir; runtime now
pins 2f90fae (20 files). Epoch-handling for write_generation is the open
follow-up.
## 2026-10-10 EV-196 resolved (0ac7e77)

write_generation now self-heals stale-era generation directories for the
same commit under a digest proof (generation bytes are a deterministic
function of commit+catalog); foreign bytes and the ACTIVE commit's
directory are hard refusals. The landing validated the normal activation
path end-to-end - post-commit auto-activation installed 0ac7e770 with no
manual bootstrap. Row amended in place with refs.
## 2026-10-10 T1 notary guard catch (EV-197)

The merge-predecessor BLOCK: the window guard hashed head^ while the HMAC
chain binds to the most recent mac-carrying ANCESTOR (second parent for
merges). Factored the shared selection walk; dated-merge regression test;
WARN-round LOWs (SystemExit leak, weak assert) fixed in the same session.
## 2026-10-11 T3 config-hooks saga (EV-198)

Eight BLOCK rounds on the config-hooks arming module - stacking orders,
rollback restore bugs, foreign-launcher substring matches, shell write
forms (flag, key-value, key=value), boundary evasion - plus the pilot
round's repo-wide notarization and push breakage from guessed args.
All fixed with the exact shim invocations after empirical argv/stdin
probes; landed ef40e25 THROUGH the new config hooks as the pilot.
## 2026-10-11 Plugin 0.3.7 refresh catches (EV-199)

Two BLOCK rounds on the adversary-gate marketplace refresh: flattened
shim layout broke the installer and self-check; a bare timeout=60 in
the vendored _run_git (fixed at Tools source); and transplanting the
certified-runtime modules whose paths assume the source suite. Plugin
rebuilt to its own architecture; landed b7db336.
## 2026-10-11 Certified-runtime layout port (EV-200)

The runtime trio is now layout-derived (GATE_DIR, discovered generation
segment, existence-derived catalog) - the SAME BYTES run at the author
suite and ship in plugin 0.3.8. Two BLOCK rounds caught the three
paths the port missed and a runbook that would have dead-ended a plugin
operator; one finding was rebutted by the author's own render test.


## 2026-10-11 OpenRouter observability pipeline, round 1 (EV-201)

**BLOCK, 1 MEDIUM** (gate_20261011-153637): `control.py` spawned the poller with
Windows-only Popen `creationflags` unconditionally — a `TypeError` on POSIX after
`docker compose up`, poller never starts — and `cmd_stop` could only force-kill via
Windows `taskkill`. The whole control plane had been live-verified on Windows only.
Fixed, not rebutted: `_popen_creationflags`/`terminate_pid` platform splits + 4
branch-forcing tests. Notable: the remediation itself re-committed the same class once
(`signal.SIGKILL` at call time, absent on Windows) and the author's own RED-first
platform-forcing test caught it before re-review — the T1 invariant-test pattern paying
for itself inside one cycle.


## 2026-10-12 Observability backfill, round 3 (EV-202)

**BLOCK, 1 MEDIUM + 2 LOW** (gate_20261011-215739): `day_windows` treated
`--end` as an exclusive midnight — single-day backfills enumerated nothing and
every run silently skipped the end day's generations (the author's live test
only passed because it ran after UTC midnight). Plus an IndexError on a bare
`sk-or-v1-` prefix and the new command missing from the usage text. Fixed with
inclusive-end/exclusive-boundary windows + 6 new tests (suite 30); landed in
Tools 89d6633. Lesson: boundary semantics escape authors who test only the
happy middle — the reviewer reads the arithmetic, not the live-run luck.

## EV-203 - 2026-10-12 - Tools 3544504 - the new tier-2 ladder reviews its own replacement

**Rounds:** gate_20261012-122708 (BLOCK, 4 findings) -> 130726 (WARN/3) -> 131547 (WARN/2) -> 132223 (WARN/1) -> 132752 (CLEAR).

**Catch:** deepseek-v4.1-flash effort high (the newly pinned tier-2) reviewed the ladder swap that installed it. Headline: `BatchReviewPending` SUBCLASSES `SystemExit`, so the new audit-fallback's inner `except SystemExit` swallowed the pending-resume signal and would have paid a second batch alongside the live one (HIGH, fixed by clause order + delist-gated fallback). Plus: fleet `GATE_LADDER` left mirroring retired hy4/kimi (MEDIUM, parity restored); audit rows misattributing the serving model (LOW); pre-write path losing the tier-2 effort/budget via the compat API (LOW); non-hermetic test (LOW); money-safety comment corrected to the adjudicated sunk-receipt semantics (LOW); batch scan_queue not forwarding the documented effort + stale docstring (LOW); `or "high"` resurrecting the documented empty-disable (LOW); pending-test not arming the fallback (LOW); manual `--model` overrides inheriting forced effort/budget against the verbatim-override doctrine (LOW).

**Lesson:** when a fallback wraps an exception that SUBCLASSES the pending signal, clause order is the money-safety invariant - and a moved call seam (compat -> new API) must sweep every consumer in the same diff: fleet mirror, pre-write caller, batch transport, tests.

## EV-204 - 2026-10-12 - DEFERRED: two unadjudicated evaluation findings (owner order: docket for later consideration)

**(1) Epoch rollback** (`_current_rules_epoch` reads the working tree; `.githooks/` stays editable; gate reviews staged-only): unstaged epoch writeback defeats stale-clearance expiry. Premises verified in live code; flagged independently by flash-high and unanimously by the fusion council. Originally hy4-CLEAR (suspected false negative). **(2) Chain-mac re-anchoring** (audit-time GENESIS walk vs write-time prior; note-authored exemption fields): later-arriving notarized ancestors can flag valid notes as tampered. PLAUSIBLE (multi-clone path not executed). Also originally hy4-CLEAR.

Both deferred for a later adjudication round; refs in the machine-readable row.


## EV-205 - 2026-10-13 - Tools 517f28c - the daily-docket ship gate, 19 rounds (13 carrying findings)

**Rounds:** 021017..052126 (18 BLOCK/WARN + WARN-land). The deepest review battle in the gate's history - over a push-gate refinement, not new surface area.

**Catches (headline):** every escape hatch in the author's own first drafts: unresolvable BLOCK rows (no fix-forward path, ever); REJECTED-as-resolved (a 4xx submission storm silently disarming the barrier); notarization-exemption dead branch (every outgoing commit is notarized by construction); stale-ROW poisoning of all future commits touching the same files; partial-staging subset escape from tree-equality keying; spanning-rounds bypass of single-entry matching; a HIGH union matcher that permanently refused ALL tier-2/gate-suite pushes; POSIX killpg on an inherited group killing the stop command itself.

**Meta-lesson (the docket's strongest row yet):** three of the author's own remediations were broken by the NEXT round - each fix addressed the reported trigger and opened a different hole (self-resolution -> dead branch; REJECTED-resolves -> laundering; single-entry union -> spanning bypass). Consecutive adversarial rounds on the SAME diff are the only thing that caught them; single-round review would have shipped all three.

**Resolution:** Tools 517f28c - time-scoped file-coverage matching throughout; 2 LOWs landed recorded (mixed-tier commit gap, per-checkout audit state).
## EV-206 - 2026-10-13 - Tools 4cedc53/158d6b8 - prompt-layer consumer matrix

- **Catch (LOW):** round gate_20261013-114935 found a dead, divergent duplicate of the
  _builtin_instructions/_resolve_instructions pair in hy4_review.py - the 2b insert
  anchored at def review() landed a second pair after _feed while the tranche-2 pair
  (without the expectation-audit branch) stayed above it. Runtime was correct (Python
  rebinds to the later pair; 10/10 tests green) but a future edit at the first grep hit
  would have been silently inert on the fail-open path (F811-class).
- **Author initially:** shipped the WARN inside the landing commit, duplicate unnoticed
  and invisible to the passing tests.
- **Resolution:** same-session remediation 158d6b8 deleted the earlier EA-less pair;
  batteries green, py_compile clean; the follow-up round took VERDICT: CLEAR with no
  findings (artifact gate_20261013-115326.md).
- **Refs:** Tools 4cedc53, 158d6b8; .adversary/reviews/gate_20261013-114935.md (WARN
  round); Tools .adversary/reviews/gate_20261013-115326.md (CLEAR round).
## EV-210 - 2026-10-14 - Blink afbf650 - planner budget raised, deadline forgotten

- **Catch (LOW):** round gate_20261014-135109.md reviewed the PLANNER_MAX_TOKENS
  16000->65536 fix for the multi-song starvation outage and caught what the author's
  own live proof recorded but the author never reasoned about: the successful 8-song
  probe took 123s while call_openrouter still rode the shared HTTP_TIMEOUT_SECONDS=90.
  The reviewer tied the finding to the diff's own remediation row ("the new budget is
  the first configuration that can sit past it"), traced the TimeoutError path to both
  LLM_ATTEMPTS failing -> plain-video posting (the exact outage the fix claims closed),
  priced the paid-for-and-discarded completion risk, and named the one-call verification.
- **Author initially:** treated the 123s probe as proof, not noticing it exceeded the
  90s constant it ran under - it survived on per-socket-op semantics (server delivery
  luck), not on a deadline the code guaranteed.
- **Resolution:** same-session PLANNER_HTTP_TIMEOUT_SECONDS=300 via a default-preserving
  _http_json(timeout=...) param; default/override threading pinned by tests; round 3
  CLEAR (gate_20261014-135957.md). Blink afbf650.
- **Refs:** Blink afbf650; Blink .adversary/reviews/gate_20261014-135109.md;
  birdcam/enricher.py PLANNER_HTTP_TIMEOUT_SECONDS.

## EV-211 - 2026-10-14 - Blink afbf650 - the offline-contract test that did live DNS

- **Catch (LOW):** round gate_20261014-135713.md caught a defect IN the round-2
  remediation itself: the new test_http_json_timeout_default_and_override patched only
  _open_url, so _guard_url ran a live socket.getaddrinfo('replicate.com') - the suite
  would error on any offline box, contradicting the test file's own module contract
  ("Offline unit tests ... no network, no ffmpeg"). The reviewer verified the positive
  too (assertion shapes match the real call) before clearing the fix itself.
- **Author initially:** wrote the no-network test with a network dependency - the exact
  class the file's existing guard tests had already solved by pinning getaddrinfo.
- **Resolution:** same-session fix pinned enricher.socket.getaddrinfo like its siblings;
  battery 256 OK; round 3 CLEAR (gate_20261014-135957.md). Blink afbf650.
- **Refs:** Blink afbf650; Blink .adversary/reviews/gate_20261014-135713.md;
  tests/test_enricher.py test_http_json_timeout_default_and_override.
## 2026-10-16 colibri-bounty P0 landing rounds (EV-223)

- **EV-223 (gate-review BLOCK x4 + WARN, tier-1 deepseek-v4.1-flash with one qwen3.8-omni-flash failover):** 
  five dispatch rounds on the Nexusmill colibri-bounty P0 sync-layer landing (6adaa1c6). 
  Ten findings across six review rounds, none disputed, every code remediation RED-first (offline suite 19 -> 27): r1 - a failed sherlock 
  issues fetch persisted has_issues_dump=0 WITH the repo's pushed_at, so the skip guard blocked every retry 
  forever while status/CLI reported success (+2 LOW: null warden/tag joins; wrong-premise default-root test); 
  r2 - --max-pages bounded against the cumulative checkpoint counter (bounded runs on advanced checkpoints 
  fetched ZERO pages, exited 0); r3 - `if limit:` conflated 0 with None (--limit 0 from a budget counter 
  triggered the MOST expensive full sync) and negatives tail-sliced; r4 - the pushed_at skip guard applied 
  uniformly, but sherlock findings publish as ISSUES with NO git push: pre-publication syncs kept empty dumps 
  forever, silently; r5 WARN 3 LOW - --max-pages 0/-1 silent zero-page ok, wrong-shape-but-valid-JSON 
  config.json crashed every CLI path, skip guard ignored tarball existence; r6 WARN - a comment-wording LOW on the F1 raise's rationale (comment-only, not re-raised on the final CLEAR). The r4 fix triggered a live 
  corpus heal (460/460 issue dumps re-fetched, tarballs skipped, zero errors). Final dispatch one-round CLEAR. 
  Full row with refs: gate_evidence.json EV-223-P0-LANDING-ROUNDS.

## 2026-10-17 3DPrinting arming: pre-gate biome stdin false-block (EV-224)

- **EV-224 (pre-commit local pre-gate, deterministic layer; biome 2.5.15):** the pre-gate refused the
  3DPrinting zcode-arming commit with `biome-parse tools/zcode_stop_gate.mjs` on a file with NO parse error
  - a byte-identical vendored copy of the gate-cleared Nexusmill twin (e5995de1). Reproduced live with a
  captured transcript: biome 2.5.15 `check` exits 1 "The contents aren't fixed" on canonical minimal input
  (P1: `const x = 1;`) and on the format-canonical + shebang-stripped twin (P3; P4: the not-fixed exit is not
  even stdin-specific) - the disable flags do not prevent it - so the pre-gate fires on any non-zero exit whose
  output matches /pars/i, and the match lands on `JSON.parse` inside the source biome echoes (P2). Any staged
  .js/.mjs containing "pars" false-blocks; content-preserving fixes do not clear it. EV-124 "deterministic
  layers never false-block" class: tool-version drift re-evaluating under broken exit semantics. Remediation:
  local .mjs left uncommitted (junk/), Stop hook wired to the committed Nexusmill twin by absolute path; the
  arming commit landed CLEAR (3DPrinting b425415, artifact cited in refs); real regex/invocation fix is
  owner-ordered work on adversary_gate.py `_pregate_check_one`. Full row with artifact refs:
  gate_evidence.json EV-224-PREGATE-BIOME-STDIN-PARS-FALSEBLOCK.

## EV-225 - the EV-224 fix session: three WARN-round catches and the runtime refusing to install WARN-cleared engines (2026-10-17)

Owner option (a): a SEPARATE session fixed the biome pre-gate (the session whose
commit was blocked did not edit the gate). The remediation itself was policed:
round 1 WARNed that the temp-cwd probe dropped repo biome.json authority; round 2
WARNed that _repo_root()/_run_git fails via SystemExit (degrade path would hard-
abort) and that the check logic changed twice under one _PREGATE_LOGIC_VERSION;
and post-commit activation REFUSED to certify either WARN round as installed
enforcement - the machine kept executing the old engine until round 3 landed
CLEAR (d18b0af). validate_generation also caught a -B-less snapshot import
dropping __pycache__ into the generation package (cleaned same session). The
blocked universal-tools 1.2.0 tranche then landed UNCHANGED through the fixed
engine (bea1a55, tier-2 CLEAR). Full row with artifact refs:
gate_evidence.json EV-225-PREGATE-BIOME-FIX-3-ROUND-ACTIVATION-GATEKEEPING.


## 2026-10-17 Tools zcode arming twin: nine BLOCK rounds on agent-authored guard code (EV-226)

- **EV-226 (gate-review BLOCK, nine rounds, Tools 65eb0c7):** the repo-by-repo zcode twin
  port (owner order: "the port is to be completed by you for you, its repo by repo") put
  five hook scripts + a health helper + a project .zcode/config.json through the gate, and
  the external reviewer caught nine real defect classes the author's own 21-test suite sat
  green over: the G42 fail-arm denying its own recovery command; the suite able to burn the
  owner's one-shot escape; a stale-index re-commit reviewed against pre-fix bytes; payload
  caps summing past the 10000-char budget so the snapshot was silently dropped (the
  blank-slate condition the hook exists to prevent); subprocess latency unbounded inside
  the 45s hook window; the mid-FAIL apparatus lock covering only 3 of 6 mounts and omitting
  the git metadata dir (one silent Write could defang the stop gate or the commit gate);
  fail-triggers with no in-band remediation; locale-codepage stdout silently losing G44
  ingestion for non-ANSI summaries while tests passed on the shared failure prefix; and a
  mkdir remediation arm first admitting traversal, then rejecting split-residue whitespace.
  Every fix landed test-first (23 decision-level cases); one rebuttal - the shared one-shot
  escape as the mjs gate family's cross-gate contract - was filed and ACCEPTED by the
  reviewer (round 8 explicitly did not re-raise it). The pattern this row evidences: the
  gate's value on the agent's OWN enforcement code, where self-review is weakest. Full row
  with artifact refs: gate_evidence.json EV-226-ZCODE-TWIN-9-ROUND-PORT.


## EV-229 - the tier-2 catch on the colibri-code-review twin port (2026-10-18)

The first repo-by-repo port of the arming twin INTO colibri-code-review (from the Tools
twin) was BLOCKed by its own tier-2 review with two real defects the port had carried
in verbatim from its sources: the G6 guard's one-shot OVERRIDE escape failed OPEN on a
directory or undeletable OVERRIDE (Test-Path is true for directories; Remove-Item
without -Force silently no-ops; the guard then allowed without burning - the exact M2
class the co-shipped stop gate had already fixed in mjs), and the G43 one-shot unlock
flag was bound by a 15-bit path hash whose stored content was never read back, so a
colliding path could ride another target's unlock. Both were fixed red-first with
verdict-named tests (27/27); the same unfixed OVERRIDE shape remains exposed in the
Nexusmill and Tools G6 guards until those repos take the fix. The pattern this row
evidences: porting reviewed code re-imports its review debt - every port needs its own
gate round. Full row with artifact refs: gate_evidence.json EV-229-TWIN-PORT-TIER2-CATCHES.


## EV-230 - the later rounds on the twin port: read-side codec, test hygiene, serialization (2026-10-18)

Rounds 2-3 of the colibri twin port's own gate kept earning their keep: the G44 ingest
reader rode the locale codec instead of the UTF-8 the memory server emits (latent on
this UTF-8-locale host, live on any cp1252 machine - the read side of the silent-loss
class the file's own comment claimed fixed), the burn-positive override test could
strand a REAL machine-global one-shot escape with no cleanup (an interleaving this
session's own parallel gate rounds demonstrated live), the same test was order-dependent
on a missing parent dir (the Tools round's WARN), and the docket JSON itself was
reserialized at the wrong indent - the EV-158 class, a one-row addition dressed as a
7,400-line diff. All fixed with a stub-server contract test; suite 28/28; the sibling
Nexusmill and Tools guards took the EV-229 fix the same session. Full row with artifact
refs: gate_evidence.json EV-230-INGEST-READ-CODEC.
## EV-231 - the jcodemunch-mcp arming port gauntlet: nine rounds, two MEDIUMs, and the near-false rebuttal (2026-10-18)

Fully arming a fourth repo for zcode (grounding twin, guards, repo_health suite, gate
driver) took the gate nine rounds. The port's own hole: the two newly wired hook scripts
sat in none of the three apparatus enumerations, so mid-FAIL the G6 guard itself was
defangable (the r64 class). The deeper catch: the shared-ledger outage rows wrote
current=null, which the guard's own-name test can never honor - G42 disarmed exactly in
the fail-closed state it exists for; the ledger now self-identifies via its own location.
Round 6 is the row's cautionary core: a rebuttal claiming a staged .gitignore rule the
reviewer could not see was ONE VERIFY STEP from shipping false - the rule's patch had
silently never applied (a failed earlier script aborted before reaching it); the
check-ignore probe caught it and converted the rebuttal into a fix. Six LOW classes
fixed besides (notary signalling, foreign-verdict ownership, skip/dirty display,
recovery-path marker, fallback-name asymmetry, budget-era drift); the master-side
backlog (sticky tamper per-repo keying, add -A gating) is reported to the owner. Full
row with artifact refs: gate_evidence.json EV-231-JCM-PORT-GATE-GAUNTLET.

## EV-232 - the RSI corpus library's own birth gauntlet: four rounds, six census defects, one unprovable rebuttal (2026-10-18)

The recursive-self-improvement program's very first tranche - the library that mines every colibri review into root causes - went through four BLOCK rounds and a WARN. The catches: append-mutated ledgers duplicated wholesale on every collect, edited sources left phantom findings behind, distinct review records (base vs __r2 files, same-sha re-audit segments) collided and deleted each other, manifest modes collapsed to the last row, the certain-skip tier was unreachable dead code, and the rollback test proved nothing. A clean rebuild after the fixes recovered 33 reviews and 143 manifest rows the defects had silently destroyed. The cautionary core is round 1's rebuttal: the fixtures WERE staged, but .md files never reach the code-review payload, so the reviewer correctly refused out-of-band citations - upheld-as-unprovable, then fixed structurally by inlining the fixtures as code. Suite 19 -> 30; landed e8b01231. Full row with artifact refs: gate_evidence.json EV-232-RSI-T1-GATE-ROUNDS.

## EV-233 - the RSI trend instrument's own honesty claims: two rounds, both about the baseline comparison (2026-10-18)

T5 - the measurement tranche of the same RSI program - drew two BLOCKs on the honesty
instrument's own honesty. Round 1: with no snapshot denominator, the renderer still
printed "at or below baseline" - a directional claim nothing measured, two sections under
a headline that said n/a. Round 2 (tier-2 after a provider error): the headline summed
every agent and compared the aggregate against a single-author baseline - agent-mix
drift alone could read as improvement; proven live on the real corpus, where the pre-fix
83.7 aggregate was the owner's rows diluting phantom-man's true 86.2 into a false
below-baseline read. Both fixed RED-first (verdict-named regressions; suite 79 -> 85): a
missing denominator now renders an explicit no-comparison statement, and the headline is
matched to the baseline's own author population with per-author rows as never-compared
context. Landed c82015de round-3 CLEAR. Full row with artifact refs: gate_evidence.json
EV-233-RSI-T5-HONESTY-INSTRUMENT.
Round-3 CLEAR artifact: Nexusmill .adversary/reviews/gate_20261018-144707.md.

## EV-234 - the context-pack tranche: three WARN findings, one visible in the author's own smoke (2026-10-19)

The RSI-inverted priors module drew two WARN rounds on the quality of the context it
hands the reviewer: commented-out contracts polluted the protocol surface; a big code
map could silently push the priors section - the reason the change exists - out of the
pack; and bare import segments were counted as external dependencies. The third is
the lesson: the napier live smoke had PRINTED the bogus "src (5x)" dependency line and
it went unexamined until the reviewer quoted the generating code. All three fixed
RED-first (comment stripping; priors-reserved budget; only @scope/pkg counts).
Landed 8509d25f round-3 CLEAR. Full row with artifact refs: gate_evidence.json
EV-234-BOUNTY-T2-CONTEXT-PACK.

## EV-235 - the forge-path tranche: two BLOCK rounds, one reintroducing the tranche's own failure class (2026-10-19)

The foundry wiring drew two BLOCK rounds with the same core catches: the dep-prep root
walk used an exclusive boundary while framework choice used an inclusive one, so a
foundry.toml AT the code root silently no-op-ed dependency preparation while the runner
forced the foundry platform - every file would skip silently, the exact class the
tranche exists to kill. The author's live napier verification had passed only because
napier's projects are nested, and the tests dodged the boundary the same way. Also:
unguarded forge invocation (abort-the-contest, breaking fail-soft) and failed installs
recorded as installed. Fixed RED-first with a single shared _foundry_root helper,
fail-soft prepare, and rc-checked installs recorded in stats. Landed 33383e72 round-3
CLEAR. Full row: gate_evidence.json EV-235-BOUNTY-T3-FORGE-PATH.

### EV-242-BOUNTY-P2FOUNDRY-BATCHAUDIT - 2026-10-20 - Nexusmill
**Layer:** tier-2 batch audit (deepseek-v4.1-flash:batch) BLOCK on landed tree 771ad9 (p2_scanner/p2_static/test_p2_foundry), surfaced by the W3 docs commit's audit drain

**Caught:** (LOW) _remapping_pins re.search took only the first remapping per line so one-line remappings arrays under-installed deps; (LOW) default_runner forces the foundry framework for any file under a foundry.toml with no forge-presence guard, skipping every file when forge is absent; (LOW) adding 'lib' to SKIP_DIRS excludes any contest source living under a path component named lib from static AND llm review.

**Severity:** LOW x3 (fail-soft bounded; reviewer-bounded premises)

**Author initially:** Verified against CURRENT on-disk source per G35 before any re-fix: F1 verified-stale - _remapping_pins now uses re.finditer with the EV-237-F1 docstring ('ALL entries per line'), fixed by the W5 wave (dedb6722) AFTER the audited tree; F2+F3 adjudicated as documented design trades, not open defects - in-source comments state the deliberate choices (autodetection never trusted: fail-loud foundry prep errors beat the silent-skip; lib/ = foundry deps, never scan units) and both residuals are premise-bounded (forge installed per P2.1-T3 premise; no pack contest ships source under lib/).

**Resolution:** No re-fix shipped: one finding verified-stale (fixed in a later landed tranche), two adjudicated-by-design with residuals on the record. The audit_findings BLOCK row stands as the catch; this row is the same-session record. Residual watch: if a future contest tarball ships source under lib/ or forge goes missing on the host, revisit SKIP_DIRS/framework forcing.

### EV-243-G6V2-SKILL-ENFORCEMENT - 2026-10-20 - Nexusmill
**Layer:** gate-review BLOCK x2 during the G6 v2 build (owner order 2026-10-20: jcodemunch as hook-enforced skill after the second grep drift)

**Caught:** (MEDIUM) the v2 inRepo blob widening matched PATTERN tokens - 'zcat app.log | grep nexusmill' from an outside cwd false-denied, contradicting the v2 contract and risking a wasted one-shot OVERRIDE; (LOW) POSIX-token comments claimed a nexusmill-substring collapse test the code no longer performed; (HIGH) the Claude-guard reason-block rewrite collapsed the here-string terminator onto the next statement ('"@    $out = @{') - a PowerShell parse error that silently disabled the Claude-mount G6 guard, and the zcode-only test suite structurally could not see it.

**Severity:** HIGH x1 + MEDIUM x1 + LOW x1 across the arc

**Author initially:** All accepted, fixed RED-first: blob terms gated on $sawTarget (cwd-only commands with no path-like targets cannot deny); comments rewritten to the actual v2 rule with the bare-/nexusmill spelling documented as the r8-F2 residual class; terminator newline restored + PARSE_OK verified; two permanent tests added (PSParser tokenize of both Claude twins + empty-payload fail-open).

**Resolution:** Landed across b11bc87c + 43ca69fb + 7de50ff2 (all gate CLEAR + notarized) and the final Tools backport 97292ce (twins byte-identical each round). Suite 80/80 final (observed sequence 72/75/77/78/80 across the arc, each a fresh full-suite run). AMENDED 2026-10-20 (rounds 3-4): the arc ran FOUR gate rounds with FIVE real catches and zero rebuttals - 'rg -e VAL <repopath>' outside-cwd allow (round 3, fixed via the flagPattern discriminator after the naive fall-through broke the r9-F1 decoy tests), 'cd <repo> && rg' outside-cwd escape + the cross-repo mark-header claim (round 4, fixed via the cd-operand pre-pass + an accurate header). The arc is the enforcement loop working as designed: the gate caught defects in the guard that enforces the rules, including one class (cross-twin parse rot) the existing suite was blind to.

### EV-244-GIT-DO-ONLY-DRIVER - 2026-10-20 - Nexusmill
**Layer:** gate-review BLOCK/WARN x6 rounds on tools/git_do_only.py + tests (the parallel-session scoped-commit driver, owner order after the git-2.56 --only tip verification)

**Caught:** (MEDIUM x5 r1) glob metacharacter re-interpretation of expanded names; core.quotePath C-escaping corrupting non-ASCII round-trips; notary failure hidden from the exit code; check-to-commit TOCTOU in a disarmed clone; the driver's log committable by a broad pathspec. (MEDIUM x2 + LOW r2) test helper decoding git output with the locale codec (cp1252 mojibake); print() crashing on non-cp1252 filenames AFTER a successful commit; droppings test that proved nothing. (MEDIUM r3) basename matching silently dropped same-named files at depth. (MEDIUM x2 + LOW r4) deep in-repo msg files riding broad pathspecs; tree-mismatch fallthrough still notarizing unverified bytes; a test comment contradicting its assertion. (HIGH r5) THE BASE-REV RACE: a parallel commit landing during the gate check made the driver's commit PARENT the new HEAD while carrying a tree built from the old base - silently reverting the other session's landed work, with the tree guard giving a false all-clear. (LOW x2 r5) UTF-16 msg-file decode crash; glob test not exercising the input-pathspec case.

**Severity:** HIGH x1 + MEDIUM x10 + LOW x4 across five finding rounds (r1-r5) plus the CLEAR landing round (r6); the r4 WARN+BLOCK pair reviewed the same diff

**Author initially:** All accepted, fixed RED-first each round: the frozen-index commit construction (the commit consumes the reviewed scratch index - the TOCTOU closes by construction, not detection); ls-files -z everywhere; notary rc flips exit; reserved-paths semantics settled over three rounds (exact repo-relative path for the log filename + this run's msg file at any depth - a named lockfile reservation, everything else commits); pre-commit HEAD re-check + post-commit parent verification closing the base-rev race; stdout/logfile UTF-8 hardening; every catch carries a regression test (suite grew 6 -> 11).

**Resolution:** Landed 58db4452 - the driver's own dogfood commit, made BY the driver through the real armed gate (gate CLEAR + notarized, exit 0): the ultimate integration proof. Live verification of the underlying git behavior precedes the build (junk/verify_only_commit.py + GIT_TRACE: --only fires the config pre-commit hook against git's private next-index; anti-sweep, correct review bytes, notarization all proven on 2026-10-20). Six rounds, ~16 findings, zero rebuttals - the budgeted arc for a concurrency-critical tool.


### EV-245-MATCHER-V3-ROUNDS-1-2 - 2026-10-20 - Nexusmill
**Layer:** gate-review BLOCK x2 rounds on the matcher v3 tranche (colibri-bounty match_llm.py + match.py::match_findings_v3 + s5 adjudicator passthrough + the p2_llm slug-pin repair)

**Caught:** (MEDIUM) match_llm.adjudicate_pairs: bool('false') is True - a stringified same_bug NO verdict promoted as YES, violating the fail-closed contract the module's own docstring states; the accompanying unit test even ASSERTED the buggy truthiness ('definitely' -> True). (LOW) match_findings_v3: title-equality used_s marked every same-title twin of a v2-matched title used, so an unmatched twin could never be adjudicated - a recall gap in the new channel. (LOW) stats['promoted'] counted YES verdicts, not landed promotions (the greedy drops conflicting pairs) - misleading channel-health accounting.

**Severity:** MEDIUM x1 + LOW x2, one round

**Author initially:** All accepted, fixed RED-first: a literal JSON true is the only YES (the test rewritten to the strict contract: 'false'/'0'/'no'/None/absent -> NO); multiset Counter used_s so exactly K twins of a K-matched title are marked used; the stat renamed yes_verdicts with an honest-name test. Suite 162 -> 164.

**Round 2 (BLOCK, both accepted):** the r1 multiset used_s fix was itself defective - v2 matching the LATER same-title twin left the already-consumed twin eligible (double-match); REVERSED to v2's conservative title-equality (the funnel's title_key dedup makes duplicate titles unreachable - the r1 'recall gap' could not occur in practice while its fix opened a real defect). int(2.5)/int(True) pair numbers coerced to valid indices; now only real JSON integers count. Suite 162 -> 165.

**Resolution:** Landing commit follows this row in the same session (git_do_only scoped tranche); the round's artifact is .adversary/reviews/gate_20261020-211455.md.

### EV-246-GROK47-DOCKET-SCHEMA (2026-10-21, Nexusmill)

**Layer:** gate-review WARN x2 rounds on the grok-4.7 feature-run artifacts commit (3 JSON ledgers; Nexusmill 0dd80699).

**Severity:** LOW x2, two rounds

**Caught:** 6 new manifest rows appended as ROOT KEYS outside `entries[]` (invisible to live-queue consumers); deferred rows used `reason`/`unblock` instead of the array's established `why_deferred`/`unblocks`.

**Author initially:** Rows placed at manifest root + wrong field names - schema taken from the `_convention` docstring, not the live rows.

**Resolution:** Both fixed in Nexusmill 0dd80699 (relocation + renames; adjudication 'fixed': 3). Lesson: convention docstrings drift; the bytes are the contract.

### EV-247-AUDIT-BLOCK-771AD9D9-ADJUDICATED (2026-10-21, Nexusmill)

**Layer:** tier-1 sampled batch-audit BLOCK (2026-10-19, tree 771ad9d9bb, p2_static.py foundry wiring) - driver-check warning on every commit since; adjudicated same session as the GROK47 run.

**Severity:** LOW x3 (adjudicated: 1 fixed / 1 premise-excluded / 1 deliberate)

**Caught:** (F1) `_remapping_pins` first-match-per-line only; (F2) forced-foundry skips all files when forge absent; (F3) `lib` in SKIP_DIRS excludes contest source under lib/.

**Author initially:** None - adjudication row; no new code touched.

**Resolution:** F1 FIXED on current bytes (finditer - the P2 session's EV-237 F1); F2 premise-excluded (forge installed is the P2.1-T3 premise; fail-soft records skip_reasons); F3 DELIBERATE (P2.1-T3 comment: lib/ = foundry deps, never scan units; lib/-sourced-contest edge risk accepted). No new remediation owed.

### EV-248-GROK47-T1-LEDGER-RECONCILIATION (2026-10-21, Nexusmill)

**Layer:** adversary gate tier-2 BLOCK (gate_20261021-033617, qwen3.8-omni-flash) on the GROK47 T1 p2_llm calls_detail ledger

**Caught:** Claimed the reconciliation test fails deterministically because per-row rounded costs cannot sum to the rounded cumulative. The arithmetic was wrong (round(0.000078, 4) is 0.0001, not 0.0 - the suite passed twice), but the underlying class was real: an independently rounded per-call cost diverges from the rounded cumulative for arbitrary inputs.

**Severity:** MEDIUM (rebutted as a deterministic-failure claim; the divergence CLASS was real)

**Resolution:** Rebutted with the arithmetic correction AND hardened by construction: ledger cost_usd is now the cumulative counter's after-minus-before move (telescoping invariant - rows sum back to cost_usd for ANY sequence), pinned by a second test on arbitrary prices. Reviewer verified the rebuttal against the bytes (follow-up WARN cleared). Landed in 42636710.

**Landing commit:** 42636710  
**Lesson:** A wrong arithmetic table can still point at a real invariant gap - close the class by construction instead of arguing the example.

### EV-249-GROK47-T1-TITLE-KEY-JOIN-COLLISION (2026-10-21, Nexusmill)

**Layer:** adversary gate tier-1 BLOCK (gate_20261021-041546, deepseek-v4.1-flash-1017) on the GROK47 T1 verify_unit originals join

**Caught:** The first verify_unit fix joined model echoes to input candidates on frozenset(norm_tokens(title)) - NOT injective: two distinct candidates whose titles are token-order variants share one key, so a kept finding could be silently dropped or a deleted one returned.

**Severity:** MEDIUM

**Resolution:** Real catch, addressed by construction: identity is now the prompt-assigned candidate number n (VERIFY_PROMPT numbers candidates; the adjudicator pair-number discipline - real JSON int in range only, ghosts/duplicates dropped fail-closed). Titles left the join entirely. Landed in 42636710.

**Landing commit:** 42636710  
**Lesson:** A join key must be injective on the inputs it reconciles; normalized-title sets are not (token-order variants collide).

### EV-250-GROK47-T4-SOLC-PIN-PARSING (2026-10-21, Nexusmill)

**Layer:** adversary gate rounds gate_20261021-052200 (WARN, LOW x2) + gate_20261021-053143 (tier-1 BLOCK) on the GROK47 T4 _foundry_solc/select_hits add-ons

**Caught:** (1) unknown min_impact labels fell back to floor 0 - silently keeping only High-ranked hits; (2) _foundry_solc was section-blind (a [profile.ci] pin could win over [profile.default]); (3) TOML trailing comments after a header ([profile.ci] # x) defeated section detection entirely.

**Severity:** LOW x2 + MEDIUM

**Resolution:** All three addressed in the landing commit: unknown budget labels filter NOTHING; section-aware parsing accepts only root/[profile.default] pins; the header is parsed to the FIRST ] so trailing comments count. Pinned by tests (unknown-label membership, ci-vs-default, comment-header shapes). Landed in 1aa035db.

**Landing commit:** 1aa035db  
**Lesson:** Line-oriented TOML parsing needs section awareness AND comment tolerance; fail-closed defaults must be chosen for least surprise (unknown label = no filter, not max filter).

### EV-251-GROK47-T5-TABLE-SEPARATOR-CELLS (2026-10-21, Nexusmill)

**Layer:** adversary gate tier-1 BLOCK (gate_20261021-055752, deepseek-v4.1-flash-1017) on the GROK47 T5 honest_table separator row

**Caught:** The tier-generic separator row used a hand-counted multiplier (5 + 4 + 4 = 13 cells) against a 12-cell header/body - GitHub-flavored Markdown then renders the single consumer-facing artifact as literal text instead of a table. Shipped green because tests only asserted substrings.

**Severity:** MEDIUM

**Resolution:** Addressed by construction: the separator is derived from the header's own pipe count (agreement is structural, not counted), pinned by a cell-count test over header/separator/body. Landed in fb55646e.

**Landing commit:** fb55646e  
**Lesson:** Never hand-count structural pairs (header/separator cells) - derive one from the other; substring tests do not catch layout defects.

### EV-252-GROK47-T5-OWNER-TP-DOUBLE-CREDIT (2026-10-21, Nexusmill)

**Layer:** adversary gate tier-1 BLOCK (gate_20261021-060607, deepseek-v4.1-flash-1017) on the GROK47 T5 owner_tps bucketing

**Caught:** Claimed two different-tier findings with morphological-variant titles could both match one judged truth, double-crediting owner_tps against union matched. The premise is unreachable today: the matcher is one-to-one per truth (used_t) and title_key dedup means one title has one owner - at most ONE record exists per truth.

**Severity:** MEDIUM (premise unreachable; invariant risk was real if the matcher ever changes)

**Resolution:** Rebutted with the one-to-one proof AND made the invariant structural regardless: truth credit is GLOBAL across owners (a truth is credited to at most one owner, so sum(owner_tps) can never exceed matched), pinned by the exact morphological-variant test the reviewer proposed. Landed in fb55646e.

**Landing commit:** fb55646e  
**Lesson:** When a BLOCK's trigger is unreachable but the invariant it fears is load-bearing, make the invariant structural and pin it with the reviewer's own scenario.


### EV-254-G47R2-T1-GATE-ARC-ROUNDS-1-4 (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T1 data-layer commit - BLOCK x3 + WARN x1 (qwen3.8-omni-flash once, deepseek-v4.1-flash-1017 three times)

**Caught:** 12 findings, all real, all fixed RED-first in-session. R1: `start_after` skipped `r.name <= cursor` while `resume_after` names the JUST-FAILED repo - the documented resume dropped it forever (the 2026-10-16 F1 class one layer up); `paid-skipped` in the header was structurally 0 (read pre-collection). R2: the fixed cursor still skipped recorded-but-incomplete repos (tarball-only row with failed issues; deleted tarball); readonly connect bypassed schema identity; invalid-UTF-8 `config.json` raised through `corpus_probe`'s never-raise contract; report-less `fetch_issues` wrote no sidecar; the mismatch path leaked the sqlite handle blocking Windows delete-and-refetch. R3: the cursor still skipped repos whose latest issues REFRESH failed or whose dump file was deleted; limit sliced BEFORE the cursor filter so a capped resume processed zero new repos; the `sync_*` cursor helpers never committed - not durable across restart. R4 (WARN): readonly rejected pre-stamp corpora the write path upgrades in place (delete-advice on a losslessly-upgradable paid-channel corpus); `resume_after` pinned the failed repo so resumes re-fetched post-failure successes' issues.

**Severity:** MEDIUM arc (7 MEDIUM + 5 LOW over four rounds)

**Resolution:** Cursor skips only the FULLY recorded prefix (`_cursor_skip`), applied before the limit slice; `resume_after` names the LAST ATTEMPTED repo; paid-skipped moved to `pytest_report_collectionfinish`; readonly reads pre-stamp corpora like the write path does; `UnicodeDecodeError` caught; sidecar always written; every mismatch path closes the connection; each `sync_*` step commits. 14 named regression tests; suite 202 -> 250.

**Landing commit:** f0085bb4
**Lesson:** A resume cursor must key on FULL recordedness (row + artifact on disk + dump when in scope), never on name arithmetic or row existence alone - and each round catching the previous round's fix-gap is the multi-round arc doing its job, not a failure of it.

### EV-253-STRAT-DOCKET-STATUS-FIELD (2026-10-21, Nexusmill)

**Layer:** adversary gate tier-1 BLOCK (gate_20261021-102829, deepseek-v4.1-flash-1017@deepinfra/fp8) on the GROK47-STRAT docket commit

**Caught:** Six new docs/deferred_manifest.json entries (GROK47-STRAT-1..5 + NTH, the owner-accepted grok-4.7 architecture proposals) omitted the status field that 155/162 live sibling entries carry - a docket consumer reading or filtering on entry['status'] would skip or KeyError the accepted rows so they never enter the docket despite why_deferred saying they were accepted.

**Severity:** MEDIUM

**Resolution:** status=deferred added to all six rows via validated text surgery (json.load verified), manifest re-indexed, commit re-run clean.

**Landing commit:** 51c7e8cb
**Lesson:** A docket row the gate forced into remediation must carry the schema every consumer iterates - the covenant fields are not optional garnish.
### EV-255-G47R2-T2-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T2 acquisition+status commit 17267d1c - BLOCK x2 (round 1 via the tier-2 backstop after a tier-1 transport error)

**Caught:** 6 findings, all real, all fixed RED-first. R1: cmd_mirrors compared receipt dicts against the "error" string so the CLI always exited 0 (HIGH); db.sync_start's ON CONFLICT reset pages_done/next_page, wiping the persisted resume cursor the old inline SQL preserved (MEDIUM). R2: contract_gaps checked a misspelled join key (issues_item_finders vs issues_issue_finders) - a guaranteed false-clean from the re-check that exists to catch it; a successful run kept the previous run's error message beside status=ok; resolve_contest_root's "shallowest descendant" was lexicographic; the fingerprint guard could not fire on legacy upgraded cursors.

**Severity:** HIGH arc (1 HIGH + 5 MEDIUM/LOW over two rounds)

**Resolution:** All six fixed in-commit (status read from entry["status"], sync_start touches only liveness fields with reset_run the sole cursor resetter, join key corrected, sync_finish always writes message, depth sort, legacy-cursor refusal). Suite 250 -> 276.

**Author's initial reaction:** All accepted on read and re-traced against the bytes; the tier-2 backstop carried round 1 after the tier-1 transport error - the ladder failover working as designed.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/mirrors.py (cmd_mirrors)
- Nexusmill colibri-bounty/colibri_bounty/db.py (sync_start/sync_finish)
- Nexusmill colibri-bounty/colibri_bounty/github_corpora.py (contract_gaps, resolve_contest_root)
- Nexusmill commit 17267d1c (gate-round notes in the message)


### EV-256-G47R2-T4-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T4 replay+spend-integrity commit 41d4b04e - 5 rounds per the session record; the landed commit message documents round 1 (the remaining rounds' fixes landed with the same commit)

**Caught:** Round 1 (BLOCK, documented in the commit message): per-contest severity lines inside the GFM table body terminated the table - every later contest row rendered as literal text (the EV-251 class reintroduced); tier_state never read the status:failed meta run_replay_tiers itself writes (a failed tier rendered not-run, under both meta conventions); the channel partition bucketed a whole MIXED contest into llm (per-MATCH bucketing via methods["llm"] now). Later rounds fixed: stale dump mtime precedence masking a later failure; severity-slice precision mixing populations (scan_matched by scan severity); rescore ignoring failed meta; --max-cost overshoot silent (now disclosed + exit 3); a FAILED baseline row with 10 cells against an 11-cell header.

**Severity:** MEDIUM arc (~10 findings over five rounds)

**Resolution:** All fixed in-commit with structure/mixed-contest/precision tests; severity lines moved after the last table row, tier_state classifies failed and renders FAILED, channel buckets are per-MATCH with channel-share labels. Suite 297 -> 315.

**Author's initial reaction:** Accepted on read; the GFM table-termination catch is the second recurrence of the EV-251 class inside table-rendering code - the structure test now pins the two-contest shape.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/replay_runner.py (tier_state, rescore)
- Nexusmill colibri-bounty/colibri_bounty/s5.py (severity lines, channel buckets)
- Nexusmill colibri-bounty/colibri_bounty/cli.py (--max-cost disclosure, exit 3)
- Nexusmill commit 41d4b04e (gate-round notes in the message)


### EV-257-G47R2-T5A-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T5a foundry/solc pinning commit e0440167 - BLOCK x2 + WARN x2 (four rounds)

**Caught:** 9 findings, all real, all fixed. R1: _pragma_window's caret bumped the MAJOR for 0.x pragmas (^0.7.6 read <1.0.0 so 0.8.19 "fit" and solc rejected the file - Solidity 0.x carets bump the MINOR); a bare pragma was treated as a caret span instead of an exact pin; the vendor-skip test imported names from another module so a swallowed NameError made it pass vacuously. R2: --remappings is not a slither flag (the option is --solc-remaps and takes remapping TEXT); ^0.0.x carets must bump the PATCH (full npm caret ladder now). R3 (WARN): docstring claimed a caret window for bare pragmas; skip-path comments claimed deterministic skip where solc=None means autodetect/fail-soft. R4 (WARN): foundry_installed extend sat OUTSIDE the prepare guard (truthy non-iterable would abort the scan); extra_skip matched lowercased parts verbatim while a bare string split into characters.

**Severity:** MEDIUM arc (3 MEDIUM + 6 LOW over four rounds)

**Resolution:** All fixed RED-first in-commit; the caret ladder is pinned for 0.0.x/0.x/1.x and bare pragmas exact-pin. Suite 315 -> 327.

**Author's initial reaction:** Accepted on read; the vacuous-test catch (NameError swallowed into a pass) is its own lesson - cross-module test imports can silently disable the gate the test exists to be.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/p2_static.py (_pragma_window, default_runner, extra_skip)
- Nexusmill colibri-bounty/colibri_bounty/p2_scanner.py (foundry_installed guard)
- Nexusmill commit e0440167 (gate-round notes in the message)


### EV-258-G47R2-T5B-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T5b PoC/inv execution commit 3b301847 - BLOCK x4

**Caught:** 12 findings, all real, all fixed RED-first. R1: rc!=0 with zero parsed counts and no recognized phrase read "invariants-held" - a false success; the harness marker stamped only the FIRST revert literal (an unmarked assertTrue body could never CONFIRM, a guard revert monopolized the stamp); the Suite-result regex made "; N skipped" required, regressing the semicolon-less shape into a comma fallback that dropped the failed count. R2: all-SKIPPED matched invariants fell through to invariants-held; poc_source_gaps substring membership made testPoc1 "found" inside testPoc10, wasting the 600s forge budget. R3: auto-stamping every string literal turned guard reverts and data strings into bogus CONFIRMEDs (wrap-only + refuse unmarked now - which strings are assertion messages is not statically knowable); the match trio did not follow a per-contest contract; exception path lacked the candidates key; contract= param unusable with the module runner; phrase checks misclassified failing test-authored text; valid {} labeled compile_or_non_json. R4: POC-1 is a strict PREFIX of POC-10 - the substring guard accepted 10's marker for 1 and adjudication would CONFIRM 1 on 10's evidence (money-safety: a false grounded candidate; marker IDENTITY via not-followed-by-digit, pinned by the cross-collision fixture).

**Severity:** MEDIUM arc (3 MEDIUM + 9 LOW over four rounds)

**Resolution:** All fixed in-commit; dispositions come from parsed failures first (phrases only for zero-parse runs), the marker is caller-owned identity, and adjudication matches marker identity. Suite 327 -> 338.

**Author's initial reaction:** Accepted on read; the R4 prefix collision is the strongest row of the arc - a false CONFIRM would have grounded a candidate on another candidate's evidence, exactly the money-safety failure the disposition layer exists to prevent.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/p2_poc.py (render_poc_harness, adjudicate_poc, poc_source_gaps)
- Nexusmill colibri-bounty/colibri_bounty/p2_inv.py (run_forge_tests dispositions)
- Nexusmill commit 3b301847 (gate-round notes in the message)


### EV-259-G47R2-T5C-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T5c unit-hub links commit 2d26d1d6 - BLOCK x1

**Caught:** 4 findings (1 MEDIUM + 3 LOW), all fixed RED-first: the suffix FALLBACK broke on a per-file first-match break that locked the match at k=1 - pkg/lib/Math.sol lost to pkg/a/Math.sol for "../lib/Math.sol", splitting exactly the integration the module exists to keep in-unit (each file's LONGEST suffix now); components_split_by_budget counted files not components; the edge position field was a char offset where a LINE number is documented; cluster_files' preserve_hub seeding mis-seeded budget-cut bins (gate_20261021-180140 FINDING 4).

**Severity:** MEDIUM arc (single round)

**Resolution:** All fixed in-commit with the longest-suffix pinned by the pkg/lib collision fixture. Suite 338 -> 347.

**Author's initial reaction:** Accepted on read - the k=1 lock was a first-match break masquerading as a tiebreak policy.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/p2_units.py (suffix resolution, components_split_by_budget, edge lines)
- Nexusmill commit 2d26d1d6 (gate-round notes in the message)


### EV-260-G47R2-T6-GATE-ARC (2026-10-21, Nexusmill)

**Layer:** adversary gate arc on the G47R2 T6 paid-channels/priors/matcher commit ddf52a2d - BLOCK x4 + WARN x1 + one malformed review retried to CLEAR (six rounds, deepseek-v4.1-flash-1017@deepinfra/fp8 throughout)

**Caught:** 15 findings, all real, all fixed. R1: the new P2X unreadable-unit branch referenced an undefined name (unit_name0) - a NameError killed the whole paid scan after billing (MEDIUM); the replay-cache hit path counted the replay as a call and re-folded the PREVIOUS real call's cost (double billing in attribution); verify_unit booked a full model reject as a join-drop; the conditions stamp stored prompt_ids as a set (usage serializes verbatim - TypeError at reporting time). R2: type-unchecked model rows - a null detail reached the attribution substring test and 'stem in None' aborted the scan (MEDIUM); the verify ledger did not balance on subset echoes; budget_headroom omitted the input pre-estimate chat applies; an errored unit landed in no manifest bucket. R3: the BudgetExceeded branch REPLACED units_remaining, discarding units the new error-append had added (MEDIUM - extend, never assign); estimate dropped a whole unit on one unreadable member while scan reviews on any readable member. R4 (WARN): disposition-mask reuse crash; registry keywords not lowercased at install (mixed-case scores zero); classify tie-break silently alphabetical instead of curated order; estimate compared raw chars against the assembled-source truncation. R5: the r4 mask resize preserved a prior call's prefix - stale model_yes on unmeasured slots (MEDIUM; the mask resets every call, like the verdicts vector).

**Severity:** MEDIUM arc (5 MEDIUM + 10 LOW over five substantive rounds)

**Resolution:** All fifteen fixed RED-first in-commit with verdict-named gate tests; the reviewer explicitly verified each prior round's fixes in the following round (cache no-double-bill, n-join fail-closed, type normalization, twin/capped/greedy dedupe, band-guard inversion cleared three times as an exact complement). Suite 347 -> 389.

**Author's initial reaction:** Every finding accepted on read; three rounds caught defects IN THE PRIOR ROUND'S FIX (r3's replace-vs-append against r2's append; r5's prefix-preserving reset against r4's resize; r2's type hazard riding the r1-authored branch) - the multi-round arc earning its cost, and the exact reason findings are fixed one hypothesis at a time.

**Refs:**
- Nexusmill/.adversary/reviews/gate_20261021-191136.md
- Nexusmill/.adversary/reviews/gate_20261021-194035.md
- Nexusmill colibri-bounty/colibri_bounty/p2_scanner.py (unit ledger, estimate, type normalization)
- Nexusmill colibri-bounty/colibri_bounty/match_llm.py (replay cache, pair_disposition)
- Nexusmill colibri-bounty/colibri_bounty/p2_llm.py (verify_join ledger, conditions, budget_headroom)
- Nexusmill colibri-bounty/colibri_bounty/priors.py (keyword install, tie-break)
- Nexusmill commit ddf52a2d (gate-round notes in the message)


### EV-261-AUDIT-LANE-20261019-ADJUDICATION (2026-10-21, Nexusmill)

**Layer:** sampled tier-1 batch audit (audit-drain lane) BLOCK on LANDED P2.1-T3 foundry wiring (tree 771ad9d9, queued 2026-10-19) - surfaced as the standing commit-time WARNING during the G47R2 T6 arc and adjudicated on current bytes at T7 close-out

**Caught:** 3 LOW findings against the landed foundry wiring: _remapping_pins' re.search took only the first remapping per line (second dep never installed, forge build dies); default_runner forces the foundry framework whenever a foundry.toml ancestor exists, so a missing forge binary skips every file in that project (the failure mode a removed comment described); SKIP_DIRS gained "lib" globally, excluding any contest source living under a lib/ component from both static and LLM review.

**Severity:** LOW arc (advisory WARNING; sampled audit of landed code, not a commit refusal)

**Resolution:** Adjudicated verified-stale/intended on CURRENT bytes, no re-fix (G35): finding 1 was already remediated under EV-237 (the parser is re.finditer with the docstring 'ALL entries per line - a one-line remappings array must install every dep' and the EV-237 F1 comment naming the exact defect); finding 2's silent-skip harm is addressed by the T5b/T4 disposition layer (named skip_reasons + skip_sample, and files_dep_incomplete excludes unresolved-dep roots from the clean-zero denominator), bounded by the P2.1-T3 premise that forge is installed on this machine; finding 3 is intended by design - the in-code comment documents foundry deps under lib/ as 'dependencies, never scan units', and the audit itself noted the test asserts intent.

**Author's initial reaction:** The lane worked as designed: the sampled audit flagged landed code, the WARNING carried it to the next commit, and the T7 adjudication closed it with per-finding current-bytes evidence instead of a reflexive re-fix.

**Refs:**
- Nexusmill .adversary/audit_findings.jsonl (row 20261019-050724)
- Nexusmill colibri-bounty/colibri_bounty/p2_static.py (_remapping_pins, default_runner, SKIP_DIRS)
- Nexusmill colibri-bounty/colibri_bounty/p2_scanner.py (skip_reasons/files_dep_incomplete disposition)

### EV-262-G47R2-PHASEB-W6-GATE-ARC (2026-10-22, Nexusmill)

**Layer:** adversary gate arc on the Phase B W6 blinded-S3-protocol commit 40af8e43 - BLOCK x1

**Caught:** 2 findings, both fixed RED-first in-commit. MEDIUM - the sealed key was co-located with the trees INSIDE the pool root, so the module's 'the blinding is STRUCTURAL, not procedural' claim was false at the first review: a fresh session operating in the pool directory could read key.json directly. Fixed: key_path() puts the sealed key at a SIBLING file (<pool>.key.json); the pool directory holds ONLY trees (pinned by a pool-listing assertion); the real E:/ pool key relocated. LOW - an unmeasured control arm (a pristine id missing from the dumps) read as clean while matched mutants scored detected - the false-positive arm silently unmeasured. Fixed: controls_measured gates every detected flag (voided + control_arm 'unmeasured' + score_valid False, per-tree match evidence preserved); gate test test_unmeasured_control_arm_voids_the_score.

**Severity:** MEDIUM arc (1 MEDIUM + 1 LOW, single round)

**Resolution:** Both fixed in-commit; suite 397 -> 398 inside the 391 -> 398 tranche (the tranche message also corrects tranche 1's suite count to 391).

**Author's initial reaction:** Accepted on read; the key-co-location catch demolished the module's own docstring claim before it ever landed - and the audit lane (EV-263) then found the claimed guarantee was still false on a different axis after the fix.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/w6.py (key_path, build_pool)
- Nexusmill colibri-bounty/tests/test_w6.py
- Nexusmill commit 40af8e43 (gate-round notes in the message)

### EV-263-G47R2-W6-AUDIT-LANE-ARC-ADJUDICATION (2026-10-22, Nexusmill)

**Layer:** sampled tier-1 batch audit (audit-drain lane) - TWO BLOCK rows against the landed W6 protocol: 20261022-001039 (tree a991631876, artifact gate_20261022-000157.md) on the W6 tranche's bytes and 20261022-010425 (tree 89031e881d, artifact gate_20261022-005558.md) on the marker-fix commit 2f5cc66c; both adjudicated on current bytes at Phase C close-out

**Caught:** Row 1 carried the pre-fix attempt's findings (key co-location, unmeasured control arm - already caught and fixed by the commit gate's own r1, EV-262) PLUS one real residual the commit gate missed: every pristine tree was a byte-identical copy of the source, so hashing the pool directory revealed exactly the n_pristine-member identical group - the control arm - defeating the blinding through tree CONTENTS regardless of the opaque ids. Remediated by 2f5cc66c (per-tree '.w6-tree-id' marker + a pairwise-distinctness content-hash test; the real E:/bounty-corpus/w6_blind_v1 pool trees marked in place, sealed key untouched). Row 2 audited the marker commit itself and found the fix INEFFECTIVE: the marker adds no entropy the auditor does not already have (the id is the directory name), and the pristine trees' subtrees remain byte-identical - hashing each tree's contents EXCLUDING the marker (or simply diffing tree pairs: the pristine pair is the only pair whose entire diff is the marker file) still identifies the control arm; the new test verifies the symptom (whole-tree hash uniqueness), not the property (arm indistinguishability).

**Severity:** MEDIUM (protocol-validity: the false-positive arm of the synthetic scorecard is de-anonymizable by an auditor who hashes or diffs; no money path)

**Resolution:** Row 1's pre-fix findings verified fixed in-commit (key_path sibling + pool-listing pin are in the landed bytes); the identical-pristines residual remediated by 2f5cc66c. Row 2's finding adjudicated CONFIRMED on CURRENT bytes (build_pool's pristine loop is copytree + marker and nothing else, w6.py:135-142): the structural-blinding claim does not hold against a subtree/minus-marker hash or a pairwise diff. STATUS OPEN, escalated to the owner BEFORE the W6 cold audit - options on record: (a) single pristine control per pool (no identical pair exists), (b) distinct pristine sources per pool, (c) proceed on the sealed v1 pool with the residual disclosed in the protocol and the auditor barred from content-hashing/diffing pool trees. With this row all three standing audit-lane BLOCKs (20261019 = EV-261, 20261022-001039, 20261022-010425) are adjudicated; amended below the same day after the owner ruled 'we harden first'.

**Amended (2026-10-22, later the same day - owner ruling 'we harden first'):** hardened in Nexusmill 52fabfa5 (first-round gate CLEAR) - EXACTLY ONE pristine control is the pool contract (n_pristine != 1 refuses up front, nothing on disk), the marker is bookkeeping, the minus-marker pairwise-distinctness property is pinned by test, and the structurally-uncloseable residual (cross-tree diff-degree hubs on the single unmutated tree) is DISCLOSED in the module docstring + bias_disclosure() with the protocol bar on cross-tree hashing/diffing. RED-first gates; suite 438/1. Pool rebuilt as E:/bounty-corpus/w6_blind_v2 (seed 20261022); v1 + key deleted; the cold audit moves to the NEXT fresh session (the hardening session is the v2 injector). Remediation manifest row w6_blinding_control_arm_2026_10_22 in the same commit. CLOSED (hardened + residual disclosed). Note: the drain row's artifact field points at the COMMIT GATE's CLEAR (gate_20261022-005558.md) - the drain's BLOCK text survives only in the row's truncated text_head; artifact-path defect flagged to the gate's owner.


**Author's initial reaction:** Accepted on read; the second row is the audit lane catching what the commit gate had just cleared, and the third link in a chain (gate: key co-location -> lane: identical pristines -> marker fix -> lane: marker ineffective) where each fix restored the CLAIMED guarantee only against the exact probe that caught it. The session-state guess that the third standing BLOCK was a strat tree was wrong - it was this row.

**Refs:**
- Nexusmill .adversary/audit_findings.jsonl (rows 20261022-001039, 20261022-010425)
- Nexusmill .adversary/reviews/gate_20261022-000157.md
- Nexusmill .adversary/reviews/gate_20261022-005558.md
- Nexusmill colibri-bounty/colibri_bounty/w6.py (build_pool pristine loop, key_path)
- Nexusmill commits 40af8e43 + 2f5cc66c

### EV-264-G47R2-PHASEB-S5-DOCSTRING-WARN-CLOSURE (2026-10-22, Nexusmill)

**Layer:** audit-lane WARN 20261021-002638 (artifact gate_20261021-001740.md) on the inv-tier wiring tree c3419122 - the s5.py module docstring still enumerated three dedup tiers after TIER_PRIORITY gained 'inv'; remediated in the Phase B tranche-1 commit 4e150da6 and docketed at close-out

**Caught:** LOW, documentation-contract: the priority order a maintainer reads from the docstring omitted the inv tier, so its last-place dedup participation was undiscoverable from the documented contract.

**Severity:** LOW (advisory WARN on landed code)

**Resolution:** Closed in 4e150da6: the docstring enumerates all four tiers (agent > t5 > poc > inv) AND a drift-guard test (test_docstring_names_every_priority_tier) now fails whenever TIER_PRIORITY grows without the prose following - the WARN class made structurally unrepeatable rather than text-patched.

**Author's initial reaction:** Accepted; the fix landed inside Phase B tranche 1 (the queue item closed there) but the catch itself had no docket row - added now to keep the every-catch-gets-a-row covenant.

**Refs:**
- Nexusmill .adversary/audit_findings.jsonl (row 20261021-002638)
- Nexusmill .adversary/reviews/gate_20261021-001740.md
- Nexusmill colibri-bounty/colibri_bounty/s5.py (module docstring, TIER_PRIORITY)
- Nexusmill commit 4e150da6

### EV-265-G47R2-STRAT5-GATE-ARC (2026-10-22, Nexusmill)

**Layer:** adversary gate arc on the STRAT-5 verify-deletion shadow commit f0f8fbfa - BLOCK x1

**Caught:** 2 findings, both fixed. MEDIUM - the raw-candidate stash stored the model title UNNORMALIZED, re-opening the T6 r2 crash class at the shadow matcher, OUTSIDE every fail-soft handler, after billing, meta unwritten = total run loss. Fixed at BOTH layers: the stash coerces like the kept-loop AND _score_and_dump coerces at the consumption point (last_stats is scanner-authored data); gate test test_null_title_raw_candidate_cannot_kill_the_scoring (RED: crashed). LOW - deleted_matched_truths counted BudgetExceeded/API-errored units as verify-deletions, corrupting the future exemption-gate decision; fixed: the stash happens only AFTER verify succeeds (errored units unmeasured, not deleted) and the shadow carries budget_stopped/llm_errors health flags; gate test test_errored_unit_is_unmeasured_not_deleted. (A duplicated verify block from the first fix edit was caught by the suite and removed.)

**Severity:** MEDIUM arc (1 MEDIUM + 1 LOW, single round)

**Resolution:** Fixed in-commit; suite 398 -> 403 inside the tranche. The EXEMPTION half stays deferred per the row: gated on STRAT-1 core-flow candidates and on these shadow numbers accumulating across replays.

**Author's initial reaction:** Accepted on read; the untyped-boundary defect at a scanner-authored-data consumption point is the G47 class again - the third recurrence the gate has caught at exactly this seam.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/p2_scanner.py (shadow_raw_candidates stash)
- Nexusmill colibri-bounty/colibri_bounty/replay_runner.py (_score_and_dump)
- Nexusmill colibri-bounty/tests/test_strat5.py
- Nexusmill commit f0f8fbfa (gate-round notes in the message)

### EV-266-G47R2-STRAT2-GATE-ARC (2026-10-22, Nexusmill)

**Layer:** adversary gate arc on the STRAT-2 known-issues pre-check commit 8d439f85 - four rounds (BLOCK x3 documented in the commit message: rounds 1, 3, 4; round 2 the in-round test repair)

**Caught:** Round 1 (2 findings): MEDIUM - match_known ran on RAW review output upstream of every coercion, so a numeric/null title crashed the paid scan after billing (the T6 r2 class, third recurrence; the gate now coerces at its own boundary; gate test test_gate_survives_untyped_review_rows, RED: AttributeError). LOW - P2 counted the known-issue drop BEFORE verify but candidates_raw only after, so an API-errored verify left dropped > raw (P2X disagreed); candidates_raw now increments right after review, before the gate, in BOTH twins (test_drops_never_exceed_raw_on_verify_error pins the invariant on the error path). Round 3 (3 findings): MEDIUM - the harvest else-branch took the head of ANY doc wholesale, so ordinary protocol prose could swallow a fully-covered candidate title out of the default-ON paid verify set (silent recall loss, counter-only record); scoped sections only for every doc now, whole-file harvest reserved for KNOWN_ISSUES-named files, and every drop leaves a per-candidate audit record (known_issue_dropped_titles). LOW - flag_truth_hits lacked the r1 coercion (the guardrail could crash on untyped titles). LOW - the manifest resolution was dishonest (403->409 with 8 tests; corrected to the honest 403->412). Round 4 (1 finding): the wholesale branch was guarded by 'not _SECTION_RE', so a HEADED KNOWN_ISSUES.md fell into scoped extraction where its issue sub-headings match nothing - the text was silently dropped and the layer no-opped on the most natural file layout; KNOWN_ISSUES* files are now wholesale unconditionally, with the headed layout gate-tested.

**Severity:** MEDIUM arc (3 MEDIUM + 3 LOW over four rounds)

**Resolution:** All fixed in-commit. Suite-count correction for the record: the commit message's round-4 note says 'Suite 413' - the honest final is 412 (the r4 gate test extended an existing function, so no net new test); the session-state correction is applied here.

**Author's initial reaction:** Accepted on read; round 4 is the arc's lesson - the round-3 fix for over-broad harvest introduced its own silent no-op on the headed layout, found only because the gate re-read the bytes with the new guard in mind.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/known_issues.py (harvest_known_text, match_known, flag_truth_hits)
- Nexusmill colibri-bounty/colibri_bounty/p2_scanner.py (the gate between review and verify)
- Nexusmill colibri-bounty/tests/test_strat2.py
- Nexusmill commit 8d439f85 (gate-round notes in the message)

### EV-267-G47R2-STRAT3-GATE-ARC (2026-10-22, Nexusmill)

**Layer:** adversary gate arc on the STRAT-3 corroboration/exec/locus commit 2807a6bd - BLOCK x1

**Caught:** 3 findings, all fixed. MEDIUM - count_duplicate_claims_v2 checked only folded/mechanism while v2 now scores through locus too: the double-report metric the T3 row created to see 'the channels the funnel actually scores with' was BLIND to the new channel (locus_accepts joins the check; gate test test_dup_claims_v2_sees_the_locus_channel). LOW - the locus name match was a raw substring ('Token' inside 'tokenomics', 'Core' inside 'score') - now a word-boundary regex (test_locus_naming_requires_a_word_boundary). LOW - max_pairs capped the band BEFORE the exec/paid split, so free exec pairs (and sub-band exec pairs exec then refuses) consumed paid-budget slots - the split now precedes the cap, which applies to the PAID band only; band_capped counts paid-band overflow.

**Severity:** MEDIUM arc (1 MEDIUM + 2 LOW, single round)

**Resolution:** Fixed in-commit; suite 412 -> 416 inside the tranche.

**Author's initial reaction:** Accepted on read; the blind-metric catch is the meta-lesson - every new scoring channel must be joined into the metrics that exist to observe the channels, or the anti-blending guard itself goes blind.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/match.py (_channel_scores, match_findings_v2/v3, count_duplicate_claims_v2)
- Nexusmill colibri-bounty/colibri_bounty/s5.py (union_findings corroboration pooling)
- Nexusmill colibri-bounty/tests/test_strat3.py
- Nexusmill commit 2807a6bd (gate-round notes in the message)

### EV-268-G47R2-STRAT4-GATE-ARC (2026-10-22, Nexusmill)

**Layer:** adversary gate arc on the STRAT-4 live finalist path commit 1b0eabee - EIGHTEEN rounds (BLOCK x16 + WARN x2 per the commit message's own round notes), the deepest arc in the docket

**Caught:** ~35 findings, every one real, all fixed in-commit; they cluster into six classes. (1) CLI/parse: argparse nargs handed TIER=DUMP strings but cmd_live called .items() on the raw list (AttributeError on the exact documented CLI form); --tiers was not repeatable (last-flag-wins silently dropped a paid tier dump - caught TWICE, the r14 action=append fix had not actually landed and r15 re-caught it); duplicate tier keys silently overwrote a dump. (2) MONEY-SAFETY on the $100 program ceiling: a $0 'reservation' committed nothing (two $60 passes both budgeted); check+record non-atomic (two concurrent reservations both passed a $0 ledger); record() ran UNLOCKED (lost updates understated spend); record() had no stale-lock recovery (a killed process left fail-open accounting); the chat headroom check was READ-ONLY (two concurrent chats near the ceiling both spent); the reserve-then-amend flow double-billed against the live entry's own reservation; negative/NaN estimates bypassed the ceiling; an UNPRICED frontier client stayed callable (now fail-closed: price_out_usd_per_m must be pinned or chat refuses); final r18 shape - chat gates through the ATOMIC reserve (per-call hold), records the actual post-call, releases the hold clamped at what the same label reserved; the ceiling counts ACTUAL spend only and consumption is atomic. (3) LOCK DISCIPLINE: the lock derived by with_suffix('.lock') collided with a --ledger ending in .lock (the stale path renamed THE LEDGER ITSELF away and silently reset the ceiling); stale-lock reaping was TOCTOU three times over (unlink, rename, and os.replace each able to hit a FRESH holder's lock) - final shape: pid+time-token locks, re-read ownership verification, PID-UNIQUE stale names, release only when still ours. (4) LEDGER FILE RACES: non-atomic JSON IO (torn reads), init racing a recorded row, a $0-reservation write ordering that stranded on failed writes - write-temp-then-atomic-replace, O_EXCL creation, bounded retries, packet-serialized-before-reserve. (5) OUTPUT HONESTY: a FALSE $0.0 spend claim with no producer (n/a without a producer; one unknown usd poisons a mixed sum); tier-evidence fallthrough scoring t5 Highs at 1.5 instead of 3.0 (the tier names now ride the evidence table); a stringified severity '['High']' scoring silent 0.0; docstrings overclaiming (reserves vs checks) rewritten to what the code does; the cost expression dividing a known-subset sum by the FULL matched-High count while rendering spend n/a. (6) UNTYPED TIER-DUMP FIELDS crashing the packet build TWICE (r9: detail/severity/title/path; r11: corroboration left unvalidated) - the loader coerces what the packet reads (the G47 untyped-boundary class, twice more).

**Severity:** MEDIUM-HIGH arc (~35 findings over eighteen rounds; the money-safety class dominates)

**Resolution:** All fixed in-commit with verdict-named gate tests through r18. SpendLedger is now atomic check/record/reserve/release under a pid-verified sibling .reserve.lock (never with_suffix), program-wide default ledger at the corpus root (COLIBRI_PROGRAM_LEDGER overridable), JSON IO atomic; FrontierClient rides its own budget namespace outside max_calls and REFUSES all wire calls unpriced; the live entry CHECKS headroom (the runbook's actual spend is the only charge - the reservation class killed entirely). Suite 419 -> 437.

**Author's initial reaction:** Accepted throughout, zero rebuttals; rounds 9-18 repeatedly caught defects in the PRIOR ROUND'S OWN FIX (r11 completing r9's coercion; r12/r13 closing the estimate/amendment hole r9's own test masked; r15 finding r14's append fix never landed) - the longest fix-begets-fix chain in the docket, and the reason the row's manifest resolution names all eighteen rounds.

**Refs:**
- Nexusmill colibri-bounty/colibri_bounty/portfolio.py (rank_finalists, SpendLedger, FrontierClient)
- Nexusmill colibri-bounty/colibri_bounty/s5.py (matched_high, weighted_recall, honest_rollup)
- Nexusmill colibri-bounty/colibri_bounty/live.py (cmd_live)
- Nexusmill colibri-bounty/tests/test_strat4.py
- Nexusmill commit 1b0eabee (round-by-round notes in the message)

### EV-269-GATE-AUDIT-ROW-ARTIFACT-DEFECT (2026-10-22, Tools)

**Layer:** found during the w6 EV-263 adjudication (a defect IN the gate's own machinery, not a commit refusal): the audit-drain's audit_findings.jsonl row writer named the COMMIT GATE's review as its 'artifact' (meta.get('artifact') copied from the queue entry) and never persisted the drain's own review beyond the 2000-char text_head - when the drain CONTRADICTS a clearance (the 20261022-010425 w6-marker BLOCK vs the commit gate's CLEAR), the row points auditors at the wrong review and the real evidence is truncated. Owner order after the note: 'fixing the gate always is paramount'

**Caught:** (1) MEDIUM, evidence integrity: every drain verdict row carried a pointer to a review it did not produce; the drain's own full text (the actual evidence for BLOCK/WARN verdicts that gate shipping) existed only as text_head. Historical full texts are unrecoverable - recorded, not fabricated. (2) The fix run exposed a stale battery dating to the 2026-10-20 owner repin to flash-1017: test_tier2_chain_is_flash_high_plus_qwen_fallback still expected the retired baidu slug; FleetLadderParityTests::test_gate_ladder_parity_with_default_chain was red (the gate moved, the fleet mirror did not); fleet_selftest's fixture catalog and fleet-gate-ladder-order were green BEFORE the mirror fix only because both sides were stale together.

**Severity:** MEDIUM (post-commit audit-lane evidence integrity; verdicts were never wrong - their pointer and persistence were)

**Resolution:** Tools 6d75be7 (first-round CLEAR, notarized, runtime enforcement re-installed from the reviewed source): cmd_audit_drain now writes the drain's OWN full review to .adversary/reviews/audit_<queued>.md (audit_-prefix can never collide with gate_* artifacts) BEFORE the row lands; the row's 'artifact' names that file and the commit-gate review rides a new 'gate_artifact' field as provenance only. Consumers verified safe (the warning counter counts outcomes; the push guard matches tree/files/when - nothing reads row['artifact']). RED-first: test_drain_row_artifact_is_the_drains_own_review failed on pre-fix bytes. Battery repinned green: test_ladder_20261012.py 16/16 (incl. the new gate test), test_batch_review.py 19+13 subtests, fleet_selftest 21/21 PASS.

**Author's initial reaction:** Accepted on read; the defect sat invisible because drain rows usually AGREE with the commit gate, so the wrong pointer surfaces exactly when it matters most - a contradiction. The sister lesson: two pin batteries had been red-or-hollow since the 2026-10-20 repin on files nobody ran; the gate's own battery is part of the gate.

**Refs:**
- Tools commit 6d75be7 (adversary-gate/adversary_gate.py cmd_audit_drain row writer; test_ladder_20261012.py; autoland/fleet_config.py GATE_LADDER; autoland/fleet_selftest.py)
- Nexusmill .adversary/audit_findings.jsonl (row 20261022-010425 - the row whose artifact field held the commit gate's CLEAR)
- Nexusmill .adversary/reviews/gate_20261022-005558.md (the CLEAR the row mis-cited)
- colibri-code-review docket EV-263 (the adjudication that surfaced the discrepancy)
## 2026-10-22 Crucible T0: four inherited port defects caught on the copy (EV-270)

**Layer:** gate-review BLOCK (tier 2, artifact gate_20261022-144454) on the Crucible founding tranche 3 (the ported llm/match_llm cores).

**Caught:** four defects ALL inherited from upstream colibri-bounty code the faithful port copied verbatim - cache-hit chunks re-fold stale spend rows and inflate usd/token stats (~Nx over-report on cache-heavy reruns); a 429 retry posted one billed wire attempt beyond max_calls; budget_headroom().next_chat_raises omitted the input cap; duplicate pair rows left the verdict vector and the disposition mask in disagreement.

**Severity:** MEDIUM (spend-reporting integrity + absolute-budget breach on the dispatch core every future paid Crucible tier rides; unreachable at T0 - tiers are stubs - but the T2 foundation).

**Author's initial reaction:** Accepted on read, no rebuttal - and the irony is the row: the faithful-port discipline imported upstream's silent defects, and the gate caught on the COPY what had shipped in the ORIGINAL. The upstream funnel still carries all four.

**Resolution:** all four fixed RED-first in Crucible ca18262 (contract tests, suite 17->21, RED run on record); remediation manifest rows; upstream flagged in Crucible docs/REFERENCE_FINDINGS.md for the funnel lane.

**Refs:**
- Crucible .adversary/reviews/gate_20261022-144454.md (BLOCK) + gate_20261022-150940.md (CLEAR)
- Crucible ca18262, tests/test_smoke.py, docs/remediation_manifest.json, docs/REFERENCE_FINDINGS.md
- Upstream Nexusmill colibri-bounty match_llm.py + p2_llm.py @ ed30d181 (all four present)

## 2026-10-22 Crucible T0: snapshot findings rebutted as fix-upstream, re-verified CLEAR (EV-271)

**Layer:** gate-review BLOCK (tier 2, artifact gate_20261022-142709) on the founding snapshot tranche (verbatim 28-module funnel copy).

**Caught:** three LOW findings against snapshot bytes - truth.py tokenless-title collapse (recall denominator hole), truth.py non-UTF-8 judging dump crashes replay instead of the disclosed skip, portfolio.py FrontierClient dead _pinned condition makes the documented bounded config unusable.

**Severity:** LOW (upstream-live-code defects surfaced through a never-imported reference tree).

**Author's initial reaction:** Rebutted on WHERE the fix belongs, not severity - the snapshot is a byte-frozen provenance anchor (fingerprint pinned); patching it destroys the port diff-anchor. Fixes belong upstream or at port time.

**Resolution:** rebuttal re-verified against the bytes -> CLEAR (gate_20261022-143415); snapshot landed unmodified (9ea934c); findings discharged to Crucible docs/REFERENCE_FINDINGS.md with port-phase dispositions. All three remain OPEN upstream.

**Refs:**
- Crucible .adversary/reviews/gate_20261022-142709.md (BLOCK) + gate_20261022-143415.md (CLEAR)
- Crucible 9ea934c + docs/REFERENCE_FINDINGS.md
- Upstream Nexusmill colibri-bounty truth.py + portfolio.py @ ed30d181 (OPEN)

## 2026-10-22 Crucible T1 oracle: two BLOCK arcs + WARN-cleared, corpus +141 rows from one catch (EV-272)

**Layer:** gate-review BLOCK x2 (gate_20261022-162448, gate_20261022-164037) then WARN-cleared (gate_20261022-165231) on the T1 oracle tranche.

**Caught:** loader scalar-field crash class; PERF_RE inflection recall gap; head/log race; binary anchor drop (arc 1) — then a tok/s regex that FABRICATED per-second claims from per-sequence counts and an empty-repo crash (arc 2).

**Severity:** MEDIUM (oracle integrity — fabricated evidence class + a silent 141-row corpus shrink).

**Author's initial reaction:** accepted on read, no rebuttals; 5 of 6 RED-proven before fixing.

**Resolution:** all fixed RED-first in Crucible 0407f95; the corpus re-mined after each arc — the recall fix alone took it 312→453 rows (A 73→94), a measured gate earning. Residual LOW (binary diff_stat '+0 -0') owed next tranche; the landed commit message's '312 rows' is stale round-1 text — the committed corpus/baseline (453) is authoritative.

**Refs:**
- Crucible .adversary/reviews/gate_20261022-162448.md / -164037.md / -165231.md
- Crucible 0407f95, docs/ORACLE_BASELINE.md, tests/test_oracle.py

### EV-273-GATE-RECURRENCE-SCREEN-ARC (2026-10-22, Tools)

**Layer:** owner order 2026-10-22 ('this drift will reoccur... I want this scenario screened... an abstracted version... automatic and enforced... a centralized container that all armed repos can access and are forced to scan themselves against by structural design. I dont want any more lessons gone unlearned anymore'): the RECURRENCE SCREEN - a centralized container of ABSTRACTED recurrence lessons (RL-0001 coupled-duplicate drift, RL-0002 guarantee claim without a machine-held test, RL-0003 coordinated rotation stragglers) with machine detectors, enforced at EVERY commit in EVERY armed repo (cmd_check runs it first, unconditionally, against the repo's own recurrence_screen.json bindings, reading the INDEX - the state the commit would land). Eight review rounds on the landing itself; LIVE PROOF after activation: a plain git commit in a temp repo with a drifted binding REFUSED through the machine-wide hook (generation 7f7d992)

**Caught:** R1: arm_repo str/str TypeError aborting every arming; the screen reading the WORKING TREE (partial staging could split a coupled pair past the screen - the exact RL-0003 bypass - and WIP edits refused unrelated commits); malformed bindings escaping into a silent engine-failure degrade. R2: the raw git child dropping _run_git's hardenings (a local git replace could substitute the screened bytes; no timeout; inherited stdin); any git failure reading as 'nothing bound' (silent pass); the arm-repo docstring contradicting its caller. R3: separate catalog files can NEVER reach the installed generation (the active generation builds the next from its own catalog); the override bypass neither consumed nor recorded the one-shot; a fresh repo's missing-manifest message misclassified as engine failure. R4 (no review dispatched): folding into adversary_gate.py pushed that CERTIFIED_CATALOG file over MAX_FILE_BYTES and the runtime-catalog coupling refused outright. R5: guarantee bindings with typo'd keys or no claims/tests had empty patterns that match EVERYTHING (checked nothing, passed); a nonexistent --repo printed a false PASS; the override double-consumption wrinkle. R6: a non-list bindings value iterated zero times (silent pass); parity groups with no sites yielded empty sets - empty == empty PASSED (the parity twin of R5-F1); the CLI's raw-CWD default false-PASSed from a subdirectory. R7 (WARN, blocking runtime deployment until R8): the code-override record dropped the screen_refusals provenance; a stale invariant comment (the reviewer noted both were the RL-0002 class the change itself encodes).

**Severity:** MEDIUM-HIGH arc (18 findings over eight rounds; the screen is now the machine-wide enforcement point for every abstracted recurrence lesson)

**Resolution:** All landed in Tools 0166f88 + 7f7d992 (engine + centralized container live in docscan.py - an EXISTING catalog file - with the cmd_check wiring, OVERRIDE release semantics consumed+recorded, the recurrence-screen CLI, arm-repo manifest seeding, the Tools repo's own ladder bindings, and a 24-row battery). The round-8 clean CLEAR authorized the runtime deployment and generation 7f7d992 activated. Canon G45 added + propagated (370 targets); Nexusmill's bindings (the w6 guarantee claims) landed through the live screen (031aed56).

**Author's initial reaction:** Every finding accepted on read, zero rebuttals. The arc is the docket's thesis in miniature: the gate caught its own enforcement machinery's deployment deadlock, its size-cap invariant, its runtime-credit standard (WARN rows never deploy enforcement bytes), and six fail-open holes - before any of it shipped. Two deployment truths are now banked for every future gate change: new catalog files cannot reach the installed generation (fold into an existing one), and adversary_gate.py must stay under the 300k catalog cap.

**Refs:**
- Tools commits 0166f88 + 7f7d992 (adversary-gate/docscan.py _RS_* engine + _RS_LESSONS; adversary_gate.py cmd_check wiring + CLI; test_recurrence_screen.py 24 rows; recurrence_screen.json Tools bindings; arm-repo/arm_repo.py seeding)
- Tools review artifacts gate_20261022-144051 / -150401 / -153429 / -160812 / -162840 / -164732 (the six BLOCK/WARN rounds)
- Tools .adversary/runtime/active.json (generation 7f7d992 active; live refusal proof on a drifted temp-repo commit)
- Nexusmill commit 031aed56 (recurrence_screen.json w6-guarantee bindings, screened live); docs/GLOBAL_RULES.md G45
- colibri-code-review docket EV-269 (the audit-drain artifact fix whose battery-staleness discovery triggered the owner's order)
