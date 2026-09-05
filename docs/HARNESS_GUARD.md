# HARNESS_GUARD.md - the agent-side deny guard: every rule, its reason, and the 2026-09-04 arc

One-line abstract: the catalogue of what `Tools/adversary-gate/harness_guard.py` (the Claude Code
PreToolUse guard) and its ZCode twin `Caliper/tools/git-guard.mjs` refuse, why each rule exists,
the day both were hardened together, and the owner sweeps that followed.

## What the guard is, and is not

The guard binds the AGENT, never the operator. It is layer 2 of `LAYERED_ENFORCEMENT.md`: a
pure `decide(tool_name, tool_input)` core behind a thin stdin/stdout wrapper, registered as a
Claude Code PreToolUse hook on `Bash|Write|Edit|MultiEdit|NotebookEdit`. It fails OPEN on
malformed input. It raises the cost of a bypass; the post-commit notarization and the vendored
auditor (layer 3) are the trust anchor. `GUARD_PORTABILITY.md` in Tools explains why the same
core ports to any mount and where it deliberately does not (the owner's own shell).

The guard is a TEXT guard. Every rule below encodes a fact about git or the shell, and every
rule is deny-on-doubt: when a command's text could be a bypass, it is refused, and a command that
merely QUOTES a guarded string is refused too. That is documented, not a defect: put such text in
a file and run the file by path.

## Bash rules (evaluated per shell segment, case-insensitive)

| Rule | Why |
|---|---|
| `--no-verify` anywhere | the flag skips the pre-commit gate; it can be smuggled across lines via a variable |
| `FLAG=-n` / `FLAG=--no-verify` assignments, `set -- -n` | shell-variable smuggling of the flag (best-effort; the auditor backstops unbounded indirection) |
| `git ... commit ... -<bundle>n` where no value-taking option (`m F c C t`) precedes the `n` | `-nm x` is `-n -m x` (deny) but `-mn x` is `-m "n"`, the hook RUNS - denying it was a live false positive until 2026-09-04 |
| `$VAR ... commit ... -n` | a variable-built git word (`c=git; $c commit -n`) leaves a `commit` token with no `git` token in the segment (found by probe 2026-09-04) |
| `hooksPath` anything except arming `.githooks` | re-pointing or unsetting `core.hooksPath` detaches the gate |
| `commit-tree`, `update-ref`, `fast-import`, `git replace` | plumbing that creates or moves commits without hooks |
| mutating `git notes` subcommands | adversary notes are written only by `adversary_gate.py record` |
| `ADVERSARY_FAKE` outside `*_selftest.py` | fakes the reviewer verdict |
| any literal `.adversary` | the gate's state dir: clearances, OVERRIDE, notes staging. No read exemption (EV-022: once shadowing / PATH / aliases are in play a text guard cannot tell a read from a write) |
| any `skill_gate/` reference | the G38 skill gate's ledgers and OVERRIDE, same covenant |
| any `.git/hooks` path token, in any spelling | the LIVE hook dir: rewriting or deleting the inner pre-commit hook disarms the gate. No read exemption. The reviewed shim is `.githooks/`, which never matches |

The hooks-dir trigger is `\.git[. ]*[\\/](?:[^\s;&|'". ]|[. ]+(?=[\\/])|\.(?![. ]*[\\/]))*\bhooks\b`:
any token that starts at `.git/` (or a Windows-trimmed `.git./`, `.git../`) and reaches a
`hooks` segment, whatever redundant components lie between (`./`, `//`, `../`, trimmed `.. `
tails). The three alternatives are disjoint on `.`, which keeps matching linear; an overlapping
form backtracked exponentially on `./` repeated forty times and hung the hook.

## File-tool rules (Write / Edit / MultiEdit / NotebookEdit)

The path is lower-cased, back-slashes become slashes, a leading drive letter is stripped, and
each segment is stripped of its trailing dot/space run (Windows trims those). Segments are then
classified: exact `""` or `.` is CURRENT and exact `..` is PARENT (unambiguous); every other
all-dot/space segment (`...`, `.. `, `. .`) is AMBIGUOUS, because platforms disagree on whether
it is a parent, the current directory or a literal name. The guard enumerates every assignment
over the ambiguous segments (cap 8, more refuses outright) and refuses if ANY reading:

- contains a `.adversary` segment (clearance / OVERRIDE forgery),
- contains a `skill_gate` segment (skill-gate ledger / OVERRIDE forgery),
- has `.git` immediately followed by `hooks` (the live hook dir).

Accepted over-denies in the deny-on-doubt direction: `.git/../hooks` (resolves outside the hook
dir), and any path with more than eight ambiguous segments. `Read` is never refused.

## The 2026-09-04 arc (docket rows EV-028 to EV-030)

`GUARD_PORTABILITY.md` (2026-09-03) compared the two guards and listed what each lacked. The
owner ordered the Claude Code side implemented. Each claim was re-verified by probe against the
live bytes first; the case-folding item was already true and is recorded as verified-stale. The
three real items (hooks-dir protection, the `-mn` false positive, the variable-built commit word)
landed test-first, and then the gate's own reviews took the hooks-dir rule through seven rounds
across two repos:

1. Redundant path components (`./`, `//`, `..`, trailing dot) passed an adjacency regex and a
   raw-segment adjacency test (EV-028, two rounds).
2. The Caliper port's review, the first that actually received the `.mjs` (EV-029), found the
   `..` test ran before the trailing dot/space strip; the identical order sat in the harness guard
   that had just CLEARed (EV-030).
3. The fix's `startswith("..")` pop threw `.git` away on `.git/.../hooks`.
4. The widened pop reading deleted the state-dir segment while membership checked only that
   reading, and the regex's overlapping alternatives backtracked exponentially.
5. A whole-path all-pop / all-skip pair missed the mixed `x\...\..\hooks`.

Final shape: the enumeration above, in both guards, with every form pinned in both batteries
(harness guard selftest 91 to 148; Caliper battery 10 tests, full suite 351). Lessons, recorded
because they cost seven rounds: canonicalise the way the filesystem does BEFORE comparing; test
every check against every reading, not just the one you added; a single-form timing probe does
not reproduce backtracking, construct the input both alternatives can consume; and a second
reviewer reading a port catches what three rounds on the original did not.

## The twin: Caliper's git-guard.mjs

Same `decide()` shape, same battery rows, one documented divergence: Caliper keeps a
readish/writeish split after the `.git/hooks` trigger (so `ls .git/hooks` passes there), while
the harness guard refuses every reference. Caliper has no state-dir check because the ZCode mount
has no `.adversary` equivalent. Any new rule lands in both in the same change; each battery
imports the other's regression rows. The plugin cache copy that actually runs is re-synced with
`node tools/install-git-guard.mjs` after every guard commit.

## Code-class extensions (EV-029)

The gate and the vendored auditor classify a staged file as code by extension; `.mjs`, `.cjs`,
`.mts` and `.cts` were missing, so an ES-module security guard passed a gate run with a
clearance covering only its test file. Both copies now carry them (the audit selftest's parity
check keeps the two sets identical). Consequences handled the same day:

- every armed repo's vendored `.githooks/adversary_audit.py` was re-vendored with
  `install_gate.py <repo>` and re-audited (eight clean; Caliper reports five commits whose notes
  predate the classification),
- those Caliper commits are backfilled by the OWNER with OVERRIDE-typed notes carrying the full
  file map (`Nexusmill/junk/mjs_backfill_owner_notes.py`, dry-run by default); agents never write
  notes, so this step is not automated,
- the distributed plugin copy of the gate tools in `colibri-marketplace` is synced from Tools
  byte for byte.

## Working with the guard

- A command whose TEXT quotes a guarded string is refused (deny-direction false positive): write
  the text to a file and run the file by path. This applies to commit messages, probes and docs
  appends alike.
- Inspect gate state with `adversary_gate.py status`, never `ls .adversary`.
- Read hooks from the tracked `.githooks/` shim, never from `.git/hooks`.
- The one-shot `.adversary/OVERRIDE` is the owner's alone; an agent creating it is a violation.

## References

- Tools/adversary-gate/harness_guard.py, guard_selftest.py, GUARD_PORTABILITY.md, TOOLS_MANIFEST.md
- Caliper/tools/git-guard.mjs, git-guard.test.ts, install-git-guard.mjs
- docs/gate_evidence.json rows EV-022 (the no-read-exemption doctrine), EV-028, EV-029, EV-030
- docs/LAYERED_ENFORCEMENT.md (layer 2 summary), docs/ADVERSARY_GATE.md (what counts as code)
- Nexusmill docs/remediation_manifest.json rows GUARD-HOOKS-DIR-AND-VAR-COMMIT-BYPASS,
  GATE-CODE-EXTS-ES-MODULES, GUARD-HOOKS-CANONICALISER-AMBIGUOUS-SEGMENTS
