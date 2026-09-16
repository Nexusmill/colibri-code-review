# ADVERSARY_GATE.md - the mandatory adversarial commit gate (G39) in this repo

> **Doc version: 3.1 - 2026-09-15.** See [DOCS_VERSIONS.md](DOCS_VERSIONS.md). 3.1: the removed-symbol
> refusal shadows a bystander's OWN binding and nothing else (Tools ca686ed + 7935480 + 8b4e40c + b0de7ab, EV-088), and the docs
> lane's evidence gate withdraws on a one-character literal (c33a704, EV-089) as well as on the
> describing verbs and model slugs of 51ba4b3 (EV-083/086); selftest counts updated. Machine-wide
> arming (the dispatcher hook dir, the census, HOOK_NAMES, the rules epoch) is its own doc:
> [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md). 2.1 added the owner rulings of 2026-09-07:
> fixture repositories skip the review (EV-045); secrets warn and are scrubbed at commit and
> are refused at push (EV-046) - see the "Secrets" section. **3.0 (2026-09-14) re-baselines the
> doc on Tools 6773f97:** the hook REQUESTS the review itself (auto-review on commit, Tools
> 9597241 - the working loop changed); the reviewer is a fallback CHAIN, not `tencent/hy3`; the
> docs lane is a LOCAL semantic reviewer behind an evidence gate; a deterministic removed-symbol
> refusal runs before any model call (EV-060); repos are armed at birth (ROOT baseline, EV-055);
> the owner tools `owner_ff_merge.py` and `owner_scrub_notes.py` exist; the selftest inventory
> is current.
>
> Source of truth: `C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py`
> (the tool) and `.githooks/pre-commit` here (the shim). Born 2026-08-30 from the owner's
> order after plan-triangulation proved that authors - external models AND the in-session
> agent - defend invented claims: *"every bit of code written, before it's committed,
> needs an adversarial review... build it so you have no choice."* This repo is ARMED.

## What it is

A git pre-commit hook (routed via `core.hooksPath .githooks`, so it fires on EVERY commit
path - CLI git, helper scripts, IDEs) that **refuses any commit staging code** unless an
INDEPENDENT external model has issued `VERDICT: CLEAR` keyed to the exact sha256 of each
staged blob. The reviewer is never the author. Re-editing a cleared file invalidates its
clearance automatically - clearance follows bytes, not intentions.

## What counts as "staging code"

- Files with a code extension: `.py .js .json .ts .jsx .tsx .html .css .ps1 .sh .bat .c
  .cpp .h .rs .go .java .glsl .osl .mjs .cjs .mts .cts` (`.json` added 2026-08-31, owner's
  order: manifests, registries and configs are load-bearing - a forged manifest row is a code
  change; the four JS/TS module forms added 2026-09-04, EV-029: an ES-module security guard had
  passed a gate run with a clearance covering only its test file - the same set lives in the
  vendored auditor, and re-vendoring it makes the auditor demand notes for module files in
  post-baseline history, which is the fail-closed direction)
