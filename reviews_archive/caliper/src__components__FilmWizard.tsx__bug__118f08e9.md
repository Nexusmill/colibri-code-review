# colibri bug review - src/components/FilmWizard.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 118f08e9 - 2026-08-25
mode: bug - context: jcodemunch importers (ScreenStage only consumer + test), git 9804e27/6b10472 (clicking-is-free + draft-persistence era), localStorage contract traced with the ScreenStage mount, api/film mock surface in FilmWizard.test.tsx

## Verdict

Shippable after the one fix below. The commit-point state machine (local pending → server record) had a leak that minted duplicate runs.

## Fixed since this review (same session)

- [HIGH] ensureRecord never cleared draft.pending when it created the record - the localStorage effect only clears "caliper.wizard-draft" when pending is null, so the saved local draft survived the commit point and SHADOWED the server-side auto-resume on next open (the local-draft branch returns before the server-record branch). The user then re-pressed DRAFT THE STORYBOARD, autopilotCreate minted a SECOND run, orphaning the drafted storyboard. The 9804e27 harness workaround ("clears leftover drafts when a server draft resumes") papered over exactly this. FIX: both ensureRecord outcomes clear pending; a failed extras-carry now still adopts the created record instead of returning null (re-press could twin there too). Regression test added: "the commit point retires the saved local draft".

## Missing safeguards

- The local-draft resume path lives inside autopilotList().then - a failed list call skips resuming a purely client-side draft (recoverable by reopening).
- autopilotBill failure at THE BILL leaves "pricing the run…" until the user re-enters the step (BACK/NEXT retriggers); no auto-retry.

## Verified-correct (adversarial passes, findings deleted)

- RE-DRAFT uses the closure record's id (server re-drafts the same run, no twin).
- The producing poll's dep pair, APPROVE PLAN step gating, adjust onBlur closure freshness, drafting-disable double-click guard, needsRating close gate (owner's rating rule, deliberate).
- Line 469 dead expression and line 638 `title-prefix` attr noted as dead code - harmless, left untouched under the no-visual-change rule.
