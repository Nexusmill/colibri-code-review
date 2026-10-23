# Colibri review — adversary-gate/GATE_TOP_TO_BOTTOM.md (feature)

- Source: C:\Users\User\source\repos\Tools\adversary-gate\GATE_TOP_TO_BOTTOM.md (453 lines, 28166 bytes)
- sha256: 385bcbb2e646a9f474478abbb70c92e2720c9ff282b9fa8a9b1dc04ece43ee40
- Reviewer: tencent/hy4-preview via OpenRouter (universal-tools hy4_review, mode=feature, effort=medium)
- Reviewed at: 2026-10-08 (273 s; in=8364 out=23406; cost ≈ $0.07)
- Mode: feature (owner-commissioned design evaluation: robustness + speed, trade-offs explicit)
- Context pack: the spec itself (written this session from live source, evidence-basis
  sha 89ac3f24… for adversary_gate.py @ HEAD 3f1bde1); the owner's commission verbatim;
  constraints flagged as owner rulings (independence, fail-closed, sha-keyed clearance,
  push barrier, OVERRIDE, one-directional escalation).
- DISCLOSURE: hy4-preview is the gate's own tier-2 escalation model — self-evaluation
  bias possible; no self-serving recommendation detected (its "first change" is a cache;
  its "refuse" choice matches owner doctrine).

## Reviewer output (verbatim)

## 1. VERDICT

