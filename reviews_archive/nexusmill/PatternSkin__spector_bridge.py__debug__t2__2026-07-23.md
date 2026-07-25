# Debug/remediation: spector_bridge Tier-2 (K3 top20 triage) — 2026-07-23

Mode: debug (colibri G37, verify-first G35/G36) · Reviewer: Claude Fable (Cowork)
Context pack: K3_FEAT_TOP20_TRIAGE.md item 5 · prior blind review 6ff28666 (K3 2026-07-20) ·
deferred PS-1 · remediation manifest (0 prior rows for this file) · callers via jCodemunch
(__init__.py 5410/5521/5524/5748/5873/5898).

## Verdicts (all traced on CURRENT bytes before fixing)
1. CONFIRMED — index_scan non-atomic + 13 connections/scan (== deferred PS-1; its unblock note
   prescribed the exact fix). Fixed: store_part(db=) shared transaction; one connection.
2. CONFIRMED — locked-DB write silently dropped index rows (debug-level log). Fixed: _connect()
   5s busy timeout + WAL; WARNING logs; atomic rollback.
3. CONFIRMED (latent) — no UNIQUE(mesh_sig,part_id). Fixed: INSERT OR REPLACE + dedupe-then-
   unique-index migration for legacy DBs.
4. CONFIRMED — dangling scan_path: ai_part_pick promised "saved scan available" without isfile
   (prune_cache evicts npz). Fixed: scan_exists in both finders + honest message.
5. SELF-FOUND (by the repro battery) — one malformed DNA blob raised in np.frombuffer inside the
   row loop and silently bricked ALL matching (warehouse b1aaf71 class). Fixed: per-row guard.

## Verified-stale (NOT re-fixed, G11)
The 6ff28666 blind review's degenerate-DNA / zero-query / blob-size findings are already in
current source (raise at shape_dna L94-96; guards in both finders). Recorded, no action.
Also adjudicated: K3 triage Tier-2 "selectcore get_ctx stale-sig collision" = fixed 703fceb.

## Evidence
junk/_spector_bridge_t2_repro.py — 7/7 PASS: upsert-no-dup, legacy-dedupe+index,
atomic-rollback-keeps-old (under a held BEGIN EXCLUSIVE), find_part dangling+bad-blob,
find_part exists, find_object exists, WAL mode. Harness feature PS-SPECTOR-BRIDGE runs the
battery; features tier green.
