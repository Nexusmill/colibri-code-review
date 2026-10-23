# colibri-review — plugins/adversary-gate (DELTA re-verification of the 2026-09-10 audit)

- **source:** `plugins/adversary-gate/tools/adversary_gate.py` (payload anchor; unit = the whole `plugins/adversary-gate` plugin)
- **model:** claude-opus-5 (in-session)
- **sha256:** `491e57e075ee581375e6ec944064c56b994248fe61f85ffd1d3c20888f82b92f` (adversary_gate.py — UNCHANGED since the 09-10 audit)
- **date:** 2026-09-14T17:49:52+00:00
- **mode:** bug (DELTA against `reaudit/marketplace/summary_marketplace_plugin.json`, session 47f51db8)
- **context pack:** marketplace HEAD f636f4f vs Tools HEAD 6773f97; per-file git-blob freeze table
  (all 8 payload .py blobs == Tools tree at `5cd90e7`, 2026-09-04; 3 hook shims == Tools HEAD);
  `marketplace.json` vs each `plugin.json`; RED probe `probe_marketplace_plugin_1.py` re-run;
  Tools `adversary-gate/` local-import map (what a re-vendor must ship); `owner_ff_merge.py` /
  `owner_setup.py` landing flow (protected main, ff-push of an audited sha).

## Verdict
Payload is still a clean, unmodified Tools snapshot (5cd90e7) — no plugin-specific edits, no
gate-logic defect. Shippable as docs/manifest metadata after this tranche; the payload's
staleness (12 commits behind on the gate, incl. EV-045/046 secret hardening) is an OWNER
RULING (re-vendor / freeze+document / retire), not a unilateral fix.

## Findings re-verified against current bytes (all 5 CONFIRMED still live at f636f4f)
1. **[MEDIUM] marketplace.json version drift** — adversary-gate 0.1.0 vs plugin.json 0.2.0;
   colibri-review 0.2.1 vs 0.2.2. **FIXED this tranche** (`.claude-plugin/marketplace.json`).
2. **[MEDIUM] README Provenance cites `d7d496f`** (README.md:93) for a snapshot whose 8 payload
   blobs all match Tools `5cd90e7` (verified blob-for-blob this pass). **FIXED this tranche.**
3. **[LOW] `--model z-ai/glm-5.2` in README:34/64, SKILL:36/50/78** contradicts the shipped
   `DEFAULT_MODEL = "z-ai/glm-5.3-flash,xai:grok-4.6"` (a fallback chain, `_call_model`;
   identical at Tools HEAD so the doc fix is stable across any ruling). README:34 also attached
   an unsourced per-commit cost figure to the wrong model — replaced with the actual chain and
   the override knobs, no cost figure asserted (G2). **FIXED this tranche.**
4. **[LOW] install_selftest.py:90 unhandled FileNotFoundError** on a machine with machine-wide
   arming active — RED reproduced again (probe exit 1, traceback present). **OPEN — gated on the
   ruling:** fixed upstream by the 09-06..09-09 Tools commits; patching the vendored copy alone
   would fork the snapshot and destroy the "pure unmodified Tools history" property.
5. **[LOW] adversary_gate.py:641 owner-machine fallback path** for `NEXUSMILL_XAI_ENV` — Tools
   HEAD carries the identical default at line 928. **RE-SCOPED upstream (Tools hygiene), not a
   marketplace defect;** patching here alone would diverge from canonical.

## Refuted premises carried forward — do NOT re-raise
- "adversary_gate.py matches no Tools blob" — matches `5cd90e7` exactly (re-confirmed).
- "hardcoded GATE=/PYBIN= in the shims brick a third-party install" — installer substitutes
  GATE=; PYBIN= has a python3/python fallback.
- "gate_selftest's 2 FAILs are a code bug" — honest degraded-mode messaging (docscan.py absent).
- "the plugin wires a bare-python hook row" — plugin.json declares no hooks at all.

## New fact for the ruling (not in the 09-10 record)
Tools HEAD `adversary_gate.py:47` does `import docscan` (optional; absent → docs domain degrades
LOUDLY to the pattern floor, 2 gate_selftest FAILs). `docscan.py` (428 lines, no local imports)
runs a LOCAL model via `llama-cli` — default Qwen3-4B GGUF, ~2.5 GB, env-configurable, CPU or GPU.
A re-vendor at HEAD is therefore either the same 8 files + a permanently degraded docs lane, or
10 files (+`docscan.py`, `docscan_selftest.py`) with a documented optional local-model setup.
The 8-file set at HEAD is otherwise self-contained (sibling references are comments/strings only).

## Ruling options (unchanged from 09-10, restated with the docscan fact)
- **(A) re-vendor from Tools HEAD + bump plugin version** — closes the 28-commit gap (secret
  hardening EV-045/046, push-guard secret refusal, ROOT/attic baseline, machine-wide arming);
  sub-choice: ship docscan.py or not. Fixes #4 for free.
- **(B) keep frozen, document the freeze point + known gaps** — near-zero cost; adopters stay
  silently behind on security fixes.
- **(C) retire the plugin in favour of `install_gate.py <repo>` from a live Tools clone** — no
  vendor lag ever again; loses the one-command `/plugin install` story.

## Repo notes
- `.colibri_reviews/` is gitignored here — this record is local-only by repo policy; the commit
  message carries the ledger for G35.
- Landing flow: main is protected (linear history + `audit` check); side branch → PR → CI audit →
  `owner_ff_merge.py --only marketplace --pr N --head <branch> --apply` (owner step).

## Tranche 2 (same day) — owner ruling A executed: re-vendor from Tools HEAD 6773f97 + docscan
- 14 payload files copied from Tools HEAD COMMITTED blobs (`git cat-file blob`), each re-read and
  git-blob-sha-verified after write; staged blobs re-verified against `HEAD:adversary-gate/<f>`:
  adversary_gate.py 0dcb91f1, adversary_audit.py 46db9046, harness_guard.py 790a21fc,
  install_gate.py 2b614c34, gate_selftest.py 6b98e27b, guard_selftest.py c9f7816b,
  install_selftest.py dcba989b, audit_selftest.py 38270aa2, docscan.py b957bc8b (NEW),
  docscan_selftest.py 3d91b162 (NEW), hooks/{pre-commit d7530414, post-commit 8d14155e,
  pre-push 8269f740, .gitattributes 0bb0c997} (NEW dir - required by the HEAD installer's
  absolute `core.hooksPath` pin; dispatchers tracked 100755 as in Tools).
- Selftests run from the PLUGIN tree on this machine: gate 113/113, install 73/73 (finding #4's
  RED probe now ALL PASS), audit 50/50, guard 231/231, docscan 14/14 (real local model).
- Version 0.2.0 -> 0.3.0 (plugin.json + marketplace.json). README: trust-model bullet now states
  the hooksPath pin + the versioned-plugin-dir re-install caveat (verified on this machine:
  `~/.claude/plugins/cache/<mkt>/<plugin>/<version>/`); real selftest counts; a docs-lane section
  with docscan's env knobs (read from docscan.py:52-82); Provenance -> 6773f97. SKILL: code-class
  list incl. .mjs/.cjs/.mts/.cts + hook names (adversary_gate.py:54-67); "Plain .md passes free"
  replaced by the real docs-lane contract (cmd_check, adversary_gate.py:746-789); unsourced cost
  figure removed; moved/UPDATED-plugin troubleshooting entry.
- Finding #5 (NEXUSMILL_XAI_ENV owner path) intentionally still present - identical at Tools HEAD.
