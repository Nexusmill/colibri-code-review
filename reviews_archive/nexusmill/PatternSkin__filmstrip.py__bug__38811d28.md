# colibri-review — PatternSkin/filmstrip.py — bug (hunt round 1, effort=low)

- **Source:** PatternSkin/filmstrip.py · **Scanner:** general-purpose subagent @ claude-haiku (low
  effort) · **Verification:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 38811d280481454e41d759b22250204801ef326b67cbfcaaae6cd36c1cba3a68
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (low-effort diversity pass)
- **Context pack:** prior review `PatternSkin__filmstrip.py__bug__90441958.md` (K3, all 6 findings
  since fixed); no refuted-ledger entries or remediation rows for this file at dispatch.

## Verdict
The low-effort pass produced 2 candidate findings; **both were refuted on Phase-3 verification**,
and one of the two proposed "fixes" would have INTRODUCED a bug. No change made. filmstrip stays
active for a higher-effort round — a null low pass is not evidence the file is clean.

## Findings
None confirmed this round.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- **[claimed HIGH] `s.ps_part_patterns.remove(j)` passes an index where a Blender collection wants
  the item (`filmstrip.py:311`)** — REFUTED, and the proposed fix is harmful. `ps_part_patterns` is
  `CollectionProperty(type=PS_PartPattern)` (`__init__.py:1492`), i.e. a `bpy_prop_collection`,
  whose `.remove(index)` takes an **integer index**. `remove(j)` with the enumerate index is
  correct; the suggested `remove(a)` would pass an RNA struct and raise `TypeError`. The scanner
  assumed Python-list semantics.
- **[claimed MEDIUM] regex split on `\band\b` breaks "black and white blade" (`filmstrip.py:85`)** —
  REFUTED as a defect. `_dress_parse`'s docstring defines the heuristic explicitly: "last word of
  each comma/'and' clause names the PART" — `and` is a documented clause separator, not an
  accident. The one plausible-harm case ("black and white blade") is also not silent: a part word
  that matches nothing is surfaced to the user via the "(no part matched)" skip
  (`filmstrip.py:304-305`). Truly resolving the ambiguity needs NL understanding beyond a last-word
  heuristic; this is a recorded design limitation, not a correctness bug. Not reported (would
  relitigate a documented decision).
