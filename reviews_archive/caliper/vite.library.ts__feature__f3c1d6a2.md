# Colibri review — vite.library.ts (feature)

- **Source:** `vite.library.ts` · **sha256:** f3c1d6a2
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the library's file side (delete + export + the harness fixture); the film-manifest-reference dependents rule (adversary round-1 m3); the Recycle-Bin doctrine for run deletion (owner 2026-09-02); zipWriter at the repo root; verified: delete uses fs.unlink; last touch a0077ba (2026-09-03).

## What this module does

173 lines: `resolveArtifact` (type-rooted, traversal-safe, subfolder segments filtered), honest per-item delete — physical files AND the provenance record leave together, with film dependents proven BY MANIFEST REFERENCE (a film is a dependent only if film.json still names the artifact — directory existence alone overclaims), byte-exact STORE export (entry paths mirror each artifact's home, collision suffixes, absolute-dir validation, exclusive-create so same-minute exports never overwrite), and the deterministic harness fixture (a real PNG / decodable WAV one-off).

## Suggested add-ons

**Recycle instead of unlink** — Value Med · Effort S-M
- What: route library deletes through the Windows Recycle Bin (the `recycleToBin` queue machinery lives in vite.film — lift it to a shared module) instead of `fs.unlink` (line 94).
- Why: run deletion recycles reversibly by owner doctrine ("recoverable from the desktop bin"); library deletion — the SAME class of user-initiated destroy — is permanent today. One wrong CONFIRM on a model asset and the file is gone; the app already built the reversible path.

**An export manifest inside the zip** — Value Med · Effort S
- A manifest.txt entry naming each file's provenance (bundle, prompt, seed, queuedAt — all on the provenance records already read here) turns an asset zip into a portable formula pack: open elsewhere, or re-run through REPRODUCE's format by hand. Byte-exact media plus one small text file; the STORE doctrine unaffected.

## Nice-to-haves

- The fixture seeds one-off records with a `:fixture` promptId suffix; a fixture-clear action would let the harness clean its residue in one call (today tests delete through the library UI they're testing). Low, test-infrastructure.
