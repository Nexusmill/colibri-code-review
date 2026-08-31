# MODES.md - the five review modes

> Source of truth: `analyzer.py` (`MODES`, `_SYS`, `_TEMPLATES`, `review_code`). Every mode
> reviews ONE file per call, receives the source with a line-number gutter (`N| code`),
> and - for Python - the deterministic static-signal block
> ([STATIC_SIGNALS.md](STATIC_SIGNALS.md)). Where each mode is available:

| mode | console | run_batch.py | grok-review / hy4-review CLIs |
|---|---|---|---|
| `bug` Bug Hunt | yes | yes | yes |
| `quality` Code Quality | yes | yes | yes |
| `feature` Feature Ideas | yes | yes | yes |
| `spec` Spec Conformance | yes | **no** (gap - [BATCH.md](BATCH.md#known-gap---specplan-not-in-the-batch-cli-deliberate-until-ordered)) | yes (`--mode spec --spec ... [--spec-ids ...]`) |
| `plan` Remediation Plan | yes | **no** (same gap) | yes (`--mode plan [--findings ...]`) |

An unknown mode string silently falls back to `bug`. The console's "All three" choice is
bug + quality + feature (never spec/plan).

## bug - Bug Hunt

Persona: rigorous senior staff engineer + application-security reviewer; real defects
only, exact line numbers, no style padding. Hunts logic/correctness errors, off-by-one,
None/undefined, unhandled error paths, boundaries, races, resource leaks, missing
validation, injection / deserialization / path traversal / SSRF, auth and secret
handling, overflow, wrong API usage, silent failures. Output contract: `## Verdict`
(safe to ship? single biggest risk), `## Bugs & vulnerabilities` worst-first
(`[CRITICAL|HIGH|MEDIUM|LOW] title - line N` with What/Trigger/Impact/Fix), `## Missing
safeguards`. Severities with no findings are omitted.

## quality - Code Quality

Persona: principal engineer focused on long-term health; concrete refactors, never
invented bugs. Assesses naming, readability, complexity, DRY, cohesion/coupling,
abstractions, SOLID, error-handling style, docs, dead code, idiom, testability. Output:
`## Health score` X/10, `## Improvements` (impact-ranked, before/after where it
clarifies), `## Quick wins`, `## What's done well`.

## feature - Feature Ideas

Persona: pragmatic product-minded staff engineer; every idea grounded in what the code
actually does, with realistic effort. Output: `## What this module does`, `## Suggested
add-ons` ranked by value (`Value: High/Med/Low · Effort: S/M/L`, What/Why/How with the
exact hook points), `## Nice-to-haves`.

House convention (Nexusmill): accepted AND rejected suggestions are both logged in the
product's `features_manifest.json`, so the signal/noise of a feature run stays visible.

## spec - Spec Conformance

Persona: conformance reviewer against **the maintainer's authoritative feature
expectations** - the contract travels IN the prompt. Reports ONLY divergences between the
code and the stated expectations, quotes the violated clause for every finding, never
critiques the expectations themselves, never reports unrelated generic bugs (Bug Hunt
owns those). Explicitly told to check the quiet clauses hardest: disabled/greyed states,
error paths, sentinels, cost disclosure, side effects, wrap/boundary behavior. A clause
the code satisfies gets silence.

Output: `## Verdict`, `## Divergences` worst-first (each with the quoted **Expectation**,
Trigger, actual **Behavior** vs contract, Fix), and `## UNJUDGEABLE HERE` - one line per
clause whose behavior lives outside the file under review, naming where it likely lives.
That last section is load-bearing: single-file review cannot judge cross-file clauses,
and pretending otherwise produces confident false findings.

**Prerequisite:** expectations text. Without it the call returns a message and spends $0.
How to author expectations for any program: [SPEC_AUTHORING.md](SPEC_AUTHORING.md).

## plan - Remediation Plan

Persona: senior staff engineer who **plans only and never executes** - the plan is carried
out later by someone else under strict TDD. For the few most load-bearing real defects
(or, when a previous review is injected, for exactly its still-open findings - no
re-litigating, expanding, or dropping), each item gets: Objective, Root cause
(line/symbol), Fix design (smallest change, exact edit sketched), **Test first** (the
failing test to write BEFORE the fix), Steps, Verification (commands + expected
outcomes), Risk & rollback. Ends with `## Execution order & batching` in commit-sized
tranches.

House law: plan output is archived, and execution happens in a separate tranche under the
remediation-manifest discipline - a plan is never treated as a fix.

## Delta re-review

Console toggle "Delta re-review for changed files" / batch `--delta`. When a file's
status is *stale* (content changed since its last review in this mode), the previous
saved review (capped at 20,000 chars) is appended to the prompt with instructions to
report ONLY findings that are NEW or CHANGED, add a `## Fixed since last review` section
confirming resolved items, and not restate unchanged findings. This is the
iterate-until-clean loop refusing to re-pay to re-hear known findings.

## JSON output (`fmt="json"` / batch `--format json`)

Appends a strict instruction to return ONLY a JSON object:
`{"verdict": str, "findings": [{"severity", "line", "title", "detail", "fix"}], "notes": [str]}`.
Parsing is tolerant (strips fences/prose, takes the outermost object, requires
`findings`). On a parse failure there is exactly ONE corrective retry ("That was not
valid JSON..."); a second failure keeps the raw text and flags `json_error` - a paid
review is never thrown away. Usage accounting sums both calls.

## The call itself (all modes)

- Client: `openai.OpenAI` against the configured base URL, headers
  `HTTP-Referer: http://localhost`, `X-Title: Colibri Code Review`.
- Key: `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`); no key = no call, friendly message.
- `max_tokens`: explicit value, or AUTO = the model's own `max_completion_tokens`
  (`model_max_tokens`, cached, fallback 131072) so a reasoning model is never truncated
  into a zero-finding "review".
- Empty-content handling: `finish=length` renders a raise-the-ceiling notice;
  reasoning-only responses render the raw reasoning labeled as such; anything else
  renders the finish_reason. Truncated-but-present output gets a truncation footnote.
- Usage: real billed cost from the API when present, else `price_in/price_out` estimate;
  saved with every review ([STORAGE.md](STORAGE.md)).
