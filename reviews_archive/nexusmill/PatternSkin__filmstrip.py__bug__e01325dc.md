# colibri gate — PatternSkin/filmstrip.py (grok round 5)

- **source:** PatternSkin/filmstrip.py
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_filmstrip_grok43.md) gated in-session by claude-fable-5
- **sha256:** e01325dc889bcf0b53d74f41c7dbb1160f29107d57cf99a5a056c25865ac85ea (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** bug (grok round 5; delta vs three prior in-session reviews — 795e1c2 fixes pre-declared)
- **context pack:** module role/outline, HIG + paid-generation invariants, 795e1c2 closed findings and the mesh-signature stale-cache docket pre-declared; verification traced keystore.py (secret_get/_secrets_load/_mac_keychain/token_present) and all repo save_text_select call sites.

## Verdict
Shippable; both raw findings kept but each materially corrected by the trace. The
load-bearing one: the GROK-AIP2 #2 billing fix (round 2) covered only ai_parts'
internal wrapper — two direct call sites still swallow the paid-result persist failure
silently, one of them outside this file.

## Findings after adversarial verification

**[MEDIUM, CONFIRMED — billing honesty, scope WIDENED] save_text_select persist failure still swallowed at two direct call sites** — filmstrip.py lines 299-303; sibling PatternSkin/__init__.py lines 6929-6934
- Round 2 (GROK-AIP2 #2, commit 69d0c2e) made `ai_parts.text_select`'s internal persist loud (`_log.error`, ai_parts.py:1436-1443). But `dress_line.modal` (filmstrip.py:300) and the text-select operator's finalize (`__init__.py:6931`) call `save_text_select` DIRECTLY inside their own `try/except: pass` — a persist failure (disk full, permission, cache-dir loss) silently drops the just-PAID sam3 match, and the next dress/select of the same part-word re-bills with no signal to the user. Same defect class as the closed row; different, unfixed call sites — NOT verified-stale.
- Fix shape: mirror the ai_parts pattern at both sites — keep the in-hand result (never raise), log `_log.error("save_text_select failed (%s) - the paid match was NOT cached; re-dressing will re-bill", e)` (filmstrip already has the `_obs.swallow` idiom at line 286 for the free png-cleanup path; the paid path deserves ERROR, not swallow-debug).

**[LOW, CONFIRMED — re-scoped from Grok's crash claim] film_generate.poll does uncached keystore I/O per redraw** — filmstrip.py lines 569-571
- Grok's stated trigger (exception escaping poll) is REFUTED on every Windows path: `_secrets_load` contains corrupt/permission failures by design and its comment explicitly cites the draw path ("they run in the panel draw() (G20/G29)"); `_dec` is guarded at the call site; `_migrate_legacy_token` wraps its reads. Only the macOS `subprocess.run(["security", ...])` branch could raise, and only if `security` itself is missing — theoretical.
- What the trace DID expose: keystore.py provides `token_present(ttl=5.0)` — "Cheap + cached (TTL) so it is safe to call from a Blender panel draw()" — and this poll bypasses it, calling `_read_replicate_token()` raw: disk open + JSON parse + DPAPI round-trip (+ a providers.env scan on the miss path) on EVERY redraw of the panel. Violates the module's own draw-safety design and keystore.py:144's stated contract. Fix: `return token_present()`.

## Refuted and dropped
- Finding 1 as-stated (unhandled exception from poll on keystore permission/corrupt file) — contained upstream by design; see trace above. The line keeps a finding only in the re-scoped perf/design form.
