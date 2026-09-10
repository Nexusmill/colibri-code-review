# Full bug-hunt synthesis - Caliper, 2026-09-05

Scope: 133 in-scope files (test files, tools/gen_* one-shots, the 17 chassis/CAD .py art scripts, vendored .githooks copy, and ambient types excluded per the established precedent).
Coverage: 62 cache-hits at current sha + 53 delta reviews (against exact reviewed-base commits, including 15 CRLF-normalized matches) + 1 EOL-artifact determination (caliper_vram.py - no logical change; manifest sha normalized) + the api/types.ts manifest typo corrected. Every file in scope now carries a bug review at its current bytes.
Method: colibri-review v0.2.0 delta protocol (Phase 0 freshness/cache, Phase 1 context packs via jcodemunch + cross-file traces, Phase 3 adversarial passes with refutations recorded, Phase 4 sha-keyed persistence + atomic manifest).

## Cross-file findings, ranked

1. **[HIGH] The draft-first bill is strategy-blind - the finishing switch runs unpriced.** autopilot-bill (vite.film.ts) prices the shoot leg from engines.shoot-override-or-ladder-default, never from shape.draftEngine/finishEngine, and never prices the FINISH pass as a second pass. FilmWizard SHOWS the honest two-pass number at engine-pick time (secs x (draftP + finishP)) but APPROVE SPEND locks the one-pass ceiling; autopilot-finish then discards all segments and re-shoots on the finish engine under that ceiling - the ledger-sync gate halts within ~the 15% margin, and re-approval re-bills the same wrong number. Money-safe (nothing crosses unapproved) but the finishing switch cannot complete for pricier finish engines and the approval quoted the wrong number. Files: src/film/budget.ts, vite.film.ts, src/components/FilmWizard.tsx.
2. **[MEDIUM] The classic film server routes are trapped dead ends under the universal gates.** planProduce plans segments only for boardApproved shots; the only writers are autopilot-adjust (requires an autopilot record) and FilmWizard. A classic film (action "create" -> "produce") can never plan a segment; multi-window classics crash earlier at kfReviewNow's readAutopilot ENOENT. No UI caller exists today (filmCreate..filmProduce are client-orphaned) - a trap for API use or UI revival, failing with a filesystem error instead of an honest message. Files: vite.film.ts, src/film/produce.ts.
3. **[MEDIUM] xfade assembly crossfades the SONG at dissolves.** Contiguous song spans overlap 0.4s at every dissolve (two moments of the same song mixed - audible smear on rhythmic material) and each dissolve silently consumes 0.4s of song (the film ends 0.4s x N-dissolves short of the song). By-construction confirmed; whether the trade is acceptable is an owner ruling (ruling 38 makes the song the only sound). File: vite.film.ts assembleFilm.
4. **[LOW] "VID N done in Xs" logs after HELD BACK for the same shot** (truthful-status). vite.film.ts:1178.
5. **[LOW] Literal ${d}s placeholder ships to the brain** in the micro-film protocol (double-quoted string, never interpolated; true duration stated elsewhere). src/film/autopilot.ts:446.

## Closures verified this pass (prior hunts' findings)

- The 2026-08-25 vite.film HIGHs (ungated rerolls, local->cloud fallback poisoning) - fixed and present.
- The 2026-09-03 adversary findings (anchor-contaminated shorthand gate, size words, inflection asymmetry, B-vocabulary comment, seconds<=0) - all fixed; the 20s hard ceiling literal remains open (LOW, carried).
- The fmtGb rounding twin (StatusFooter), the key-mismatch classes, the failure-TTL caches (replicate/openrouter), the export race (library), the vacuous harness checks, the enum-seeding shown-vs-sent fixes, the winner-keying (resolveLadder), the peek probe click-through, analyze-song's silent empty beats, install-git-guard's truncated-copy/version-sort/structural-presence classes - all fixed and present.
- Still open (accepted/documented residuals): queueAndWait's unbounded poll (ComfyUI-reachable-but-stuck), PATCHABLE unvalidated record shapes (local surface), the documented git-guard regex residual (full flag indirection), agent's concurrent-apply last-write-wins, adversary's single-strip actionOf, caliper_vram CORS+200-zeros (owner shelf), MediaView's reading-placeholder-on-error, autopilotDelete's missing queued flag in the client type.

## Scope decisions recorded for the owner

- tools/gen_*.mjs and the 17 tools/*.py chassis/CAD scripts are out of scope (one-shot art generators, not live tooling - no references from package.json or the harness). Override if you want them reviewed.
- 62 files were cache-hits at their current sha (the sha-keyed cache held; no re-review spent on unchanged bytes).
- Delta reviews cite exact base commits; 15 files' prior reviews hashed CRLF working-tree renderings (recorded per-file).
