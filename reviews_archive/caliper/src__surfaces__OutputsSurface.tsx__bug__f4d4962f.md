# colibri bug review - src/surfaces/OutputsSurface.tsx (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 f4d4962f - 2026-08-26
mode: bug (delta on badb9f63, 2026-08-19; the file was rewritten by Era 24's archive) - context: the archive's two divisions, REPRODUCE flow into the wizard, filmList artifact-manifest degradation

## Verdict

Shippable - the rewritten file is clean.

## New findings

None confirmed. The jobs+provenance merge mirrors the reviewed Library path; kind-then-day grouping with unique keys; the schema-lag guard (noArtifacts fallback) matches Library's; REPRODUCE's loading per-film state and the honest "only autopilot-era films carry their formula" error; FilmPanel strips ordered by TYPE_ORDER.

## Missing safeguards

- Sound-only ModelCards render a blank media well - MediaView has no solo-audio branch (a known, repo-wide design gap; the film strips show a typed glyph, the model card shows nothing).
