# Colibri review — src/kb/chunk.ts (feature)

- **Source:** `src/kb/chunk.ts` · **sha256:** 1ff1ccad
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the markdown-aware chunker (heading chains as context — "## Krea NVFP4" under "# Measured results" stays findable); 1400/140 constants; the corpus includes code-bearing docs (sources/, craft); unchanged since 064b753 (2026-08-19).

## What this module does

56 pure lines: split on headings (level-1 resets the base, deeper headings CHAIN onto it), buffer body lines, and cap size with a 140-char overlap so sentences aren't orphaned at the seam; each chunk carries `{source, heading, text}` where heading is the full chain.

## Suggested add-ons

**Code-block awareness** — Value Low · Effort S
- What: treat fenced code blocks as atomic units — never slice the middle of one (a long block either fits whole or splits at line boundaries), and keep the fence markers with their halves.
- Why: the corpus carries code (film-craft examples, manifestos with prompt templates); a mid-block slice at MAX_LEN cuts a prompt template or command in half with a 140-char overlap that garbles both halves — retrievable garbage for the brain. The heading logic already treats structure as primary; fences are the same idea.

**Frontmatter strip** — Value Low · Effort S
- YAML frontmatter (sources/ docs carry it) becomes body text in the first chunk; a one-line skip until the closing `---` keeps metadata out of retrieval. Trivial.

## Nice-to-haves

- None — the file is exactly its job.
