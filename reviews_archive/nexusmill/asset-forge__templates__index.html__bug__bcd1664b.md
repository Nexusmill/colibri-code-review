# colibri-review — asset-forge/templates/index.html (bug) [+ byte-identical asset-forge-user twin]
- model:claude-fable-5 (in-session,max) · sha256:bcd1664badfd8ca6a6b11eb1e0132a8fff31caea3372c48b98e6fc1a1d29f533 · date:2026-07-22 · mode:bug
- context: DeepSeek batch (4 HC) as hints; twin byte-identical + NOT sync_builds-whitelisted (must
  stay identical); Asset Forge = LOCAL single-user Flask app on the user's own machine + Replicate key.
## Verdict
Shipped client template hardened. DOM-XSS was self-XSS today (user's own prompts/names), elevated to
real stored-XSS only if a poisoned name/prompt arrives via an imported/shared library — worth escaping.
## Fixed
**[MED] DOM-XSS: unescaped interpolation into innerHTML** - refgrid (it.id,it.type/name), gallery tile
 (it.file,it.thumb,it.prompt). Added esc() HTML-escaper + wrapped every untrusted field. VERIFIED node --check.
**[MED] boot() unhandled promise rejection** - `boot();` had no catch; a failed /api/options left init
 half-done silently. Added .catch(console.error).
**[MED] poll setInterval leak** - re-running the generate flow without clearing the old interval stacked
 pollers. Added clearInterval(poll) before setInterval.
## Refuted / not-fixed
- [HIGH] "DOM-XSS via location.href in dlSelZip" — REFUTED: r.zip is a server-generated filename, not a
  javascript: sink; it's a same-origin download navigation.
