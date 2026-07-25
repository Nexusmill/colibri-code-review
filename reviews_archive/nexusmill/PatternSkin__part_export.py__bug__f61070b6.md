# BUG review: PatternSkin\part_export.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\part_export.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 00:57
- tokens: in 5771 / out 2345
- est cost: $0.0525

---

## Verdict
Not safe to ship as-is: every writer interpolates user-controlled strings (`name`, `colour`, `unit`, `basename`) into XML with no escaping, so crafted input produces corrupt or attacker-influenced 3MF/config files. Secondarily, the documented default format `"3MF"` silently routes to a different writer than the docstring promises, and empty meshes crash with an unhandled numpy error.

## Bugs & vulnerabilities

**[HIGH] XML injection / malformed output via unescaped attributes** - `lines 88-89, 93, 96, 127, 129, 207, 219-225, 242`
- What: `unit`, `name`, `colour`, and `basename` are spliced into XML attributes with plain `%` formatting. No `xml.sax.saxutils.escape`/`quoteattr` anywhere.
- Trigger: a part name like `"><object id="9"` or a basename containing `"`, `<`, `&` (trivially common in file-derived names, e.g. `Benchy "v2" & co`).
- Impact: generated `3dmodel.model` / `model_settings.config` is not well-formed XML → slicer import fails or, worse, parses injected elements. Since names may come from mesh/object names in the host app, this is a real injection sink into a format consumed by third-party software.
- Fix: run all interpolated strings through `xml.sax.saxutils.quoteattr` (or build with `xml.etree.ElementTree`), and validate `colour` against `^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$` before writing `displaycolor`.

**[MEDIUM] Default fmt contradicts docstring — `"3MF"` and `"3MF_BAMBU"` are indistinguishable** - `lines 253-260`
- What: the docstring says fmt `"3MF"` (DEFAULT) writes per-triangle face colours via `write_3mf_facecolor`, but line 259 routes both `"3MF"` and `"3MF_BAMBU"` to `write_3mf_bambu`. The face-color path is only reachable via the undocumented `"3MF_FACECOLOR"`.
- Trigger: calling `export_parts(..., fmt="3MF")` expecting the documented Bambu-Studio-standard face-color file.
- Impact: callers silently get the Bambu-native production-extension package (which fails on meshes with >16 parts — line 169 — while the documented default has no such limit), or get a format PrusaSlicer can't paint-import. Behaviour and docs diverge; the 16-part `ValueError` becomes a surprise on the "default" path.
- Fix: route `"3MF"` → `write_3mf_facecolor` (per docstring) and keep `"3MF_BAMBU"` → `write_3mf_bambu`; update docs if the code is actually intended.

**[MEDIUM] Crash on empty mesh in `write_3mf_bambu`** - `lines 177-178`
- What: `V[:, 0].min()` / `V[:, 2].min()` raise `ValueError: zero-size array to reduction operation` when `V` is empty (possible after upstream filtering, e.g. all triangles unassigned and dropped by the caller).
- Trigger: `export_parts(path, np.zeros((0,3)), np.zeros((0,3),int), np.zeros(0,int), fmt="3MF")`.
- Impact: unhandled exception mid-export; note the zip file at `path` may already be opened/created depending on call site ordering — here the exception fires before the `ZipFile`, so the user just gets a raw traceback instead of a clear error.
- Fix: early `if len(V) == 0 or len(F) == 0: raise ValueError("empty mesh")` (or write an empty-but-valid object).

**[MEDIUM] Negative face indices silently accepted** - `lines 31, 40, 74, 130-134`
- What: `F` is used to index `V` with numpy semantics, so `F == -1` wraps to the last vertex instead of erroring; `_mesh_xml`/`write_3mf_facecolor` then emit `v1="-1"` literally, which is invalid per the 3MF spec, while STL silently exports the wrong geometry.
- Trigger: any upstream mesh routine that uses `-1` as a sentinel (common) leaking into `F`.
- Impact: STL: silently wrong triangles. 3MF: corrupt file rejected by slicers. No error raised in either case.
- Fix: `assert/raise if F.size and (F.min() < 0 or F.max() >= len(V))` in `split_parts`, `write_stl_binary`, `_mesh_xml`, `write_3mf_facecolor`.

**[LOW] All-degenerate Bambu export produces a mesh with 0 triangles but non-zero vertex list** - `lines 189-198`
- What: triangles collapsing at 0.01 mm snapping are skipped, but the object is still written and `kept=0` flows into `face_count="0"`. Some slicers treat a triangle-less `<mesh>` as a parse error rather than an empty object.
- Trigger: mesh smaller than ~0.01 mm in extent (e.g. wrong unit scale upstream).
- Impact: import failure with a confusing slicer error; no diagnostic from this code.
- Fix: if `kept == 0`, raise `ValueError("all triangles degenerate at export precision")`.

**[LOW] STL header/type and count edge cases** - `lines 36, 49-50`
- What: (a) `header[:80].ljust(80, b" ")` raises `TypeError` if a `str` (not `bytes`) header is passed — unguarded public parameter. (b) `struct.pack("<I", m)` overflows for `m > 2**32-1` triangles (unlikely but unguarded). (c) Non-ASCII bytes in header are fine for STL but the module claims "ASCII-only".
- Fix: coerce `header = header.encode("ascii", "replace") if isinstance(header, str) else header`; optionally guard `m < 2**32`.

**[LOW] `write_3mf` `pindex` assumes object order == basematerial order** - `lines 92-96`
- What: correct today (same list iterated in same order), but the coupling is implicit; any future sorting/filtering of one loop but not the other silently mis-assigns colours. Also `displaycolor` is written without the alpha byte (`#RRGGBB` vs spec-preferred `#RRGGBBAA`) — tolerated by most slicers, rejected by strict validators.
- Fix: enumerate once and share the index; append `"FF"` alpha if missing.

## Missing safeguards
- No escaping/validation helper for any XML attribute (single biggest gap — one `quoteattr` wrapper fixes most of the HIGH).
- No validation of `F` bounds (negative / ≥ len(V)) in any entry point.
- No validation of `colour` format; `colours.get(p, "#B0B0B0")` happily passes through garbage strings.
- No empty-mesh guards in `write_3mf_bambu` / `write_3mf_facecolor` / `write_3mf` (the latter two tolerate empties and emit degenerate-but-legal XML; bambu crashes).
- `export_parts` accepts any `fmt` string; unknown values silently fall through to the STL branch (typo `"3mf"` → STL files). Should `raise ValueError` on unrecognised fmt.
- No `NaN`/`inf` check on `V` — `write_stl_binary` would emit NaN vertices/normals silently.
- No tests visible for: XML well-formedness of output (parse with `ElementTree`), round-trip of part→slot mapping, degenerate-triangle filtering count vs `face_count`, and the fmt routing table.