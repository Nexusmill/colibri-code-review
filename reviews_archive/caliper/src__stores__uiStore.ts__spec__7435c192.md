# Spec review — src/stores/uiStore.ts

- Source: `src/stores/uiStore.ts` (39 lines) · Reviewer: ZCode in-session (GLM-5.3) · sha256: `7435c1927e719fd97e66082802405cd1cba941199dd55b989e86a11dfa44fb2e` · 2026-08-31 · mode: **spec** · registry: `spec/screen-os.json`
- Context pack: full read; persistence partialize checked against SCR-RELOAD-RESTORE; the three console booleans noted for the one-at-a-time clause.

## Verdict
Conforms for what it owns — the active surface persists under `caliper.ui` (partialize: surface only), consoles are ephemeral. Two registry-authority notes below for the owner's ruling, no code divergence.

## Divergences
None. (PLAUSIBLE observation, not confirmed here: `aiConsoleOpen` / `filmWizardOpen` / `settingsOpen` are independent booleans with no mutual exclusion in this store — if no component-layer code closes the others on open, SCR-PANELS-IN-PLACE's "one at a time" would be violable. Unverified because the enforcement call sites were not traced this run; lives in ScreenStage/wizard components.)

## UNJUDGEABLE HERE
- SCR-RELOAD-RESTORE window survival — screenStore.ts (`caliper.screen`).
- SCR-COMMAND-PALETTE open/filter/close UX — palette component (state lives here, behavior there).
- SCR-PANELS-IN-PLACE enforcement — component layer (see PLAUSIBLE note).

## Registry-authority note (for the owner, not a code finding)
SCR-RELOAD-RESTORE's side_effect reads "screen persistence lives under the storage key caliper.screen" — the ACTIVE TAB half actually persists under `caliper.ui` (this file); `caliper.screen` covers windows. The clause should name both keys.
