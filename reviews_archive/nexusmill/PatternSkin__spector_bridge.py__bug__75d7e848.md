# Colibri Review - bug (DELTA) - PatternSkin/spector_bridge.py

- **Source path:** `PatternSkin/spector_bridge.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 7
- **sha256 reviewed:** `75d7e848c4baf7a4428a7bf12c42b2a4c3dd0b21c958dbdc28f8034099d7b7b9` (sha8 `75d7e848`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `06c863ca` (2026-07-23 hunt round 1)
- **Delta reviewed:** 2 commits / 92 diff lines: 6d833ebe (`_open`/`_open_obj` honour the returns-None contract and close the connection on failure), 60bbde28 (GLM-POLISH: migration gated behind `_ps_parts_migrated` so reads stay reads; `store_object` DELETE+INSERT under `with db:`) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. `PRAGMA index_list` row[1] is the index name; the one-time dedup migration runs only until the unique index exists; both openers close a half-opened connection before returning None.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/spector_bridge.py

- **Source path:** `PatternSkin/spector_bridge.py` (junction twin identical)
- **sha256 reviewed:** `75d7e848c4baf7a4428a7bf12c42b2a4c3dd0b21c958dbdc28f8034099d7b7b9` (sha8 `75d7e848`, 364 lines)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), colibri G37 FULL bug review
- **Date:** 2026-09-10 - **Mode:** bug, FULL read of the current bytes (owner ruling: the file's pre-gate reviews of 07-20..08-20 are CLAIMS re-verified here, not a baseline)
- **Context pack:** jCodemunch outline (16 functions) + the six `__init__.py` call sites (`_auto_upgrade_companions` 1520, multiview scan 7185/7347, native-3D scan 7883, load-saved-scan 8064, `_ai_spector_recognize` 8080), every one wrapped in `try/except Exception: pass`; `_sel_ctx` (ctx.V is OBJECT-space `me.vertices`, the same space `_ai_spector_recognize` reads - so `geom_sig` compares like with like); `ai_parts.mesh_signature`; `_spector_installed` / `PATTERNSKIN_OT_open_spector` (UI display gate, deliberately NOT `spector_home()`); Spector's own `app.py` (creates `~/.spector` on first run - log dir and library); remediation rows 07-20 (degenerate DNA), 07-23 (PS-1 one transaction, busy timeout + WAL, unique index migration, scan_exists, per-row blob guard), 07-24 (`_open`/`_open_obj` contract + no leak), 08-15 (GLM-POLISH `with db:` in store_object), 08-20 (GROK-SB2); feature PS-SPECTOR-BRIDGE; prior records 06c863ca / 6ff28666 / 75d7e848 + the 07-23 debug record. Note: this module has NO HTTP surface - the Spector app's origin/token guard is exercised only by nothing in Pattern Skin; the bridge talks to a sqlite file it owns.

## Verdict
Clean at the bytes: no confirmed code defect. Every remediation row is present (one connection + one `with db:` transaction in `index_scan` with `store_part(db=)` re-raising sqlite errors so the block rolls back; 5 s busy timeout + WAL; the one-time dedup migration gated on the unique index; per-row `frombuffer` guard; degenerate-DNA refusal on both the stored and the query side; `scan_exists`; both openers honour the returns-None contract and close on failure). No network anywhere; nothing here runs in `draw()`; every entry point is a no-op without `~/.spector`. The bridge is a paid-scan CACHE (a lost row costs a re-scan, never user data), which caps every residual below.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards / staleness (not fixed here)
- Docstring staleness (lines 8-9, 29, 176): "Everything is gated on Spector being installed (free with Pattern Skin)" / "the bundled companion" - Spector has been a separately-sold product since 2026-07-28. The code does not depend on the claim, but a commercial statement in shipped GPL source should not contradict the store. One-line docstring fix (snippets in the summary); no probe warranted.
- `spector_home()` treats a bare `~/.spector` directory as "installed" and creates it when a `spector` module is importable; `PATTERNSKIN_OT_send_to_spector` creates `~/.spector/inbox` even without Spector. From then on every scan pays the DNA cost (an `eigsh` per part, up to 12 parts) to index into a cache nobody reads. Cost only; `_spector_installed` (the UI gate) deliberately does not trust it.
- `shape_dna`'s face-stride decimation above 20 000 faces keys on face ORDER: a re-imported copy of the same model with re-ordered faces samples a different sub-mesh and can miss the match (false negative - the user pays a scan they could have reused). PLAUSIBLE, unverified because it needs two real re-imports.
- `index_scan` DELETEs the prior rows and commits even when every part of the new scan fails to fingerprint (no SciPy, all-degenerate spectra): replace semantics leave an empty index for that mesh. Recoverable by re-scan.
- `ai_parts.spector_home` (line 920) is a duplicate of this module's `spector_home` - two homes for one decision.

## Adversarial verification pass (refuted claims)
- "`geom_sig` mixes world-space scan vertices with object-space pick vertices, so every pick reads `changed_since_scan`" - REFUTED: `_sel_ctx` builds ctx.V from `me.vertices` (object space) and `_ai_spector_recognize` reads the same, so both signatures live in object space.
- "A customer with the installer build of Spector never gets indexing because `spector_home()` only looks at `~/.spector`" - REFUTED: Spector's `app.py` creates `~/.spector` (log dir + `library`) on its first run, so an installed-and-used Spector satisfies the gate.
- "The scale-invariant DNA (`vals / vals[0]`) makes a 10 mm and a 100 mm copy of one part 'the same part', so a wrong scan is auto-loaded" - REFUTED as data loss: `geom_sig` carries the bbox, so the scale twin comes back `changed_since_scan=True` and the caller shows the "model changed since - verify" warning rather than trusting it.
- "An `IndexError` from a mis-sized `tri_labels` inside `index_scan` escapes the `except sqlite3.Error` and leaves the DELETE committed" - REFUTED: the DELETE runs inside `with db:`, which rolls back on ANY exception, and the connection closes in `finally`; the caller swallows the exception.
- "`store_part` swallowing non-sqlite exceptions inside the shared transaction hides a failed part" - REFUTED as a defect: a degenerate spectrum is per-part and expected; the row for that part is simply absent, and `stored` reports the count.
