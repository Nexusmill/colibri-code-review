<!-- colibri review
source: src/components/SettingsConsole.test.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 9273a7d350bcae830fd6fd6f1c264754c77eb294cfb9fa7465217f0cedcb3e06
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable after one in-pass fix. New cases: LIVE chip with account, DEAD chip with tooltip + danger style, stale flag on a gone pick, unflagged current pick. The pre-existing CLEAR test clicked the row's FIRST button - TEST now precedes CLEAR in the DOM, so it selects by button text (caught before commit, not after).
## Postscript (adversary round 1 remediation, same session)
Added the two regression cases the gate's findings demanded: verdict-drop on
key replacement (probe DEAD, clear, paste, save - chip says SAVED again) and
danger-register reset when a flagged type switches to local. The replacement
case needed a typed draft (native setter + input event) so SAVE enables.
(bytes advanced to 88b3140f - this postscript covers the delta)

## Postscript 2 (adversary round 2 remediation, same session)
The fresh-mount triviality the gate correctly rejected is gone: the
local-switch test now drives the REAL in-session path (CHANGE -> the
picker's onClose refetch, counter-mocked for StrictMode's double mount)
and holds the catalog fetch on a deferred released AFTER the switch. The
late-probe test holds testKey on a deferred released after save. Both
assert the wrong-answer case would have flagged if applied.
(bytes advanced to 050eadc0 - this postscript covers the delta)
