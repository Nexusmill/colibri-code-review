# Real engine / Iris functional integration probe — 2026-09-08

This is functional acceptance, not a self-review of engine source. Production untouched. Real frozen engine, terrain, shield rules and voice modules executed together. Only the HTMLAudioElement boundary was faked. Firstprobe completed audio according to actual WAV durations in voice-manifest.json; frameorder mirrors UI: E.step, voice.update with actualcounts/time/docking/timer, then handleEvent for actual engineevents. A secondprobe independently checked actualcaption strings against English remainingcounts.

## Results
PASS: sixteen blackcells, submarine garden15, starting x139/y485 with residualvx30. Dock atframe1 announces sixteen. Firstremoval/callout at3s says oneblackremoved,fifteenremain; eachsubsequent180frames removesexactlyone; finalat48s says oneblackremoved,allclear. Exactly16removalclips and16matching captionstrings, all15→0remainingvalues verified. Position remains139,485.

PASS: goldpickup collected atframe1 producesnoadded announcement then; actualrecycle at0.8s emits exactlyone added-gold-2.wav. Actualshield event drives announcement.

PASS: onevioletpacket creates2cells and19secondcycle. Actualtimer crosses10remaining atsimulation9.0s, exactlyone teleport-10.wav starts. Movingto violetstation before nextframe keepsremaining9.999999999999872 unchanged, immediatelycancels warning;120moreparkedframes preserve timer anddo not repeatwarning.

Actual outputs: firstreset2.9999999999999942,last47.99999999999856 (expectedbinary floatingpointseconds). Assertionsuse exact180framecadence, notrounded timestamps. Nodeprobes exit0. No browserhearing/visual rendering claim; parentowns thatacceptance.

## Exact source hashes
- engine.js: c7ee052410977cc94870a6c496614cb2c8f4a05d633c99ebb00a3ca202c4b876
- terrain.js: d234643fabfe42ad6335c976bbe4c4afeebdd144afa8043e75e2d1d2afed012a
- voice.js: 3121593a917c09e147e8e6121015f266838786902f64b0abd60d11fc06b653f8
