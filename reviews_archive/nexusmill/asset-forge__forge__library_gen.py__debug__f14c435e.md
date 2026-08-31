# Debug: "a great many near duplicates" in a generated fantasy/sci-fi library set

- Source: asset-forge/forge/library_gen.py (+ asset-forge/forge/imagegen/prompts.py, asset-forge/forge/catalog.json, docs/deferred_manifest.json, docs/research/KLEIN_ALTERNATIVES_2026-08-03.md)
- Model: claude-sonnet-5 (in-session)
- sha256 (library_gen.py): f14c435e...
- sha256 (imagegen/prompts.py): eba5a5d1...
- Date: 2026-08-09
- Mode: debug
- Context pack: catalog.json's `fantasy_scifi` pack (7 types, single core prompt each);
  `_expand_prompts`/`expand_theme`/`_assignments`/`_prompt_line` read end to end (the
  library-regime prompt-variety engine: colour-hint cycling, mood cycling, finish
  cycling, composition intentionally flattened per DOCTRINE-2); the ACTUAL job that
  produced Damien's output read directly from
  `C:\Users\User\Documents\AssetForge\library\.af_jobs\20260809_183220_fc438cc4e9\
  LIBRARY.manifest.json` (48 items, model `flux-2-klein-4b`); `docs/deferred_manifest.json`
  entries PROMPT-REWRITE-V3 and LIB-RESHIP-NB2; `docs/research/KLEIN_ALTERNATIVES_2026-08-03.md`.
  Damien's report: "a great many near duplicates... i thought the forge and library had
  been cleansed... audit the prompts and make sure all the selectable options are
  employed."

## Hypothesis ledger

1. A selectable variety axis (palette/mood/finish) isn't actually wired into the prompt
   sent to the model - **checked directly against the real job's LIBRARY.manifest.json**:
   REFUTED. Every one of the 42 fantasy_scifi items in this job carries a genuinely
   different colour-hint clause ("spring colors" / "aged patina colors" / "jewel tones" /
   "deep sea colors" / ...) AND a genuinely different mood/finish clause ("waxed and
   polished" / "blackened and corroded, deep shadowed pitting, sinister worn surface" /
   "chalky and matte, pale luminous tonality..."). `_assignments()` shuffles and cycles
   `COLOR_HINTS` (72-hint library, confirmed loaded - `color_hints.json` present in both
   source and the compiled dist's `_internal/forge/`) and `MOODS_TEXTURE` per item exactly
   as designed. The engine is correctly varying every axis it has.
2. `_expand_prompts`'s silent `except Exception: pass` around `expand_theme()` (library_gen.py
   line ~199) is swallowing an error and falling back to the much weaker `_variation()`
   fallback (2 short clauses, no logging at all - unlike `_load_color_hints`'s LOUD
   fallback) - **checked**: REFUTED for this run specifically (the manifest prompts match
   the rich `expand_theme` shape, not the crude fallback shape). Still a real
   observability gap worth fixing on its own merits (see below), just not what happened
   here.
3. **The CORE subject text is 100% identical across all 6 draws of a type, by design**
   (catalog.json gives each fantasy_scifi type exactly ONE prompt string; only the
   colour/mood/finish suffix varies) - **confirmed**, and this is where the real problem
   lives: `docs/deferred_manifest.json`'s PROMPT-REWRITE-V3 docket (2026-08-03/04)
   explicitly measured that colour-only variation is insufficient once a specific model
   is involved: "6-slot real-variant tables for all 59 types (each slot a different
   nameable object - **the only variety lever under klein's per-prompt diversity
   collapse**)". That variant-table work was scoped but never delivered (not listed among
   the docket's two carried-forward sub-items on closure) - it fell through a process
   crack rather than being explicitly dropped.
4. **The job used `flux-2-klein-4b`** - CONFIRMED as the actual root cause. This is a
   documented, already-researched limitation (`docs/research/KLEIN_ALTERNATIVES_2026-08-03.md`):
   klein is 4-step distilled for its ~$0.001/image cost, and that same distillation
   causes prompt-diversity collapse - different colour/mood suffixes on an otherwise
   identical prompt still converge toward similar-looking output. This is EXACTLY why
   `catalog.json`'s `defaults.model` is `"nano-banana-2"`, not klein - docket
   **LIB-RESHIP-NB2** records the deliberate move away from klein for the shipped default
   library for this reason ("the model decision is made (nano-banana-2, $0.07/image
   billed-verified)... The library customers receive is still the klein-era V2 content").
   klein-4b is still selectable in the model dropdown (cheapest option), and nothing in
   the UI warns that picking it for a multi-draw catalog run reintroduces the exact
   collapse the team already moved away from by default.

## Verdict

**No code defect in the prompt-variety engine** - it is correctly wired and was
correctly used for this job. The near-duplicates are the known klein-4b diversity-collapse
limitation, triggered because this run manually selected klein-4b (not the current
default, nano-banana-2) - most likely for its near-zero cost, without the model-choice
consequence being visible at selection time. "The forge and library had been cleansed"
refers to the 2026-08-03/04 prompt-TEXT doctrine cleanup (106 rule violations -> 0) and
the 2026-08-07 file-dedup pass over EXISTING library content; neither of those changes
model behavior at generation time, so a new run on klein can still reproduce this.

Two real, still-open gaps surfaced (not fixed here - product/UX decisions, not blind
code fixes):
- No UI signal when a user selects klein-4b for a multi-draw run, despite the team
  having already moved the shipped default away from it for exactly this reason.
- `_expand_prompts`'s silent `except: pass` (library_gen.py) has zero logging, unlike the
  `_load_color_hints` fallback it sits next to - a genuine `expand_theme` failure on some
  future catalog entry would be invisible the same way this symptom initially looked.

## Fixed since last review

N/A - first review of this file/symptom.
