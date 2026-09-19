<!-- source: src/providers/modelRoutes.ts | reviewer: glm-5.3-zai-in-session | sha256: dbe64730efe313405323b8dbe59e1607ea2828be7556de2d6478b164dbb3470f | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict

Shippable core, but the hunt found three defects none of the prior reviews (dbe64730 bug, cc62d771 spec, r2 feature, or the twin's 18df6b55) contain: the core's modelless cloud placeholder is consumed by the film engine as an executable route and silently routes a cloud-only machine onto the local GPU, plus two JSON-boundary gaps on the read path.

## Bugs & vulnerabilities

**[MEDIUM] Modelless cloud default leaks LOCAL GPU work on cloud-only machines** - `line 86`
- What: `resolveRoute`'s no-stored-route fallback returns `{backend:"cloud", service:"replicate", cloudModel: undefined}` — a route the module's own `validateRoute` (line 74) rejects. The doc comment (lines 80-81) says this is "what a FORM should use when the user has not chosen", but the twin (vite.routes.ts `resolvedRoute`, called with no `cloudDefault` for image/video) feeds it to the ENGINE as a runnable route. The film engine's guards (`route.service === "replicate" && route.cloudModel`, vite.film.ts lines 776/855/922) skip the cloud branch and fall through to `purgeIfResident("ltx")` + `queueAndWait` — LOCAL ComfyUI work (vite.film.ts lines 814-821).
- Trigger: cloud-only profile, no stored route for image (or video) — e.g. a fresh machine switched cloud-only before any pick, then a manual film produce. Music is safe (passes `base.replicate?.slug` as cloudDefault) and speech throws honestly ("no cloud speech engine routed", vite.film.ts line 986); image/video alone fall through.
- Impact: the exact profile law the gate was built for (2026-09-02: "a stored LOCAL route never resolves on a cloud-only machine") is violated by the default path instead — an unrequested local GPU attempt (VRAM purge included) that either fails confusingly against an absent ComfyUI or, if ComfyUI is up, does local work the profile forbids.
- Fix: either side — `resolvedRoute`/the film image/video paths must throw like speech when `backend === "cloud" && !cloudModel`, or the core should distinguish "no cloud pick" from a resolvable cloud route so consumers cannot mistake the placeholder for executable.

**[LOW] gatedRouteConfig crashes on null-valued route entries the twin's shape check admits** - `line 96`
- What: `r.backend` dereferences every `Object.entries` value unchecked. `readRoutesConfig` (vite.routes.ts lines 63-64) validates only the profile enum and `typeof c.routes === "object"`, so a hand-edited/corrupted `model-routes.json` like `{"profile":"cloud-only","routes":{"image":null}}` passes the read check and throws `TypeError` inside the filter — the entire GET /api/model-routes 500s and `resolvedRoute` (film produce) throws.
- Trigger: out-of-band damage to model-routes.json — the same corruption class the twin's try/catch + shape check exists to defend, incompletely.
- Impact: total routes-endpoint outage on cloud-only (the deck rail, settings, chips all read it), while the identical file under multimodal is tolerated (line 84's `if (stored)` treats null as unset). The null tolerance is inconsistent within this file.
- Fix: filter for truthy routes (`filter(([, r]) => r && r.backend !== "local")`) or validate route values in `readRoutesConfig`. CONFIRMED behavior by trace; PLAUSIBLE trigger.

**[LOW] A stored LOCAL route outlives its bundle — shelf candidates are ignored when a stored route exists** - `lines 83-84`
- What: `resolveRoute` computes nothing from `localCandidates` once `cfg.routes[type]` exists. `validateRoute` (line 70) checks shelf membership only at WRITE time; nothing re-validates on shelf change — Library delete (vite.library.ts) touches no routes — so deleting a bundle leaves `{backend:"local", model:"<gone>"}` resolving forever.
- Trigger: pick a local image/video bundle as the route, delete the bundle in Bundles, run produce (or read the GET `resolved` row, which computes candidates at vite.routes.ts line 134 only to have them ignored).
- Impact: the engine throws at `loadBundle` mid-run (vite.film.ts line 816), and the "resolved" row states a dead model. The cloud twin of this staleness shipped as GONE FROM CATALOG (E-2); the local side has no equivalent.
- Fix: mirror the gate — treat a stored local route whose model is not in `localCandidates` like a gated-out route (fall to the default), either in `resolveRoute` or the twin's `resolvedRoute`. CONFIRMED chain (delete flow touches no routes; loadBundle reads bundles.json by id and throws).

## Missing safeguards

- `validateRoute` declares `type: GenType` (line 64) but never uses it, so no per-type law is enforceable at the write gate — a direct POST can store a cloud route for a non-cloud-runnable type (`llm`, `cloudRunnable: false`); enforcement is picker-side only.
- Garbage-backend routes (neither `local` nor `cloud` from file damage) pass the gate filter at line 96 and are returned verbatim by line 84 — same JSON-boundary family as the LOW above.
- preset-apply (twin, vite.routes.ts line 159) writes the snapshot into model-routes.json without `readRoutesConfig`'s shape validation — a corrupted route-presets.json can replace the live config with a shape every subsequent read silently discards to DEFAULT (a config reset). Distinct from the twin review's accepted route-validity LOW: this is the config-shape hole.

context-pack: prior dbe64730 bug + cc62d771 spec + r2 feature + twin 18df6b55 loaded; consumers traced (vite.routes.ts resolvedRoute/GET, vite.film.ts image/video/music/speech call sites, vite.library.ts delete flow, test pin of the modelless default).
new-findings: 3
