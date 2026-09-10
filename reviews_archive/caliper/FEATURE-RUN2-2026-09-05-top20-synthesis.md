# Feature run round 2 — synthesis (2026-09-05)

20 more single-file feature-mode reviews covering the product surfaces round 1 couldn't
fit: the film wizard front door, the deck, the universal picker, settings, first-run,
the cloud pane, the formula sheet, the three remaining surfaces, the power/kb/comfy
middleware, and the data tier (api/types, bundles/files, provenance). All 20 were fresh
(no cache hits); every add-on adversarially checked with cited lines. Combined with
round 1 (1516d31), 40 of the app's core files now carry feature-mode catalogs.

## Round-2 cross-file findings, ranked

**1. THE PLAN never shows the built world.**
The wizard renders title/adversary/styleBible/shots at THE PLAN (FilmWizard.tsx:1123-1154)
— `record.world` appears nowhere in the file; the world is visible only as the inspector's
collapsed dim ANCHOR line. The ruling-42 plan explicitly included "THE PLAN shows the world
model for approval," and a mis-built constant (wrong hair, wrong height) is discoverable
today only after money spends. With the worldmodel.ts edit-gate add-on (R1), this is the
run's highest-value completion: server pieces all exist (PATCHABLE includes world,
compileAnchor is pure), only the wizard section is missing. [FilmWizard + worldmodel]

**2. The billing-honesty theme gains a second display gap.**
R1 found priceSource computed but rendered nowhere (the bill). R2 finds the one-off cloud
pane never pins duration/resolution for video models (CloudPane.tsx:68-70 pins required +
image only) — the exact class that billed 46 seedance renders at the default tier ($7.01
against a $4.82 quote). The film path fixed it by always sending explicit tier; the pane
still relies on schema defaults. Pin them like image inputs. [CloudPane]

**3. Power lifecycle is asymmetric.**
The app can cycle a RUNNING backend (restart, observed-down-then-up) and kill itself
(POWER OFF) but cannot RAISE a dead one — restart 409s ("start it from the launcher").
A comfy-start action reusing the detached start tail (flags pipeline preserved) closes
the loop; the footer lamp already knows when to offer it. [vite.power]

**4. The delete idiom has one outlier.**
Library delete and run delete are arm-then-confirm pairs with consequences in titles;
bundle remove (BundlesSurface.tsx:79-81) rewrites bundles.json on a single press beside
"edit" in a row of small links. The pair costs nothing and matches the app's own rule.

**5. The retime drawer caps at a dead literal.**
The adjust drawer's seconds input is hardcoded max=12 (FilmWizard.tsx:1393) while the
server accepts the pair's ceiling (15 on the default medium pair) — the same 1-12 literal
the spec-run-#1 fix removed server-side. 13-15s retimes are legal and unreachable.

**6. Install completes unproven.**
R1 flagged no post-download verification server-side; R2 adds the user-facing half — the
first-run wizard moves multi-GB engines onto disk and never offers a one-frame smoke
test, and no free-space read precedes INSTALL on Wan-class packages. [FirstRun]

**7. The palette is navigation-only.**
The app's discoverability surface lists no verbs — OPTIMIZE, FILM/SETTINGS/LIBRARY,
clear queue, unload — all of which exist as truthful store actions. Plus the hotkey
legend both rounds keep asking for. [CommandPalette + DeckControls + App]

## Round-2 add-ons by value (top of the 40+ suggestions)

| Add-on | Value · Effort | File |
|---|---|---|
| THE PLAN world display + edit gate (with R1) | High · S-M | FilmWizard |
| CloudPane pins duration+resolution for video | Med-High · S | CloudPane |
| POWER ON from the app | Med-High · S-M | vite.power |
| Post-install one-frame smoke test | Med-High · S-M | FirstRun |
| Frame capture from video windows → references | Med-High · S-M | MediaView |
| Key liveness TEST per service | Med-High · S-M | SettingsConsole |
| Retime drawer follows the pair ceiling | Med · S | FilmWizard |
| Arm-then-confirm on bundle remove | Med · S | BundlesSurface |
| Duplicate bundle action | Med · S | BundlesSurface |
| Status-well done-line jump + copy diagnostics | Med · S | DeckControls/StatusFooter |
| Per-model value memory + recents | Med · S | ModelPicker/CloudPane |
| Constraint feedback in the formula sheet | Med · S | ReproduceSheet |
| Backup picker (restore by timestamp) | Med · S-M | GraphSurface |
| Script prompt copy affordances | Med · S-M | DocView |
| Superseded-marker convention for wrong measurements | Med · S | vite.kb |
| Palette verb actions | Med · S | CommandPalette |
| Malformed-config surfacing (residual-shelf item) | Med · S | vite.comfy |

## Coverage after two rounds

40 files reviewed in feature mode. Deliberately still uncovered (the long tail):
DeckControls' widget children (Stepper/ScrubInput/OrnateSlider/Latch/Icons), ChassisNav,
Rail, AdvancedDrawer (its behavior is reviewed via the BundlesSurface/schema reviews),
generateStore, routesStore, assetsStore, the api/* client family beyond client.ts, the
providers beyond modelRoutes (openrouter/replicate/eachlabs adapters), the film pure
modules (analysis, budget, produce, joins, grader, adversary, calibrate, i2v,
storyboard-doc), vite.tokens/keys/routes/replicate/openrouter/eachlabs/library/bench,
arcadeSound, power/state, workflows/fill+toUiGraph, install/{catalog,plan,tiers,client},
llm/{client,tools}, kb/{bm25,chunk}. The pure film modules in particular are a natural
round 3 (they carry the run's arithmetic).
