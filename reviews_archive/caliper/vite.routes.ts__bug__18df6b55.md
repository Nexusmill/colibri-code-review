<!-- source: vite.routes.ts | reviewer: zcode-glm-5.3 | sha256: 18df6b556cee59a3aab1a476fb8c606074e7326d5de66090e65d975e83fb9900 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation + adversarial commit gate __proto__ catch). Live evidence: harness PASS 75/0/8 with the __proto__ pin, vitest 499/499, tsc 0. -->

## Verdict
Shippable - the two stores (route health, route presets) are fire-and-forget memory by design and never gate a run; the adversary gate's prototype-pollution catch is fixed and pinned through the real app.

## Fixed since last review (this delta)
- **[CONFIRMED by the adversarial commit gate|FIXED] `__proto__` preset name polluted the presets record** - the name regex admits it (all word chars) and on a plain JSON.parse object `presets["__proto__"] = config` invoked the inherited setter (the save silently never persisted) while `name in presets` walked the prototype chain (a FIRST save answered replaced:true - the dishonest-success this wave exists to prevent; a direct preset-apply POST could even reset the routes table). FIXED: readPresets returns null-prototype records on both paths - the name lands as an OWN key, `in` sees only own keys, save/apply/remove/serialize all behave. Pinned by the harness through the real server: a preset literally named __proto__ saves with the honest "saved" status, renders as a chip from the server's own list, and the armed delete removes it.

## Bugs & vulnerabilities (delta)
**[LOW|PLAUSIBLE] read-modify-write race on the JSON stores** - fire-and-forget stamps under concurrent callers could lose one update; serialized in practice (one ACTIVE run; preset clicks client-serialized). Memory only, never a gate.
**[LOW|CONFIRMED behavior, accepted] preset-apply bypasses validateRoute** - presets are self-authored snapshots; the read side shape-validates; stale cloud picks surface as GONE FROM CATALOG.
- `replaced` computed BEFORE the write on an own-key check - server truth, not client inference; API-pinned.
