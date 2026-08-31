# Cross-file synthesis — Asset Forge 48-hour bug hunt (2026-08-11)

> **STATUS: ALL FINDINGS FIXED (2026-08-11, same day).** Damien authorised the full fix tranche
> in importance order. Everything ranked below is closed — commits `a78fa6d`, `0652c8b`,
> `d4ebf79`, `ab339c8`, `d04e805` — each carrying its `docs/remediation_manifest.json` row in
> the same commit (G35), twins byte-identical (G23), and registry updates where a registered
> feature changed (Feature Harness Covenant). Three new verification suites live in `junk/`
> (`test_colour_intent_floor.py`, `test_wildcard_opts_and_userlib.py`,
> `test_money_accounting.py`) — 56 assertions, all passing. The compiled user edition was
> rebuilt (stamp `2026.08.11.1537`); `sync_builds --check` reports builds in sync including
> dist freshness; the features harness is back to its **pre-existing 6-FAIL Spector baseline
> with 0 DRIFT**, i.e. the series introduced no new failures. The findings text below is left
> as written at hunt time — it is the evidence, not a to-do list.
>
> Two fixes went beyond the original finding, both recorded in the manifest: the saturation
> metric's brightness inversion was corrected as well as gated, and
> `tools/colibri_manifest_repair.ps1` turned out to be *writing* null shas (17 of 90 rows),
> which is why the drift in finding B kept recurring.

- Model: claude-opus-5 (in-session), colibri-review protocol (G37), one file per review unit
- Scope: every Asset Forge source file touched between 2026-08-09 09:00 and 2026-08-11 09:00,
  **excluding `app.py`** at the user's direction (hunted 2026-08-11, `…app.py__bug__2d557bd3__r2.md`)
- Editions: `asset-forge/` (creator) reviewed as canonical. **All six Python units verified
  byte-identical to their `asset-forge-user/` twins at review time (G23)**, so every verdict
  applies to the end-user build unchanged. `app.py` also verified identical across editions.

## Units

| # | File | sha256 (8) | Review | Findings |
|---|------|-----------|--------|----------|
| 1 | `forge/quality.py` | `997037b4` | r2 (delta vs `3646fb9d`) | 1 HIGH · 1 MED · 1 LOW |
| 2 | `forge/imagegen/replicate_flux.py` | `3959605d` | r3 (delta vs `d7dfb395`, `ab57fa34`) | 2 MED |
| 3 | `forge/imagegen/prompts.py` | `97a06762` | r1 (first ever) | 1 MED · 2 LOW |
| 4 | `forge/bundle.py` | `d6ab2547` | r2 (full-file redo) | 2 MED |
| 5 | `forge/library_gen.py` | `4e7bd2f6` | r4 (full-file redo) | 2 MED |
| 6 | `forge/userlib.py` | `d51070f3` | r2 (full-file redo) | 1 MED |

Data files touched in-window (`forge/catalog.json`, `forge/color_hints.json`) were audited
inside their consumers' context packs rather than as standalone units, per their contracts.

## Ranked cross-file findings

**1 · [HIGH] The colour-hint pool and the saturation floor contradict each other — Units 1 + 3.**
`color_hints.json`'s `family` group ships `"monochrome"` and `"near-monochrome with one accent"`;
`prompts.py:274-312` flattens every group into one 69-entry pool and `:495` cycles it; then
`quality.py:109`'s `MIN_SATURATION = 0.10` rejects the result, spends a second paid generation
retrying the same prompt, and files the output under `flagged/` with a false `quality_warning`.
Expected rate ~2.9% of library items, certain once a run wraps the pool; also reachable through
the `catalog.json` `"monochrome"` palette and the `"Line-art seamless pattern"` style.
**The decisive evidence is inside the change itself:** commit 487781a swept the `intensity`,
`temperature` and `register` groups for hints "honestly satisfied by literal grayscale" — fixing
two and deleting `"neutral tones"` outright — and added `MIN_SATURATION` in the same commit,
but never swept `family`, whose two entries do not merely permit greyscale, they name it.
*Fix:* gate the saturation floor on colour intent (the assigned hint and the `colour_locked`
flag are both already in scope), or finish the sweep. The two files must change together.

**2 · [MEDIUM] Money-accounting is wrong on three separate failure paths.**
Each is small; together they mean the spend a customer can see does not match the spend incurred.
- `replicate_flux.py:280-289` — a 404 on the final create attempt leaves `pred is None`, which
  surfaces as a `BilledFailure` even though a 404 creates nothing. The item is killed (the
  `BilledFailure` contract forbids retry) *and* counted as spent by `library_gen`'s `spent_est`.