The layered architecture is sound and unusually well-reasoned for a commit gate: independence (the reviewer never shares the author's context), a fail-closed spine (every ambiguity — dead chain, truncated verdict, unpersistable artifact, staging drift — refuses), sha-keyed clearance (re-edits self-invalidate), and a detection tripwire (history auditor + push guard) that judges immutable output rather than process. Its strongest points are the $0 deterministic pre-gate (which refuses junk before any paid call), the tiered reviewer with one-directional blind escalation to a strong rung, and the fact that the push barrier and auditor do not care *how* a commit was made — only whether matching evidence exists.

Its weakest point is the local trust boundary: ledgers (`.adversary/**`, `refs/notes/adversary`) are protected from *agents* by harness guards, but the spec explicitly disclaims prevention against a human at a shell, and the git notes themselves are unsigned — so a forged note (or a forged clearance + review artifact) is indistinguishable to the auditor, and the "absence of a note" tripwire never fires because a note is present. Second-weakest is that tier-1 trust is bounded only by a 10% post-hoc sample, so a false CLEAR lands before its contradiction surfaces, and the audit model has no liveness probe (a catalog delisting silently dead-letters the queue).

## 2. ROBUSTNESS holes

**Hole 1 — Unsigned notarization / forged note is trusted by the auditor**
- *What breaks:* The history auditor (`adversary_audit.py` `_audit_commit`) and push guard treat `refs/notes/adversary` as proof. A human at a shell (or an agent that escapes the harness) can `git notes add` a forged note, or forge `.adversary/clearance.json` plus a matching `.adversary/reviews/` artifact; `cmd_record` (adversary_gate.py:3397) will then embed the fake artifact and write a "valid" note. The auditor sees shas that match the commit and classifies it `clean`. The absence tripwire never fires because a note exists.
- *How it happens:* `record` trusts on-disk clearance rows and artifacts; notes are not cryptographically signed or hash-chained. Harness guards deny agents, but the spec says prevention is not claimed against a human at a shell.
- *Fix:* Sign each note (GPG-sign the note payload, or embed an HMAC over the note + prior note hash using a gate-held key) and have `adversary_audit.py` verify the signature/chain. Additionally, `cmd_record` should verify the cited artifact's sha256 matches the on-disk artifact and that the artifact's embedded staged shas match the commit before writing the note. (Additive; does not violate any owner ruling.)

**Hole 2 — >25 MB docs bypass the semantic secret scan**
- *What breaks:* Docs >25 MB are scanned by no layer (§4.5, §14). At push, the secret barrier catches hard literals, but the local docs model (`docscan.py`) does not run on >25 MB files, and the commit-time pattern floor is only a WARN. A soft/prose secret (or a malicious instruction) in a huge doc is not semantically scanned and can be pushed — only hard literals would be caught.
- *How it happens:* `docscan.py` caps at 25 MB; the push guard's docs re-scan inherits the cap. Degraded/capped states are loud but non-blocking for soft hits.
- *Fix:* Chunk >25 MB docs into ≤25 MB segments (or stream them) for the local docs model at commit and push, or at minimum run the commit-time secret pattern floor on them at push as a hard check for soft heuristics too. (Respects the push-barrier ruling; purely additive.)

**Hole 3 — Catalog delisting silently dead-letters the sampled audit (erosion)**
- *What breaks:* The sampled tier-1 audit model (`TIER2_AUDIT_MODEL`) is pinned by name with no liveness probe (§14). When the previous default was delisted, every sampled audit silently dead-lettered. The false-CLEAR measurement silently drops to zero, eroding the only feedback loop on tier-1 trust.
- *How it happens:* `audit-drain` uses the batch API and the pinned model; if the model is delisted, the batch job fails or is never enqueued, and nothing alerts.
- *Fix:* Add a liveness/health probe for `TIER2_AUDIT_MODEL` (and all pinned models) in `fleet_selftest` or as an `audit-drain` precondition: before enqueueing, verify the model is still in the catalog; if not, fail loudly and fall back to a known-good batch model. Also alert on `audit_queue` depth vs drain rate. (Additive.)

**Hole 4 — Stale clearance reuse across rules epochs / model pins**
- *What breaks:* `record` requires a "fresh" CLEAR/WARN row, but clearances are keyed only by blob sha and never expire (§5.10, §12). A blob cleared months ago (before a rules epoch advance or a model/policy change) still matches and is notarized today, bypassing re-review under current rules.
- *How it happens:* `check` clearance match (adversary_gate.py:920) and `cmd_record` compare only sha + verdict; there is no epoch or model-pin binding.
- *Fix:* Stamp clearances with the rules epoch (and model pin/version) at review time; in `check`/`record`, require the clearance's epoch to be >= the current `.githooks/adversary_rules_epoch` (and text epoch) read from HEAD's tree. If the epoch advanced, treat the clearance as stale -> refuse/re-review. (Additive; respects sha-keyed invalidation, adds epoch binding.)

**Hole 5 — Docscan degradation is a fail-open edge for soft secrets**
- *What breaks:* If the local llama model is absent, docscan degrades loudly but effectively passes prose/dictionary secrets to the push barrier (§14). The push barrier only hard-blocks on hard literals, so soft semantic secrets in docs are missed entirely on those machines.
- *How it happens:* `docscan.py` absent model -> no semantic scan; commit warns, push barrier only does hard literals + (absent model degrades loudly).
- *Fix:* Make the absence of the local docs model a hard fail-closed for outgoing doc lines at push (refuse the push, or require owner OVERRIDE) rather than degrade — consistent with the "fail-closed everywhere" ruling. (Additive.)

## 3. SPEED wins (additive, trust spine untouched)

**1. Version-keyed cache for the $0 deterministic pre-gate and AST guards**
- **Value:** Med | **Effort:** S
- **What:** Cache the pass/fail result of the G-A pre-gate (`py_compile` + ruff E9 / biome / `json.loads` / `bash -n`) and `_removed_symbol_callers` (pure-AST removed-symbol scan), keyed by (blob sha, tool version, rules epoch). Store in `.adversary/pregate_cache.json`. On `cmd_run`, skip re-running for blobs with a cached pass.
- **Why it helps:** Rebuttal rounds and re-commits of unchanged blobs re-run the same local checks; this cuts pre-gate latency to near-zero for unchanged files without changing any verdict logic (still fail-closed on cache miss or version change).
- **How:** Extend the deterministic-refusal block in `cmd_run` (adversary_gate.py:1663) and `_removed_symbol_callers`; add a cache lookup before invoking the tools and write results after a pass. Invalidate on tool version bump (record tool versions in the cache key).

**2. Parallelize the independent deterministic pre-gate checks**
- **Value:** Med | **Effort:** S
- **What:** Run `py_compile`, ruff E9, biome, `json.loads`, `bash -n`, and the removed-symbol AST scan concurrently per file (e.g., `concurrent.futures.ThreadPoolExecutor`) instead of sequentially.
- **Why it helps:** These are independent and CPU-bound; concurrency cuts the wall-clock of the $0 pre-gate, which is on the critical path before any paid call. No verdict logic changes.
- **How:** In the G-A pre-gate section of `cmd_run` (adversary_gate.py:1663), wrap the per-file tool invocations in a thread pool; keep the fail-closed aggregation (any failure -> refuse).

**3. Version-keyed cache for local docscan results**
- **Value:** Med | **Effort:** S
- **What:** Cache `docscan.py` semantic scan results keyed by (doc blob sha, vendored model sha/size pin, rules epoch). Skip re-scanning unchanged doc blobs at commit and at push.
- **Why it helps:** The local llama.cpp scan is the slowest local step for doc-heavy commits; caching unchanged blobs cuts commit and push latency. Same model + same bytes -> same result, so no trust change.
- **How:** Extend the docs scan step in `cmd_check` (adversary_gate.py:920) and the push-guard docs re-scan in `cmd_check_push` (adversary_gate.py:3554); add a cache read/write around the `docscan.py` invocation, keyed on the pinned model sha + blob sha.

**4. Overlap the push-guard docs-model scan with the note audit**
- **Value:** Low/Med | **Effort:** S
- **What:** After the hard-literal secret barrier passes, run the outgoing-docs local model scan in parallel with the note audit, then join before allowing the push.
- **Why it helps:** The note audit is local and fast; the docs model is the slow part of the secret barrier. Overlapping them cuts push latency. The hard-literal check still runs first and can refuse immediately.
- **How:** In `cmd_check_push` (adversary_gate.py:3554), after the hard-literal scan, dispatch the docs-model scan to a worker and run the note audit on the main thread; wait for both before the final allow/deny.

**5. Finish replay catch-rate instrumentation to un-gate the local $0 rung as a pre-filter**
- **Value:** High (cost) | **Effort:** M
- **What:** The `local:` Ollama rung exists in code but is not in `GATE_LADDER`, gated on replay catch-rate data (§6, §14). Complete the replay harness to measure its catch-rate; if it proves out, add it as a pre-filter that can only BLOCK/escalate (never CLEAR) before tier-1.
- **Why it helps:** Cuts paid tier-1 calls for obvious junk. (This is a trade-off — see §4.)
- **How:** `replay_local.py` for the measurement; `fleet_config.py` `GATE_LADDER` and `_call_model_ex` (adversary_gate.py:1085) to accept the `local:` prefix. Requires owner ruling to change the ladder.

## 4. TRADE-OFF TABLE

| Proposal | Speed/cost effect | Robustness effect | Recommendation |
|---|---|---|---|
| Add local `local:` Ollama rung to `GATE_LADDER` as a paid-tier replacement / pre-filter | Cuts paid calls & latency ($0, no network) | Risks weaker verdicts (false CLEARs/BLOCKs) if catch-rate is unproven; local model may miss what paid models catch | **Do NOT add to the verdict path** until `replay_local.py` catch-rate data proves parity. If added, restrict to a pre-filter that can only BLOCK/escalate, never CLEAR, and keep paid tier-1 for all CLEARs. (Requires owner ruling.) |
| Widen tier-1 eligibility (payload >40k chars, allow removals / gated prefixes) to avoid tier-2 | Big latency/cost win (more commits clear on cheap flash rung) | Increases false-CLEAR exposure; tier-1 trust is only bounded by a 10% post-hoc sample, so bad CLEARs land before detection | **Refuse.** Keep eligibility strict (`_tier1_eligible`, adversary_gate.py:2052). If forced, pair with 100% sampled audit for the widened class — but that trades cost for robustness, not speed. |
| Cache deterministic pre-gate / docscan results **without** tool+model version in the key | Cuts latency on repeats | Stale cache after a tool/ruff/model update could pass a file the new tool would fail (fail-open) | **Only with version-keyed cache** (blob sha + tool version + model pin + rules epoch). Then no conflict; adopt (see §3.1/§3.3). |
| Lower tier-2 timeout below 600s to fail faster | Lower worst-case latency | More refusals on slow-but-valid strong-model responses (availability down, integrity unchanged/stronger) | Not a trust-spine weakening; it trades availability for latency. Keep 600s (owner's ladder bounds the wedge). If changed, it is an availability trade, not a robustness trade. |
| Make tier-1 BLOCK terminal (skip blind escalation) to save the 600s strong review | Cuts cost/latency on every flag | Violates one-directional escalation + EV-124 (cheap models over-flag); converts cheap-model noise into hard blocks and loses verified findings | **Refuse** (requires owner ruling; recommend against). |

## 5. First change and refused change

**Single change I would make first:** Add a **version-keyed result cache for the $0 deterministic pre-gate, `_removed_symbol_callers`, and `docscan.py`** — keyed by (blob sha, tool version, model pin, rules epoch) and checked in `cmd_run` (adversary_gate.py:1663), `cmd_check` (adversary_gate.py:920), and `cmd_check_push` (adversary_gate.py:3554). It is purely additive, kills the most repeated local latency (rebuttal rounds, re-commits, doc pushes), and with version keying it cannot weaken the fail-closed spine.

**Single change I would refuse to make:** Let the cheap **tier-1 rung issue a terminal BLOCK (or otherwise skip the blind escalation to the strong tier-2)** to save the second review. This violates the one-directional escalation owner ruling and EV-124 (cheap models over-flag); it trades verified findings and fail-closed integrity for latency/cost. It is a "requires owner ruling" proposal, and I recommend against it.

---

## Phase 3 — adversarial verification (in-session GLM-5.3, against live source)

- **Hole 1 (unsigned notes): CONFIRMED with framing correction.** `_audit_commit`
  (adversary_audit.py:228-255) verifies note existence/JSON/sha-match only; notes are
  unsigned. BUT harness_guard BASH_RULES deny agent-side `git notes add|append|copy|
  edit|remove|prune|merge` and `update-ref` (harness_guard.py:147-155), and file-tool
  rules deny `.adversary/**` writes — so the actor class that can forge is exactly the
  disclaimed human-at-shell / harness-escape. Signature/HMAC chaining + artifact-sha
  verification in `record` would upgrade DETECTION for that class. Valid hardening.
- **Hole 2 (>25 MB docs): CONFIRMED at commit time** (cmd_check emits the
  ">25MB - NOT scanned by any layer" warning verbatim); **PLAUSIBLE for the push-side
  inheritance** (_push_secret_audit's size handling not traced end to end this session).
- **Hole 3 (audit-model delisting): CONFIRMED** — the TIER2_AUDIT_MODEL source comment
  documents the real dead-lettering incident (deepseek-v4-pro-0813:batch delisted
  2026-09-22). Nuance: `fleet_selftest`/`validate()` already check ladders against the
  live catalog ON DEMAND; nothing gates `audit-drain` pre-enqueue. The fix is additive.
- **Hole 4 (no epoch binding on clearances): CONFIRMED** — cmd_check/cmd_record compare
  sha + verdict only; no epoch or model-pin field is consulted. Practical exposure is
  bounded (clearances are usually consumed in the same session) but the gap is real.
- **Hole 5 (docscan degrade fail-open for soft secrets): CONFIRMED** (degrade paths
  warn only) — but the proposed hard-fail at push contradicts the owner's EV-046
  loud-degrade ruling; **requires owner ruling**, same class hy4 applied to others.
- **Speed wins 1-4: CONFIRMED ABSENT today** (no result caches exist; `_local_pregate`
  iterates files sequentially; `cmd_check_push` runs the barrier strictly before the
  note audit). All four are additive and preserve fail-closed semantics if keyed as
  proposed. Win 5 (local rung) matches the repo's own standing gate (fleet_config
  comment) and correctly carries a "requires owner ruling" label.
- **Citation accuracy:** every adversary_gate.py line number hy4 cites (920, 1085,
  1663, 2052, 3397, 3554) matches the live source read this session.
- **Bias check:** hy4-preview is the gate's own tier-2 reviewer. It recommended no
  change to its own role, proposed no tier-2 downgrade, and its "refuse" pick protects
  the escalation invariant (owner doctrine). No self-serving pattern detected; treat
  its tier-2-adjacent advice as reviewed-but-vested regardless.

## Remediation queue (owner order 2026-10-08, same session as the evaluation)

**R1 — live hook reviews ran the pre-restructure model chain (REMEDIATED).**
Observed on commit f0d6375: the hook's review executed
`deepseek/deepseek-v4-pro-0813@baidu/fp8+streamlake` — a pin absent from the current
`DEFAULT_CHAIN`. Root cause traced end to end, and it is NOT an environment variable:
no `ADVERSARY_MODEL` exists in the session env, `HKCU\Environment`,
`HKLM\...\Session Manager\Environment`, the hook shims, or any repo config (the
owner's "unpin the env vars" order had no target — recorded so nobody hunts it
again). The real mechanism: the installed dispatchers exec
`$SUITE/.adversary/runtime/launch.py`, which loads the gate from the ACTIVE
CERTIFIED GENERATION named by `adversary-gate/.adversary/runtime/active.json` — and
that pointer was stuck at `e2c4d42` (gate sha `50beccca…`, the pre-restructure
bytes) because every in-hook `activate` deploy failed (R2), so it never advanced
past the four certified generations written today (`fa5c6dd`, `4fce8f3`,
`3f1bde1`, `f0d6375`). Fix applied: `launch.py activate` run OUTSIDE any hook →
active.json = `f0d6375`, active generation's `adversary_gate.py` sha
`89ac3f24…` (byte-identical to the working tree), tier-1 `deepseek-v4.1-flash` and
tier-2 `hy4-preview` pins verified in the active bytes, old `streamlake` pin gone,
launcher executes (`gate status` rc=0). Live reviews now ride the designed ladder.

**R2 — in-hook runtime activation self-deadlocks on Windows (FIXED — see the
remediation close-out below, commit `4eb201b` + `e8482ae`).** `deploy_material` atomically replaces the dispatcher shims
during post-commit's `activate` step; Windows holds the executing
`hooks/post-commit` locked, so `os.replace` fails with WinError 5 on every commit,
activation refuses loudly (previous installation restored — fail-closed as
designed), and the active-generation pointer can NEVER advance from inside a hook.
Consequence: any run of code commits without a manual out-of-hook activation
leaves the live gate silently running an older certified generation — R1 was
exactly this, one full day and four generations deep. Fix directions (one of,
through the gate): (a) activation skips the currently-executing shim file and
defers its swap to a later commit's hook; (b) post-commit schedules a detached
activation to run after the hook process exits (the audit-drain detached-spawn
pattern already exists); (c) minimum viable: `status`/`install_gate --census`
warn loudly whenever HEAD's certified generation differs from `active.json`, so
staleness is visible instead of silent.

## Remediation close-out (2026-10-08, same session, owner order "fix it")

**R2 — FIXED (commit `4eb201b`, Fix-Contract
`docs/plans/2026-10-08-runtime-activate-deadlock.md`).** Deploy layer reworked per
contract direction (a)+(c): dispatcher entries are idempotent (identical bytes
are never rewritten — the every-commit case now touches nothing, so the executing
shim's lock is never contested), a genuinely-changed-but-locked dispatcher defers
to `<runtime>/pending/` and completes at the next install whose context does not
hold it (`complete_pending`, called under the installation lock; still-locked
entries stay pending with a warning), `status` reports pending dispatchers, and
`install_gate --census` now warns when the active generation lags HEAD in
certified bytes (`_runtime_lag`, docs-only drift silent; AMENDMENT: surfaced in
census rather than verify-only, and root resolution is `git rev-parse
--show-toplevel` so relocated suite copies work — both forced by the battery
rows). Evidence: 5 new verdict-named rows in `test_enforcement_runtime.py`
(RED-first: 1 failure + 4 errors on pre-fix bytes), 4 rows in
`install_selftest.py` (RED-first: MISSING → 82/82 PASS), siblings green
(206/206 gate, 40/40 tiering, 19/19 hooks, 50/50 audit, 18/18 fleet, 23/23
callmodel), live lock-tolerance verified on the real runtime (activation rc=0
with an external open handle on `hooks/pre-commit`, no pending written).

**R3 — FIXED (same commit `4eb201b`, owner order mid-session: "max tokens must
be a derivative of payload size"; Fix-Contract
`docs/plans/2026-10-08-output-budget-derivative.md`).** The G-C flat 2000-token
output cap starved every tier-2 reasoning rung on the 132,486-token
catalog-coupled review payload: `finish_reason=length`, 100% reasoning tokens,
zero content — at flat 2000, 8000, AND 16000 (metadata captured; ~$0.16 burned
diagnosing, kimi's empty reply alone cost $0.128). The ceiling is now
payload-derived at every request site (interactive, batch, xAI, local): floor
`ADVERSARY_MAX_TOKENS` (2000) + 15% of the payload's estimated tokens, hard cap
`ADVERSARY_MAX_TOKENS_CAP` (32000). PROOF ON THE LIVE LADDER: with the derived
~21.9k ceiling the default tier chain cleared this very commit — hy4@tencent
starved again, the pin chain advanced, and **hy4@novita returned `VERDICT:
CLEAR` in 14 content bytes**. Battery: `max_tokens_scales_with_payload` +
`max_tokens_capped` rows (RED-first), 40/40 tiering, 206/206 gate.

**Open finding for the owner — RESOLVED OPERATIONALLY by the same-session floor
amendment (see below), ruling optional: `tencent/hy4-preview@tencent/fp8` (the
tier-2 PRIMARY pin) starved at every sub-22k output budget on gate-sized
payloads, while the same model at `novita/fp8` completed at ~21.9k.** The R3
floor amendment (32k floor + payload share ≈ 51.8k on the catalog-coupled
payload) cleared the TENCENT primary first-try on the very next review
(commit `e8482ae`, `VERDICT: CLEAR` in 14 bytes, tier 2) — the starvation was
the budget policy, not the pin. Residual owner option: the dead-attempt tax is
gone at current budgets; revisit only if providers change behavior.
