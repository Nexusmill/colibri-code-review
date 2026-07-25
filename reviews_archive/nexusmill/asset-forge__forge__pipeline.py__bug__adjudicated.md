<!-- source: asset-forge/forge/pipeline.py + asset-forge-user/app.py::generate | reviewer: claude-fable-5 (colibri-review G37, verify-first over deepseek-v4-pro batch) | 2026-07-22 | mode: bug | context pack: jcodemunch (make_token/make_serial/public_fingerprint all return str; generate_set 03b56ef validation + glm20-8 manifest-phase guard + INCOMPLETE markers; app.py generate route), live sale run -->

## Verdict
NO code change. pipeline.py's headline CRITICAL and the user-app "formats traversal" HIGH are both
VERIFIED FALSE POSITIVES (blind single-file misses); the remaining pipeline findings are
refuted/accepted, most re-flagging already-remediated guards (03b56ef, glm20-8).

## pipeline.py adjudication
**[CRITICAL] "manifest JSON fails on binary token/serial -> every sale aborts" (88-90,109) — VERIFIED FALSE**
- make_token / make_serial / public_fingerprint all return STR (fingerprint.py: f"{MAGIC}|{_b64e}|{_b64e}",
  keys.py: hexdigest[:16]). The manifest dict holds only str/int/None/dict/list. PROVEN by a live sale:
  generate_set(seamless_pattern/terrazzo, count=2, buyer set) wrote a valid SALE_*.manifest.json that
  json.loads round-trips, item token/serial are str "AF1..."/"AFS1...", manifest_signature present, NO
  INCOMPLETE.txt. Sales work. The reviewer assumed bytes without reading fingerprint.py.
**[HIGH] creator_id path traversal (50) — REFUTED**
- creator_id is never a path component: it flows into the manifest as a json-escaped string value and
  into set_id=sha256(...)[:12]. out_dir (validated separately, 03b56ef family/category guards) is the
  only path input. Source is the local creator key file / display-name update — creator-only trust boundary.
**[MEDIUM] palette/density injection (34,69,105) — REFUTED**
- palette -> pick_palette (returns a builtin only); density -> {..}.get(density,1.0) dict lookup; both
  land in the manifest as json-escaped strings. Colors reach SVG only via hex_to_rgb validation
  (base.py choke point, baab92d/glm20-6). No injection sink.
**[LOW] set_id collision race (52-53) — ACCEPTED (idempotent)**
- set_id=sha256(creator|buyer|base_seed|_ts())[:12]; distinct buyer/seed -> distinct set. Same
  buyer+seed+second producing the same set is idempotent, not a data-loss race. (library_gen's separate
  path already uses uuid suffixes for its many-file case.)

## asset-forge-user/app.py::generate adjudication
**[HIGH] path traversal via `formats` param — VERIFIED FALSE**
- app.py passes formats=tuple(d.get("formats",...)) to generate_set, which consults it ONLY by
  membership: `if "png" in formats` / `if "svg" in formats`, writing hardcoded `{base_name}.png/.svg`.
  Arbitrary/malicious format strings are never iterated into a path — they simply match neither branch
  and write nothing. formats is a membership-tested allowlist by construction. (Route also clamps
  count min(64,max(1,int)), sanitizes family to [alnum_], and downloads go through _safe_under_output.)

## Note
This confirms the AGENT_STATE observation for the DeepSeek batch: the genuine defects were front-loaded
(units 1-6); the 2-HC tail is trending to blind-review false positives / re-flags of closed guards.
Verify-first (G35/G36) each remaining file; do not mass-"fix".
