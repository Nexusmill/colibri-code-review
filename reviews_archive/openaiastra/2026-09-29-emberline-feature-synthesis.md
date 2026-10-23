# Emberline — top-ten Colibri feature reassessment

Date: 2026-09-29 10:41 America/Denver
Reviewer: GPT-6 Codex /root, in-session primary reviewer
Mode: feature; recommendations only

## Outcome and scope
Ten core units reviewed individually: engine.js, game.js, gardens.js, spectrum.js, terrain.js, world3d.js, civilizations.js, music.js, voice.js and index.html. This follows the original core-file scope; CSS/tests/tooling are supporting context, not replacement units. There are four new lead ideas and six explicitly developed from older optional suggestions. The earlier ten main features remain closed. No gameplay, test, asset, preference or checkpoint bytes were changed.

Nine files match their feature-cache SHA; the owner's request for another run was interpreted and announced as a forced reassessment. voice.js changed with Emma narration and cleansing queue continuity. Matching-hash reports retain their prior closure verbatim under a historical section; the changed voice report uses a new hash-keyed path and preserves its old report. Latest report findings are proposals, not defects or newly implemented features.

## Ranked opportunities
Value and effort are reviewer estimates, not measured user outcomes. S means a localized integration, M means several runtime/UI/test surfaces. Each row has a lead module, not exclusive file ownership.

| Rank | ID | Lead module | Proposal | Value | Effort | Provenance | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | F10 | index.html | Visible checkpoint status and portable checkpoint backup | High | M | New | [Report](implementations__emberline__index.html__feature__cdf86b34.md) |
| 2 | F2 | game.js | Remappable keyboard actions and controller dead zone | High | M | New | [Report](implementations__emberline__game.js__feature__3dae2db7.md) |
| 3 | F4 | spectrum.js | Conditional cleansing planner | High | M | Carried forward, refined | [Report](implementations__emberline__spectrum.js__feature__6cf2bc83.md) |
| 4 | F5 | terrain.js | Active drilling progress and contact feedback | High | S | New | [Report](implementations__emberline__terrain.js__feature__b193b562.md) |
| 5 | F9 | voice.js | Full and concise navigator modes | High | M | Carried forward, refined | [Report](implementations__emberline__voice.js__feature__a4fbc3a6.md) |
| 6 | F1 | engine.js | Per-garden delivery debrief | High | M | Carried forward, refined | [Report](implementations__emberline__engine.js__feature__00c4c12d.md) |
| 7 | F8 | music.js | Saved music level that composes with narration ducking | Med | S | Carried forward, refined | [Report](implementations__emberline__music.js__feature__6ad8aa98.md) |
| 8 | F7 | civilizations.js | Illustrated encounter reference in the journal | Med | M | Carried forward, refined | [Report](implementations__emberline__civilizations.js__feature__f8966353.md) |
| 9 | F3 | gardens.js | Read-only campaign milestone trail | Med | M | Carried forward, refined | [Report](implementations__emberline__gardens.js__feature__3583a896.md) |
| 10 | F6 | world3d.js | Optional player visibility through foreground terrain | Med | M | New | [Report](implementations__emberline__world3d.js__feature__56721bd4.md) |

## Recommended sequence and dependencies
1. Make recovery explicit: F10's persistent-versus-session-only save status is the smallest useful first slice. Add checkpoint backup only after a validated import preview/cancel design. Entry-save semantics must remain visible; developer replay traces already exist and are not portable entry saves.
2. Improve control and in-play decisions: F2 keyboard bindings/dead zone, F4 conditional cleansing information and F5 actual drill-contact progress. These preserve the existing simulation. F4 must state queued packets can change its estimate; F5 must derive progress from contacted terrain, not a cosmetic timer.
3. Let players tune narration/audio: F9 Full/Concise using the existing recordings, then F8 music level that composes multiplicatively with duck state. Keep warnings, silent captions, current-reset continuity, mute and hidden/pause behavior intact. F8's gain target is explicitly zero while globally or individually muted; volume and duck updates share that gate.
4. Add reflection and campaign context: F1's accurate per-garden debrief provides completion facts for F3's read-only trail. F7 extends the existing culture journal with current-region encounter cards; species appearance must never override drone/hunter role evidence.
5. Prototype F6 only after actual browser scenes show useful actor-visibility behavior. Source drawing order supports this idea, but this run does not establish a visibility defect. Use existing actual-game canvas audits rather than a second renderer.

