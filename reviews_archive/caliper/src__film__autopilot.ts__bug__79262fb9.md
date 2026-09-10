# colibri bug review - src/film/autopilot.ts (delta)

source: src/film/autopilot.ts · reviewer: ZCode GLM-5.3 in-session · sha256 79262fb9 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 78994f9b @ b0212df 2026-08-24; cited lines re-opened fresh - line 446 verified in current bytes)
context: diff 324+12 (the world-model/manifesto/pair-doctrine era); prior review 78994f9b carried; consumers already traced end-to-end in the vite.film.ts e827383d review (draft/critique/world/redraft loops).

## Verdict

Shippable after one cosmetic-string fix. The new machinery is strict where it must be (parseRedraft's window/duplicate/canon/completeness/loud-bound checks; parseCritique's verdict discipline; PATCHABLE growth).

## Bugs & vulnerabilities

**[LOW] literal `${d}s` placeholder ships to the brain in the micro-film protocol** - `src/film/autopilot.ts:446`
- What: the MICRO-FILM PROTOCOL consequent is a double-quoted string containing `${d}` - plain text, never interpolated. Films <=20s tell the brain "(this film is ${d}s)" instead of the number.
- Trigger: any draft with grid.duration <= 20 (micro-films).
- Impact: confusing prompt text only - the true duration IS stated in the fixed-timeline line; no functional break.
- Fix: make the consequent a template literal with ${Math.round(grid.duration)}.

## Missing safeguards

- PATCHABLE now also accepts adversary/world sections unvalidated (prior note, grown): a crafted local autopilot-patch can poison the record's world/adversary; the wizard's client only sends well-formed patches. Local-surface accepted risk, unchanged posture.

## Fixed since last review

- [HIGH] resolveLadder win-rate keying (bare slug vs full service/slug) - FIX VERIFIED in current bytes (winOf() helper, best/balanced both keyed by full reference).

## Verified-correct (adversarial passes, findings deleted)

- validateStoryboard's seconds now come from the grid with no 12s literal (the old clamp silently re-timed 15s-doctrine slots - the removal is the fix); upper nonsense bounded by grid construction + the adversary's 20s ceiling.
- parseRedraft: NO silent truncation (4000-char loud error - the anchor-mid-block-cut class), window containment, duplicates, canon, completeness all enforced; beats/seconds frozen by contract (only prompts+cutIn parsed).
- buildDraftPrompt's world-mode contract omits the anchor field from the JSON ask (matches withWorldAnchor's code-side injection - the brain cannot garble what it is not asked to write); CONTINUITY LAW text consistent for both world/non-world modes.
- ENGINE_CARDS/TIERS/maxClipSeconds: pair ceiling = min of the two caps, unknown refs default 20; questions/critique ride the draft like the brief.
