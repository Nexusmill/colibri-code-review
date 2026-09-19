# Emberline — ten-file Colibri feature synthesis

Date: 2026-09-16
Mode: feature (proposals only)

## Scope and evidence
Reviewed ten core runtime files individually, then synthesized their relationships. Native broker reads supplied exact UTF-8 bytes and whole-file hashes; a separate reread of all ten found unchanged hashes. Native jCodemunch outlines, current callers, project ledgers, README, progression/combat request and selected test assertions supplied context. No prior feature-mode cache entries existed. Runtime tests, browser rendering, physical input and listening were not performed for these proposals.

The current working tree includes uncommitted primary-fire/drone/hunter/progression code. These reviews cover those working bytes; they are not an endorsement or release of that separate work. The progression task's old statement that implementation has not begun is stale relative to code; its authoritative requirements still guide this review.

## Ranked cross-file recommendations

| Rank | Lead module | Proposal | Value | Effort | Individual report |
| --- | --- | --- | --- | --- | --- |
| 1 | game.js | Primary fire on touch and gamepad | High | M | [Review](implementations__emberline__game.js__feature__c4c6cb06.md) |
| 2 | engine.js | Primary-weapon progress and upgrade feedback | High | S | [Review](implementations__emberline__engine.js__feature__306ea0d9.md) |
| 3 | music.js | Lower soundtrack volume while Iris speaks | High | S | [Review](implementations__emberline__music.js__feature__aaa191ad.md) |
| 4 | voice.js | Captions that can stay on with voice audio off | High | M | [Review](implementations__emberline__voice.js__feature__3121593a.md) |
| 5 | index.html | A pause-accessible flight manual and current objective card | High | S | [Review](implementations__emberline__index.html__feature__8797c66d.md) |
| 6 | gardens.js | Briefings that explain the actual encounter role | High | M | [Review](implementations__emberline__gardens.js__feature__ff056a7a.md) |
| 7 | spectrum.js | Explain the next queued packet before it recycles | High | M | [Review](implementations__emberline__spectrum.js__feature__f343606f.md) |
| 8 | terrain.js | Distinct traversable layouts for habitat families | High | L | [Review](implementations__emberline__terrain.js__feature__d234643f.md) |
| 9 | world3d.js | Optional terrain readability overlay | Med | M | [Review](implementations__emberline__world3d.js__feature__534f6a83.md) |
| 10 | civilizations.js | An automatically unlocked civilization field journal | Med | M | [Review](implementations__emberline__civilizations.js__feature__888c03d5.md) |

## Integration and sequencing
1. Control access and combat feedback: game.js owns primary input aggregation; engine.js supplies one primary-progress calculation; index.html supplies semantic controls and contextual help. Keep held primary input separate from edge-triggered FIFO reserve input. The field manual and progress UI are one integrated improvement, not duplicate implementations.
2. Narration clarity: music.js needs a gain control, voice.js already emits onDuck, and game.js must connect them. Caption-only mode is a separate voice scheduling change; it must not duck music when no speech plays. Existing global mute, pause, hidden-tab and cancellation behavior remain explicit tests.
3. Better decisions during play: gardens.js briefings must describe actual encounter roles; spectrum.js owns next-packet prediction so UI does not reimplement replacement logic. Conditional forecasts must not promise outcomes after intervening cleansing or pickups.
4. Larger content work: terrain.js templates and world3d.js readability should share collision geometry and retain HOME/pad/resource reachability. Civilization discoveries can add campaign flavor afterward without unlocking level selection or craft choice.

## Verification limits and invariants
CONFIRMED in individual reports refers to traced code structure or missing integration, not measured player value. Product benefit and subjective clarity are proposals requiring playtesting. No fresh bug/spec clearance, feature implementation or gameplay test pass is claimed. Preserve sequential gardens, curated vehicles, unlimited Ctrl primary, manual oldest-first reserve, saved progress compatibility, plentiful reachable opening resources, offline operation and mute/reduced-motion behavior.

No paid optional second-opinion review was commissioned. Report writes use the repository's mandatory independent pre-write review; any closing commit must pass its separate automatic gate. Per-mode cost 0 records in-session feature-review cost, not the cost of mandatory repository gates.

## Historical manifest timestamp migration
All 48 old mode records retain their original SHA, output path, cost and mode. Timezone-aware timestamps are converted to America/Denver minute precision. Twelve date-only timestamps are represented as 00:00 solely to satisfy the schema; their true time of day is unknown. Original values are retained below so this does not manufacture historical evidence.