- **Anything under `.githooks/`** regardless of extension - a hook edit could neuter the
  gate itself (finding from the gate's own birth review, round 2)
- **Extensionless git hook files (`pre-commit`, `post-commit`, `pre-push`) wherever they
  live** (2026-09-06, EV-042): the canonical shims in `Tools/adversary-gate/` and the
  dispatchers in `adversary-gate/hooks/` are the single source of every vendored hook and had
  never been gated. `HOOK_NAMES` in the gate and the vendored auditor classifies them as code,
  confined to commits after the per-repo rules epoch so history is not reclassified. See
  [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md)
- **Anything under `.github/workflows/`** - the CI audit workflow is enforcement config
  too; editing it un-gated would be the same hole (layered-enforcement review 2026-08-31)
- **Deletions of code files and renames-away** (code renamed to a non-code extension) -
  removing or hiding code is a code change (birth review, round 3); keyed as `D:<path>`
  with the removed HEAD blob's sha
- **Merges are NOT exempt** - a merge can carry un-gated commits; the staged result is
  reviewable like any other change

Docs (`.md`) and other non-code files need no EXTERNAL clearance - they are never sent to the
external reviewer - but they are not unexamined: their ADDED lines pass the local pattern
floor and the local docs model at commit time (warnings only) and again at push time, where a
block refuses the push (see "The docs lane" under Secrets). JSON does NOT pass free since
2026-08-31: manifest/registry rows are reviewed with the change they describe.

**A deterministic refusal runs before any model call (Tools de3f953, 2026-09-09, EV-060):**
`run` refuses (exit 1, callers listed) a staged `.py` that REMOVES a module-level `def`/`class`
- present in its HEAD blob, absent from its index blob; a deleted, unparsable or
renamed-to-non-`.py` file removes all of its names - while any tracked `.py` OUTSIDE the staged
set still references it (name, attribute or import binding; the listing is root-anchored so a
run from a subdirectory cannot fall open). The case that built it: Tools 8245433 removed
`_scan_text_secrets` while the Codex reviewed-write broker still called it, and the gate had
CLEARed the removal because the caller was not staged. **Names are matched unqualified, with
exactly two shadows (Tools ca686ed, 2026-09-15, EV-088):** a bystander that DEFINES the name at
module level (its own `def main`) is not a caller, and neither is a bystander whose
`from X import name` is PROVEN to bind something else - X names a tracked, unstaged file at the
repo root that is the only path with that suffix anywhere in the tracked, staged or untracked
tree, no ignored file hides under the same name at the root or beside the bystander, and X's
index blob defines the name and binds it nowhere else in MODULE SCOPE (the `from fleet.cli import
main` shape). Module scope is every statement reachable without entering a def, lambda or class
body, plus the definition-time expressions of those - decorators, default arguments, annotations,
return annotations, class bases and keywords; a method or a function-local of the same name does
not count. A `def keep` followed by `from lib import keep` is not proof (Tools 7935480, round seven);
a module-level `from lib import *` disqualifies every def in that module, and a walrus, a `del`, an
`except ... as`, a `match` capture (`case N:`, `case [*N]:`, `case {**N}:`), a `global` or a second
def of the same name each exclude it (8b4e40c, rounds eight to ten), and so does a `global` declared
inside any nested body - a class body runs at import (b0de7ab, round eleven). Rounds seven, eight
and eleven were found by the MARKETPLACE gate reviewing the byte-identical re-vendored plugin: a
second repo's review of the same bytes is a second independent reviewer (EV-090). Everything unprovable
still refuses: a bare use, an attribute use, a plain `import X`, a relative import, an import
from the definer, a staged or deleted or untracked source, a duplicated module name, a
re-exporter, or a module static resolution cannot find at all (a src/ layout or a sys.path
entry can hide repo code behind such a name, so "not found" is never "external"). The case:
the fleet Atlas whole-package deletion was refused for sixteen lines that were every other
module's own `main`; the fix took six review rounds because five drafts each kept a
"not found -> external -> vouch" branch (selftest checks 43-54; check 54 pins twenty module-scope
binding shapes on `_sole_module_level_defs` directly - twenty-three since b0de7ab).

## The working loop (auto-review on commit since Tools 9597241, 2026-09-07)

```text
1. edit + stage everything (git add <paths>)
2. git commit
     -> the pre-commit hook runs `adversary_gate.py check`. When staged code lacks a fresh
        clearance it REQUESTS THE REVIEW ITSELF ("ADVERSARY GATE: requesting automatic
        independent review of staged changes."): the model gets the staged diff (unified=8)
        + full staged files (250KB/file, 900KB total caps; oversized files judged from
        hunks), read from a frozen index snapshot and a pinned base so later staging cannot
        acquire a clearance for bytes the reviewer never saw.
3a. VERDICT: CLEAR  -> clearance written, the commit lands, post-commit notarizes it.
3b. VERDICT: BLOCK  -> the commit is refused with findings (severity/file/line/trigger/impact).
     Fix each real finding, restage, commit again (a fresh review).
     A WRONG finding is rebutted FACTUALLY, before the next commit:
       python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py run \
         --context "why the finding does not hold, with file/line evidence"
     The reviewer re-verifies rebuttals against the bytes and will call out a false
     rebuttal - never argue a finding away in prose outside the loop. `run` is also how
     design intent or the provenance of copied bytes reaches the reviewer: the automatic
     review carries NO context, so run it explicitly whenever the reviewer needs one, then
     commit (the hook finds the clearance while the staged bytes stay identical).
4. re-editing after a CLEAR invalidates it (clearance follows bytes); the next commit
   simply reviews again.
```

The proof that the hook fires is the "requesting automatic independent review" line (or a
BLOCK) during `git commit`; a code commit that lands SILENTLY means the hook did not run -
stop and `install_gate.py <repo> --verify-only`. Other commands: `... verify` (what the hook
used to be: reports stale/unreviewed files WITHOUT calling a reviewer - diagnostic only),
`... status` (staged files vs clearance state), `... check-push <remote>` (the push guard).

## Configuration

- **Key:** `OPENROUTER_API_KEY` env - required to RUN the adversary; never printed. The
  fallback model on xAI needs `XAI_API_KEY` (or `xaikey=` in the `.env` named by
  `NEXUSMILL_XAI_ENV`).
- **Model:** `DEFAULT_MODEL` is a comma-separated FALLBACK CHAIN - GLM-5.3-Flash on
  OpenRouter first (owner ruling 2026-09-01: similarly priced to the old default and it
  FINISHES), then xAI Grok-4.6 through the `xai:` prefix, which routes to api.x.ai rather
  than OpenRouter (owner ruling 2026-09-03; it replaced a flash model that emptied on heavy
  payloads). The exact ids are the `DEFAULT_MODEL` line in `adversary_gate.py`;
  `ADVERSARY_MODEL` env or `--model` overrides. The chain advances only on a transport /
  provider failure (HTTP errors, 429s exhausted after 3 retries with 30s backoff, an error
  payload) or an EMPTY response - never on a rendered verdict; if the LAST model is empty
  too the run fails CLOSED (auto-BLOCK), never an exception. The reviewer prompt names the
  canonical colibri manifest shape as doctrine it must not re-litigate (Tools 8db2fbe,
  2026-09-10) while still catching a duplicate entry, a `files` wrapper or a relative-keyed
  row.
- **State:** `.adversary/` (gitignored) - `clearance.json` (per-file sha-keyed verdicts),
  `reviews/gate_<timestamp>.md` artifacts (model, usage, files, full verdict text) and
  `write-reviews/` (the Codex broker's per-write evidence, see
  [CODEX_GATE_IMPLEMENTATION.md](CODEX_GATE_IMPLEMENTATION.md)).
- **Selftests** in the tool folder, offline via `ADVERSARY_FAKE` (honored ONLY inside
  `advgate_*`-named selftest repos - it cannot stub the real gate, birth review r2), counts as
  run on 2026-09-14 against Tools 6773f97 (`gate_selftest.py` and `docscan_selftest.py` re-run
  2026-09-15 on b0de7ab): `gate_selftest.py` 126, `install_selftest.py` 73,
  `guard_selftest.py` 231, `audit_selftest.py` 50, `hooks_selftest.py` 19 (the dispatchers),
  `docscan_selftest.py` 14 (runs the real local model), `codex_guard_selftest.py` 19,
  `owner_ff_merge_selftest.py` 11, `owner_scrub_notes_selftest.py` 17,
  `owner_setup_selftest.py` 12, the pytest trio (`test_reviewed_write.py`,
  `test_codex_policy.py`, `test_enforcement_server.py`) 24, and
  `arm-repo/arm_repo_selftest.py` 23.

## The escape hatch is not yours

`.adversary/OVERRIDE` (a file containing a written reason) lets exactly ONE commit
through with a loud warning, then deletes itself. It exists for the OWNER's emergencies.
An agent using it is a protocol violation, full stop - equivalent to disabling the gate.

## Arming truth (machine-wide since 2026-09-06)

**Superseded:** the old "a fresh clone is UNARMED until `git config core.hooksPath .githooks`"
claim was retracted (EV-041 - the premise that per-clone arming is a git limitation was
false). Arming is now **machine-wide**: git's GLOBAL `core.hooksPath` points at the dispatcher
dir `Tools/adversary-gate/hooks` (owner-set, once), so every checkout and future clone/worktree
on the owner's machine is armed for the commit wall; `install_gate.py` additionally pins the
same **absolute** value per repo and vendors `.githooks/` for CI and other machines. Other
machines still arm per clone with the installer. Full architecture: [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md).
Verify any checkout, or the whole machine:

```bash
python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py <repo> --verify-only
python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py --census
```

Two hardening facts learned in the field (2026-08-30, now baked into this repo's
arming): the hook must be committed with index mode **100755** - POSIX git silently
*skips* a non-executable hook, turning the mandatory gate into a no-op on any POSIX
checkout (`git update-index --chmod=+x .githooks/pre-commit`); and
`.githooks/.gitattributes` pins the shim to `eol=lf` so an `autocrlf=true` checkout can
never hand `/bin/sh` a CRLF script it refuses to parse.

## Durable notarization + the audit tripwire (2026-08-31)

The hook alone is advisory - git offers `--no-verify`, plumbing, GUI escapes, unarmed
clones, and (worst) direct forgery of `.adversary/clearance.json`. The answer is layered
(full doc: [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md)): a `post-commit` hook runs
`adversary_gate.py record`, which writes a durable **git note** on
`refs/notes/adversary` iff every changed code blob matches a fresh CLEAR (fail-closed:
no match, no note - note ABSENCE is the tripwire signal); the vendored
`.githooks/adversary_audit.py` re-verifies every commit after
`.githooks/adversary_baseline` and screams on unnotarized or sha-mismatched history;
CI runs the same auditor on push. Owner OVERRIDEs become provenance-carrying OVERRIDE
notes - visible forever, blessing only the exact blobs they were invoked for. The notes
travel with every push: the `pre-push` dispatcher pushes `refs/notes/adversary` to the same
remote itself (a hand push, `git push origin refs/notes/adversary`, is only for clones
without the guard).

**Armed at birth (Tools 9e46976, 2026-09-08, owner ruling; docket EV-055).** An EMPTY repo
no longer waits for a first commit: the installer anchors `.githooks/adversary_baseline` at
`ROOT` and the rules epoch at `hook-names ROOT`, and the auditor, its epoch walker, the gate's
mirror walker and the installer's assessors all understand `ROOT` - every commit including
the root commit is challenged. `--json` on an unborn ROOT-baselined repo emits a JSON document
(83b45f1). Existing repos keep their sha baselines until re-anchored. The auditor's ROOT path
was then hardened twice by catches on other repos (EV-063 / EV-064, Tools 3c1243a / 70835b6):
deleting the current branch ref no longer makes a ROOT repository with remaining commits read
clean (successful object enumeration with no commits is required; a corrupt or hidden ref
fails closed), and the ROOT epoch shortcut runs the shallow-history probe first (a shallow
clone with valid notes had returned clean).

## Secrets: warn and scrub at commit, refuse at push; fixture repos skip the review (2026-09-07)

Owner rulings of 2026-09-07, landed in Tools 1f287bb (EV-045), 8245433 and ad484fa (EV-046):

- **Fixture repositories.** A repository whose git dir lies under the user profile's Temp
  folder - resolved through the Windows known-folder API, never TMPDIR/TEMP (an env-keyed
  locator would let a committer reclassify a real checkout); `/tmp` and `/var/tmp` on POSIX -
  is a test fixture: `check` skips the review with a one-line notice and `record` writes no
  note. Disabled under `ADVERSARY_SELFTEST=1`, so the selftests' own temp repos stay gated. The
  push guard still runs there, so nothing pushed from such a repo escapes the audit: the lane
  is local-only. Why: machine-wide arming plus auto-review-on-commit (Tools 9597241) had every
  pytest fixture commit running a PAID external review (jcodemunch-mcp alone has 327 such
  tests; a suite ran 35 minutes spending a review per commit before it was killed).
- **Secrets at commit time WARN.** The local pattern floor and the local docs model no longer
  block a commit or consume the OVERRIDE; hits are listed as file:line + label, values never
  printed.
- **Nothing unredacted is transmitted.** The exact review payload (the diff including removed
  lines, the full staged files, the author's context) is scrubbed before it leaves the
  machine: every matched value becomes `<REDACTED:label>` - every value on a line, whole
  private-key blocks through their END line (bounded at 200 lines; an unterminated block is
  warned), per `str.splitlines()` segment so a lone CR cannot hide a value behind the
  4096-char heuristic gate - and a REDACTION NOTE heads the payload so the reviewer reads a
  tag as a matched value, not a missing one. The vendor-documented AWS example key and the
  bare-name idiom (`user:password@host`, the ssh flag given the word secret) are placeholders.
- **The push guard is the barrier.** Before the note audit, every outgoing commit's ADDED
  lines (first-parent diff; `--src-prefix`/`--dst-prefix` pinned against `diff.noprefix`;
  `+++` treated as a header only outside a hunk; C-quoted paths unquoted; NUL lines dropped)
  are scanned: a hard literal (known key prefixes, private-key blocks, ssh / URL credentials)
  REFUSES the push with the rewrite recipe - a hook cannot scrub history; the assignment
  heuristic warns; the outgoing doc lines are re-run through the local docs model (block
  refuses, degraded or capped warns). Owner-OVERRIDE-notarized commits pass with a warning;
  shallow-clone boundary commits are skipped loudly by the barrier and the note audit; an
  unknown remote tip switches the recipe to "rotate, do not rewrite". A deliberate fixture is
  built at runtime from parts - the gate's own selftests do.
- **The docs lane's evidence gate (Tools f2fdfd4 + 724d095 / 14d1f09 / fb0d9a6 / d9876ff /
  6d24c55, 2026-09-07..09).** The local docs model (`docscan.py`: Qwen3-4B through
  `llama-cli`, env-configurable - `NEXUSMILL_LLAMA_CLI`, `NEXUSMILL_DOCSCAN_MODEL[_SHA]`,
  `NEXUSMILL_DOCSCAN_NGL`, `NEXUSMILL_DOCSCAN_TIMEOUT`) reads the ADDED doc lines in 6000-char
  chunks (24 per commit; the tail is pattern-floor-only, reported) and answers BLOCK / CLEAR
  with a REASON line. A BLOCK stands ONLY if the REASON quotes a VALUE: `_evidence_is_name()`
  withdraws it - loudly, on stderr - when every token is descriptive vocabulary, a provider
  name, an env-var NAME, a placeholder (`yourpassword`, `changeme`, `<redacted>`), a bare
  credential ROLE word (`pw`, `user`), an ELIDED vendor prefix (`sk-ant-...`, `AKIA...`), a
  prose verb or noun that DESCRIBES a credential (`needs`, `requires`, `references` - 51ba4b3,
  EV-086), a vendor/model SLUG with a model shape on the right (`z-ai/glm-5.3-flash` - 51ba4b3,
  EV-083) or a single ALPHANUMERIC character (`"k"` - c33a704, EV-089: a plan document's
  embedded test code set a key variable to a one-letter fake); any digit/symbol token, an
  un-underscored ALL-CAPS string, a two-character-or-longer unknown word or a provider/PASSWORD
  slug is a value, and an empty REASON keeps the block (fail closed). Absent a model the lane degrades LOUDLY to the
  pattern floor, never silently. At push the docs feed excludes commits already reachable from
  the remote's tracking refs (`git fetch --prune origin` first) - a fresh branch once re-fed 124
  published commits (EV-061) - while the pattern floor and the note audit keep the full
  outgoing set. The false-positive classes found live so far - a provider/model slug (EV-083),
  a describing verb across a chunk boundary (EV-086), a one-character literal (EV-089) - are
  each closed by a rule above; the recipe that finds the next one is the guard's own feed
  builder run over the exact outgoing revs and `docscan._run_one_full` on the named chunk,
  three runs, then a rule with a measured RED/GREEN - never a rewrite of history.
- **The receipts.** Landing the scrub took SEVEN gate rounds and the push guard THREE; every
  BLOCK was a real leak path or blindness the author's own tests had missed (docket EV-047).

## Owner tools (never the agent's)

- `owner_setup.py` - the one owner script: registers the harness guard, adds the gh
  `workflow` scope, performs the outstanding pushes, sets branch protection (12 selftest
  checks).
- `owner_ff_merge.py` (Tools ae014e0 / 15555dd / a5ca6b7, 2026-09-07..10) - lands an audited
  PR head on a protected `main` by FAST-FORWARD. The merge buttons are squash-only under
  linear-history protection and a UI squash mints one unaudited sha, so the tool pushes the
  SAME sha the `audit` check already passed, after live checks (PR open + mergeable with the
  expected refs, origin/main an ancestor, a successful `audit` check-run for that exact sha,
  polled up to `--wait`), then polls for MERGED and deletes the remote side branch; local
  branches are left alone. Dry run by default, `--apply` to act; `--only <repo> --pr N --head
  <branch>` override the configured PR (the built-in table goes stale the day each PR lands);
  `nexusmill`, `colibri` and `marketplace` are the configured targets. Every landing on this
  system since 2026-09-07 went this way.
- `owner_scrub_notes.py` (b01c8fb, 2026-09-08) - reviewers quote what they read, so a value
  the reviewer SAW can sit in `refs/notes/adversary` after the tree itself was scrubbed; the
  push guard never scans notes and the harness guard forbids agents to touch them. This
  owner-only tool scrubs a value class out of the notes (orphan-rebuilt ref, unreachable notes
  pruned, the auditor re-verified; a dry run reports and changes nothing).

## Why it exists (the receipts)

The gate's own birth review ran SIX adversarial rounds and caught: a merge bypass, an
empty-response crash, a hook-edit bypass, a deletion bypass, a dismissed-as-rendering
artifact that was a literal BEL byte, a per-clone arming overpromise - **and one false
rebuttal from the very agent building it** (round 5: a claimed fix that had never been
written; the adversary read the staged bytes). The installer's birth review (7 rounds,
11 findings, one more conceded false rebuttal) repeated the lesson the same day. Authors
defend invented claims; the gate is structural distrust of exactly that.
