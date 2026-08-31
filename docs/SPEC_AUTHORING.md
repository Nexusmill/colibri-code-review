# SPEC_AUTHORING.md - how to make a spec for ANY program and run it through spec mode

> Spec Conformance mode ([MODES.md](MODES.md#spec---spec-conformance)) reviews a file
> against **expectations you supply** - it finds where code diverges from what the
> maintainer says it must do. This doc is the authoring guide: the accepted formats
> (source of truth: `analyzer.load_spec`), the craft of writing judgable clauses, and how
> to dispatch the result on every surface that speaks spec mode (colibri console,
> grok-review, hy4-review).

## What `load_spec` accepts

You pass ONE source (a file path or raw text). Resolution order:

1. **A path to a file** - its content is read (`utf-8-sig`, errors ignored). Otherwise the
   string itself is treated as the content.
2. **JSON with registry rows** - if the content parses as JSON *and* is an object with a
   `controls` or `features` array, each row renders to readable contract text:

   ```
   ### <id> - <label or feature>
     <KEY>: <value>        (one line per truthy key of the row's `contract` dict)
     EXPECTED: <value>     (used when there is no `contract` dict)
     STATUS: <value>       (when present)
   ```

3. **Row filtering** - an optional comma-separated id list keeps only matching rows
   (console field "Row ids"; CLIs `--spec-ids`). Zero matches raises
   `no matching spec rows` rather than silently reviewing against nothing.
4. **Anything else passes through verbatim** - non-JSON text, or JSON without
   `controls`/`features`, is used as-is. Hand-written contracts are first-class.

So there are exactly two authoring routes: a **registry JSON** (structured, filterable,
reusable by test harnesses) or **plain contract text** (fastest path for a one-off).

## Route A - a registry JSON (recommended for any program you'll spec more than once)

Minimal viable registry for an arbitrary program:

```json
{
  "controls": [
    {
      "id": "TODO-ADD-1",
      "label": "add command",
      "contract": {
        "expected": "`todo add <text>` appends one item with a unique incrementing id and prints `added #<id>`; empty <text> is refused with exit code 2 and nothing is written.",
        "error_paths": "an unwritable store file prints `cannot write <path>` to stderr, exit 3, and the store is left byte-identical.",
        "side_effects": "exactly one line is appended to the store; no other line is touched or reordered."
      },
      "status": "VERIFIED-definite"
    },
    {
      "id": "TODO-LIST-EMPTY",
      "label": "list with no items",
      "expected": "`todo list` on an empty store prints `nothing to do` and exits 0 - never a traceback, never an empty string.",
      "status": "PROVISIONAL"
    }
  ]
}
```

Field semantics:

- **`id`** (required in practice) - stable, unique, SHOUTY-slug per clause. This is what
  you filter by and what findings/dockets cite forever. Never renumber.
- **`label`** / **`feature`** - the human name rendered in the heading.
- **`contract`** - a dict of named clause groups. The KEYS ARE YOURS - `load_spec`
  renders every truthy key uppercased, so choose names that force coverage of quiet
  behavior: `expected`, `error_paths`, `disabled_state`, `side_effects`, `cost`,
  `boundaries`, `authority` all work. Falsy values are skipped.
- **`expected`** - the single-clause shorthand when a `contract` dict is overkill.
- **`status`** - free text rendered as `STATUS:`. House convention: `VERIFIED-definite`
  (behavior confirmed as-a-user), `PROVISIONAL` (awaiting the owner's ruling - the
  reviewer sees this and can weigh it), `RESOLVED`, `deferred`.

Nexusmill's own spec-harness registries (`tests/harness/specs/<product>/<surface>.json`)
follow this shape, which is why the console accepts them directly.

## Route B - plain contract text

Write clauses in any format; the whole text is injected as the authoritative
expectations. Same craft rules apply. Use this for a quick one-file conformance check
where building a registry isn't yet worth it - then promote surviving clauses into a
registry when the program grows a harness.

## The craft - what makes a clause judgable

The spec reviewer's whole value is precision; a vague clause produces either silence or a
confident false divergence. Rules that earn their keep:

1. **One observable behavior per clause.** "The dialog works correctly" judges nothing.
   "Clicking Cancel closes the dialog WITHOUT writing the store" judges exactly one path.
2. **State the trigger and the observable.** input/precondition -> visible outcome
   (output text, exit code, file bytes, UI state). If you can't name the observable, you
   don't have a spec yet - you have an intention.
3. **Write the quiet clauses.** The template explicitly tells the model to check these
   hardest, so author them deliberately: disabled/greyed states, error paths, sentinels,
   cost disclosure before spend, side effects, wrap/boundary behavior, "and changes
   NOTHING else" guarantees.
4. **"Changes nothing else" clauses age.** A deliberate later change can make such a
   clause stale, and a stale registry produces false CONFIRMED divergences (this bit a
   real run: a row's 'changes NOTHING else' predated a deliberate field fix). When
   behavior legitimately changes, update the registry row IN THE SAME COMMIT as the
   behavior change.
5. **Intent first, implementation last.** Spec the outcome ("view frames the selected
   part"), not the mechanism ("calls view3d.view_selected") - mechanisms refactor,
   contracts persist. Cite the mechanism only as an `authority:` note when provenance
   matters.
6. **Scope each registry to a surface** (one panel, one subcommand family, one endpoint
   group) and dispatch per-file packs - a reviewer judging file X against clauses that
   live in file Y produces noise. Cross-file clauses are exactly what
   `## UNJUDGEABLE HERE` exists for: expect the reviewer to name where the clause's
   behavior lives instead of judging it blind, and treat that as a correct answer, not a
   failure.
7. **Provenance in the clause when it's a promise** - quote marketing copy, an owner
   ruling, or a doc line the clause enforces. A conformance finding that can cite "the
   listing says X" closes arguments fast.

## Dispatching a spec run

**Colibri console:** Review type = Spec Conformance -> Expectations file = your registry
(or text file) -> optional Row ids -> select files -> Confirm & run. The loaded-chars
caption confirms what the model will actually see; $0 is spent until expectations load.

**grok-review / hy4-review (headless, per file):**

```bash
python C:\Users\User\source\repos\Tools\grok-review\grok_review.py <file> --mode spec --spec <registry.json> [--spec-ids ID1,ID2]
python C:\Users\User\source\repos\Tools\hy4-review\hy4_review.py  <file> --mode spec --spec <registry.json> [--spec-ids ID1,ID2]
```

(`run_batch.py` does not speak spec yet -
[BATCH.md](BATCH.md#known-gap---specplan-not-in-the-batch-cli-deliberate-until-ordered).)

## After the run - the gate discipline

Spec findings are candidates, not verdicts. Every finding is adversarially verified
against the current bytes before it is docketed (CONFIRMED) or deleted (REFUTED);
`UNJUDGEABLE HERE` rows route the clause to the file that owns it. Field calibration from
the first production spec runs (hy4, 2026-08-30): dispatch **per-file registry packs**
with an already-fixed context list; prefer **medium** reasoning effort (high can burn the
entire completion ceiling on reasoning and return zero content - money spent, no review);
expect real cost ~2-3x naive estimates; and cross-check every finding against the
remediation manifest so already-closed issues are not re-flagged.
