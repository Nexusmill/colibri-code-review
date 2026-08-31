Source: Spector/templates/index.html
Reviewer: claude-sonnet-5 (in-session)
sha256: 96c6e5fa31a6bde0e1bf1bf2fa1fd20b5a574770549ac064d9519619fc5ed894 (POST-FIX)
Date: 2026-08-07
Mode: bug (FIRST review - never in .colibri_reviews/_manifest.json)
Context pack: full 176/187-line file read; confirmed via search_text this is the sole
render_template() target in Spector/app.py (line ~417) and is served with NO Jinja variables
(a fully static shell, all dynamic content injected client-side via fetch()+innerHTML) so the
only injection surface is client-side string interpolation, not server-side template injection;
traced the `name` field's full provenance end to end through Spector/app.py's /api/ingest
(os.path.splitext(f.filename)[0], NOT the secure_filename()-sanitized `safe` variable that sits
right next to it in the same function) and Spector/warehouse.py's _clean_row (.spectorpack
import path - _s() truncates to 1024 chars, never strips HTML); checked docs/DESIGN_BIBLE.md /
prior asset-forge template reviews for the established esc()-everywhere pattern this file now
matches.

## Verdict
Was NOT shippable as found - a confirmed, evidence-backed stored XSS via the part `name` field,
reachable via ordinary file upload (attacker sets the filename) or via importing an untrusted
.spectorpack (a documented sharing feature). Fixed in this pass; now shippable.

## Bugs & vulnerabilities

**[HIGH] Stored XSS via part name in tile()** - `tile()` (JS, was ~line 98-106)
- What: `p.name` (attacker-controlled - see provenance above) was spliced unescaped into two
  places inside an HTML template-literal string that both `refresh()` and the find-results
  handler assign via `.innerHTML =`: `<div class="nm">${p.name||p.id}</div>` (zero escaping at
  all) and `onclick="delPart('${p.id}','${(p.name||p.id).replace(/'/g,"\\'")}',this)"` (escaped
  single quotes only, but that value sits inside a DOUBLE-quoted HTML attribute, so a bare `"`
  in name breaks out of the attribute and injects arbitrary markup/handlers).
- Trigger: upload a file whose filename contains e.g. `<img src=x onerror=...>` (HTTP multipart
  filenames are attacker-set strings, not filesystem-constrained), or import a .spectorpack
  whose `name` column was crafted the same way (_clean_row never HTML-sanitizes it).
- Impact: arbitrary JS executes in the Spector desktop webview on library refresh or after a
  find - same-origin access to every /api/* endpoint (delete, backup-to-arbitrary-folder,
  export/reproduce), i.e. a full same-session compromise of the local app's data.
- Fix (applied): added `esc()` (HTML-entity escaping of `&<>"'`) and applied it to every
  reflected field (id/name) in every template-literal insertion point. Replaced the inline
  onclick-with-string-building pattern with a `data-id`/`data-name` attribute pair (itself
  esc()'d, so only single-layer HTML-attribute escaping is ever needed) plus one delegated
  `click` listener on `document.body`, eliminating the two-layer HTML-attribute-vs-JS-string
  escaping that was the second, independently-broken vector. Behavioural proof
  (junk/hunt_verify_index_html_esc.js): pre-fix both a live `<img onerror>` and the attribute
  breakout were reproduced and confirmed live; post-fix both are neutralized, and an
  esc()->browser-decode round trip reproduces the original name exactly (legitimate names still
  display correctly).

## Missing safeguards
- `tags` (also foreign/attacker-controlled via the same two paths) is never rendered anywhere in
  this template - confirmed by full-file read - so it carries no XSS risk today, but it is
  stored with the same lack of server-side sanitization; if a future UI change ever displays
  `tags`, apply `esc()` to it too rather than assuming it is safe by precedent.
