# Colibri review — src/kb/bm25.ts (feature)

- **Source:** `src/kb/bm25.ts` · **sha256:** 927454f8
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the retrieval core (the plan's guarantee: retrieval works with the GPU off; embedder/reranker refine LATER, never replace); indexed over heading+text by vite.kb; unchanged since 064b753 (2026-08-19) — stable.

## What this module does

56 lines of textbook BM25: tokenize (keeps dots/dashes — version strings and flag names match), term-frequency maps, document frequencies, average length, and search with k1=1.4, b=0.7 and the standard IDF — pure, instant, dependency-free; score>0 filter, top-k.

## Suggested add-ons

**Heading-field weighting** — Value Med · Effort S
- What: index the heading and body as separate fields with a heading boost (classic BM25F-lite: sum body score + α × heading score).
- Why (verified): `textOf` concatenates `heading + " " + text` with equal weight (vite.kb.ts:44) — a chunk whose HEADING names the query ("LTX cold renders") ties against one that buries the words in prose. The chunker deliberately builds heading chains as context; weighting them makes that design pay off in rank.

**Adjacent-term bonus** — Value Low-Med · Effort S
- Pure bag-of-words: "vram headroom" matches a chunk containing both words far apart. A small bonus when query bigrams appear adjacently in the doc improves precision on the guardrail-style queries the brain actually issues.

## Nice-to-haves

- k1/b as constructor options for tuning experiments — Low; the defaults are sound.
