# colibri review — birdcam/cli.py

- source: `birdcam/cli.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: c0a0713b… (206 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: subcommand wiring verified against the armed-gate session (argparse parents fix, `--dry-run` after subcommand); callers are the seven .bat launchers and the scheduler; error contracts of blink_client/config/pipeline/compiler reviewed in their own units.

## Verdict

Does its job and the launcher-facing flags now parse in any position, but the error-translation
layer is incomplete: two of the pipeline's own exception families escape as raw tracebacks.

## Bugs & vulnerabilities

**[LOW] CompileError / PipelineError / YoutubeError escape as tracebacks** - `lines 193-201`
- What: `main` translates `ConfigError` (exit 2) and `BlinkError` (exit 3) into clean messages;
  `YoutubeError` is recognized by string-matching `type(err).__name__`; `compiler.CompileError`
  (ffmpeg missing — the single most likely first-run failure of `compile`/`run`) and
  `pipeline.PipelineError` are not translated at all, so they re-raise as full tracebacks in a
  beginner-facing console window.
- Trigger: `4-run-now.bat` with ffmpeg not on PATH; or any youtube_client error raised before its
  type-name check can match (it only matches the top-level raised error — youtube errors are
  already wrapped by `pipeline.upload`'s per-batch except, so the name check is near-dead code).
- Impact: the "what do I do now" signal is buried in a stack trace for exactly the users the
  .bat launchers exist for.
- Fix: import youtube_client/compiler at the top of `main`'s except chain and map:
  `CompileError → "ffmpeg problem: … (see README)" exit 5`, `PipelineError → exit 6`, drop the
  type-name string check.

**[LOW] exit-code collision between refusal classes** - `line 196` (`except blink_client.BlinkError → 3`)
- What: BlinkError covers both "not logged in yet" (recoverable by double-clicking login) and
  "Blink rejected the client" (406-class, needs VPN/API diagnosis). Launchers can't distinguish,
  so `check-setup` remains the only triage tool.
- Trigger: any BlinkError path.
- Impact: minor — guidance is in the message text; noted for polish.

## Missing safeguards

- No `--version` (trivial; the value lives in `birdcam.__init__`).
- `cmd_check_setup` doesn't verify the Blink media endpoint reachability (a login can be valid
  while videos listing fails); accepted — that's what a dry run is for.

Adversarial pass: the CompileError traceback path traced `cmd_compile → _run_pipeline →
compile_batches → find_ffmpeg raise → asyncio.run → main except chain` (no matching handler →
re-raise); CONFIRMED. The type-name near-dead-code claim traced: pipeline.upload wraps all
youtube failures per batch and marks them failed, so no YoutubeError reaches `main` through the
normal path; CONFIRMED (as dead-in-practice, hence the simplification suggestion).
