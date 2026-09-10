# Colibri review — src/surfaces/GraphSurface.tsx (feature)

- **Source:** `src/surfaces/GraphSurface.tsx` · **sha256:** af17e99a
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the graph tab; seeds through client.ts's graph family (seed/exists/boot/backups/restore); the 5-deep backup rotation (vite.caliper.ts:137); verified absence: restore is newest-only; unchanged since 2026-08-19 (af17e99a) — the most stable surface.

## What this module does

The stock ComfyUI graph bridge: visiting seeds ONLY missing Caliper-<bundle> graphs (force is the button's job, never the tab's), boot-syncs the selected bundle's SAVED graph (user edits included) into the template slot the iframe boots from, handles bundle switches mid-tab, re-seed-all from current settings, restore-last-backup, and the honest away-server note.

## Suggested add-ons

**Backup picker (restore by timestamp)** — Value Med · Effort S-M
- What: the server keeps the newest 5 backups per graph; restore (GraphSurface.tsx:72-81) can only take the latest. A dropdown of the stamped names (listGraphBackups already returns them, newest first) with restore-by-name.
- Why: "restore the latest" is the right default, but the whole point of a 5-deep rotation is going further back — one bad graph edit + one save = the good copy is second-newest, unreachable today. Needs a small server change (restoreGraphBackup takes a name only).
- How: `POST /api/graph-restore {name, backup?}` in vite.caliper; the UI lists `backups` it already holds.

**Graph drift indicator** — Value Low-Med · Effort S
- The seeded graph reflects settings AT SEED TIME; re-seed is manual. A quiet "settings changed since this graph was seeded — RE-SEED to match" marker (params hash vs a stamp stored at seed time) would keep the two truths from silently diverging.

## Nice-to-haves

- The iframe away-state: when 8188 never answers, the iframe shows ComfyUI's own error — the seeding note covers it; a bordered away panel would be clearer. Cosmetic; commission.
