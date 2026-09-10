# Guardian vehicle-mode probe — 2026-09-08

Source: work/docking/engine.js, SHA-256 6eb94d7140babbe4d027721813a842e068423fd64ee18f186f6ca572ecc303ff. Actual engine executed without source changes. This is bounded balance evidence, not a fixed regression suite or full-campaign playtest.

## Result

Reacting only when the fixed guardian warning appears is insufficient for a stationary healthy neutral rover, drill/burrower, or submarine. All three take an actual hull hit despite immediate sustained outward input. Flight escapes with zero or 0.1s input delay, but takes a hit with 0.2s delay. Starting to leave at 50% patch heat avoids damage in every tested early/late garden. This is a measured limitation of the requested faster camping punishment and fixed short warning, not evidence that every mode has the same escape window.

## Exact method

Node required the actual frozen scratch engine. For each garden, create seed12345, set gardenIndex, then checkpoint/restore to construct that garden's actual zone and vehicle handling. Set transition=0 and invulnerable=0, retain three lives and the default sixteen neutral white cells. Disable unrelated nextEnemy/nextEmber/nextSpectrum spawning, remove existing ordinary/spectrum pickups, and set player at actual patch center with zero initial velocity. Keep native submarine current. No enemies, buffs, debuffs, manual weapons, safety exemption or synthetic hazard.

Call E.step at default DT=1/60. Strategy A: wait until the engine first reports zone.warning>0, then apply x=1,y=0 on the very next tick and sustain. Direction +x has unobstructed room through each first strike and aligns with the positive submarine current. Capture locked position/radius, first guardian event, distance from locked position, and actual lives. Continue 0.3 seconds after strike to catch delayed collision. Strategy B: begin the same sustained input on the first tick following zone.heat>=0.5; bound the run at240ticks (4seconds) when no strike occurs. Raw results: guardian-mode-probe.json.

## Immediate warning reaction, first strike

Warnings started at1.0000s; strikes at1.4167s. Locked radius62px plus player collision11px requires73px displacement.

| Mode | Gardens (one based) | Distance by strike | Lives after strike |
| --- | --- | ---: | ---: |
| Flight | 1,35 | 100.00px | 3 |
| Rover | 6,50 | 56.95px | 2 |
| Drill / burrower | 26,40 | 71.12px | 2 |
| Submarine | 16,45 | 46.05px | 2 |

Identical outcomes in both representative gardens of each mode. The submarine drifts0.97px during the initial one-second wait and starts warning with vx2.30px/s; distance is measured from the captured warning position, so this small head start is not conflated with escape distance.

## Departing at half heat

Movement began0.5167s after entering the patch in every fixture. All eight runs retained three lives. Flight gardens1/35 and drill garden26 left before warning, so no guardian strike occurred within the4second bounded window. Rover gardens6/50 displaced85.82px after warning lock, drill garden40 displaced93.46px, and submarine gardens16/45 displaced84.26px; each escaped the73px first-strike collision threshold. The patch heat meter therefore supplies an earlier actionable departure signal even where reacting only to the final warning is too late.

## Small reaction-delay probe

Additional actual-engine runs in gardens1,6,26,16 delayed movement by0,6,12ticks after warning (0,0.1,0.2seconds). Raw results: guardian-reaction-probe.json. Flight moved100/76/52px; only0.2s delay took a hit. Rover moved56.95/38.20/21.29px; drill71.12/49.42/28.87px; submarine46.05/30.00/16.44px. Every inertial-mode case took its first hit at1.4167s. No human reaction-time conclusion is asserted beyond these measured schedules.

## Limits and disposition

Neutral healthy craft only; no collision obstacles or enemies, no shot, no buff/debuff, and first strike begins at alert0. Black slowdown, blue direction locks and green steering disruption are expected to make escape harder; cyan thrust may help, and a suitable manual weapon can cancel/cool warnings. These combinations were not measured. Repeated alert growth raises strike radius and may tighten escape further. Actual player behavior, different headings/current phases, approach velocity, fullcampaign balance and all50gardens are not established by this small sample.

No source change requested or performed from this probe. Parent explicitly chose to preserve the measured limitation: faster camping punishment was requested and pre-warning heat is an escape signal. Earlier opening-flight dodge test remains valid; it must not be described as proving warning-only dodging in all four vehicle modes.