- `library_gen.py:962-967` — `_bills()` correctly counts retries, billed failures and dual-pass
  renders for `spent_est`, but **none of those fields is copied into `LIBRARY.manifest.json`**,
  the durable receipt. A retried-then-passing item leaves no trace at all, so a doubled charge
  is invisible to the customer. The block's own comment claims it is "a complete record of what
  happened to every paid image".
- `bundle.py:88` — recipe-sourced `model_extra` skips `_clean_schema_extra`, so a hand-edited
  recipe can set `num_outputs` and multiply billed spend past the quoted price. The adjacent
  AF-1 guard proves hand-edited recipes are already in this function's threat model.

**3 · [MEDIUM] Superseded protections left behind as dead code, one of them certified by a
vacuous test — Unit 3.** `_COMP_GEOMETRIC_ONLY`, `_COMP_ORGANIC_ONLY` and
`_FINISH_GEOMETRIC_ONLY` name strings that exist in no live pool after DOCTRINE-2 and
DOCTRINE-6, so all four filter expressions are guaranteed no-ops. Harness feature
**AF-FORMAL-CLASS** asserts "emblems still class-filter compositions" and passes **vacuously** —
it cannot fail. Image output is correct (the newer doctrine is stricter than the filter it
replaced); the safety net and the record are not. Separately, the entire LLM-output parser
(`_parse_array` and its three helpers) has had no caller since DOCTRINE-4, and
`usecase_manifest.json` still registers a test for it that lives in gitignored `junk/`.

**4 · [MEDIUM] The wildcard path never received wiring the catalog path has — Unit 5.**
`build_wildcard:335` calls `_finish_prompt(core, cat)` with no mode and no `bg_fragment`, and
stamps no `"mode"` on its items, where `build_plan:259-274` does all three. Consequences:
in emblem mode wildcard items get the tiling suffix and height hint — the exact defect
LIB-SEAM(b) fixed for catalog items — while being filed into `emblem/`; and with transparent
background selected they can never produce alpha, hitting `alpha_error = "no keyable backdrop
clause in the prompt"` (`:814`). The second is the "silent product-contract no-op" class that
AF-OUTPUT-KNOBS remediated for the catalog path on 2026-08-04.

**5 · [MEDIUM] Shared mutable index destroyed before rebuild — Unit 6.** `userlib.list_items`
does `_INDEX = {}` and then repopulates over up to 2000 files. A reference resolve racing a
listing returns `None`, and the bundle generates without the style reference the user chose.
`app.py:1036-1039` surfaces it as a job warning (G19-conscious, deliberate), so it is not
silent — but the run is still billed. One-line fix: build a local dict and swap it in.

**6 · [MEDIUM] Quality-floor retries record a seed they did not use — Units 4 + 5.**
Both callers retry at `seed ^ 0x5F5F5F` while recording the original. Stated after refutation:
the alt seed is deterministically derivable, so reproduction is not categorically broken. What
survives is that `bundle.py`'s `recipe_out` omits `quality_floor`, so a regen inherits today's
default *and today's thresholds* — `MIN_SATURATION` landed on 2026-08-10, so any earlier recipe
can now take a different branch. `library_gen` handles the same situation better: its retry
writes to a distinct filename encoding the alt seed, preserving the evidence on disk.

## Repo-hygiene defects found while assembling context (not in any unit)

