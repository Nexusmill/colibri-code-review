# Colibri review — src/components/DocView.tsx (feature)

- **Source:** `src/components/DocView.tsx` · **sha256:** e1f8a0be
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the document renderer behind `sound-plate`'s words half; FEATURES.md `storyboard-compound-doc`; the film-relative image resolution in MediaView; verified absence: no copy affordances, no in-doc search; last touch b3b3578 (2026-08-27).

## What this module does

The markdown-subset renderer for film words: headings (three weighted tiers), paragraphs with inline bold/italic/code, block images (film-relative, resolved by the caller), tables, lists, rules — plus the storyboard's own grammar: "→ JOIN" lines render as physical direction arrows between panels, and an unproduced panel image degrades to the truthful PENDING frame instead of a broken icon.

## Suggested add-ons

**Copy affordances on the script's prompt lines** — Value Med · Effort S-M
- What: script.md's "## Prompts" section carries each shot's exact board:/shoot: engine prompts (writeScriptFile, vite.film.ts:525-526) as plain paragraphs; a copy-on-hover/press chip per prompt line.
- Why: those paragraphs ARE the engine asks — the artifact users quote into other tools, compare against footage, or reuse as references. Today selection-by-mouse over a rendered doc window is the only path. The "show the output / reproduce" doctrine is served by making the formula copyable where it's displayed.

**In-document find** — Value Low-Med · Effort S
- Storyboards run 60+ panels; a doc-scoped find with next/prev and match count beats window-level Ctrl+F (which also escapes the pane).

**Panel → shot bridge** — Value Low-Med · Effort M
- Panels are numbered headings; a panel image press could open that shot's evidence (the wizard owns the inspector). Cross-surface; needs a shot-index hook. Deferred unless the world-review gate (R1) reshapes THE PLAN anyway.

## Nice-to-haves

- Heading anchors for deep links (open at panel N) — Low.
