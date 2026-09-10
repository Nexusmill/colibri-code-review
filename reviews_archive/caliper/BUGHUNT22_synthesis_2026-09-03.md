# BUGHUNT22 — cross-file synthesis (2026-09-03)

Scope: the 22 never-bug-hunted live files (10 feature code + 12 live tooling), colibri bug
mode, fresh-context subagent per file, every finding adversarially traced (CONFIRMED /
PLAUSIBLE), artifacts sha-keyed beside this file, `_manifest.json` updated atomically.
The ui-harness manifest-gap finding was independently re-verified by the consolidator
(jcodemunch citable absence + line 1514 exit logic read).

**Tally: 0 CRITICAL · 11 HIGH · 34 MEDIUM · 53 LOW.**

## Ranked findings (worst first)

1. **[HIGH·film·money] Window-redraft truncates the world anchor out of shot prompts** —
   `autopilot.ts:569` slices redrafted prompts to 600 chars; a world anchor (≥1 character
   sheet + set line) exceeds that, so every world-built window redraft ships a cut-mid-anchor
   prompt with NO re-judgment — off-model renders billed at real money, invisible to every
   gate (`worldmodel.ts` review, CONFIRMED). Fix locus: parseRedraft cap + anchor-coverage
   re-check (`carriesAnchor` helper exported from worldmodel.ts).
2. **[HIGH·film·money] Critique gate's shorthand check is disabled by ordinary anchor prose** —
   `adversary.ts:172-174` tests RAW shootPrompt for camera/timing tokens; anchor words
   ("first", "hold", "through", "wide-brimmed") match, so the manifesto's terse-prompt gate
   fails OPEN for essentially every world-anchored film (CONFIRMED mechanism). Same root
   cause as the size-variety MEDIUM at line 163: anchor must be stripped before craft checks.
3. **[HIGH·gate] git-guard has four live-tested bypasses** — separate-token `-n`, env-var
   `GIT_CONFIG_KEY_0=core.hooksPath`, `comm\it` escaping, and verb-gap `.git/hooks` writes
   (`node -e fs.writeFileSync` got through the armed guard during the review itself);
   plus a `-mn` false positive and case-sensitive paths on NTFS. The guard needs token-based
   matching, not substring adjacency. The inner git hook remains the real gate (doctrine
   intact — findings are review to address, layer-2 hardening is the work).
4. **[HIGH·harness] The feature contract is permanently red** — `film-adversary` and
   `sound-plate` have FEATURES.md rows but no harness tests; line 1514 makes every
   `test:ui` run exit 1 (independently verified). Either the gate trains ignore-exit-1 or
   commits stall — both bad. Two rows close it.
5. **[HIGH·harness] `film-defaults` test rewrites the owner's persisted film defaults** on
   every fast-tier run and never restores them — quality pinned to balanced, score engine
   pinned from AUTO. Violates the file's own fixture discipline; restore-in-finally.
6. **[HIGH·verify] see.mjs certifies the PREVIOUS render** — persisted windows satisfy the
   media check, so run 2 screenshots run 1's output while the new job still queues. The
   screenshot-verification protocol's own tool produces false confirmations.
7. **[HIGH·harness] `library-window` has two vacuous pass paths** — precondition-yields-zero
   silently PASSES (fixture seed swallowed); the exact class the adversary banned. Sibling
   tests `skip()` honestly; this one must too.
8. **[HIGH·data] analyze-song swallows ffmpeg failure** — corrupt/non-audio input yields a
   valid-shaped empty `beats.json` and exit 0 (empirically reproduced); downstream
   film-proof then crashes only AFTER the expensive render. Cascade across two files.

## Cross-file patterns (the meta-findings)

- **The anchor is both payload and contaminant.** Findings 1+2 are the same architecture
  gap from two sides: the compiled world anchor is mandated verbatim into every prompt, but
  the redraft path slices it and the craft checks read it as shot content. The manifesto
  layer (rulings 41-43) needs anchor-awareness at EVERY consumer: strip before judging,
  verify coverage after any rewrite.
