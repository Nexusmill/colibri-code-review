# Colibri review - atlas/services/asset_validator.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\asset_validator.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__asset_validator.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `e833eaa7cedea65965e323583baa08ff3704d5fc8a103ca2369de75fc0fb1e4e` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `get_file_outline` (21 symbols); `get_symbol_source` validate_file (142-245) + _get_file_info (247-296); `find_importers`: only `atlas/services/__init__.py` (which itself has ZERO importers - the whole services layer is unwired: absence evidence via find_importers on 7 files); rows: FLEET-P0-SERVICES-TEMPFILE-HYGIENE; fork probe re-run today: RED (both checks).

## Verdict
The fork's HIGH (it had left it PLAUSIBLE, unre-verified) is now CONFIRMED by trace and by the re-run probe: `_get_file_info` writes `tmp.write(file_obj.read())` (line 291) for any file-like object BEFORE `validate_file` compares `file_size` (line 191), and `file_size` is the client-declared `.size` attribute when present (line 271) - a 5 MB upload declaring `.size=10` was written to disk in full and accepted VALID. The MIME check trusts `.type`/the filename (line 311) and never inspects bytes. Costs nothing today: the services layer has no importer outside itself; Phase 3 carries and rewires it. Docketed.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] size guard runs AFTER the unbounded temp write and trusts the client-declared size - CONFIRMED (trace + probe RED), DOCKETED - `line 271, 291 -> 191`
### [MEDIUM] type validation trusts client-declared MIME/filename, never the bytes - CONFIRMED (probe RED), DOCKETED - `line 311`
- Disposition: deferred row `FLEET-P0-ASSET-VALIDATOR-TRUSTS-CLIENT` (fix shape for the rewrite: cap the read at `max_file_size + 1` bytes and size from the bytes actually read; sniff magic bytes for the asset type).
### [LOW] `delete=False` temp never unlinked - verified-present, already `FLEET-P0-SERVICES-TEMPFILE-HYGIENE` (row amended: re-verified 2026-09-15).

## Adversarial pass
- `validate_file`'s `except Exception` wraps everything, so no crash path - the defect is acceptance, not a raise. The Streamlit `UploadedFile` is the only producer of `.size`/`.type` today and Streamlit sizes honestly; the exposure is any future caller passing an arbitrary file-like - which is why it is a Phase 3 hardening row, not a live cost.
