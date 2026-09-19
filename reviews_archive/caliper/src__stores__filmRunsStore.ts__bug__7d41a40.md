source: src/stores/filmRunsStore.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: 7d41a402ec8c610152d6794f9344a5b6c74bffaab96e4c9dfdc0f6de739a48b9
date: 2026-09-19 11:38
mode: bug
context: runs store; derivePin; BUGHUNT12 provenance laws excluded

First-ever bug scan. 1 finding, CONFIRMED + FIXED:
- [MEDIUM] reset() did not bump refreshGen - an in-flight refresh/derivePin overwrote the cleared store after the window closed, leaving pins pointing at destroyed runs. FIXED: reset bumps the generation before clearing. Pinned (in-flight list released after reset stays null).
