# Colibri review — src/surfaces/OutputsSurface.tsx (feature)

- **Source:** `src/surfaces/OutputsSurface.tsx` · **sha256:** ba7219d0
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the archive; FEATURES.md `outputs-archive` (the two-division contract, REPRODUCE the one action, copy-settings retired); the film-TYPE ownership truth; verified absence: no search/filter, no library cross-link; last touch 82ff326 (2026-08-31).

## What this module does

The archive in two divisions. FILM ASSETS: each film a case file — header (date, shots, typed counts, REPRODUCE) and its artifacts in pipeline order (FINAL first, then CUTS/FOOTAGE/STORYBOARDS/SCRIPTS/LYRICS/SOUND/OTHER), each cell typed and openable with reveal (ruling 40). MODEL ASSETS: the one-off shelf grouped kind→day, with film-owned records excluded by OUTPUT TYPE (not the film list — a failed filmList can never leak film work onto the shelf), live jobs merged before server records, and REPRODUCE per card opening the formula sheet.

## Suggested add-ons

**"SHOW IN LIBRARY" on the film header** — Value Low-Med · Effort S
- What: a press beside REPRODUCE that opens the Library scoped to this film (`pickFolder("film:<id>")` exists in screenStore; the Library mounts on Generate).
- Why: the two surfaces present the same film two ways (case file vs. selectable/zip-able rail); today the scope jump is manual. One press, ruling-40 carry.

**A filter lens for the shelf** — Value Low-Med · Effort S
- The Library's prompt-aware filter (`name + bundle + prompt`) has no Outputs counterpart; with hundreds of one-offs the kind→day groups are the only narrowing. Same lens, same honest empty states.

**Film strip freshness** — Value Low · Effort S
- films load once on mount (line 133-137); a produce run finishing while Outputs is open doesn't refresh the case file counts. The Library has the same mount-once shape (its review notes it) — a shared refresh-on-reopen fix.

## Nice-to-haves

- Group collapse memory (kind→day groups stay open) — cosmetic; commission.
