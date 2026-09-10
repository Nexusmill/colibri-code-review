# Spec review — vite.keys.ts

- **Source:** E:\AI\Caliper\vite.keys.ts (60 lines)
- **Reviewer:** ZCode fresh-context subagent
- **SHA-256:** be9fe8c0156f3c88280beb02b186ba900e516b19c183d180ac6baa6da03a3697 (sha8: be9fe8c0)
- **Date:** 2026-08-31
- **Mode:** spec conformance (registry: E:\AI\Caliper\spec\settings-keys.json)
- **Context:** The settings area's single key route (GET presence / POST set-or-clear) over six per-service token files, mounted at `/api/keys` in vite.caliper.ts:505 (both configureServer and configurePreviewServer). Store layer is vite.tokens.ts `makeTokenStore` (bare filenames resolved beside the repo root); catalog is src/providers/serviceKeys.ts.

## Verdict

**PASS — no divergences.** Every clause judgeable against this file is satisfied; the remaining clause surface is UI or film-defaults behavior owned by other files.

Adversarial residue (considered, refuted as clause divergences):

- `stores[k.id]!` (line 39) and `stores[body.id]!` (line 45) use non-null assertions over a `Record<string, Store>`. Safe today: the `ServiceKeyId` union and the `stores` map are in lockstep (6/6 ids, src/providers/serviceKeys.ts:6 vs vite.keys.ts:11-18), and `isServiceKeyId` gates every request-supplied id (lines 30, 44) before any lookup. A future SERVICE_KEYS entry without a store would 500, but that is latent fragility, not a current clause violation.
- Empty-string POST token is treated as clear (line 46). This is a lenient superset of "CLEAR removes it"; the UI sends explicit `null` (SettingsConsole.tsx `save(k.id, null)`). Not a divergence.

## Divergences

None.

Checked and satisfied (silence per protocol, listed here only as scope evidence):

- **SET-SECRETS-NEVER-COMMITTED (CONFIRMED):** all six stores write via `makeTokenStore` with fixed bare filenames (`hf-token.json`, `replicate-token.json` — preserved names — plus `openrouter/spacexai/groq/eachlabs-token.json`, vite.keys.ts:11-18), resolved to repo root by `path.resolve(import.meta.dirname, file)` (vite.tokens.ts:12) with the bare-filename guard at vite.tokens.ts:11. Request input can never steer the path. Evidence from E:\AI\Caliper\.gitignore: line 21 `hf-token.json`, line 22 `*-token.json` (covers all five sibling token files at any depth). No key material can enter a commit from this code path.
- **SET-KEYS-ONE-PLACE, server half (CONFIRMED):** GET lists every SERVICE_KEYS entry with `present` derived from an actual file read (vite.keys.ts:39), so all six services appear in one place; POST sets or clears (normalize to non-empty string or null → `store.write`, vite.keys.ts:46-47; null → `fs.rm` in vite.tokens.ts:23). The wrong-service advisory works as declared: `formatOk`/`expected` are returned only for ids with a known prefix (hf_, sk-or-, xai-, vite.keys.ts:23-27) and only when a token was actually pasted (line 52); a mismatch is advisory, never a rejection — matching the file's stated contract and consumed by the UI (SettingsConsole.tsx:30).

## UNJUDGEABLE HERE

- **SET-KEYS-ONE-PLACE, UI half** — SAVED chip with "where it lives" tooltip, no typing box while a key is stored, CLEAR-then-paste unlock. Owner: `src/components/SettingsConsole.tsx` (chip and gating live at its lines 55-63; formatOk consumed at line 30). Also the **wizard key gate** (per registry authority docs/FEATURES.md settings-keys; owner: the wizard flow, not the key route).
- **SET-FILM-DEFAULTS-SERVER-SIDE** — film autopilot standing orders persisting server-side in a gitignored file. This file contains no film-defaults code. Owner: `vite.film.ts` (`DEFAULTS_PATH = path.resolve(import.meta.dirname, "film.defaults.json")`, line 81; file gitignored at .gitignore line 37), with the defaults shape in `src/film/autopilot.ts:195`.