**A · TWO of the three governance manifests are not valid JSON, and have not been since
2026-08-11 00:47.** Both `docs/remediation_manifest.json` and `docs/features_manifest.json` end
with the two literal characters `\` `n` after their closing brace, so `json.load` fails
(`Extra data` at line 2341 and line 1828 respectively). **Both were corrupted by the same
commit, 15a8e8e** — verified by walking the last several commits touching each file and dumping
the final bytes: through 19db681 they end `}` / `]\n}`; from 15a8e8e they end `}\n` with a
*literal* backslash-n. `docs/deferred_manifest.json` ends with a real newline and is intact.

This is a live compliance failure, not cosmetics. **G35 requires the remediation manifest to be
consulted before any fix and `index_file`'d so it stays searchable**, and the repo's own rule
says to consult the features and deferred manifests before starting work in a file — every
automated consumer of two of the three is currently broken. I could complete the G35 and
deferred-docket steps of this hunt only by stripping the trailing two bytes in memory. It is
also G9-adjacent: an escape sequence written literally into a machine-bound payload, which is
exactly the sentinel-containment class the canon warns about. **Fix: delete the final two
characters of each file** (and check whatever wrote those rows in 15a8e8e, since it emitted
`\n` as text into both). Recommended as the first thing to land, ahead of any finding above.

**B · `.colibri_reviews/_manifest.json` has drifted from the reviews on disk — again.**
Prior full reviews existed for `quality.py` (`3646fb9d`) and `replicate_flux.py` (`d7dfb395`,
`ab57fa34_r2`) but were **absent from the manifest**, so a Phase-0 cache/delta check driven by
the manifest alone reports "no prior review" and loses the delta. I hit this directly: my first
drafts of Units 1 and 2 claimed to be first reviews and had to be corrected after listing the
directory. This is the same failure class as the 2026-07-23 `colibri-manifest-repair` row.
`tools/colibri_manifest_repair.ps1` exists for exactly this and should be re-run; the six rows
from this hunt were written atomically (tmp → `os.replace`) and verified by read-back.
Two pre-existing rows are also malformed (`patterns.py` has `reviewed_at: null`; one row has
`modes: null`), which crashes a naive walk of the manifest.

**C · `forge/catalog.json` differs between editions — deliberate, recorded so it is not
re-flagged.** The only difference is the creator-only `_model_note` field, stripped from the
user edition by `make_user_edition.py`'s catalog scrub. Every one of the 47 models differs by
exactly that key and nothing else — verified field-by-field. This is the intended transform
behind the 2026-08-05 remediation row about internal decision-log text reaching the customer UI,
**not** a G23 twin-drift defect. `color_hints.json` and all six Python units are byte-identical.

## Scope notes

- **`app.py` was excluded at the user's direction and that exclusion is accurately scoped, with
  one caveat worth stating:** its r2 hunt reviewed sha `2d557bd3`, and the fixes it prompted
  landed afterwards in 15a8e8e. Current on-disk `app.py` is `a9c30de9…` — *newer than the bytes
  that were hunted*. The three findings that review raised are fixed; the post-fix file has not
  itself been reviewed.
- `tests/harness/run_assetforge.py` was also touched in-window (19db681). Not reviewed as a unit
  — it is test code, not shipped product — but it is where finding 3's vacuous assertion lives,
  and it will need editing to close that finding.
- **No code was changed by this hunt.** Findings ship as CONFIRMED (or explicitly labelled
  otherwise); one draft finding was downgraded HIGH → MEDIUM during Phase 3 after the
  derivable-seed refutation, and several candidates were refuted and deleted — recorded in the
  unit files where the reasoning is useful (`extra` body-key injection, in-place pool shuffling,
  `_host_ok` traversal, PIL file-handle leaks, `render_class`/`palette` recipe omissions).
- **Deliberately not re-opened (G35/G1):** `_FETCH_HOSTS` allowing all of
  `r2.cloudflarestorage.com` is `AF-CDN-HOST`, status `decided-accepted-risk` (Damien,
  2026-08-04), with three named reopen conditions, none of which has changed.
- **Deferred and features manifests were checked against every finding** (68 deferred rows, 15
  naming a hunted file). **No finding collides with an open docket.** The two open rows touching
  these files — `LIB-KLEIN-WARN` (klein-4b diversity warning in the model select) and
  `LIB-RESHIP-NB2` (reship the default library on nano-banana-2) — are unrelated to anything
  reported here. The closed dockets `AF-1`, `LG-1`, `LG-2`, `LG-3`, `RF-2`, `AF-CKPT-STREAM`,
  `GROQ-RM`, `AF-FINISH-POOL-THIN` and `AF-TYPE-PROMPT-QUALITY` were each verified still closed
  in current source. Two findings are best understood as **incomplete closures of dockets marked
  `done`**, and are labelled as such in their unit files rather than presented as new ideas:
  finding 4 (`AF-OUTPUT-KNOBS` — closed 2026-08-04, but the wiring never reached
  `build_wildcard`) and the Unit 5 note on manifest-write timing (`LG-2` — closed the
  graceful-early-return gap; the hard-crash gap and the docstring's "every checkpoint" claim
  remain).

## Suggested fix order

1. **A** — restore `docs/remediation_manifest.json` to valid JSON (2 characters; unblocks G35).
2. **1** — the monochrome/saturation contradiction (money + wrong flagging, every library run).
3. **4** and **5** — wildcard mode/background wiring; the `userlib` index swap. Both are small,
   self-contained, and each fixes a paid run that ignores what the customer selected.
4. **2** — the three money-accounting gaps, ideally together so `spent_est` and the durable
   manifest tell one story.
5. **6** — add `quality_floor` to `recipe_out` and record the seed actually used.
6. **3** and **B** — delete the dead guards and the orphaned parser, correct AF-FORMAL-CLASS so
   it can fail, and re-run the colibri manifest repair.

Anything acted on needs a `docs/remediation_manifest.json` row in the same commit (G35) and a
harness registry update if it changes a registered feature (Feature Harness Covenant).
