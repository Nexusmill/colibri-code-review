# Content review: `asset-forge/forge/catalog.json`

- **Source path:** `asset-forge/forge/catalog.json` (creator edition, canonical)
- **Reviewer:** claude-sonnet-5 (in-session), Colibri G37 protocol
- **sha256:** `7b04f1f28f822159737def7005615ddb034376ef24ccb1df3b48d3bf0a7247f0` (sha8 `7b04f1f2`)
- **Date:** 2026-09-11 · **Mode:** content/quality (this is data, not code — no prior
  colibri review of any mode exists for this file; first review, ever)
- **Twin parity:** `asset-forge-user/forge/catalog.json` verified byte-identical (G23).
- **Context pack:** loaded and cross-referenced programmatically (not just read as text)
  against `structure.py`'s `TYPE_FORMS`/`TYPE_FAMILY`/`classify()` (this session's earlier
  full re-audit) and `colour_forms.py`'s `colour_variants`/`colour_axes` contract (this
  session's full re-audit); `forge/library_gen.py`'s consumption of `defaults`,
  `prompt_suffix`, `height_hint` re-checked at the call sites already identified in the
  `prompts.py`/`colour_forms.py` reviews.

## Summary

153 types across 12 packs. Structurally clean — no malformed entries, no duplicate ids
within a pack, `prompt_suffix`/`height_hint` are genuinely global (applied to every type
uniformly; there is no per-type override field at all, so the cross-file concern raised in
this session's `prompts.py` review — "if any type lacks `prompt_suffix`..." — is now
**resolved as moot**: no type can lack it, there is nowhere to omit it from).

## The finding this session was launched to find: Tranche 2, quantified

`structure.py`'s own comment documents 47 catalog types as hand-authored "Tranche 1"
(2026-08-12) and explicitly defers the rest: *"Remaining candidates are listed in
docs/CURATED_DEFAULT_PROMPTS.md for tranche 2."* Cross-referencing all 153 catalog type
ids against `TYPE_FORMS` (47) ∪ `TYPE_FAMILY` (76, overlapping with TYPE_FORMS) against
the LIVE module:

- **79 of 153 types (51.6%) have no authored entry at all** and resolve purely through
  `classify()`'s keyword-hint inference — Tranche 2 was never executed.
- Of those 79: **19 land on the `"formal"` fallback with no hint matching at all**
  (aboriginal_dot, rangoli, batik, art_deco, memphis, scallop, quilted, cracked, dot_grip,
  stipple, geode, snowflake, christmas_tree, hearts, halloween, waves, dot_gradient, noise,
  bauhaus) — mostly plausible by luck, since `"formal"` is a reasonable default for a
  designed/geometric pattern with no strong material signal.
- The remaining **60 land on an ACTIVELY-matched family** via a specific hint word. I
  traced which word triggered each one (not just which family it landed in) and spot-checked
  each against the type's actual prompt text, the way the tranche-1 worksheet is described as
  having done.

## A confirmed, systematic misclassification pattern (not isolated cases)

