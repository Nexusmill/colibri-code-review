<!-- source: src/components/DocView.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: eb478db36f839a966ff6e702d0bafafafb97ae2a591a7799901390e069d050b9 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); LINEAGE pass at identical bytes (eb478db3) beyond the recorded verdict-only review - prior review loaded as context, new material only. -->

## Verdict (1-2 sentences)
The suite guards real behavior against the real component tree, but two named promises are structurally unprovable as written (per-block COPY isolation, the last-panel no-join negative), and the emitter's most documented hardening — the `one()` newline flattening added after the 2026-09-03 forged-heading incident — has zero regression coverage anywhere.

## Fixed since last review (closure of the prior pass's findings)
The prior review (`.colibri_reviews/src__components__DocView.test.tsx__bug__eb478db3.md`) recorded no findings — it is a 12-line verdict-only file ("Shippable. Code block parse + clipboard-stub copy + lens narrow/empty/restore, all against the real component tree."), sha `eb478db3…` matching the current on-disk file (verified via `sha256sum`). Nothing to close; this pass hunted only new material.

## Bugs & vulnerabilities (worst first)

**[MEDIUM] "Their own COPY key" cannot fail with a single code block** - `line 39` (test name) / `line 40` (fixture)
What: the test name promises each fenced block renders with *its own* copy state (DocView.tsx line 6: "each with its own COPY key"), but the fixture adds exactly one fenced block, so per-block isolation is never exercised.
Trigger: hoist `copied` state from `CodeBlock` (DocView.tsx line 105) into `DocView`, or key the state so blocks collide — clicking one block's COPY flips every block's button to "copied ✓".
Impact: the named protection ships broken with this test green. Confirmed: only one ```text fence exists in `docWithCode`; assertions at lines 51-52 inspect only that block.
Fix: add a second fenced block, copy the first, assert the second's button still reads "copy" (and its clipboard contribution is absent).

**[MEDIUM] Unguarded anchor lets the last-panel no-join assertion pass vacuously** - `line 120`
What: `const panel2 = md.slice(md.indexOf("## PANEL 2"))` never checks the `indexOf` result; on `-1`, `md.slice(-1)` yields the final character, and `expect(panel2).not.toContain("→ JOINS")` (line 121) passes without testing anything.
Trigger: the PANEL 2 *heading* emission drifts (numbering or format change in `## PANEL ${i + 1}`, storyboard-doc.ts line 53) while the alt-text assertion (line 111, `![Panel 2](kf_01.png)`) and join-line assertion (line 118) still hold — nothing in the file positively asserts the substring `"## PANEL 2"` exists (line 109 pins only PANEL 1's heading).
Impact: the sole guard for the documented "last panel has no join line" contract (comment, line 119) silently disarms. PLAUSIBLE (currently the anchor is found; the defect is the unguarded negative).
Fix: `expect(md.indexOf("## PANEL 2")).toBeGreaterThan(-1)` (or `expect(md).toContain("## PANEL 2")`) before slicing.

**[LOW] Unanchored count regex admits wrong counts ending in 2** - `line 61`
What: `/2 blocks? match/` matches `"12 blocks match"` (substring at offset 1), and also tolerates the wrong singular `"2 block match"`.
Trigger: `visible.length` regresses to 12/22/… (e.g., counting lines instead of blocks, or counting pre-filter blocks ending in 2) while real filtering stays intact — the sibling hiding assertions (lines 62, 64, 66) still pass because they don't observe the count.
Impact: the "spoken count" feature (DocView.tsx line 146) can lie with the test green. Confirmed by regex semantics against the actual placeholder template.
Fix: anchor it — `/^2 blocks match/` — or assert the full placeholder string.

**[LOW] Clipboard stub and mounted hosts are never restored** - `lines 42-44`, `lines 10-17`
What: `navigator.clipboard` is overwritten with the stub and never restored; `mount()` appends a host div to `document.body` that `unmount` never removes. Both persist across all later tests in the file.
Trigger: any future test in this file reads `navigator.clipboard` (gets the fake from test 1) or queries `document.body` globally (sees leftover hosts).
Impact: latent cross-test state leakage (class 4); no current assertion is poisoned because queries are host-scoped and no later test touches the clipboard.
Fix: capture and restore the original descriptor in a `finally`; remove `host` from `document.body` inside `unmount`.

**[LOW] Floating act promise on unmount (tests 2 and 3)** - `lines 82`, `91` (vs the awaited `line 67`)
What: `unmount()` returns act's thenable (`() => act(() => root.unmount())`, line 16) but tests 2 and 3 drop it; test 1 correctly awaits it.
Trigger: any async work still queued at unmount time resolves after the test ends.
Impact: class 6 hygiene — unhandled-rejection/act-warning surface on otherwise-passing tests; also inconsistent with test 1's own pattern. Related: the copy reset timer (DocView.tsx line 113, real `setTimeout(2000)`) is neither faked nor asserted and fires after unmount in real time (benign today only because the root is gone).
Fix: `await unmount()` everywhere; use fake timers if the 2s reset is ever asserted.

## Missing safeguards
- **The `one()` newline-flattening has no regression test** — storyboard-doc.ts lines 28-33 exist specifically because "a dialogue containing `\n## x` once forged a panel heading inside the owner's approval artifact (2026-09-03 bug hunt)", and this is the only test file importing `storyboardMarkdown` (verified repo-wide). The exact documented bug can recur green. A shot with `beat: "x\n## PANEL 9"` must NOT produce a second panel heading.
- **No round-trip test** — `storyboardMarkdown` output is never rendered through `DocView`; test 2's handcrafted `DOC` has already drifted from the emitter: line 22 uses the old single-line anchor form `"**Anchor** (the frozen continuity block) - …"` while the emitter now emits the labeled-list form (`**Anchor** (the frozen continuity block):` + `- item` lines, storyboard-doc.ts lines 43-45). Nothing fails because test 2 never asserts the anchor line and test 4 never renders.
- The clipboard **"blocked" fallback** (DocView.tsx lines 110-112, "select below") is untested — only the happy path is stubbed, though bare jsdom has no clipboard and would exercise it naturally.
- The **copy reset** ("copied ✓" back to "copy" after 2 s) is unasserted — needs fake timers.
- `joinArrow` canon values `match / sound / smash / invisible / hard` are untested (`action` is covered incidentally at line 118, `dissolve` at line 125, default at line 126); a typo in `JOIN_ARROWS` ships silently.
- FIND lens matching against **image ALT text** (`blockText`, DocView.tsx line 97) and the **singular** `"1 block match"` placeholder branch are untested.
- `storyboardMarkdown`'s optional branches — `scorePrompt`, missing `logline`, `"(none)"` anchor, multi-line anchor split — are unexercised by the fixture (sb uses a single-line anchor; production anchors are multi-line by construction per storyboard-doc.ts lines 40-42).

context-pack: prior review eb478db3 (verdict-only, no findings); src/components/DocView.tsx (parseBlocks, CodeBlock, PanelImage, FIND lens); src/film/storyboard-doc.ts (storyboardMarkdown, joinArrow, one()); src/film/autopilot.ts (Storyboard/StoryboardShot interfaces, cutIn canon); vite.film.ts:636 and src/components/MediaView.tsx:38 (production consumers); vitest.setup.ts + vite.config.ts (jsdom, isolation); git log ea80d20/b3b3578; live run `npx vitest run src/components/DocView.test.tsx` = 5/5 passed; sha256 re-verified eb478db3.
new-findings: 5
