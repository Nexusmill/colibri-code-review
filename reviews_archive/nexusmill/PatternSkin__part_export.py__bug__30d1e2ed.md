# colibri-review — PatternSkin/part_export.py — bug (hunt round 1, effort=high)

- **Source:** PatternSkin/part_export.py · **Scanner:** general-purpose subagent @ claude-opus
  (deep effort) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 30d1e2ed0de8ea71cbfcc75669bffc7f0f50ed57f0ae4bb63348cd5a92a6906c (281 lines)
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (deep pass)
- **Context pack:** prior review `PatternSkin__part_export.py__bug__f61070b6.md` (K3) + remediation
  rows — every prior HIGH/MEDIUM (XML injection, empty-mesh, missing `_check_geometry`, negative
  indices, NaN vertices, unknown-fmt fallthrough) verified FIXED in current bytes, excluded up front.
  Sole in-tree caller `filmstrip.py:466` (`PATTERNSKIN_OT_export_parts`) verified: passes finite
  world-space geometry, sanitised basename, enum-checked fmt — no caller-contract break.

## Verdict
No HIGH/MEDIUM defects survive. The delta since the prior review closed the injection/validation
class properly. What remained were three LOW file-write-robustness gaps (all in the write tail) and
one stale docstring — all fixed this round.

## Bugs & vulnerabilities (all CONFIRMED, all fixed)

**[LOW] Non-atomic writes clobber a prior good export with a truncated file on IO failure** - `write_stl_binary:78`, `write_3mf:135`, `write_3mf_facecolor:170`, `write_3mf_bambu:281`
- What: each writer opened the destination directly (`open(path,"wb")` / `zipfile.ZipFile(path,"w")`).
  Geometry validation runs before the handle opens (so bad DATA never produces a partial file), but
  a disk-full / permission / interrupted-write error inside the `with` block leaves a partial file
  that has already overwritten any prior good file of the same name.
- Trigger: disk full, network-path drop, or process kill during the final serialize step.
- Impact: the user's previously-good export is destroyed and replaced with an unopenable file.
- Fix: shared `_atomic_finalize(path, write_into)` — write to `path + ".pstmp"` (with `fsync` on the
  STL handle), then `os.replace()` onto the target (atomic on one volume); temp removed on any
  failure. Matches G30 fail-closed write doctrine.

**[LOW] STL fan-out orphans partial files on a mid-loop failure** - `export_parts:307-312`
- What: the `STL` branch writes one file per part; if part N raised, parts `0..N-1` stayed on disk,
  a partial set posing as complete.
- Trigger: verified by execution — a part with a NaN vertex after a good part left `fan_part0.stl`
  on disk (pre-fix). Not reachable from the operator (finite geometry only); bites direct/IO-error
  callers.
- Fix: wrap the loop; unlink every written path on exception, then re-raise.

**[INFO] `export_parts` docstring mislabeled the `'3MF'` default** - `export_parts:292`
- What: docstring said `'3MF'` writes per-TRIANGLE face colours; code routes `'3MF'` →
  `write_3mf_bambu` (native paint-slot project). The spec face-colour writer is `'3MF_FACECOLOR'`.
  Operator enum labels were already correct — doc-only drift. Fixed the docstring.

## Deferred (recorded in `docs/deferred_manifest.json`, not fixed)
- STL fan-out overwrites derived `_partN.stl` names the file dialog never confirmed. Standard
  per-part-exporter behaviour; changing it (existence prompt / uniquified subfolder) is a product/UX
  decision, so deferred rather than silently changed.

## Verify
`junk/_partexport_test.py` 8/8 PASS against the real bytes (module is pure-numpy, imports
headlessly). The fan-out orphan check is the true regression discriminator: it FAILS on the pre-fix
bytes (`fan_part0.stl` left behind) and PASSES after. The single-file atomic writes are verified
functional (all formats write via the tmp→replace path, no `.pstmp` leak); the IO-failure-mid-write
clobber scenario isn't directly triggered by the test (its induced failures occur at validation,
before the open) — the protection is inherent to `os.replace`. NOT exercised in a live Blender
session.

## Refuted during verification (deep scan self-refuted; recorded in `_refuted_ledger.json`)
- `_PAINT_CODES[slot]` off-by-one — 1-based slot indexing is correct by design (comment at :180);
  a prior review's false positive.
- `struct.pack("<I", m)` overflow / native-endian `rec.tobytes()` — overflow needs >4.29B
  triangles; endianness only wrong on a big-endian host (no real target).
- Degeneracy filter (0.01 mm snap) vs `%.2f`-written vertices shipping a collapsed triangle —
  refuted by a 20,000-case probe: 0 kept-but-collapsed triangles.
- `slot[int(p)]` KeyError / `_PAINT_CODES` overflow — `slot` is built from `np.unique(tri_part)` so
  covers every part; >16 parts guarded; max index 16 within the len-17 table.
