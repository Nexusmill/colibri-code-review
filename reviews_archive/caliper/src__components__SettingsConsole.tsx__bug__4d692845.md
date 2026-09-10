<!-- colibri review
source: src/components/SettingsConsole.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: fa6421a7d70a0fd69f076710faa49a9cab84791d2f2456e10d23c0868fa7abe2
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. Delta: per-row TEST key + verdict chip states (SAVED / testing / LIVE with account / DEAD in the danger register via inline style mirroring the green chip's anatomy - .settings-saved is plain CSS so a Tailwind utility would lose the cascade), the runTest status sentences, and the stale-route effect (one catalog fetch per routed service+type, silence when the catalog is away).

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "a stale verdict could linger after CLEAR" - CLEAR flips the row to keyless, which renders the paste box branch; the tests entry only feeds the present-key branch, so a stale verdict cannot display on a keyless row.
## Postscript (adversary round 1 remediation, same session)
Both BLOCK findings fixed at the root: save() now drops the row's stored
verdict on every set/clear (a replaced key is never spoken for by the old
probe), and the stale effect resets types that left the cloud set (a switch
to local can never inherit the danger register; the dead service:type
dedupe folded away). Two regression tests pin both (SettingsConsole.test).
Re-verified: tsc 0, vitest 451/451, build 0, tier pending below, LIVE chip
re-probed through the running app.
(bytes advanced to 5111a736 - this postscript covers the delta)

## Postscript 2 (adversary round 2 remediation, same session)
Round 2's three findings all fixed at the root: (1) runTest carries a
generation counter - a probe whose key was replaced/cleared mid-flight
discards its verdict on resolution (the MEDIUM race the ordered-path test
could not see); (2) the stale effect gained an alive guard - a catalog
fetch whose routes object was replaced before it answered is dropped; (3)
the danger styling/tooltip now gate on the route BEING cloud, beside
routeText's own branch. Regression tests: deferred probe resolved after
clear-paste-save (chip stays SAVED); deferred catalog resolved after the
picker's own in-session cloud->local switch (no flag, no danger style).
(bytes advanced to 8230f53c - this postscript covers the delta)
