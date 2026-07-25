# colibri-review — PatternSkin/spector_bridge.py — bug (hunt round 1, effort=low)

- **Source:** PatternSkin/spector_bridge.py · **Scanner:** general-purpose subagent @ claude-haiku
  (low effort) · **Verification:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 06c863ca79404bb505318c3d58e3bda8d66d2c6f7456342eeaa8c8489e621bb7
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (low pass)
- **Context pack:** prior review `PatternSkin__spector_bridge.py__bug__6ff28666.md` (K3) + T2 debug
  note (2026-07-23) + 5 remediation rows — all verified fixed by the scanner and re-confirmed
  (index_scan atomic tx, WAL + lock timeout, ps_parts UNIQUE index, dangling scan_path existence
  check, per-row malformed-DNA guard). Excluded up front.

## Verdict
The scanner's own trace confirmed every prior HIGH/MEDIUM is correctly fixed in current bytes. Its
two new candidates were both refuted on Phase-3 verification: one has no reachable trigger, the
other is documented graceful degradation. No change made. Stays active for a higher-effort round.

## Findings
None confirmed this round.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- **[claimed MEDIUM] no validation of F vertex indices before `shape_dna` → swallowed IndexError**
  (`shape_dna:82`, callers 166/198/306) — REFUTED as unreachable. All six real call sites pass
  in-range geometry: `find_object(_pc.V,_pc.F)` and `index_scan(...,ctx.V,ctx.F,...)` use MeshCtx /
  proxy contexts (selectcore validates index bounds in `__init__`), and `find_part(V[used], rm[Tp])`
  (`__init__.py:5898`) passes a compacted submesh whose indices are `rm[Tp]` remapped into
  `[0,len(used))` by construction. No caller can pass out-of-bounds F; spector_bridge is
  Pattern-Skin-internal (asset-forge never imports it). The `except Exception: return None` swallow
  is documented-intentional for the reachable case (degenerate spectrum → part skipped, not fatal).
  Internal validation gap with no reachable trigger — same class as the selectcore bounds refutation.
- **[claimed LOW/PLAUSIBLE] unique-index migration can silently fail, leaving the constraint
  unenforced** (`spector_bridge.py:149`) — REFUTED as contrived + worse-if-"fixed". The migration
  `DELETE FROM ps_parts WHERE id NOT IN (SELECT MAX(id) … GROUP BY mesh_sig, part_id)` removes all
  but one row per key, so `CREATE UNIQUE INDEX` then succeeds; failure needs the DELETE itself to
  error on an already-corrupt DB. The current log-warning-and-continue is deliberate graceful
  degradation; the proposed fail-fast would refuse to open a recoverable store — worse UX for a
  rare, low-impact condition (a few duplicate rows, slightly non-deterministic best-match).
