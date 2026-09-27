# BATCH.md - run_batch.py, the headless runner, every flag documented

> Source of truth: `run_batch.py`. It runs the exact same reviewer (`analyzer.review_code`)
> the console uses, shares the same `.colibri_reviews/` sha cache (completed unchanged reviews are reused), and needs only `OPENROUTER_API_KEY` in the environment.

```bash
python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high
python run_batch.py app.py analyzer.py --model moonshotai/kimi-k3 --budget 0.50
python run_batch.py src --glob "*.py,*.js,*.ts" --out reviews --workers 4
```

## Positional

- `paths` (one or more) - files and/or folders. Folder walks share the console scanner's exclusions: secrets, scratch, dependencies,
  virtual environments (including `pyvenv.cfg`), generated filenames and files over 2MB.
  Explicit file arguments are a deliberate opt-in and bypass directory discovery filters.
  Missing paths print `skip (not found)` and continue. The final set is deduplicated and
  sorted.

## Flags

| flag | default | meaning |
|---|---|---|
| `--model` | `z-ai/glm-5.2` | any OpenRouter model id |
| `--mode` | `bug` | `bug` \| `quality` \| `feature` - **spec and plan are console-only here** (see the gap note below) |
| `--effort` | `high` | reasoning effort `off\|low\|medium\|high\|xhigh`; `off` = unbounded (no effort hint sent) |
| `--max-tokens` | `0` = AUTO | output+reasoning ceiling. AUTO resolves the model's own `max_completion_tokens` so a review is never truncated (GLM-5.2 reasons past 20k and needs its full 131k) |
| `--temperature` | `0.15` | sampling temperature |
| `--glob` | `*.py` | comma-separated filename patterns for folder walks |
| `--root` | repository root, else requested directory | explicit shared cache root; all files must be inside it |
| `--out` | `colibri_batch` | output directory for the per-file review copies |
| `--budget` | `0` = no cap | stop new calls once recorded billed spend reaches this amount; already-dispatched calls can exceed it |
| `--force` | off | review even files whose current sha already has an up-to-date review (default: skip them - true resumability) |
| `--workers` | `1` | parallel review calls. Network-bound: 4 is ~4x wall clock |
| `--format` | `md` | `md` or `json` - validated machine-readable JSON with ONE corrective retry; on double parse failure the raw text is kept as `.md` and the summary marks `json_error` (a paid review is never lost) |
| `--delta` | off | stale files get their previous saved review injected so the model reports only NEW/changed findings ([MODES.md](MODES.md#delta-re-review)) |
| `--price-in` / `--price-out` | `0` | $/1M fallbacks used only when the API omits real billed cost |
| `--no-static` | off | disable all three static-analysis enrichers ([STATIC_SIGNALS.md](STATIC_SIGNALS.md)) |

## Behavior worth knowing

- **Resumability / the shared cache.** The cache root comes from the enclosing Git
  repository or the requested directory, with `--root` available to match a different
  console scan root. It does not depend on where the matching files happen to live.
  Only completed reviews at the current source hash print SKIP. Incomplete responses
  retain their evidence and billed cost but remain eligible for retry.
- **Two outputs per review.** The store keeps an immutable, manifest-linked report in
  `.colibri_reviews/`; a second copy lands in `--out`. Names include a digest of the
  source path so flattening or truncation cannot merge different source identities.
  JSON output is accepted only when the documented schema validates.
- **Budget under concurrency.** With `--workers > 1` the budget check happens under the
  manifest lock before each dispatch; already-dispatched calls complete, further files are
  not dispatched. This is a dispatch threshold, not a guaranteed maximum charge.
  Costs are counted immediately upon response, before persistence. A paid persistence
  failure stops further dispatch; the summary retains the response, usage and any saved path.
  If the summary cannot be written either, recovery JSON and the billed total are printed
  to the terminal and the run exits with an error.
- **Per-file console line.** `[i/n] path  seconds  $cost  finish=stop  HIGH/CRIT=x MED=y`,
  plus ` json_error->md` and ` (delta)` markers. HIGH/CRIT and MED are counted from the
  rendered severity tags (both `[HIGH]` and `"HIGH"` spellings).
- **`_batch_summary.json`** is written into `--out` at the end: model, mode, format,
  done/skipped/errors counts, total spent, and a per-file row (`status`, `cost`,
  `finish`, `high_crit`, `medium`, `output`, `delta`, `json_error`, or `error` text).
- **Exit code** is 1 if any file errored, else 0.
- **Multiple drives:** run separate projects separately. A shared root must contain every selected file.

## Gotchas

- **`--max-tokens` on high effort:** reasoning tokens count against the ceiling. AUTO
  (default) is correct for normal source files; a huge manual value (e.g. 128000) on
  `--effort high` can let the model reason for many minutes per file. If a run seems
  hung with near-zero CPU, this is why.
- **Key not visible:** `setx`/rc-file edits only apply to NEW shells. The pickup recipe
  for an already-open agent shell is in [../AGENTS.md](../AGENTS.md).

## Known gap - spec/plan not in the batch CLI (deliberate until ordered)

`analyzer.py` fully supports `spec` and `plan`, and the **console** exposes both, but
`run_batch.py --mode` accepts only `bug|quality|feature` and has no `--spec` input.
Headless spec/plan sweeps today go through the sibling CLI reviewers, which DO have them:

```bash
python C:\Users\User\source\repos\Tools\grok-review\grok_review.py <file> --mode spec --spec <registry.json> [--spec-ids A,B]
python C:\Users\User\source\repos\Tools\hy4-review\hy4_review.py  <file> --mode spec --spec <registry.json> [--spec-ids A,B]
```

Extending `run_batch.py` with `--mode spec --spec/--spec-ids` (and `plan`) is a small,
natural follow-up - it is documented here as an open gap rather than silently built,
because adding modes to the batch surface is the owner's call.
