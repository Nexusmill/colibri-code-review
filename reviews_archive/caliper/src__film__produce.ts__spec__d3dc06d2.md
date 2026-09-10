# Spec review — src/film/produce.ts

- Source: E:\AI\Caliper\src\film\produce.ts (87 lines)
- Reviewer: ZCode fresh-context subagent
- SHA-256: d3dc06d239d93520644aebe7a0e1b8c766122604c207675d9882d063295f63d6 (d3dc06d2)
- Date: 2026-08-31
- Mode: spec (registry: E:\AI\Caliper\spec\film-run.json)
- Context: planProduce owns the plan-level KEYFRAME GATE (segments plan only for boardApproved shots, segments ordered before new keyframes, universal across film types); checkpointBoundary owns the ~20s checkpoint-window accrual with the final-window exception. Verified against vite.film.ts callers (startProduce/runProduce ~930-1200, adjust handler ~1946-1977) and src/film/produce.test.ts.

## Verdict

PASS — one LOW divergence (plan bookkeeping mislabels gated work as "done"). The two behaviors this file owns — the keyframe gate and the checkpoint window/final-window boundary — conform to their clauses.

## Divergences

### 1. LOW — `skipped.segments` counts gated (never-bought) segments as work "already on disk"

- Expectation (RUN-BUDGET-STOP): "before any produce spend the owner can open and SEE the plan, with viewing instructions, the cost so far, and what's unspent; produce spends nothing until APPROVE." The plan's own report of done-vs-remaining work must be truthful; the file's interface comment (produce.ts:21-22) defines `skipped` as "work already on disk when the plan was built".
- Trigger: any film with boards not yet approved. produce.ts:34 filters segment steps to `!s.segment && !!s.boardApproved`; produce.ts:51 then computes `skipped.segments = film.shots.length - segments.length`, which equals (shots with a segment) + (all unapproved shots). For a fresh 5-shot film with zero approvals and zero footage, the plan reports `segments: 0` todo, `skipped.segments: 5` — five segments "done" that were never bought and are not on disk.
- Behavior: consumed at vite.film.ts startProduce (~line 939) as the plan log's first line — "0 segments (5 done)" — feeding the run view's log tail; the owner's picture of cost-so-far / what's-unspent overstates finished work by exactly the unapproved-board count. The refusal itself (the actual gate) is intact; only the bookkeeping conflates "refused" with "skipped".
- Fix: count on-disk truth, not the complement of the gated filter: `segments: film.shots.filter((s) => !!s.segment).length` (and mirror the test expectation in produce.test.ts:30 / :102 which currently lock in the overcount: the :30 fixture has shot 2 unapproved+empty yet expects `skipped: { keyframes: 2, segments: 2 }` — only 1 segment is on disk).
- CONFIRMED (arithmetic traced end to end: field computed here, log line composed in vite.film.ts; clause anchor is the cost-disclosure reading, which is interpretive — the registry has no clause that names the skipped counter directly).

## UNJUDGEABLE HERE

Clauses whose observable behavior lives in other files (owner file in parentheses):

- RUN-KEYFRAME-GATE — UI half: APPROVE / REROLL / EDIT per board, APPROVE ALL, CONTINUE disabled until the window is fully approved (src/components/FilmWizard.tsx ~1005-1045; `disabled={!allApproved}` exists there). Side effect "a reroll clears the approval together with the artifact" (vite.film.ts adjust handler ~1964/1977 — deletes keyframe+boardApproved and board+boardApproved together; satisfied there).
- RUN-CLIP-CHECKPOINT — the clean stop itself, review clip cut to the window's song span, APPROVE - SHOOT THE NEXT 20s, REJECT THE LOT (failures/ folder move, failure-knowledge append, the three repairs) (vite.film.ts checkpointNow/assembleReviewClip/adjust ops + FilmWizard.tsx).
- RUN-SILENT-FOOTAGE — generate_audio false, stream-copy ingest strip, muted inspector previews (vite.film.ts genSegment/ingest + FilmWizard.tsx).
- RUN-FINISHING-SWITCH — FINISH - REROLL THE FILM ON <model>, strategy+mode then engines.shoot then ladder routing (vite.film.ts + FilmWizard.tsx).
- RUN-VIEW-SHOWS-LIFE — live step line, ticking timer, log tail rendering, grade rail/legend, in-place inspector, the plan's adversary line (FilmWizard.tsx + vite.film.ts job fields; only the one plan-log number reviewed above originates here).
- RUN-RELOAD-RESUMES — reload landing on the PRODUCING film at THE RUN (FilmWizard.tsx / record persistence).
- RUN-BUDGET-STOP — bill pricing, rate-card truth, the ceiling gate HALT, autopilot-approve before spend (vite.film.ts gateStep ~1043, autopilot-approve route ~1605).
- RUN-NO-CONSOLE-ESCAPE — no SHOT CONSOLE escape rendered anywhere (UI surfaces).
