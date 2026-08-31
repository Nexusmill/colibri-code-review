# STATIC_SIGNALS.md - the deterministic enrichers

> Source of truth: `static_context.py`. The model reviews SOURCE TEXT; a tool can PROVE in
> milliseconds things the model only guesses. Before each review of Python source, three
> cheap deterministic passes run on the exact code under review and their output is
> appended to the prompt as **hints to corroborate** - never as gospel. The block's own
> preamble tells the model: corroborate each against the code, act on the true ones,
> ignore any that don't hold; line numbers match the `N| code` gutter.

## The three passes

### 1. ast + pyflakes - scope leaks, dead code, ast smells
- **ast-only smells** (no install needed): mutable default arguments (one object shared
  across all calls), bare `except:` (also swallows KeyboardInterrupt/SystemExit),
  unreachable code after return/raise/break/continue (flagged once per block, recursing
  into nested bodies/orelse/finally/handlers). A file that does not parse reports the
  SYNTAX ERROR line instead.
- **pyflakes** (optional dependency): undefined names / used-before-assignment (= scope
  leaks), unused imports and locals (= dead code). Output lines are normalized to
  `L<line>: message`. Not installed -> a one-line note says the checks were skipped
  (`pip install pyflakes`); a clean file says so explicitly (a clean report is signal
  too).

### 2. mypy - static type errors (bug/quality modes only)
Runs `python -m mypy` on a temp copy with `--follow-imports=skip
--ignore-missing-imports --no-error-summary --show-error-codes --no-color-output
--hide-error-context --no-pretty`, 60s timeout. Temp paths are rewritten back to the real
relative path so line references stay meaningful. Degrades to a one-line note when mypy
is missing, times out, or fails. The temp file is always cleaned up.

### 3. dis - bytecode of hot loop-bearing functions (bug/quality modes only)
Finds the "hottest" functions by loop nesting depth (then loop count), takes the top
**3**, and disassembles each (outermost code object wins on name collisions; nested code
objects are walked via `co_consts`). Each function's disassembly is capped at **2,500
chars**. Purpose: the model can SEE a `LOAD_GLOBAL`/`LOAD_ATTR` repeated inside a loop
that source-reading glosses over. No loops -> "nothing hot to disassemble"; a
non-parsing file is skipped.

## When each pass runs

| pass | modes | config key |
|---|---|---|
| ast + pyflakes | all five | `static_ast` |
| mypy | `bug`, `quality` only | `static_mypy` |
| dis | `bug`, `quality` only | `static_dis` |

Feature/spec/plan reviews get only the ast pass (type errors and bytecode don't inform
those judgments). All keys default True; the console exposes them as the three "Static
signals" checkboxes, batch disables all three with `--no-static`.

## Python detection

The passes run only for Python: `.py`/`.pyi` by extension; a known non-Python extension
(js/ts/go/rs/java/c/html/css/json/md/yaml/sh/ps1/...) skips immediately; an UNKNOWN
extension is ast-parsed as a heuristic - if it parses as Python it is treated as Python.

## Size + failure containment

The assembled block is capped overall by `static_max_chars` (default **8,000** chars,
truncation is announced) so signals never dominate the input budget. Every layer degrades
gracefully: a missing tool, a syntax error, or a crashed pass yields a short note - and
`analyzer.review_code` wraps the whole builder in try/except (plus `analyzer.py` imports
the module defensively), so a broken enricher can never block a paid review.
