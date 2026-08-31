# colibri gate — asset-forge/forge/imagegen/colour_forms.py (grok round 5)

- **source:** asset-forge/forge/imagegen/colour_forms.py
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_colour_forms_grok43.md) gated in-session by claude-fable-5
- **sha256:** ad2e8ae79572f15469bf5e16ea3301ca7f2021283dc7dd00ecbedbcee4f8054c (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** bug (grok round 5; first dedicated review of this module)
- **context pack:** COLOUR-FORMS design (2026-08-14), exhaustive pairwise-distinctness proof + runtime assert pre-declared deliberate; verified against live catalog.json (nested walk: 46 colour-enabled types) and the is_achromatic call site in library_gen.py.

## Verdict
Shippable. Grok's 4 raw findings all survived only in **downgraded** form; both of its
concrete HIGH/behavioural fixes were REFUTED as written (each would have broken shipped
behaviour). One real doc-contract defect + two latent hardening items + one plausible
substring hazard.

## Findings after adversarial verification

**[LOW, CONFIRMED — doc contract] allocate() docstring's "Slot 0 is ALWAYS the classic" is false for axes-only types** — `allocate` (~line 232) + module header line 16
- Catalog probe: **36 of 46** colour-enabled types have `colour_axes` but NO `colour_variants` (specials == []), so slot 0 is a seed-shuffled combo, not a classic. That behaviour is CORRECT and required — but the docstring (and prompts.py's consuming comment) states an invariant that holds only for curated types.
- Grok's severity HIGH and its concrete fix (`raise ValueError` when specials is empty) are **REFUTED**: the raise would crash plan-building for all 36 shipped axes-only types. Fix is documentation-only: qualify the claim ("when the type has curated colour_variants").

**[LOW, CONFIRMED — latent hardening] duplicate special clauses defeat the distinctness guarantee** — `_specials`/`_pool`
- Code path real: `_specials` does not dedupe, `capacity` would overcount, `allocate` could emit duplicate texts. Trigger absent in shipped data (catalog probe: zero duplicate clauses across all 46 entries). Catalog is Nexusmill-authored, so this is defence against a future authoring slip, not a live bug. Ordered-dedupe in `_specials` is the right shape.

**[LOW, CONFIRMED — latent hardening] non-list `templates` mishandled** — `_axes` line 179
- `list("str")` char-splits; chars lack `{c}` so all combos collapse → the runtime assert in `_pool` fires (AssertionError — loud, at PLAN time, before any spend). Non-iterable raises TypeError. Trigger absent in shipped data (probe: zero malformed templates, all contain `{c}`). Failure today is loud-but-cryptic, and asserts vanish under `python -O`; an isinstance gate would fail cleanly. Latent.

**[LOW, PLAUSIBLE] is_achromatic first-match-wins substring scan can misclassify** — `is_achromatic` line 261
- Grok's concrete fix (`c == cl`) is **REFUTED**: the live call site `library_gen.py:299` passes the FULL PROMPT, so substring containment is load-bearing — equality would disable the achromatic exemption entirely.
- The residual hazard is real in principle: if a special's clause text appears inside a prompt whose actual slot colour disagrees with that special's flag (e.g. via identity_guard overlap), the special's flag wins before the term scan runs. Unverified because it needs an assembled-prompt corpus scan across all types; no shipped misclassification demonstrated. PLAUSIBLE LOW.

## Refuted and dropped
- Finding 1 as-stated (HIGH + ValueError fix) and Finding 4's equality fix — see above; both fixes would regress shipped behaviour.
