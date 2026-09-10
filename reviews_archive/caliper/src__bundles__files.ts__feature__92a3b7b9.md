# Colibri review — src/bundles/files.ts (feature)

- **Source:** `src/bundles/files.ts` · **sha256:** 92a3b7b9
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** bundle file presence validation — consumed by bundlesStore.load/save (fileIssues); FEATURES.md `bundles-editor`'s Files-column sibling; the ObjectInfo enums it reads; unchanged since 2026-08-19.

## What this module does

30 lines: `validateFiles` cross-checks every bundle file reference (checkpoint via the loader-appropriate node+field, video/audio VAEs, text encoders, loras) against the live server's ObjectInfo enums — producing the "File not found on the server" issues the deck and editor surface — with the honest `COMBO placeholder = lazy enum, cannot validate` pass-through when the server hasn't enumerated a field.

## Suggested add-ons

**Name the folder it expected** — Value Low · Effort S
- The message says which FILE is missing, not WHERE the server looked (the enum is just names). Cross-referencing the install catalog's MODEL_ROOTS layout (vite.caliper.ts) — server-side — would let the issue say "expected under LTX-2.3-Distilled/checkpoint/". Needs a server companion route or a shared layout table; honest Low.

**Distinguish absent-server from absent-file** — Value Low · Effort S
- When ObjectInfo can't be fetched at all, bundlesStore keeps prior fileIssues; the validator itself has no away-server state (by design — it only runs with oi in hand). A "not checked this session" stamp on stale issues would age them honestly. Low.

## Nice-to-haves

- None; the module is exactly its size.
