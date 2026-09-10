# Colibri review — src/film/store.ts (feature)

- **Source:** `src/film/store.ts` · **sha256:** e31e742c
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 4 importers (vite.film.ts takes shotPrompt/slugify/Film; produce.ts takes the Film type; tests); the autopilot path (autopilotFilmFromRecord) builds shots from the storyboard, not from initShots; last touch 49c2bd2 (2026-08-30).

## What this module does

The legacy-local film vocabulary that the autopilot pipeline still speaks: the `Film`/`FilmShot` record shapes (keyframe/segment/voice/narration/cutIn/boardApproved per shot, film-scope referenceImages, score fields), `DEFAULT_STYLE`, `slugify` (the id grammar SAFE_ID mirrors), `initShots` (the beat-snapped ~5s local grid), and `shotPrompt` (style + shot prompt composition). The produce machine, artifacts classifier, and assembly all read this Film shape.

## Suggested add-ons

**Scene/shot-scoped reference routing** — Value High · Effort M
- What: let a shot's board/segment carry ITS OWN reference images when the run's References declare scene or shot scope, not just film scope.
- Why (verified): `References.images` in autopilot.ts explicitly models `scope: "film" | "scene" | "shot"` with scene/shot numbers — and `filmReferenceImages` (autopilot.ts:593-596) filters `scope === "film"` only; `Film.referenceImages` is a flat film-wide array; genKeyframe sends `film.referenceImages[0]` (vite.film.ts:693). The wizard can ATTACH scoped references, but scoped attachments never ride any engine call. Character-tagged refs (the References type carries `tag: "character" | "location" | "style"`) would directly serve identity consistency — the anchor doctrine's mechanical half.
- How: `FilmShot.referenceImages?: string[]` populated in `autopilotFilmFromRecord` from scene/shot-scoped refs (the record already persists them); `genKeyframe`/`genSegment` prefer the shot's refs over the film's first.

**A shot-level `holds` marker** — Value Low · Effort S
- What: a boolean on FilmShot marking shots intentionally held static (the manifesto's "static camera" hold-outs), so assembly could micro-adjust join treatment and the run view could badge them.
- Why: the doctrine already distinguishes holds in PROMPT text only; no structured field exists.

## Nice-to-haves

- `initShots` and `DEFAULT_STYLE` serve the retired classic console path (the autopilot grid lives in `shotGrid`); if the console retirement is permanent, they are candidates for the documented-dead list rather than new features.

## Notes

- This module's future is the autopilot path: every add-on should land where `autopilotFilmFromRecord` builds the Film, so the two vocabularies never fork.
