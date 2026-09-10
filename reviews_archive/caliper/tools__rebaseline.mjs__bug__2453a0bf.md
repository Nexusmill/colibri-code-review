# Colibri bug review — tools/rebaseline.mjs

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 2453a0bf192e1758e16fcd9d45bc4a829fcd7ba252bf9521194e60f9ebf8bc7a

### Meta
- path: tools/rebaseline.mjs | sha8: 2453a0bf (matches expected) | lines: 135 | context-pack: hand-run performance re-baseline tool (warm + 2 timed fixed-seed renders against ComfyUI :8188), numbers hand-appended to knowledge/measured-results.md:81; not wired into package.json or the harness; single commit a6bf669; generalizes tools/ltx-720p-test.mjs and mirrors src/workflows/fill.ts's builder.

### Review

## Verdict
Sound measurement harness with faithful slot/lora/ManualSigmas parity to the canonical `fill.ts` (verified against bundles.json and all three templates — every `{{slot}}` resolves for all four bundle ids, lora base node "1" holds in every template, and the 8-step ManualSigmas gate matches `fill.ts` exactly). It writes no files, so it cannot clobber baseline artifacts — the "baseline" is console output a human copies. Defects are in report truthfulness and hang/liveness handling, not in the graph it builds. No CRITICAL/HIGH issues.

## Bugs & vulnerabilities

- **[MEDIUM] `/free` purge outcome is never checked — a missing route silently voids the cold-warmup measurement** - `line 120` — CONFIRMED (code); trigger PLAUSIBLE (documented failure class). What: the fetch result is discarded (`await fetch(...)` with no `.ok`/status read), and the log at line 119 asserts "purging card (/free)…". Trigger: ComfyUI running without the caliper custom node (which owns `/free`), or any route regression — exactly the incident AGENTS.md records ("a missing /free route once made every browser-side unload a silent 404"). Impact: the warmup run then measures a warm card, and that number gets hand-appended to knowledge/measured-results.md as a cold-load figure; the standing repo rule is "status text must be truthful: report what the SERVER says". The timed runs are unaffected (they run after the warmup regardless). Fix: `const r = await fetch(...); if (!r.ok) throw new Error(`/free refused: ${r.status}`)` — and optionally log the /caliper/vram residency after purging.

- **[MEDIUM] No timeout or progress output on the completion poll — a wedged job hangs the script forever** - `lines 103-116` — CONFIRMED. What: `for (;;)` polls `/history/{id}` every 1.5 s with no deadline. Trigger: render wedges on the GPU, or ComfyUI restarts mid-run (history is wiped; `e` stays `undefined` forever — note `h[queued.prompt_id]` on an empty history returns undefined, not an error). Impact: an unattended rebaseline run hangs indefinitely with zero output after "purging card" (the twin tools/ltx-720p-test.mjs at least prints `${secs}s waiting/executing` each poll, lines 58-69). Fix: a deadline (e.g., 20 min for the 16 GB card) with a thrown error, plus periodic progress logging.

- **[LOW] "MEDIAN" of two runs is actually the slower run (upper element), not the median** - `line 134` — CONFIRMED. What: `runs` always has length 2 (loop at line 127); `[a,b].sort(asc)[Math.floor(2/2)]` = index 1 = `max(runs)`. The conventional median of two samples is `(a+b)/2`. Impact: the headline number hand-recorded into the knowledge corpus is systematically the slower run; the raw runs are printed alongside (line 135), so the distortion is visible, but the label misleads the copy step. Fix: print `(runs[0]+runs[1])/2`, or relabel to `SLOWER`, or take 3 runs so the index math is exact.

- **[LOW] Timed figures include poll and HTTP latency** - `lines 104, 114` — CONFIRMED mechanism. Completion is only observed on the next 1.5 s tick plus fetch round-trip, so every `ms` is inflated by 0–1.5 s+. Negligible for ~147 s LTX renders; material (~5-10%) for fast image bundles (Anima at 30 steps can be tens of seconds). Fix: subtract the last poll interval, or read execution start from the history entry's timestamps instead of wall clock.

- **[LOW] `SIGMAS` is a silent duplicate of `fill.ts`'s `LTX_DISTILLED_SIGMAS`** - `line 11` vs `src/workflows/fill.ts` (`export const LTX_DISTILLED_SIGMAS`) — CONFIRMED duplication, drift PLAUSIBLE. If the canonical distilled schedule ever changes in fill.ts, rebaseline keeps measuring on the stale recipe with no error, and the knowledge base records numbers for a recipe the app no longer runs. Node can't import the .ts directly, so a fix is a comment cross-reference at minimum (ltx-720p-test.mjs has the same duplication). Same drift class, benign direction: the `TEMPLATES`/`HAS_NEGATIVE` maps (lines 13-19) also duplicate fill.ts, but any drift there fails LOUD via the `unfilled slot` error — verified against current templates.

- **[LOW] `negative=` CLI override is silently ignored** - `line 51` — CONFIRMED. `s.negative = b.defaults.negative ?? ""` reads the file defaults directly, bypassing `p` (which holds CLI overrides). The header (line 6) advertises generic `key=value` overrides; an operator passing `negative=...` gets the file default with no warning. Fix: `s.negative = p.negative ?? ""`.

- **[LOW] `arg.split("=")` silently truncates values containing `=`** - `line 32` — PLAUSIBLE edge. `checkpoint=my=model.safetensors` destructures to `v = "my"` and drops the rest. Fix: `const k = arg.slice(0, idx), v = arg.slice(idx+1)` on the first `=`.

## Missing safeguards
- No server-context stamp with the numbers: the report (line 123) prints bundle/seed/steps/cfg/dims but not the running server's argv flags or VRAM residency (available at `/caliper/vram`, the repo's declared ground truth). measured-results.md rows carry claims like "optimizer flags active via the launcher" that this tool never verifies.
- No check that the server queue is empty before starting: a bench render or straggler job in flight contaminates the timings silently (the app itself surfaces `server busy · N untracked` for exactly this — DeckControls.tsx). A `/queue` peek before the purge would guard it.
- Errors exit via unhandled-rejection stack traces (exit 1) — acceptable for a hand tool, but the sibling ltx-720p-test.mjs distinguishes `REFUSED:` with a trimmed payload; a usage error vs server refusal distinction would help the human at the keyboard.