- **Verification tools without failure contracts produce false greens.** see.mjs (stale
  media), see-ui-720p (exit 0 on every post-queue failure; unattributable library check),
  peek (always-true `…` disjunct), gui-test-phase4 (cannot fail at all), ui-harness
  (vacuous paths, skip-shaped coverage on film-runview). Every driver in this family needs:
  fail non-zero, attribute the artifact to THIS run, try/finally cleanup.
- **Truthfulness drift cluster** — StatusFooter's rounding GB twin vs the fmtGb truncation
  doctrine; /caliper/vram's 200-with-zeros whose `error` key no client reads; rebaseline's
  unchecked `/free` purge; peek's always-green flag. All violate "report what the SERVER
  says" in the quiet direction.
- **Suspended invariants** — the caliper_vram byte-parity check reads DRIFTED forever
  (CRLF canonical vs LF vendored; content identical) — a permanently-red alarm that trains
  ignoring; .gitattributes `comfy/*.py text eol=lf` fixes the class.

## Per-file verdicts

| file | verdict | worst |
|---|---|---|
| src/components/FirstRun.tsx | shippable | MEDIUM empty-keys dead-end on recommend failure |
| src/install/tiers.ts | sound | MEDIUM rounding twin in StatusFooter |
| vite.comfy.ts | clean constants module | MEDIUM silent config-parse fallback |
| src/api/firstrun.ts | PASS | LOW silent boot-skip |
| src/api/types.ts | PASS | LOW phantom `vram_used` field |
| src/film/worldmodel.ts | sound core | HIGH redraft anchor truncation |
| src/film/adversary.ts | invariants hold | HIGH shorthand gate fail-open |
| src/film/storyboard-doc.ts | contract intact | MEDIUM multi-line anchor breaks doc grammar |
| src/components/DocView.tsx | XSS-safe | LOW parser/render traps |
| comfy/caliper_vram.py | well-built | MEDIUM parity DRIFTED / CORS power / 200-with-zeros |
| tools/see.mjs | not trustworthy for its job | HIGH stale-media certification |
| tools/peek.mjs | flags untrustworthy | MEDIUM always-true predicate |
| tools/ui-harness.mjs | FAIL — ship-blocking | 3 HIGH (gap, defaults mutation, vacuous pass) |
| tools/git-guard.mjs | porous as a control | 4 HIGH bypasses (live-tested) |
| tools/install-git-guard.mjs | shippable | MEDIUM non-atomic payload copy |
| tools/analyze-song.mjs | not data-source-safe | HIGH swallowed ffmpeg failure |
| tools/film-proof.mjs | sound workflow surgery | 3 MEDIUM (post-render crash, no deadline, lazy preflight) |
| tools/rebaseline.mjs | sound measurement | 2 MEDIUM (unchecked /free, unbounded poll) |
| tools/see-ui-720p.mjs | right wait, weak failures | 4 MEDIUM (exit-0-always, attribution, leaks, under-clearing) |
| tools/gui-test-phase4.mjs | intact but cannot fail | 2 MEDIUM (no failure contract, sidecar leak) |
| tools/ltx-720p-test.mjs | contract intact | MEDIUM unbounded wait |
| vitest.setup.ts | correct, load-bearing | none (two latent gaps noted) |

## Status & next

Artifacts + manifest are on disk, UNCOMMITTED (spec-wave precedent: review docs ride the
next code wave's commit through the gate — and the harness currently exits 1 on the F1
manifest gap, which the protocol hook would surface at commit time anyway). Natural
remediation order: (1) harness F1+F2 (un-red the gate, stop mutating owner defaults),
(2) the two film anchor HIGHs (money path, gates the fresh Super Man run),
(3) git-guard tokenization, (4) see.mjs wait-condition fix, then the MEDIUM tail.
