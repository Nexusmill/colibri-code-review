# Colibri review — adversary-gate/adversary_audit.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\adversary-gate\adversary_audit.py`
- **Model:** claude-fable-5 (in-session)
- **sha256:** `28ebdc7b4162c932308fa70d1c249d57f04ce7d5954cd544fe1fbce03e9426db`
- **Date:** 2026-09-02
- **Mode:** bug
- **Vendored twins:** 10 byte-identical copies total, sha-verified this session (all sha8 `28ebdc7b`): 1 canonical (`adversary-gate/adversary_audit.py`) + 9 vendored `.githooks/adversary_audit.py` in Tools, Nexusmill, colibri-code-review, colibri-marketplace, repo-memory, jcodemunch-mcp, deepagents-quickstarts, 3DPrinting, and Caliper. This one review covers the fleet; any fix must re-vendor to all 9 (install_gate refresh) in the same tranche.
- **Context pack:** jCodemunch outline; G39 layer model (this is L3, "the layer no local trick escapes"); the file's own honest-limits section (forged-note-with-correct-shas is out of scope by design — findings below are NOT that class); audit_selftest asserts CODE_EXTS/GATED_PREFIXES parity with the gate; docstring claims `_changed_code` mirrors `adversary_gate._changed_code_in_commit` exactly, so confirmed diff-layer blindness here presumably exists gate-side too (cross-check owed in the adversary_gate.py unit).
- **Verification:** all findings driven through the real module in throwaway repos (scratchpad `audit_probe.py`). One draft finding (copy-detection C-status smuggle via `diff.renames=copies` config) was REFUTED empirically — the explicit `-M` pins rename-only detection and the modified copy surfaced as `A`, fully audited — and deleted.

## Verdict
The note-verification core is sound (extra note rows harmless, missing/mismatched rows flagged, baseline tracked-and-gated in every armed repo so baseline tampering is self-flagging). But the DIFF layer that decides *what counts as changed code* can be steered around two ways, and one of them ("skip") means the commit is never audited at all.

## Bugs & vulnerabilities

**[HIGH] Replace refs substitute the audited bytes — auditor hashes the replacement, not the real commit** — `_git` line 48-55, used by `_changed_code`/`blob_sha`
- What: every git invocation honors `refs/replace/*` by default. `git replace <dirty> <innocent>` makes `diff`/`show` read the innocent object graph for the dirty sha.
- Trigger: proven in a throwaway repo — after `git replace`, `_changed_code(dirty)` returned the INNOCENT blob's sha256 (probe a).
- Impact: a local agent can notarize/audit-pass a dirty commit by pairing it with an innocent double. Backstop: replace refs do not transfer on default pushes/checkouts, so a fresh-clone CI audit still sees truth — but the local pre-push audit and any working-copy audit are fooled, and `git replace` is not blocked by harness_guard (unit-1 probe E3).
- Fix: run every `_git` call with `GIT_NO_REPLACE_OBJECTS=1` in the environment (one-line env injection in `_git`); mirror the same in adversary_gate.py; add `\breplace\b` to harness_guard's git rules.

**[HIGH] Typechange (`T` status) falls through every branch — the commit isn't even audited** — `_changed_code` line 75-88
- What: the status switch handles A/C/M, R, D only. `T` (e.g. a tracked `.py` becoming a symlink whose target is an ungated `.txt` payload) matches nothing → `files` stays empty → `_audit_commit` returns `skip`.
- Trigger: proven — plumbing-created symlink typechange of `main.py` produced `name-status 'T\tmain.py'` and `_changed_code` returned `[]` (probe c).
- Impact: a code file's content can be redirected wholesale in a commit the auditor classifies as "no code changed"; the mirrored gate-side `_changed_code_in_commit` presumably skips review of it the same way. Platform note: symlink materialization matters most on Linux checkouts (CI), which is exactly where the payload would resolve.
- Fix: treat `T` as change: hash the blob at `rev` (like ACM). Consider whether mode-only changes and `U` deserve handling while in there; add an audit_selftest row per the parity tripwire.

## Missing safeguards
- CODE_EXTS is extension-allowlist-only: a payload parked in `.txt`/`.md`/extensionless files is ungated by policy. Recorded design, but the T-finding shows how a gated name can be pointed at an ungated body — worth an owner-level think, not a drop-in fix.
- `blob_sha` raises `SystemExit` mid-walk on any `git show` failure — one unreadable path aborts the whole audit run rather than reporting a violation row for that path. Low, robustness only.

## Verified clean (checked, no finding)
- Extra rows in a note are ignored (only changed paths are demanded) — harmless by design.
- Merge/evil-merge handling: `rev-list` walks all parents' commits and first-parent diffing surfaces evil-merge content as needing its own note.
- `.githooks/adversary_baseline` is a TRACKED file in Tools, repo-memory, and colibri-code-review — editing it is itself a gated `.githooks/` code change, so baseline tampering self-flags.