**`_FAMILY_HINTS` has NO active keyword entries for `"formal"` at all** — it is the
`classify()` return value ONLY when every other family's hints fail to match. This means
any type whose prompt names a carving/craft MATERIAL word ("carved in stone", "carved in
wood", quilt "block") gets swept into a material family (masonry/fibrous/etc.) before
`"formal"` is ever considered — **even when the type's actual FORM is a textbook match for
`FAMILY_FORMS["formal"]`'s own vocabulary** (which literally includes "stepped fret
motifs", "quatrefoil openwork", "diamond lozenge fields", "spoked wheel motifs", "banded
stripe divisions" — architectural/geometric-motif language). Concrete, checkable cases,
triggered by the exact words shown:

| Type | Landed on | Triggered by | Actual form (from its own prompt) | Better fit |
|---|---|---|---|---|
| `aztec` | masonry | "stone" | step-fret meander | **formal** ("stepped fret motifs" is a literal FAMILY_FORMS phrase) |
| `greek_key` | masonry | "stone" | key/meander bands | **formal** (same as aztec) |
| `islamic` | masonry | "stone" | girih star-polygon tiling | **formal** ("diamond lozenge fields", "spoked wheel motifs") |
| `sacred_geo` | masonry | "stone" | flower-of-life overlapping circles | **formal** ("quatrefoil openwork", "interlaced knotwork") |
| `penrose` | masonry | "stone" | rhombus tiling | **formal** ("diamond lozenge fields" — literal match) |
| `gothic` | masonry | "stone" | cathedral tracery | **formal** ("quatrefoil openwork" is architecturally exact) |
| `mandala` | fibrous | "wood" | radial rings of petals/beads | **formal** ("spoked wheel motifs") — fibrous (wood-grain/fur vocabulary) fits worst of all options |
| `barn_quilt` | masonry | "block" (from "quilt BLOCK") | painted geometric patchwork design | **formal** ("diamond lozenge fields", "banded stripe divisions") — "block" here is quilting terminology, not masonry |
| `shibori` | woven | "cloth" | tied-and-dyed rings/puckering | **cellular** ("nested ring cells", "rounded bubble cells") fits the described rings far better than woven's strand-crossing vocabulary |

**Correction (caught by the adversary gate's factual re-check, 2026-09-11):** the "`formal` has no active hints" mechanism explains 8 of these 9 cases, NOT shibori. Shibori's better fit is `cellular`, which DOES have active hints (`"honeycomb"`, `"hex"`, `"cell"`, `"bubble"`, `"foam"`, `"pore"`, `"coral"`) - none of which appear in shibori's own prompt text ("kanoko rings of tied circles, puckered"), so the earlier-checked `"woven"` family (hint: "cloth") wins by iteration order, not by `formal`'s total hint-void. Both are instances of the same broader problem - first-match ordering picking a materially-plausible-but-structurally-wrong family over a better fit - via two distinct specific routes, not one shared root cause as originally stated.

By contrast, cases where the hint word is a genuine, intentional match were also checked
and are correctly classified: `maori`→ridged (prompt literally says "spiral ribs"),
`op_art`→ridged ("parallel ribs"), `candy_cane`→ridged ("raised helical ribs"),
`tread_grip`→ridged ("raised abrasive ribs") — the mechanism works fine when the hint word
is actually descriptive of the form, not incidental material flavour text.

**This is the concrete, checkable version of what was reported this session**: "certain
patterns have keywords that will always produce duplicates... because forcing
non-duplicates becomes less about language and more about the knowledge of the subject
matter." At minimum the 9 types above are running on a structurally-alien 10-phrase pool
today (masonry's cut-block/cobble vocabulary applied to interlocking geometric motifs, or
fibrous wood-grain vocabulary applied to a radial mandala) — exactly the mismatch class
Tranche 1 was created to eliminate, just not yet extended to these types.

## Colour coverage (secondary check, `colour_forms.py` contract)

46 of 153 types declare `colour_variants`/`colour_axes` (curated colour); the other 107 use
the generic hint-cycling path — confirmed safe by design in the `colour_forms.py` review
(guarded call site, no crash). No claim that all 153 SHOULD have curated colour — this is
a scope observation, not a defect: unlike structural form (where an uncovered type gets a
family that can be flatly WRONG for its subject), the generic colour hint-cycling path is
subject-agnostic and doesn't have the same "wrong family" failure mode. Not flagging further.

## Recommendation (handed to the owner, not executed here)

This is scoping/content work, matching what Tranche 1's own worksheet process did:
1. Add `TYPE_FAMILY` corrections for the 9 confirmed-misfit types above (cheap — one
   dict-line each, no new authored pools needed since `FAMILY_FORMS["formal"]`/`["cellular"]`
   already exist and already have appropriate vocabulary).
2. Spot-check the remaining 70 uncovered-but-unflagged types at leisure using the same (51 actively-matched types not individually verified, plus the 19 landing on the pure formal fallback with no hint match at all)
   method (print the triggering hint word, read the type's own prompt, judge fit) rather
   than trusting the fallback silently forever.
3. Consider a permanent harness/lint row (flagged in both the `prompts.py` and `structure.py`
   reviews this session) that lists every type resolving via `_FAMILY_HINTS` fallback rather
   than an explicit table entry, so this doesn't require another manual worksheet pass next
   time a type is added.
