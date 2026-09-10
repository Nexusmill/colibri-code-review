# colibri bug review - src/components/SettingsConsole.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 beb74d89 - 2026-08-27
mode: bug - context: full-sweep round five; film defaults API traced

## Verdict

Clean - the SAVED-key row never shows a typing box (the autofill-dots lesson); routes refresh on picker close; budget saves on blur.

## Missing safeguards

- keyedServices is a fresh Set per parent render, re-firing the catalog effect; server-side collection caching keeps it cheap.