| File | Mode | Original reviewed_at | Canonical reviewed_at |
| --- | --- | --- | --- |
| implementations/emberline/engine.js | bug | 2026-09-08T19:20:00.760455+00:00 | 2026-09-08 13:20 |
| implementations/emberline/engine.js | spec | 2026-09-08T19:20:00.760955+00:00 | 2026-09-08 13:20 |
| implementations/emberline/engine.js | quality | 2026-09-08T19:20:00.760955+00:00 | 2026-09-08 13:20 |
| implementations/emberline/engine.test.cjs | bug | 2026-09-08T18:47:48.225Z | 2026-09-08 12:47 |
| implementations/emberline/engine.test.cjs | spec | 2026-09-08T18:47:48.225Z | 2026-09-08 12:47 |
| implementations/emberline/engine.test.cjs | quality | 2026-09-08T18:47:48.225Z | 2026-09-08 12:47 |
| implementations/emberline/spectrum.js | bug | 2026-09-08T13:48:10.782746+00:00 | 2026-09-08 07:48 |
| implementations/emberline/spectrum.js | spec | 2026-09-08T13:48:10.782746+00:00 | 2026-09-08 07:48 |
| implementations/emberline/spectrum.js | quality | 2026-09-08T13:48:10.782746+00:00 | 2026-09-08 07:48 |
| implementations/emberline/spectrum.test.cjs | bug | 2026-09-08T18:47:48.226Z | 2026-09-08 12:47 |
| implementations/emberline/spectrum.test.cjs | spec | 2026-09-08T18:47:48.226Z | 2026-09-08 12:47 |
| implementations/emberline/spectrum.test.cjs | quality | 2026-09-08T18:47:48.227Z | 2026-09-08 12:47 |
| implementations/emberline/game.js | bug | 2026-09-09T03:47:25.059654+00:00 | 2026-09-08 21:47 |
| implementations/emberline/game.js | spec | 2026-09-09T03:47:25.060153+00:00 | 2026-09-08 21:47 |
| implementations/emberline/game.js | quality | 2026-09-09T03:47:25.060651+00:00 | 2026-09-08 21:47 |
| implementations/emberline/index.html | bug | 2026-09-09T03:47:25.061152+00:00 | 2026-09-08 21:47 |
| implementations/emberline/index.html | spec | 2026-09-09T03:47:25.061651+00:00 | 2026-09-08 21:47 |
| implementations/emberline/index.html | quality | 2026-09-09T03:47:25.061651+00:00 | 2026-09-08 21:47 |
| implementations/emberline/style.css | bug | 2026-09-08T19:02:05.701585+00:00 | 2026-09-08 13:02 |
| implementations/emberline/style.css | spec | 2026-09-08T19:02:05.702588+00:00 | 2026-09-08 13:02 |
| implementations/emberline/style.css | quality | 2026-09-08T19:02:05.703091+00:00 | 2026-09-08 13:02 |
| implementations/emberline/ui.test.cjs | bug | 2026-09-09T03:47:25.062152+00:00 | 2026-09-08 21:47 |
| implementations/emberline/ui.test.cjs | spec | 2026-09-09T03:47:25.062652+00:00 | 2026-09-08 21:47 |
| implementations/emberline/ui.test.cjs | quality | 2026-09-09T03:47:25.063152+00:00 | 2026-09-08 21:47 |
| implementations/emberline/music.js | bug | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/music.js | spec | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/music.js | quality | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/music.test.cjs | bug | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/music.test.cjs | spec | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/music.test.cjs | quality | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/terrain.js | bug | 2026-09-08T18:47:48.223Z | 2026-09-08 12:47 |
| implementations/emberline/terrain.js | spec | 2026-09-08T18:47:48.224Z | 2026-09-08 12:47 |
| implementations/emberline/terrain.js | quality | 2026-09-08T18:47:48.224Z | 2026-09-08 12:47 |
| implementations/emberline/terrain.test.cjs | bug | 2026-09-08T19:20:00.761957+00:00 | 2026-09-08 13:20 |
| implementations/emberline/terrain.test.cjs | spec | 2026-09-08T19:20:00.762456+00:00 | 2026-09-08 13:20 |
| implementations/emberline/terrain.test.cjs | quality | 2026-09-08T19:20:00.762456+00:00 | 2026-09-08 13:20 |
| implementations/emberline/voice.js | bug | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/voice.js | spec | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/voice.js | quality | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/voice.test.cjs | bug | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/voice.test.cjs | spec | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/voice.test.cjs | quality | 2026-09-08 | 2026-09-08 00:00 (time unknown) |
| implementations/emberline/world3d.js | bug | 2026-09-08T19:02:05.705094+00:00 | 2026-09-08 13:02 |
| implementations/emberline/world3d.js | spec | 2026-09-08T19:02:05.705094+00:00 | 2026-09-08 13:02 |
| implementations/emberline/world3d.js | quality | 2026-09-08T19:02:05.706097+00:00 | 2026-09-08 13:02 |
| implementations/emberline/world3d.test.cjs | bug | 2026-09-08T19:02:05.706600+00:00 | 2026-09-08 13:02 |
| implementations/emberline/world3d.test.cjs | spec | 2026-09-08T19:02:05.707101+00:00 | 2026-09-08 13:02 |
| implementations/emberline/world3d.test.cjs | quality | 2026-09-08T19:02:05.707600+00:00 | 2026-09-08 13:02 |
