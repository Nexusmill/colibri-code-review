# Colibri review — src/components/SettingsConsole.tsx (feature)

- **Source:** `src/components/SettingsConsole.tsx` · **sha256:** e85ad0d2
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** keys + model routes + film defaults; FEATURES.md `settings-keys`, `film-defaults`; the R1 modelRoutes.ts stale-route add-on's display home; verified absence: no key liveness test; last touch 91620a1 (2026-09-02).

## What this module does

Three sections: service keys (presence dots, the SAVED-no-typing-box discipline with CLEAR unlocking, wrong-shape warnings that keep a replace box mounted), MODEL ROUTES (per-type rows whose text speaks the cloud-only gating truth — "cloud (the profile gates the stored local pick)" — CHANGE opening the picker, FIRST RUN RUN AGAIN), and FILM DEFAULTS (four leg selects priced at the point of choice via every keyed catalog, quality/finish/budget/aspect, instant save).

## Suggested add-ons

**Key liveness test** — Value Med-High · Effort S-M
- What: a TEST key per service row — one cheap authenticated call (list models / whoami) answering "this key WORKS" or the provider's error verbatim.
- Why (verified): save checks only the SHAPE (`formatOk`); a well-formed but wrong/revoked key reads SAVED and fails at first spend — the film gate then blames "no keyed engine". Presence is local truth today; liveness is the provider's truth, clearly labeled as a one-call check.
- How: per-service probe adapters exist in the api layer (catalog fetches authenticate); result line under the row, never auto-refreshing.

**Route row staleness + health** — Value Med · Effort S-M
- The display home for the R1 `checkStoredRoutes` add-on: `routeText` (lines 39-46) shows `cloud · model` with no indication the model vanished from the catalog. A stale badge + the ENGINE_HEALTH denylist (R1 vite.film add-on) could mark "unavailable since <date>".

**Settings export/import minus secrets** — Value Low · Effort S
- Routes + film defaults round-trip as JSON (keys NEVER — they stay in gitignored files by design). Machine-to-machine setup shortcut.

## Nice-to-haves

- The film-defaults engine selects could group options by service (they flatten today); with three keyed services the list is long.
