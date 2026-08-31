# colibri debug — asset-forge/templates/index.html (transparency false-negative)

- source: asset-forge/templates/index.html (+ app.py estimate for the paired enhancement)
- model: claude-fable-5 (in-session)
- sha256: d96d25b9cd232aa4948141d7dd395b279325e71d9c6c5325959e3dc298214881 (post-fix bytes)
- date: 2026-08-25
- mode: debug (Phase D)
- context pack: jCodemunch symbol/route reads of app.py `/api/transparency_models` +
  `syncTransparencyModels` JS (shipped hours earlier this session, AF-BUNDLE-ALPHA);
  schema cache dir timeline; live endpoint probe of a fresh compiled exe.

## Failure signal (Damien, 2026-08-25)
"when i choose transparent it says no models are available when i know thats not true."

## Reproduce / characterize
- Fresh compiled exe, cold `/api/transparency_models`: `{"checked":52,"models":[3],"unreachable":0}`
  — server side HEALTHY. The failure is not deterministic in the current environment.
- Schema cache (~/.asset-forge/model_schemas): the one cold sweep wrote ~50 schemas at
  13:25 today; before that the capability sweep had never run.
- The shipped JS: `try{capable=(await fetch(...)).json().models}catch(e){}` →
  `if(!capable.length)` rendered **"no transparency-capable models available right now"**.
  A REJECTED/failed fetch and a genuine all-checked-zero produced the SAME message.

## Hypothesis ledger
1. **CONFIRMED (defect):** the UI conflates "capability check FAILED" with "zero capable
   models exist" — any fetch failure yields a false factual claim. Verified by stubbing
   `window.fetch` to reject in the live page: the old code path renders the
   no-models message (traced; the catch swallows everything).
2. **PLAUSIBLE (his specific trigger):** his page was open in the exe's webview while this
   session killed/rebuilt the server underneath it (two kill/rebuild cycles during the
   capture pass) — a fetch against the dead server rejects → hypothesis-1 path. Cannot be
   re-observed (instance gone); consistent with timeline. Alternative triggers in the same
   class: mid-cold-sweep failure, transient 429s on never-cached schemas.
3. Refuted: token-missing (env var present; live cold call worked), catalog/slug mismatch
   (live call returns the 3), FULL_MODEL_OPTS init race (list populated before first sync).

## Fix (root cause, one variable)
Three distinct zero states, all Generate-locked via the self-tracking transGenLock,
factored through `transRecheck(note,msg)`:
- fetch threw → "could not check which models support transparency — recheck" (never
  claims non-existence);
- models==0 with unreachable>0 → "could not reach N model schemas — recheck";
- models==0, unreachable==0 → the genuine "no transparency-capable models available".
Paired enhancement (Damien's order, same commit): `reproducible` rides EVERY estimate
(server: unconditional `_caps` lookup) and a standalone `#repronote` row surfaces
"this model has no seed — results are not reproducible from a recipe" for ANY seedless
model on ANY background (previously gated on transparent_native).

## Verify (reproducer re-run, live page against the rebuilt exe)
- fetch stubbed to reject + Transparent selected → note = "could not check which models
  support transparency — recheck", Generate disabled, picker untouched (54).
- fetch restored + one recheck click → "transparency-capable models loaded (3) — switched
  to gpt-image-1.5", picker = 3, Generate re-enabled.
- gpt-image-1.5 on WHITE background → repronote shows; flux-dev → repronote clears.
- Battery af_transparency_probe.py 22/22 (new: estimate_reproducible_always,
  ui_honest_check_failure, amended ui_zero_capable_gates_generate); twins + override
  byte-identical; user edition rebuilt; sync_builds green.

## Close
Remediation manifest row AF-TRANS-HONEST-1 (same commit). Registry row AF-BUNDLE-ALPHA
expected-text amended (reproducible-always + three-state honesty).
