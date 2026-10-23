# Colibri playability debug: game.js

Source: implementations/emberline/game.js
Reviewer: Codex /root, in-session
SHA-256: 02ce0203c4843e21b97a6aba5da5267a0373676da18cae3b93233084e0b26737
Date: 2026-09-30 06:41 America/Denver
Mode: bug (focused debug modality)
Context: current-byte native reads, jCodemunch source/call paths, owner report, required state/guardrails/feature/remediation/deferred records, prior per-file report, test-first failures and final native checks. See docs/tasks/2026-09-30-emberline-playability.md for cross-file synthesis.

## Verdict
The reported death/pickup defects are repaired in the reviewed delta. This is a focused debug review, not a blanket audit of unrelated UI behavior.

## Bugs and vulnerabilities
- CLOSED, MEDIUM: finish previously put the results overlay over breakup immediately and labeled death “light banked”. Engine hit marks over at zero hull; there is no time-limit reset. The new dying phase shows1.6seconds of projected shockwaves/debris and layered sound, hides intact craft and guards begin/reset. Explicit retry text describes garden-entry rollback. Reduced motion and mute remain supported.
- CLOSED, MEDIUM: physicalPlayer projected z52 while spectrumWorld and loose embers drew at ground coordinates. The shared collection-plane translation now keeps visible relative distance equal to engine planar distance; collected feedback remains distinct from0.8second shield recycling.

## Fixed since last review
Prior reset-menu CLEAR c3cc74a1 concerned a different delta and remains historical. Reset/input/storage assertions still pass after advancing the fixture through the deliberately added death phase. New review findings corrected immediate high-score persistence, preserved pre-run best comparison and cleared destruction when the retry overlay appears. A pickup-height finding was refuted algebraically and with actual movement/canvas tests: identical translation of both endpoints preserves collision distance.

## Adversarial verification
Traced engine hit -> frame -> finish and input -> begin/reset; ordinary bank and final victory are negative controls. Real E.hit and E.step drive UI regressions. Tests cover death caption, expanding projected blast, restart block, immediate best persistence/new-record text, every sampled retry frame without death cues, mute, full/reduced motion, good/red rings and ground/flyer collection. Source checks passed37repository tests,5skips,exit0,unchanged tree,60.862s; all nine Node suites (177 tests plus plain UI assertions). Independent pre-write CLEAR df668f03978244b3abdd774b889a0706.

## Missing safeguards
Live browser visual/listening acceptance and automatic archive-byte readback remain unverified. Canvas/audio-call assertions do not prove subjective explosion quality.
