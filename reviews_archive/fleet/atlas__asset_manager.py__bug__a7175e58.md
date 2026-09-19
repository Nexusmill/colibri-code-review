# Colibri review - atlas/asset_manager.py (bug, lead Phase-3 verification + remediation)

- source: `C:\Users\User\source\repos\fleet\atlas\asset_manager.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report under `_external_raw/` is INPUT)
- sha256 reviewed: `a7175e5848cf0c4e4a063b9aef58f0ed9e2870961fb738dbdc4b5c2a6fdc8a0e` (417 lines, CRLF; identical to the bytes the fork reviewed)
- sha256 after remediation: `024b4fe2d90070566c375dd59ad46691be88725b7c009949f48f36e7b306592f`
- date: 2026-09-15
- mode: bug (Phase 3 lead pass over the 2026-09-10 re-audit's claims, then TDD remediation in the same tranche)
- context pack: `get_file_outline` (AssetManager, 9 methods); `get_symbol_source` on `__init__`, `gcs_client`, `_upload_to_gcs`, `_get_storage_path`, `save_asset`; `search_text` for every `save_asset(` call and `extension=` argument in the repo (cinematographer x5 with no extension -> type default; composer "wav"/"mp3"; research "html" - all literals); `_get_storage_path` has no caller but `save_asset`; the fork's review + RED probe; no manifest row names this file.

## Verdict
The fork's MEDIUM held: `save_asset` turned an unvalidated `extension` into a storage FOLDER, and an absolute value escaped `base_dir` (directory creation reproduced; the content write failed on the resulting invalid filename, as the fork said). Not reachable from today's literal callers, but a public parameter of the class every agent imports, and content-type-derived extensions are exactly the Phase 3 provider-adapter pattern - fixed as a missing safeguard while the RED run also surfaced a real crash in the same path (below). Fork's refutation (title traversal) stands; its LOW (`save_text_document` `subdir`) recorded, not fixed.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [MEDIUM] `extension` escapes `base_dir` through `os.path.join` - CONFIRMED (directory creation), FIXED - `line 210-212, 121-129` (pre-fix)
- What: `extension = extension.replace(".", "")` was the only cleaning; `_get_storage_path` then did `os.path.join(category, subcategory, extension)` and `os.makedirs` - `join` discards every earlier component when a later one is absolute.
- Trigger (traced, reproduced RED): `save_asset(..., extension="C:\\...\\outside\\escaped")` -> `_get_storage_path` returns the absolute path verbatim and creates it outside `base_dir`; the file write then fails (`Errno 22`, the filename embeds the path) - so a full content write was NOT proven, matching the fork. A UNC value that completes the write was not tested (needs a listener) - PLAUSIBLE, unverified.
- Also surfaced by the RED run (new, CONFIRMED): a traversal-shaped extension (`../../evil`) raised `FileNotFoundError` OUT of `save_asset` - `_get_storage_path`'s `makedirs` runs before the method's `try`, so the caller crashed instead of getting `None`.
- Fix applied: after dot-stripping, the extension must be a bare token `[A-Za-z0-9_-]{1,12}`; anything else logs an error and returns `None` (the method's existing failure shape) BEFORE any path is built - refuse, never rewrite to another extension (the fork's fallback-to-`bin` substitution was rejected). `import re` added.
- Tests: `tests/test_asset_manager_extension_guard.py` - 7 refused shapes (absolute path, parent, traversal, separator, backslash, dots-only, over-long) each returning `None` with NOTHING created under or outside `base_dir` (all 7 RED before), plus 2 accepted shapes (".wav" saved under `Audio/Music/wav/`, omitted extension -> type default). Suite 62 passed.
- Manifest: remediation `FLEET-ASSET-EXTENSION-ESCAPE`.

### [LOW] `save_text_document(subdir=...)` joins an unsanitized `subdir` the same way - CONFIRMED (static), NOT FIXED
Both callers use the default `"Reports"`; unreachable today. Recorded here for the Phase 3 rewrite of this class (no separate deferred row: it is the same class as the fixed finding and the fix pattern is the one applied above).

## Adversarial pass
- Fork refutation re-checked: `save_text_document`'s `clean_title` strips everything but `[A-Za-z0-9 _-]`, so a traversal title cannot survive into the join. Stands.
- The URL-download branch of `save_asset` (`requests.get(data, stream=True)` on a provider FileOutput / URL) has no size cap and no address check: the URL comes from the media provider's API response (Replicate output), not from the LLM, and media files are legitimately large - noted as a Phase 3 provider-adapter item, not a defect here.
- The 12-char ceiling admits every real media extension in the repo (`png mp4 wav mp3 html md jpeg webm json`); an over-long value is refused loudly, not truncated.

## Files
- `atlas/asset_manager.py` (+9/-1), `tests/test_asset_manager_extension_guard.py` (new), `docs/remediation_manifest.json` (+1 row, +1 source), this record + `_external_raw/atlas__asset_manager.py__fork-2026-09-10.md`.
