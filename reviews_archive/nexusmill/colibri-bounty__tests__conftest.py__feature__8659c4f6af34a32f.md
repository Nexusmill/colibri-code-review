# colibri feature review - colibri-bounty/tests/conftest.py

- source: `colibri-bounty/tests/conftest.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `8659c4f6af34a32f61ecc29774fd873cf628e7e0828ce9ff04773418357a6cc6`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0298 (in=2253 out=4215)

## grok-4.7 output (verbatim)

## What this module does

This file is the suite-wide pytest bootstrap, imported before every test module in `tests/`. On import it inserts the repo root (`Path(__file__).resolve().parents[1]`) at the front of `sys.path` so tests can import the project without an install. It defines no fixtures, markers, or hooks, so corpus location, paid-channel opt-in, and run conditions are not shared anywhere in the suite today.

## Suggested add-ons

- **Value:** High · **Effort:** S · **What:** A session-scoped `corpus_root` fixture (plus a small `require_contest` helper) that resolves `COLIBRI_CORPUS` or the documented default `E:/bounty-corpus`, and skips the requesting test with the missing path or contest id in the reason. · **Why it helps the user:** Replay measurement is only honest if every test sees the same corpus root; a missing drive must show up as an explicit skip, not as a green run that looks like a completed measurement with an empty denominator. · **How:** Add `corpus_root` and `require_contest` next to the existing `sys.path.insert` in `tests/conftest.py`. Do not autouse them — unit tests stay free of the corpus. No new dependencies; pytest fixtures only.

- **Value:** High · **Effort:** S · **What:** A collection gate that skips tests marked `paid` unless an explicit env opt-in is set, so the default suite stays on the free, deterministic `adjudicator=None` path. · **Why it helps the user:** Paid spend is supposed to be strictly opt-in and disclosed. This file is the only hook that sees every test, so the cap belongs here rather than being reimplemented per module — and it does not swallow matcher transport errors or merge agent-tier with union figures. · **How:** Add `pytest_configure` to register the `paid` marker and `pytest_collection_modifyitems` to skip unmarked-as-allowed `paid` items. Leave the path insert as-is.

- **Value:** Med · **Effort:** S · **What:** A one-line run header stating resolved corpus root (or absent), whether the paid opt-in was armed, and how many `paid` items were skipped. · **Why it helps the user:** Precision/recall numbers are only interpretable next to the conditions of the run. A skip summary alone is easy to miss; the header keeps contamination-style disclosure for the harness itself (what was actually measured) without touching tier priority or the always-on contamination column. · **How:** Add `pytest_report_header` in this module, reading the same env vars as `corpus_root` and `pytest_collection_modifyitems`.

## Nice-to-haves

- `pytest_addoption("--corpus")` aliased to the same resolver `corpus_root` uses, so a one-off root does not require an env change.
- Register `corpus` and `slow` markers in `pytest_configure` so intentional skips do not emit unknown-marker warnings.
- `require_contest` skip reason includes the contest id, so a partial corpus is not mistaken for a failed like-for-like denominator.

- ACCEPT session-scoped corpus_root fixture + require_contest skip helper (no autouse) - VERIFIED: conftest is literally 4 lines (sys.path.insert only); no fixture/marker/hook exists; empty-denominator-as-green is the real risk.
- ACCEPT paid-marker collection gate (opt-in env, default free adjudicator=None path).
- ACCEPT pytest_report_header run conditions line (corpus root, paid armed, skipped count).
- DEFER 3 nice-to-haves (--corpus option alias, marker registration, contest-id skip reasons).
