# Colibri debug record — KokoroBookReader/reader/narration.py

- **Source:** `KokoroBookReader/reader/narration.py` (NarrationStore.__init__ heal + guards)
- **Reviewer:** in-session glm-5.3 (ZCode), colibri-review skill v0.4.0, Phase D debug modality
- **sha256 (reviewed bytes):** `170453f91dd598cab19bb553938023252512c5c57534069187899820da0de9a3`
- **Date:** 2026-09-22
- **Mode:** debug (failure hunt + one gate-forced hardening round)
- **Context pack:** jCodemunch symbol map for NarrationStore + both preview call sites
  (cast_ui.py:384 preview_selected, index_panel.py:104 preview_sample), app.py seeding block
  (voice-references glob + `if label not in store.voices` guard), data_root() legacy-rename
  migration, live on-disk census of `data/narration/narration.json` vs `voice-references/` vs
  `data/narration/voices/`, remediation manifest consulted (round-51 KBR row is adjacent work).

## Failure signal (owner report)
"Review detected cast: only the voice I loaded can be previewed, the libre voices can't."

## Root cause — CONFIRMED (traced end to end on live data)
`NarrationStore` persists `voices: {label: absolute_path}` in narration.json; production
`add_voice` copies each sample to a sha256-named file under `<store_root>/voices/`. The
round-50 relocation moved the data folder (`data_root()` does `legacy.rename(root)`), so the
files landed at `KokoroBookReader/data/narration/voices/` but narration.json kept 42 absolute
paths pointing at the deleted `%LOCALAPPDATA%\KokoroBookReader\...` root. The startup re-seed
guard `if label not in store.voices` sees the labels present (with dead paths) and never
refreshes them. Both preview buttons (review-cast dialog and IndexTTS cast editor) play
`store.voices[profile]` via QMediaPlayer — a dead path fails silently; the only post-move
imported voice (Myne) had a valid path and previewed. IndexTTS synthesis references
(index_client._send → `voices[part["voice"]]`) read the same dead paths, so generation for
stock voices was equally broken.

## Fix (root cause, minimal) + gate round
Round 1: `NarrationStore.__init__` self-heals on load — for each voice whose recorded path is
missing, if the same basename exists under this store's `voices/`, re-point to it (sha256
basenames are content-addressed) and persist best-effort.

Gate round (gate_20260922-115441, glm-5.3-flash, VERDICT: BLOCK — correct catch, no rebuttal):
the loop called `Path(recorded).is_file()` unguarded in the constructor, so a non-string
voices value (TypeError) or a propagated non-ENOENT OSError (deny-ACL / quarantined file /
disconnected volume — `Path.is_file()` only swallows ENOENT-class errors) would abort the
ENTIRE library load, contradicting the fix's own "never aborts startup" claim. Hardened:
`isinstance(recorded, str)` guard + per-entry `except (OSError, ValueError): continue`
(ValueError covers malformed path strings, e.g. embedded NULs).

## Verification
- TDD: `test_moved_library_repairs_voice_sample_paths` — RED against unfixed code (loaded
  store returned the dangling old path; the live failure in miniature), GREEN after the fix;
  a Ghost entry missing everywhere stays untouched.
- TDD: `test_corrupt_voice_entries_cannot_break_library_load` — RED against round-1 code
  (constructor raised TypeError on `Path(123)`), GREEN after hardening; a PermissionError
  from `is_file` (simulated via a Path subclass) skips that entry without aborting the load.
- Suite: 151/151 (`python .venv/Scripts/python.exe -m pytest tests` in KokoroBookReader/).
- Live: owner's real store loaded via the fixed constructor → 43/43 voice paths valid and
  absolute; narration.json on disk re-persisted pointing into the repo data root
  (pre-heal backup junk/kbr_narration_preheal_backup_2026-09-22.json).

## Adversarial pass notes
- Refuted alternative "QMediaPlayer can't decode LibriSpeech wavs": Myne (same pipeline)
  previews; files are standard PCM wavs; the failing variable was path validity alone.
- Heal safety: basename match implies identical content (sha256 naming); no entry is ever
  deleted or invented; cast assignments (labels) are untouched, only paths re-pointed.
- Audio-cache keys derive from voice paths (audio_identity), so healed voices re-synthesize
  once instead of reusing old-path cache entries — one-time cost, correctness preserved.
