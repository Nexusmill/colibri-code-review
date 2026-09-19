# BUG review: tests/harness/bpy_patternskin.py

- source: `tests/harness/bpy_patternskin.py`
- model: claude-fable-5-1 (in-session, colibri-review protocol)
- sha256: `ef98e98c0de4f7b66e26c65562df8ff1edb54fa94cf9345b8d72faf01b3d51a8`
- reviewed: 2026-09-19 07:25
- mode: bug (test-unit hunt per the 2026-09-19 doctrine: tests are units)
- context pack: static (Blender-bound); features registry tests/harness/features/patternskin.json (PS-AA anchors `_aa_pool`; PS-SPECTOR-BRIDGE names junk/_spector_bridge_t2_repro.py); results tests/harness/results/ps_results.json (git-tracked, written 2026-09-10, PS-AA pass); runner.py:107-121 (Blender leg SKIPs without BLENDER, critic still runs); critic.py:41-43/83 (loads results, no freshness check); specs lane probes/reveal_and_pick_bpy.py:99 (SPEC-PS-RULINGS-01 covers all three rulings); remediation row 2026-07-28 (PS-SELF-UPDATE false FAIL); .gitignore (junk/).

---
## Verdict
The PatternSkin feature tester (71 rows). One row is hard-wired green, a crash (or a no-Blender run) grades the previous run's committed results as current, several split rows go green without their own evidence, and one row's battery is gitignored scratch.

## Bugs & vulnerabilities

**[HIGH] PS-AA can never fail** - `line 91`
- What: `binfrac_c > 0.5 and float(td.std()) < 0.35 or True` parses as `(A and B) or True` - always True - and the block never calls an AA function (only `load_heightmap`). The registry row (patternskin.json:505) expects "bimodal line art pooled+blurred, damascus keeps veins, renormalized 0-1"; the results file shows PASS with detail "gate inputs sane".
- Fix: drop `or True`; call `_aa_pool` (the registry anchor) on both maps and assert the post-AA property.

**[HIGH] A mid-run crash - or a run without Blender - grades the PREVIOUS run's results as current** - `lines 51-85, 106-124, 128-141, 145-168` (unguarded) + `line 749` + runner.py:107-121 + critic.py:41-43/83
- What: the first six feature blocks have no try/except, `RESULTS` is written only at the end (749), the file is never cleared at start, and it is git-TRACKED (tests/harness/results/ps_results.json, last written 2026-09-10). runner.py runs `critic.py` after the Blender leg even when that leg was SKIPped for lack of `BLENDER` (114-115), and the critic loads the file with no freshness check.
- Impact: an `apply_pattern` exception at line 53 kills the tester with no results written, and the critic then grades 71 rows from the stale committed file - PASS rows from a previous session presented as this run's. Cross-file: cited at both sites.
- Fix: `os.remove(RESULTS)` (or write a `{"_started": ...}` stub) before the first block; guard the early blocks like the later ones; make the critic refuse a results file older than the run start.

**[HIGH] Split feature rows go green with zero own-check evidence** - `lines 464-471` (PS-ACCEL-PROBETIMEOUT / KCLAMP), `553-559` (PS-PICK-EXACT / SEL-FRESH), `648-655` (PS-HM-NORM / PRESET-AUTOLOAD / PRESET-DEFAULTS)
- What: each pair/triple grades on `_ran` = "any PASS/FAIL line printed" plus "no FAIL with MY prefix"; a battery that prints PASS lines but never emits a row's prefix passes that row. The file's own 2026-09-01 gate finding (576-580, EV-019 discipline at 599-602) established `_own_ran` guards and run-integrity fan-out for the LIB and QOL rows - not applied to these three groups.
- Fix: mirror the LIB/QOL gate - require `_own_ran` per prefix and fail every sibling row on a run-integrity FAIL. (grok-4.6 found this; verified by reading 584-585 and 614-616 against 464-471.)

**[MEDIUM] PS-SEAMLESS's stem check tests Python's `re`, not the add-on** - `lines 149-151`
- What: `re.sub(r"(_seamless)+$", "", "x_seamless_seamless") == "x"` runs on a literal inside the test; no add-on stem helper is called, so the check cannot fail and production stem-stripping can break with the row green (the score checks are the only real signal).
- Fix: call the add-on's name derivation (the make_seamless operator, __init__.py:4355+) on a real path and assert on its result.

**[MEDIUM] PS-SPECTOR-BRIDGE's battery is gitignored scratch** - `line 386`
- What: it runs `junk/_spector_bridge_t2_repro.py`; junk/ is gitignored (G4), the file exists only on this machine (2026-07-24), and the registry row itself names that path. On any other checkout the row FAILs (FileNotFoundError -> except -> FAIL) - honest, but the feature's evidence is untracked.
- Fix: move the battery to tests/harness/probes/ and update the registry anchor.

**[MEDIUM] PS-DEP-LOCK can leave a REAL queued install behind** - `lines 196-201`
- What: `mark_pending_install("cairosvg")` writes the user's real pending-installs file; the cleanup rewrite at 201 is not in a `finally`. An exception between (or a killed Blender) leaves cairosvg queued, and `finish_pending_installs` - the finisher the row itself checks at 203 - will pip-install it into the user's environment on the next start.
- Fix: try/finally around mark->clean, or point `_pending_installs_path` at a temp file for the test.

**[LOW] PS-TEXT-CACHE reuses `o`, `ctx_`, `_ap` from the PS-SCAN-RESUME block** - `lines 253-269`
- What: if the sibling block fails before binding them, this row false-FAILs with a NameError (honest, but not an independent check).

**[LOW] Hard-coded machine paths** - `lines 9, 500`
- What: both have fallbacks (line 9 only on the `__file__`-less MCP exec path; 502 falls back to Blender's python, which the comment says lacks the deps the kv batteries need -> FAIL, not a false PASS). Portability only.

**[LOW] Temp dir leak** - `line 344` (`mkdtemp` never removed) and the probe file at 339.

## Missing safeguards
- No summary line of FAIL rows on stdout; the caller reads only the count (750).

## Refuted own draft
- "three feature rows graded from one spec id (686-689)" - the specs-lane row SPEC-PS-RULINGS-01 (probes/reveal_and_pick_bpy.py:99) covers reveal law + auto-open + film_pick by design.

## External second opinions (grok-4.6, background, 392 s)
- PS-AA `or True` - adopted (same finding).
- Split rows without own evidence - adopted (verified).
- Hard-coded REPO on the MCP path - adopted at LOW (fallback documented; machine-bound harness by design).
- PS-SEAMLESS stem tautology - adopted.
- `_SYSPY` - adopted at LOW.
- PS-TEXT-CACHE coupling - adopted at LOW (fails safe).
- PS-DEP-LOCK leak - adopted (same finding).
- PS-SELF-UPDATE tempdir - adopted LOW.
