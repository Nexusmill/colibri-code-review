<!-- source: src/components/SettingsConsole.tsx | reviewer: zcode-glm-5.3 | sha256: 82ec0250e1aa741d05586b6d088615cc6b665c406aa77dd03665105724762fe2 | date: 2026-09-15 | mode: bug -->
<!-- context: Wave 6 FINAL delta review (post design-adversary remediation). Call sites traced live (curl through :4173, harness PASS 75/0/8, vitest 499/499, tsc 0); FEATURES row `route-intelligence` + docs/reviews/route-intelligence-2026-09-15.md are the contract. -->

## Verdict
Shippable - design adversary round 2: B+ SHIP with the two round-2 residuals (failed-reason tooltip clause, "table" noun regression) fixed after the verdict; every armed-state edge the judge tried to break held.

## Fixed since last review (this delta, in session order)
- **[CONFIRMED|FIXED] ok-wins-regardless-of-recency** - a succeeded-then-failed route said "last ran OK" forever; newest verdict wins now, both orders pinned by test.
- **[CONFIRMED|FIXED per adversary round 1] unguarded single-click restore** - first press arms, the chip face becomes `RESTORE "name"?` in the danger color (verb ON the control), 5s window, single armed slot, second press fires.
- **[CONFIRMED|FIXED per adversary round 1] bare x instant delete** - DELETE arms to CONFIRM (the library ruling), aria-label present.
- **[CONFIRMED|FIXED per adversary round 2] failed route's reason had no guaranteed surface** - the row tooltip now carries `the last run through this route failed: <reason> - CHANGE picks another engine`, mirroring GONE's clause; pinned by test.
- **[CONFIRMED|FIXED per adversary round 2] "table" noun regression** in the replaced status - now "current routes and profile".

## Bugs & vulnerabilities (delta)
- None remaining. The armed state machine: one slot, re-arm resets the timer, setArmed(null) precedes every fire (judge tried to break it; clean). failedNewest danger register tie logic (fail.at > ok.at) consistent with the text's (ok.at >= fail.at) on the exact-equal boundary (ok wins both).
