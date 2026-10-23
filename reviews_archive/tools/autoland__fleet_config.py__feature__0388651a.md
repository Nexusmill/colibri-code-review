# autoland/fleet_config.py - feature review

source: C:\Users\User\source\repos\Tools\autoland\fleet_config.py
reviewer: in-session GLM-5.3 (ZCode) · sha256: 0388651ab7f3fd9ec951b4d25efaa80e13e06e72eef12f8a84c581b8cd5b0b77 · 2026-10-08 17:46 · mode: feature
context pack: source read this session (ladder parity work, F21); consumer fleet_selftest validate(); CATALOG_URL fetch path at line ~85; sibling BATCH_LADDER owner-ratified 2026-09-22; no prior feature rows.

## What this module does

The fleet's duty-ladder authorization surface: GATE_LADDER (the interactive
review chain, mirroring adversary_gate.DEFAULT_CHAIN) and BATCH_LADDER (queued
scan models), plus `validate()` — the catalog check that refuses any ladder rung
the live OpenRouter catalog does not carry.

## Suggested add-ons

- **Live catalog verification mode** — Value HIGH · Effort M
  What: `validate(ladder, live=True)` (or a `--live` CLI) that fetches
  CATALOG_URL once and reports (a) rungs missing from the live catalog — the
  delisting class — and (b) rungs whose pinned-provider endpoints have vanished
  (via /models/{slug}/endpoints).
  Why: F16/F21 both happened because a config pointed at a model the catalog had
  moved on from; the fixture catalog only proves consistency with a SNAPSHOT.
  The delisted-model failure mode is silent in production (dead-lettered audits).
  How: the authorized fetch already exists for pricing pulls; add an endpoints
  cross-check per rung. Hook: `validate()` + CATALOG_URL fetch.

- **Single-source ladder parity** — Value HIGH · Effort S
  What: expose GATE_LADDER as DERIVED from adversary_gate.DEFAULT_CHAIN
  (pin-stripped) instead of a hand-mirrored tuple, keeping the tuple only as a
  fixture-era fallback; or export a `ladder_from_chain(chain)` helper both
  selftests import.
  Why: F21's root cause is structural — two sources of truth that drift the
  moment either changes; today three files must move in lockstep (chain, ladder,
  two parity assertions).
  How: import adversary_gate from autoland (it already imports it elsewhere in
  the suite) or parse via `_split_entry`. Hook: GATE_LADDER definition.

- **Price-epoch stamp** — Value MED · Effort S
  What: record in the module docstring (or a constant) the date each pin's
  pricing was verified from the endpoints API, and have `validate()` warn when a
  stamp is older than N days.
  Why: the owner rule is per-endpoint live pricing; nothing today records WHEN
  the pins were last price-checked (the 2026-10-08 pins live in comments only).

## Nice-to-haves

A ladder pretty-print (`fleet_config.print_duty()`) for status dashboards; batch
ladder health from the last N receipts (autoland/scan_queue already persists
them); uptime-aware backup ordering note in the docstring.
