# colibri review — birdcam/state.py (delta + security hunt)

- source: `birdcam/state.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 5b2c6126528363b4d33ff245c8976c6f0547f0d7ea849d17dd9b60c8e03db0715
- date: 2026-10-05 03:45
- context pack: prior bug review 01fd844c (hy4, f04d93d — one finding REFUTED + hardening); git
  delta 73225de→c88d8b6 (songs_page field, corrupt-file rotation, state-machine hardening); the
  ROUTED cross-check from the pipeline.py review this session (songs_page persistence); consumers
  pipeline/cli/enricher; the module docstring's own delete-guard invariants.

## Verdict

The state machine is tightly guarded — every deletion transition checks its precondition, and the
takedown-note refusal in retry_batch (298-303) correctly blocks automatic re-upload of deliberately
unpublished videos. The routed songs_page question resolves clean. One new LOW (power-loss
atomicity of the safety-evidence file) and one defensive-input safeguard.

## Fixed since last review / routed checks

- ROUTED CHECK RESOLVED (from pipeline.py review): `BatchRecord.songs_page` is serialized by
  `asdict` (71-72) and restored by the known-field filter (76-77) — it survives restarts between
  enrichment and upload. Not a finding.
- Corrupt-file rotation (99-110, new since last review) verified sound: rename-aside + honest
  StateError describing exactly what evidence is lost.

## Bugs & vulnerabilities (new findings only)

**[LOW] save() rename is not fsync'd — power loss can commit a zero-length state.json over the old file** - `lines 124-126`
- What: `tmp.write_text(...)` then `tmp.replace(self.path)` with no `os.fsync` on the temp file (or
  the directory). On power loss/crash after the rename commits but before the OS flushes the data,
  the filesystem can materialize state.json as zero-length — and because the rename already
  consumed the original, the rotation path then moves an EMPTY file aside and the prior state
  (which clips were already deleted from Blink — the module's core safety evidence) is gone.
- Trigger: power loss / hard crash in the rename window of any save (state.py saves on nearly
  every operation).
- Impact: worst case the store restarts empty; already-deleted-from-Blink clips become
  indistinguishable from new ones (exactly the scenario the rotation error text warns about, but
  with no .bad content left to review).
- Fix: `with open(tmp, "w", ...) as fh: fh.write(payload); fh.flush(); os.fsync(fh.fileno())`
  before the replace (directory fsync optional on Windows).
- CONFIRMED as a path (rename-over semantics verified); the triggering event is rare — LOW.

## Missing safeguards

- `from_json` filters unknown keys but not value TYPES: a hand-edited state.json (an explicitly
  documented owner workflow — retry_batch's own error message says to edit data/state.json by
  hand) with e.g. `members: "abc"` loads fine and crashes later inside pipeline loops. Type
  validation at load (rotate-aside on shape violations, mirroring the JSON-decode path) would make
  hand-editing safe. [LOW]

Adversarial pass: the fsync finding was traced through write→replace semantics (the rotation
cannot rescue a post-rename zero-length file — verified the rotation reads the NEW file's parse
failure only when bytes exist). Transition guards re-verified one by one (143-160, 176-186,
213-235, 238-244, 246-271, 304-336, 338-348). Prior findings not restated.
