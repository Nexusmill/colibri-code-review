# Review - bug mode

- source: vite.llm.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: the shelf pick branch gains the catalog download path)
- context pack: the pick validation's gate-round-1 discipline (refused pick
  leaves state seated); provision's job/streamDownload pattern; the
  LLM_MODELS name collision (aliased import - the local const is the
  models-llm PATH); the shelf/status refresh cycle.

- **[FIXED, adversary round 2] the server lacked the picker's brain-seat
  filter** - the download branch matched any catalog entry, so POSTing the
  embedder/reranker file would download knowledge-store machinery onto the
  brain shelf. The find now requires isCatalogBrain - the server is the
  enforcement point, the UI the courtesy.
- **[REFUTED with bytes] partial downloads** - streamDownload writes
  target+'.part' and renames ONLY on success (vite.caliper.ts:552-565), so
  a failed download never lands a .gguf on the shelf; noted in the branch
  comment.

## Verdict

Shippable. The download path answers BEFORE any state moves (202 + job),
mirroring the cloud branch's discipline; state only changes on a
successful setLocalBrain.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- a refused pick (not on shelf, not in catalog) answers the same 409 as
  before - local-brain-shelf's live refusal still passes.
- one download at a time (the running-job guard); a second pick during a
  download answers 409 naming the deck's progress.
- the background download writes to models-llm/<catalog file> - the name
  comes from the catalog constant, never the request (no traversal).
- the 202 returns before spawn decisions: a downloaded file joins the
  shelf (status's localModels) on the next poll; the user re-picks.

## Missing safeguards

- No auto-seat after download (deliberate - the pick again is the user's
  confirmation, and the note says so).
