# colibri bug review - src/components/FilmWizard.tsx (delta)

source: src/components/FilmWizard.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 38078272 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 118f08e9 @ 9804e27 2026-08-25 - the world-model/checkpoint/pair era rewrite; action handlers, resume machine, pricing, and review gates read fresh from current bytes)
context: full action-handler section read (240-540) + engine/bill/run-view sections via targeted reads; prior review 118f08e9 carried; cross-file: autopilot-bill/run/finish semantics (vite.film e827383d, budget 7f6c26b8), planProduce's approved-only segments.

## Verdict

Shippable except the bill-truth finding below (cross-file with budget.ts - the client side is now confirmed). The wizard's state machine is disciplined: zombie-producing guard (needsOwner: checkpoint/kfReview/lastRejected/redraft/error), no-clobber resume, localStorage commit-point contract, sequence-guarded ladder fetch, per-second live clock, settled-gated CONTINUE (win.every approved-or-rerolled).

## Bugs & vulnerabilities

**[HIGH - cross-file, confirmed client-side] APPROVE SPEND quotes a bill that prices ONE pass at the wrong engine; the finish pass runs unpriced** - lines 1040-1045 vs 1190-1198 vs 333-343
- What: THE ENGINES shows the honest two-pass number ("draft-first worst case ≈ $X (rehearsal + finishing)", secs x (draftP+finishP), line 1045), but the bill the owner approves comes from autopilot-bill (computeBill): pick("shoot") = engines.shoot override (unset - the pair lives in shape.draftEngine/finishEngine and never feeds engines.shoot) ?? ladder[0]. So the approved ceiling = one pass at the LADDER DEFAULT. runFinish then discards all segments and re-shoots on the finish engine under that ceiling - the ledger-sync gate halts within roughly the 15% margin of the finish pass, and the recovery ("re-approve a higher bill") re-bills the same wrong number.
- Impact: money-safe (nothing crosses the ceiling unapproved - the gate holds) but the finishing switch cannot complete for pricier finish engines, and the owner approved a number matching neither the pick-time display nor the actual spend.
- Fix (server-side, filed on budget.ts/vite.film.ts): make autopilot-bill strategy-aware - price the pair (draft pass + finish pass as separate lines for draft-first; finish-engine rates for straight-finish) and/or require a fresh bill+approval at the finishing switch.

## Missing safeguards (carried)

- The local-draft resume path still lives inside autopilotList().then - a failed list call skips resuming a purely client-side draft (prior note, unchanged).
- autopilotBill failure at THE BILL leaves the pricing status until BACK/NEXT retriggers (prior note, unchanged).

## Fixed since last review

- [HIGH] ensureRecord pending-clear duplicate-run leak - FIXED (both outcomes clear pending; the commit-point regression test exists in FilmWizard.test.tsx).
- The 9804e27-era harness workaround is retired by the fix (not re-papered in the current flow).

## Verified-correct (adversarial passes, findings deleted)

- Auto-resume priority chain (producing+job-or-needsOwner > localStorage pending > newest wizard/storyboard record) traced including the zombie guard's fall-through; the late-resume no-clobber guard on every branch.
- The producing poll (3s) and the 1s live clock are separate intervals with correct cleanup; adjust() refetches grades immediately on approve/reroll ops (the review gate reads them); entering THE BILL prices server-side only; the ladder refetch carries a cancelled-flag sequence guard (stale quality-toggle responses cannot land).
- Critique gate UX: use-suggestion loads the rewrite into THE IDEA (critiqueAck false - the new prompt is critiqued fresh); keep-mine acks and drafts verbatim; upscale opens the artifact in a window (openAsset) and joins the library.
