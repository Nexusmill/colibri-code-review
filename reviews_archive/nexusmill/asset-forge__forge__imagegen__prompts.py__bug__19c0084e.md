# colibri gate — asset-forge/forge/imagegen/prompts.py (grok round 5)

- **source:** asset-forge/forge/imagegen/prompts.py
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_prompts_grok43.md) gated in-session by claude-fable-5
- **sha256:** 19c0084e2cfb1f25e065bcb390cb1212c77837227ac7cf073f2ff16c630ae96f (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** bug (grok round 5)
- **context pack:** module role + curation doctrine (look-is-the-spec, identity_guard/colour_locked interplay) + unit-9 verified-stale adjudications pre-declared in the dispatch context file.

## Verdict
CLEAN. Grok-4.3 at high effort returned **no findings** against the pre-declared context
(44 s, in=13438). Nothing to verify, nothing to docket. Fifth consecutive review pass
(after the unit-9 stale adjudication) with no new defect on this file.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - asset-forge/forge/imagegen/prompts.py

- **Source path:** `asset-forge/forge/imagegen/prompts.py` (twin `asset-forge-user/forge/imagegen/prompts.py` byte-identical, G23 - fixes apply to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 22
- **sha256 reviewed:** `19c0084e2cfb1f25e065bcb390cb1212c77837227ac7cf073f2ff16c630ae96f` (sha8 `19c0084e`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the file's prior records - the 2026-08-22 grok r5 CLEAN gate at this same sha, the 08-11 dead-code row - predate the adversarial gate and are untrusted; no delta)
- **Context pack:** jCodemunch outline + importers (imagegen/__init__ re-exports expand_theme/list_moods/MOODS/list_style_presets/is_texture_intent; library_gen calls expand_theme(core, n, ..., randomize=True, library=True, palette_pool, avoid_hints, structures); app.py bundle path passes randomize=bool(params)); the 14 remediation rows and 4 deferred rows naming the file loaded as CLAIMS; feature rows AF-TEXTURE-INTENT, AF-COLOUR-TREATMENT, AF-CONTENT-VARY, MOOD-CYCLE, AF-PROMPT-UPGRADE, AF-COLOUR-VARIANTS; docs/prompt_rules_manifest.json (scan config + rules) and tools/prompt_rules.py check_string run over every live pool; forge/color_hints.json and forge/catalog.json loaded to test the pools against real data. Every one of the 768 lines read.

## Verdict
Shippable after three fixes. The doctrine machinery holds at the bytes: the colour clause is exactly one per prompt (explicit palette > curated pool > hint library minus the subject's prior, floor 8), the subject enters the RNG seed, library/mixed cycle the surface moods with slot 0 plain, colour_locked suppresses both colour axes, the LLM path is gone, and the rules scanner passes clean with the emblem pools as sanctioned exemptions. The defects are all one class - **word tests written as substring tests** - and the first sits on the paid Studio bundle path.

## Bugs & vulnerabilities

**[MEDIUM] is_texture_intent matches its hints as SUBSTRINGS - an emblem theme with 'trusty', 'reptile', 'embark', 'grainy' or 'Yellowstone' in it is routed onto the texture path** - `line 159-163`
- What: `any(h in blob for h in _TEXTURE_HINTS)` over the raw theme+style text. 'rust' is inside 'trusty', 'tile ' inside 'reptile ', 'bark' inside 'embark', 'grain' inside 'grainy', 'stone' inside 'yellowstone'. Reproduced: `expand_theme("trusty knight crest", 1)` -> `"trusty knight crest, fall colors, burnished to a soft sheen, seamless tileable, one continuous surface filling the frame edge to edge"` - no composition, a LIBRARY finish, and the seamless-tile tail on a crest. The same test misses plurals ('hex tiles' is not read as a texture because the hint is 'tile ' with a trailing space).
- Trigger: any Studio bundle whose theme or style text contains one of those words (the bundle path is the only caller with free user text; the library path forces library=True and never depends on the detector - verified identical catalog coverage before and after the fix, 0 lost / 0 gained).
- Impact: a PAID bundle rendered as a seamless surface swatch instead of the emblem set the user asked for; the prompt carries a layout instruction the doctrine bans for emblems.
- Fix: a compiled whole-word regex over the hint list (plural allowed), with the one-word surface compounds 'snakeskin'/'sharkskin' listed explicitly (they matched via the substring before). Battery `probe_af_prompts_1.py` checks A RED (2 of 2 fail on the repo bytes) -> GREEN on the patched copy; the AF-TEXTURE-INTENT feature's examples (pattern/seamless/texture/tileable/bark/marble) still detect.
- Verification: CONFIRMED (traced from `expand_theme` line 609 through `_assignments` comps/fins and `_prompt_line`'s tail; reproduced with the real module).

**[LOW] _strip_concept strips its style words as SUBSTRINGS - 'cleaning' -> 'ing', 'logotype' -> 'type', 'vectors' -> 's' - on the randomize path the library generator ALWAYS takes** - `line 236-242`
- What: `t.replace(w, "")` for each of _STRIP_WORDS. Reproduced: `expand_theme("cleaning brush", 1, randomize=True)[0]` starts with `"ing brush"`. library_gen.py line 254 passes `randomize=True` for every catalog type, and since AF-VIBE-MIXED the ONLY thing randomize still does is this stripping - so two shipped catalog prompts lose a curated word today: industrial_grunge/perforated 'clean round holes' -> ' round holes', abstract_modern/wireframe 'clean rectangular grid' -> ' rectangular grid' (measured over all 153 type prompts).
- Trigger: any theme containing a strip word inside a longer word (bundle, randomize on), and the two catalog types (library, every run).
- Impact: the paid prompt's subject text is silently altered; on the library path a curated content word is removed from the doctrine text the owner edited by hand.
- Fix (this unit): whole-word/phrase regex removal (longer phrases first in the alternation), double spaces collapsed. Battery check B RED -> GREEN. **Companion (library_gen.py line 254, the lead's call):** `randomize=False` on the library call - the curated prompt should not be style-stripped at all; the RNG seed uses `_strip_concept(theme)` regardless, so draws are unchanged. The whole-word fix alone leaves the two catalog prompts still losing 'clean' (measured: 2 altered before, 2 after).
- Verification: CONFIRMED.

**[LOW] subject_class matches geometric words as SUFFIXES - 'reptile', 'textile', 'projectile' class geometric before the organic list is consulted** - `line 419-426`
- What: `t.strip().endswith(w)` for every geometric word: 'reptile'.endswith('tile') is True, so `subject_class("reptile")` returns 'geometric' although 'reptile' is in _ORGANIC_WORDS. Only consumer: the library/mixed mood pool, which bans chaos/elemental for geometric subjects.
- Trigger: a subject whose LAST word ends in a geometric word (reptile, textile, projectile; 'integrate' -> 'grate').
- Impact: those subjects lose the two wildest surface moods - variety, not correctness; low.
- Fix: geometric words match whole words only; organic keeps the suffix test so compounds (snakeskin, sandstone, driftwood) still read organic; 'snake-skin tile' still ties to geometric. Battery check C RED -> GREEN.
- Verification: CONFIRMED.

## Missing safeguards (not fixed)
- The library call's `randomize=True` (library_gen.py:254) has no remaining purpose except the stripping above - see the companion.
- `_prompt_line` joins the user's style text verbatim; sanctioned (the user's own choice on their own key, the same ruling as the explicit palette), noted only so nobody re-flags it.

## Adversarial verification pass (refuted claims)
- "The emblem 'Mixed' vibe cycles TEXTURE moods - surface vocabulary on a crest" - refuted: feature MOOD-CYCLE / AF-VIBE-MIXED states that 'mixed' cycles MOODS_TEXTURE explicitly; by contract.
- "COLOUR_PRIOR_EXCLUSIONS entries may not match color_hints.json text, making the prior exclusion inert" - refuted: all 28 brown and 23 grey entries are present in the 69-hint pool (checked against the JSON).
- "COMPOSITIONS / STYLE_PRESETS / MOODS violate the prompt rules (symmetrical, fine detail, depth of field)" - refuted: docs/prompt_rules_manifest.json lists them as python_exempt_globals with the prior rulings (emblem path; the user's own style choice); `tools/prompt_rules.py` scans 13 files with 0 errors.
- "avoid_hints can empty the palette pool" - refuted: the floor of 8 keeps the full pool when the exclusion would drop below it.
- "palette_pool=[] leaves palettes empty -> modulo by zero" - refuted: a falsy pool falls to the hint branch and `if palettes` guards the modulo.
- "structures shorter than n -> IndexError" - refuted: `structures[i % len(structures)]`.
- "COLOR_HINTS silently falls back to the 9 legacy words on a broken bundle" - refuted: the 2026-08-05 LOUD fallback logs a warning; the fallback itself is the G20 choice.
- "expand_many drops lock_colour/structures - a contract break" - refuted: expand_many is the retired batch shim with no live caller passing those (imagegen/__init__ exports expand_theme only).

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `870495623c3e4ad561b4c33cfbb4759dc01ea910ba219368a513692153fc658e`. Rows AF-PROMPT-TEXTURE-WORDS, AF-PROMPT-STRIP-WORDS, AF-PROMPT-CLASS-SUFFIX in `docs/remediation_manifest.json`, same commit.


---

# DELTA re-review 2026-09-11 (against the 2026-09-10 FULL re-audit above, current bytes)

- **Source path:** `asset-forge/forge/imagegen/prompts.py` (twin `asset-forge-user/forge/imagegen/prompts.py` byte-identical, G23)
- **Reviewer:** claude-sonnet-5 (in-session), Colibri G37 protocol
- **sha256 reviewed:** `870495623c3e4ad561b4c33cfbb4759dc01ea910ba219368a513692153fc658e` (sha8 `87049562`) — the CURRENT, post-fix bytes named in the postscript above
- **Date:** 2026-09-11 · **Mode:** bug, DELTA against the 2026-09-10 full re-audit (same-day fix; not a pre-gate baseline — reviewed properly)
- **Trigger:** Damien's account of the pre-gate prompt-curation work, cross-checked against what's live today; scope requested was prompts.py + colour_forms.py + structure.py + catalog.json.
- **Context pack:** the review above (findings + postscript) loaded as the baseline; `find_importers` (3 callers unchanged: `imagegen/__init__.py`, `forge/library_gen.py`, `tests/harness/probes/af_studio_hints.py`); `forge/library_gen.py:194-258` re-read to confirm `COLOUR_PRIOR_EXCLUSIONS`/`avoid_hints` and `structures=`/`palette_pool=` are still threaded through; the full companion file `forge/imagegen/structure.py` read end-to-end as the direct cross-file dependency for the `structures` slot. Every one of the 784 lines re-read at current bytes.

## Fixed since last review — verified still holding
All three 2026-09-10 fixes were re-traced against the current bytes and hold:
- **AF-PROMPT-TEXTURE-WORDS** (`is_texture_intent` substring match) — `_TEXTURE_RX` is a compiled whole-word regex (`\b(?:...)s?\b`) at lines 159-164. CONFIRMED still fixed.
- **AF-PROMPT-STRIP-WORDS** (`_strip_concept` substring match) — `_STRIP_RX` is a compiled whole-word/phrase regex at line 247. CONFIRMED still fixed.
- **AF-PROMPT-CLASS-SUFFIX** (`subject_class` geometric-suffix false positive) — geometric words now match whole-word only (`" %s " % w in t`), organic keeps the suffix test for compounds. CONFIRMED still fixed at lines 432-443, docstring updated in place documenting the fix. **Correction to my own first-pass draft of this review**: I initially drafted this same code as a new LOW finding ("geometric branch has no suffix match, unlike organic") and even suggested adding suffix-matching back to the geometric branch — that would have REINTRODUCED the exact AF-PROMPT-CLASS-SUFFIX bug this file already fixed (reptile/textile/projectile misclassifying as geometric). Caught before publishing by checking `docs/remediation_manifest.json` + this file's own postscript (G35); no fix applied, no manifest row needed — struck from the findings below.

## Bugs & vulnerabilities (this pass)
**No new CRITICAL/HIGH/MEDIUM/LOW bug found in this file at current bytes.** The three prior fixes hold, and the zero-division/empty-pool guards across `palettes`/`comps`/`fins`/`mood_pool`/`structures` all trace safe (re-verified, same as the 2026-09-10 pass's refuted-claims list).

## Missing safeguards / the finding that actually matters here
**[MEDIUM] `structure.py`'s per-type curation ("Tranche 1") is explicitly incomplete, and nothing flags which catalog types are still running on inferred, unverified family classification** — `structure.py:227-246` (`TYPE_FAMILY`) cross-referenced against `catalog.json` (not yet reviewed)
- What: `structure.py`'s own comment states the authored `TYPE_FORMS` overrides cover "47 types" in "TRANCHE 1" (2026-08-12), selected as "the worst inferred-family errors" found by a worksheet run — and explicitly: *"Remaining candidates are listed in docs/CURATED_DEFAULT_PROMPTS.md for tranche 2."* Every type not in `TYPE_FORMS` or `TYPE_FAMILY` falls through `classify()`'s keyword-hint scan (`_FAMILY_HINTS`), which the SAME comment documents as having been measurably wrong before tranche 1 fixed it ("rose->fibrous, leaves->ridged, tire_tread->masonry" were live errors, corrected by adding explicit entries). Tranche 2 was never executed — no docket, no manifest row, no follow-up commit found for it.
- Trigger: any catalog type NOT in the 47-type `TYPE_FORMS` list and NOT in `TYPE_FAMILY` that the keyword scan classifies wrong today — silently gets a structurally alien 10-phrase pool, exactly the mechanism months of DOCTRINE work eliminated from the composition/finish/palette axes.
- Impact: **this is the concrete, checkable form of what Damien described this session** — "certain patterns have keywords that will always produce duplicates... because forcing non-duplicates becomes less about language and more about the knowledge of the subject matter." The engineering to fix it (per-type authored pools) exists and is proven to work (tranche 1's own before/after measurement); it has not been extended to every type, and there is no registry distinguishing "authored" from "inferred-and-never-checked" types.
- Fix: scoping/content work, not a code defect — enumerate every `catalog.json` type id (both twins byte-identical, so once), for each NOT in `TYPE_FORMS`/`TYPE_FAMILY` record what `classify()` infers today, spot-check a handful the way the tranche-1 worksheet did, and either add a cheap `TYPE_FAMILY` correction or a full authored `TYPE_FORMS` pool. This is exactly the `catalog.json` unit still queued in this session's scope — handed forward rather than duplicated here.
- Safety net gap: `classify()`'s hard fallback to `"formal"` means the system never crashes on an unclassified type, but it also means a wrong family can sit silently forever with no signal. A harness/lint check flagging any catalog type resolving via the `_FAMILY_HINTS` fallback (not `TYPE_FAMILY`, not `TYPE_FORMS`) would surface tranche-2 candidates automatically.

## Cross-file notes (flagged forward to the catalog.json unit)
- `expand_theme(..., library=True)` omits the seamless-tiling tail by design (DOCTRINE-5: `build_plan` appends the catalog's `prompt_suffix`). Cross-file contract: if any `catalog.json` type lacks `prompt_suffix`, that type's library images ship with no tiling instruction. Not verified this pass — catalog.json not yet reviewed.

## Adversarial verification (Phase 3)
- Re-traced all three 2026-09-10 fixes against current bytes line-by-line — CONFIRMED holding, not just present-by-diff.
- Re-traced my own draft `subject_class` finding against `docs/remediation_manifest.json` (AF-PROMPT-CLASS-SUFFIX row) and this file's postscript — REFUTED as a finding (it described the fix, not a defect); removed before publishing rather than shipped as a false positive.
- The tranche-2-incomplete finding was verified by reading `structure.py`'s own comment text verbatim and confirming no later commit/docket closes it (checked `docs/deferred_manifest.json`, `docs/remediation_manifest.json` for STRUCT/TRANCHE/TYPE_FORMS rows — none found for tranche 2 specifically). CONFIRMED as an open, self-documented gap.

**Verdict: shippable, no regression, no new defect. One real open item carried forward to the catalog.json review: tranche-2 per-type structural curation is incomplete and unmonitored.**
