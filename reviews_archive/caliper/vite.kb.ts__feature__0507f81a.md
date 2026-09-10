# Colibri review — vite.kb.ts (feature)

- **Source:** `vite.kb.ts` · **sha256:** 0507f81a
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the knowledge store — corpus for the optimizer's read_kb (vite.agent imports searchKnowledge), the draft's kbHits (vite.film), the bench append path, the film failure bin; append-only corpus doctrine; verified absence: no supersede convention; last touch e41ef12 (2026-08-29).

## What this module does

The optimizer's memory: knowledge/*.md chunked and BM25-indexed on demand with an mtime-stamp invalidation (any file change rebuilds — the corpus is always current); `searchKnowledge` shared by the HTTP route AND the agent's read_kb tool (one retrieval for both); `appendMeasured` (sanitized titles, dated tag headings, never silently dropped) as the A/B loop's write path; and the film failure bin append whose heading words are chosen to be findable by the grader's failure query.

## Suggested add-ons

**A SUPERSEDED convention for wrong measurements** — Value Med · Effort S
- What: an append-only correction entry form — `## <title> [superseded-by <new-title>]` — that the BM25 text naturally carries, plus a one-line doc note in the corpus README declaring that tagged entries are outranked by their successor.
- Why (verified): the corpus doctrine is append-only (never rewritten — correct), so a WRONG measurement (a mis-run bench, a price captured before a provider change) teaches the brain forever with no path to retract. Deletion violates the doctrine; an explicit supersede marker is the append-only answer. The ladder and the brain both read these entries.
- How: convention + a tiny helper appending the marker; optionally searchKnowledge could note superseded hits (keep simple: the marker text speaks for itself).

**Per-doc corpus stats** — Value Low · Effort S
- `/api/kb/status` returns docs/chunks totals; a per-doc breakdown (name → chunks, last mtime) would make corpus curation visible. Low.

## Nice-to-haves

- searchKnowledge returns no scores through the shared fn (the HTTP route exposes them); the agent could use a confidence number in its tool result. Low.
