# Bug review: `asset-forge/forge/imagegen/prompts.py`

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/imagegen/prompts.py` (creator edition, canonical)
- sha256: `97a0676243b2c7132d9aa3e7cf407c93ca25fe5b7c368f67ef4e8f6a6790630a`
- Twin parity: `asset-forge-user/forge/imagegen/prompts.py` byte-identical at the same sha
  (G23 verified this pass) — verdicts apply to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- Context pack: `get_file_outline`; `check_references` on `_parse_array`, `_scrub`,
  `_looks_like_prompt`, `_PREAMBLE`, `_COMP_ORGANIC_ONLY`, `_COMP_GEOMETRIC_ONLY`,
  `expand_many`, `_fallback_line`, `MOODS_TEXTURE` (after re-indexing
  `tests/harness/run_assetforge.py`, whose indexed line numbers were stale);
  the harness feature registry `tests/harness/features/assetforge.json` (AF-FORMAL-CLASS,
  AF-COLOUR-LOCK) and its runner `run_assetforge.py:695-707`; `forge/color_hints.json` and
  the `catalog.json` palettes pool; `docs/prompt_rules_manifest.json` exempt-globals list;
  the in-window diff `git show 487781a` (GREY-MUSH-1) with its full rationale; and the
  eleven `docs/remediation_manifest.json` rows naming this file (`prompt7-preamble`,
  `palette1-seed-and-reach`, `palette3`, `variety1`, `content1`, `composition1`, `groq-rm`,
  `af-texture-intent-styles`).
- **No prior Colibri review of this file at any sha** — verified by listing `.colibri_reviews/`
  directly, not by the manifest (which is known-drifted; see synthesis).

## Verdict

Shippable — no defect found that produces a wrong or costlier image on any live path. The
in-window change (487781a) is a one-word prompt correction and is sound. What this pass does
find is **decay around superseded doctrine**: three subject-class guard constants can no longer
filter anything, an entire LLM-output parser survives with no caller, and — the one finding with
real consequence — a harness feature registered under the Feature Harness Covenant certifies a
protection that is not running, and passes vacuously.

## Bugs & vulnerabilities

**[MEDIUM] The subject-class composition guards are dead on every path, and the harness feature certifying them passes vacuously** — `prompts.py:345, 352, 421-426`; `tests/harness/run_assetforge.py:704`
- **What:** `_COMP_GEOMETRIC_ONLY`, `_COMP_ORGANIC_ONLY` and `_FINISH_GEOMETRIC_ONLY` name
  strings that exist in **no live pool**, so all four filter expressions at lines 422, 423 and
  426 are guaranteed no-ops. Two independent reasons, both from later doctrine:
  1. DOCTRINE-2 (line 417) sets `comps = [""]` whenever `texture or library` — and lines 421
     and 425 are gated on exactly `(texture or library)`. So the composition filters only ever
     run against the single-element list `[""]`, which contains nothing they could remove.
  2. On the emblem path the guards never execute at all (`texture or library` is `False`), and
     the emblem pool `COMPOSITIONS` (lines 23-30) contains none of the four filtered strings
     anyway — they belonged to the deleted `TEXTURE_COMPOSITIONS` pool. Likewise
     `_FINISH_GEOMETRIC_ONLY`'s two strings appear in neither `FINISHES` (31-36) nor
     `LIBRARY_FINISHES` (85-92), the latter being the source of `TEXTURE_FINISHES` since
     DOCTRINE-6 collapsed them (line 93).
- **Trigger:** Every call. The guards have no reachable effect for any `theme`, `mode`, or flag.
- **Impact:** **Image output is correct** — the newer doctrines subsume the older protections by
  removing the machine-shop vocabulary entirely, which is stricter than filtering it. The harm
  is to the safety net and the record. `tests/harness/run_assetforge.py:704` asserts
  `all(x["composition"] not in _PR._COMP_ORGANIC_ONLY for x in fe)` under the comment
  *"emblems still carry compositions, and the formal/organic split still filters them"*. That
  comment is false — the split is gated off for emblems — and the assertion is **vacuously
  true**, since `COMPOSITIONS` cannot contain those strings. Feature **AF-FORMAL-CLASS**
  therefore reports PASS while verifying nothing about composition filtering. Under the Feature
  Harness Covenant a registered feature is supposed to prove its expectation; this one cannot
  fail, so if COMPOSITION-1/-3 protection were ever genuinely needed again, its guard is gone
  and its test would stay green. The same three constants are also carried in
  `docs/prompt_rules_manifest.json`'s `python_exempt_globals`, which keeps the rules scanner
  quiet about strings that no longer do anything.
- **Fix:** Either delete the three constants and the four filter expressions, correcting the
  AF-FORMAL-CLASS registry entry and the runner comment to claim only what is checked (the mood
  bans, which *are* live) — or, if the protection is still wanted as defence against a future
  pool edit, re-point the filters at pools that actually contain the vocabulary and give the
  harness a negative case that fails when the guard is removed. The first is honest and cheap;
  the second is only worth it if `TEXTURE_COMPOSITIONS` might return.
- **Verification: CONFIRMED.** Membership checked by reading all four pools in full
  (`COMPOSITIONS` 23-30, `FINISHES` 31-36, `LIBRARY_FINISHES` 85-92, `TEXTURE_FINISHES` = a copy
  of the latter at line 93) against the three constants (345-352). No overlap in any direction.
  The `(texture or library)` gating was traced from `expand_theme:537` through `_assignments`.
  Note the mood half of the same harness feature **is** live and correctly asserted: the
  `chaos`/`elemental` ban for geometric subjects (lines 478-479) does real work, and the runner
  checks both the positive and negative case. Only the composition claims are vacuous.

**[LOW] The LLM-output parser survives with no caller — ~35 lines of dead code, plus a registered test for an unreachable path** — `prompts.py:601-638`
- **What:** DOCTRINE-4 (lines 503-520, 576-589) deleted the LLM prompt-upgrade layer. Its output
  parser was left behind: `_PREAMBLE` (601), `_scrub` (606), `_looks_like_prompt` (613) and
  `_parse_array` (624). `check_references` confirms `_parse_array` has **zero** code references
  repo-wide — its only hits are prose in `docs/remediation_manifest.json` — and the other three
  are referenced *exclusively from inside `_parse_array` itself*. The cluster is an orphaned
  island; nothing can reach it now that no model output is parsed.
- **Trigger:** N/A — unreachable by construction.
- **Impact:** No runtime effect. Two costs: it invites a future reader to believe prompts are
  still parsed from model output (the exact mental model DOCTRINE-4 exists to erase), and
  `docs/usecase_manifest.json:230` still registers `junk/test_parse_preamble.py` as the test for
  it — a test for dead code, living in `junk/`, which is gitignored and therefore not in the
  repo at all. The `prompt7-preamble` remediation row it descends from is genuinely closed.
- **Fix:** Delete the four symbols and retire the `usecase_manifest.json` entry. If the preamble
  lesson is worth keeping, keep it as a comment in `docs/PROMPT_DOCTRINE.md`, not as live code.
- **Verification: CONFIRMED** via `check_references` (`import_count: 0`, no code call sites) and
  by reading the full call graph of the module — `expand_theme` → `_assignments` → `_prompt_line`
  is the only path, and it never touches the parser.

**[LOW] The DOCTRINE-4 comment states `expand_many` was removed; it is defined 13 lines below** — `prompts.py:579` vs `:592`
- **What:** Line 579 reads "Removed here: … `_replicate_polish`, `_raw_llm_replicate`, and
  `expand_many`". `expand_many` is not removed — it is redefined at line 592 as a plain loop
  over `expand_theme`, and its own docstring says so.
- **Impact:** Documentation-only, but it is the kind of contradiction that makes a reader
  distrust the surrounding (accurate and valuable) doctrine commentary, and
  `docs/usecase_manifest.json:224` still directs callers to `expand_theme/expand_many`.
- **Fix:** Reword to "reduced to a deterministic loop" — the batching rationale is still worth
  stating, the removal claim is not.
- **Verification: CONFIRMED** by direct read of both lines.

## Missing safeguards / design questions (not defects)

- **The "mixed" vibe cycles the *texture* mood table even for emblem bundles.** Lines 474-485:
  when `mode == "mixed"`, `mood_pool` is built from `MOODS_TEXTURE` unconditionally, and
  `_mood_ban` always removes `neon` and `pastel`. But `list_moods()` (641) serves `MOODS`,
  including `"mixed"`, to the Studio UI, while the library UI has no vibe control (line 471) —
  so `mode == "mixed"` arrives almost exclusively from the **emblem/bundle** path. Those runs
  therefore get surface-wear language ("blackened and corroded, deep shadowed pitting") in place
  of the emblem register ("dark cursed evil rendition, malevolent and sinister"), and silently
  lose two of the nine vibes the product advertises — for a reason (glow destroys displacement)
  that only applies to height maps. **Deliberately not reported as a bug:**
  `tests/harness/features/assetforge.json:477` registers this exact behaviour as the expectation
  ("Variants CYCLE the surface moods (MOODS_TEXTURE) when the EXPLICIT 'mixed' vibe is chosen").
  Raised as a design question because the registry text does not distinguish emblem from
  texture, and the file's own comment at lines 177-179 says the opposite — "Emblem/bundle
  callers keep the original MOODS untouched". One of the two records is wrong; that is Damien's
  call, not a reviewer's. A one-line fix exists if the answer is "emblems should use `MOODS`":
  select the table on `(texture or library)`, which is already a parameter in scope.
- **`_assignments` copies every pool before shuffling** (`list(COLOR_HINTS)` 442,
  `list(COMPOSITIONS)` 417, `list(LIBRARY_FINISHES…)` 418) — so `rng.shuffle` cannot corrupt
  module-level state across calls. Checked explicitly because an in-place shuffle of a shared
  pool would be a serious cross-request bug; **refuted, no finding.**
- **`int(seed)` at line 399 and `zlib.crc32` on the theme are unguarded** against a non-numeric
  seed or a non-string theme. Both callers now validate upstream (the 2026-08-11 `app.py` seed
  fix), so this is a contract assumption rather than a live defect.

## Cross-file note (carried to the synthesis)

The `COLOR_HINTS` pool assembled at lines 274-312 and cycled at line 495 is the *source* of the
HIGH finding filed against `forge/quality.py` this pass: `_load_color_hints()` flattens **every**
group of `color_hints.json` into one 69-entry pool, including `family`'s `"monochrome"` and
`"near-monochrome with one accent"`, which `quality.py`'s `MIN_SATURATION` floor then rejects at
a cost of one extra paid generation per affected item. The defect is a contract mismatch between
the two files rather than an error in either one alone; the recommended fix (gate the saturation
floor on colour intent, or sweep the `family` group as GREY-MUSH-1 swept the other three groups)
touches this file only if the second option is chosen.
