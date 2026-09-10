# Review - bug mode

- source: src/components/DeckControls.tsx
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: the pre-flight status line in well 3)
- context pack: the well's existing registers (danger for failures, calm
  for idles - the R2 linger rule); vramPrompt's own Unload/Keep flow;
  lastTerminal semantics.

## Verdict

Shippable. One conditional deck-status line in the established idiom; over
speaks in the danger register, tight stays calm, everything else is
silent.

## Bugs & vulnerabilities

None CONFIRMED. Traced: pf derives from activeJob ?? lastTerminal - the
line rides the job it was taken for and lingers after terminal exactly
like the queue's own last status; no new classes or layout.

## Missing safeguards

- The line was not screenshot-verified live: producing a real tight/over
  state needs a live backend with a benched bundle, and fabricating one
  would lie. The render is idiom-reuse (deck-status + text-danger), the
  route/store are live-tested, and the first real over on this rig will
  show it. Named, not hidden.