## Adversarial findings and exclusions
The review explicitly checked existing features before proposing additions. Touch/RT primary, progress, ducking, silent captions, manual/objective, role-aware briefings, next-packet forecast, habitat terrain, footprint guide and culture journal already exist. No repeat implementation is requested. Fixed Emma cleansing interruption is not reopened. Existing end-of-expedition statistics are not per-garden debriefs; existing three-second dwell is not a full-cleansing ETA; existing footprint guides are not player visibility above foreground art.

A campaign tracker cannot unlock route/craft selection. All fifty stages remain sequential with assigned vehicles. A portable save must export the actual stored entry checkpoint, not claim to reproduce a mid-flight simulation. No cloud services, new art generation, paid optional feature-review model, new rewards, control macros, or balance changes are included.

## Evidence and validation boundaries
Native jCodemunch resolved local/OpenAIAstra, supplied the bounded tree, per-file outlines and importers. Browser global callers were traced in exact current source because import counts omit them. Native broker reads supplied current UTF-8 bytes and full SHA-256; each file was read end to end and separately reread for adversarial verification. All ten matched on the second read. Project state/activity, guardrails, three ledgers, README, earlier reports/synthesis and the progression request supplied contracts/history. The old untracked progression task's 'not begun' status is historical and contradicted by current source/closure records; its sequential/assigned-craft request remains applicable.

Baseline native run_checks: 37 repository tests, five skips, exit 0, tree unchanged. This validates existing code, not proposed behavior. Returned output includes expected temporary-fixture deny cases and ResourceWarning messages; they did not make the suite fail. Final post-documentation checks/readback and the explicit-path automatic Git gate are recorded by the closing task/commit, not presumed here.

No live browser, physical-controller/touch, human listening/retention or automatic archive-byte acceptance is claimed. Native semantic retrieval worked against E:/repo-memory/openaiastra (584 rows initially, auto-index reported off). Shell/global-file reading, using-superpowers catalog entry, the optional composite context call and clock tool were unavailable/refused; supported repository reads supplied task context. No protections were bypassed. The two pre-existing untracked files remain outside this review tranche.

## Source inventory

| Source | Full SHA-256 |
| --- | --- |
| implementations/emberline/engine.js | 00c4c12d12b3ad531bdabc6f6dc199286f78df4f774d553636bf079ab009ee85 |
| implementations/emberline/game.js | 3dae2db7b79f291b9de393fd75251f29c2862c435841ddcf1710c75bf5756597 |
| implementations/emberline/gardens.js | 3583a896261211b47ed7d97904246f4bdedc813517c48f23bd4be7089f068557 |
| implementations/emberline/spectrum.js | 6cf2bc834c6417996297ab7b8a5dfbaad423c4fb01e009bbe563c5145124bd6f |
| implementations/emberline/terrain.js | b193b5625adfcc1f756d04fcf268d9363723c2efa841459eb636bb121a98e8ef |
| implementations/emberline/world3d.js | 56721bd4398b969e8027b26ac0b3efbfbfd1c22ce41a5e75804d9d2a3057a232 |
| implementations/emberline/civilizations.js | f89663533d93613693a23076e8d2845fba3e136ee11414db11ea3d760f60aa11 |
| implementations/emberline/music.js | 6ad8aa985adcfefdf60aba3ab0b5c99ae4c2f71724819d7d292e1f14f6a05877 |
| implementations/emberline/voice.js | a4fbc3a6430b82f4c2d9e878b3bca957f1a22acb682b356a13ed7ff63bd2551d |
| implementations/emberline/index.html | cdf86b346f32a929571f546150b9a3738f143d01399dad9abcd2859f38a0d147 |

Per-mode manifest cost 0 describes in-session feature review only; mandatory independent write/commit gate costs are not measured here.
