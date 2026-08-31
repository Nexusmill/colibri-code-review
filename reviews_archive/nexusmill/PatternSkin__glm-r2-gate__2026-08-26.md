# colibri gate — GLM 5.3 round-2 external review (psk-glm-review @ a45bd03)

- source: 14 review units in psk-glm-review/.colibri_reviews (snapshot @ Nexusmill 7696f88)
- model: claude-fable-5 gate over GLM 5.3 (ZCode) reviews · date: 2026-08-26 · mode: gate+debug
- context pack: every finding re-traced against CURRENT Nexusmill bytes (== snapshot bytes,
  G36); http.client MRO verified live; Blender 5.1 bundled numpy verified live (2.3.4);
  keystore.py marker mechanism read end-to-end; __init__.py property declarations checked.

## Verdicts (every finding gated)
- **replicate_client MEDIUM (HTTPException escapes billed framing, create+poll)** —
  **CONFIRMED** (MRO: IncompleteRead/BadStatusLine/LineTooLong are HTTPException, not
  OSError; live repro: monkeypatched urlopen raising IncompleteRead escaped
  _replicate_generate raw). FIXED → remediation row GLM-R2-BILLFRAME.
- **ai_parts MEDIUM (same class at _replicate_create)** — **CONFIRMED** (same trace).
  FIXED → GLM-R2-BILLFRAME.
- **keyvault MEDIUM (macOS migrate_and_shred orphans Keychain markers)** — **CONFIRMED**
  (_dec('keychain') → "" by design → orphaned → dat deleted → marker destroyed). FIXED →
  GLM-R2-KEYCHAIN (resolve markers via _legacy_keychain_get; keep dat on unresolved).
- **ai_select LOW (auto_min_views missing bounds guard)** — **CONFIRMED**. FIXED →
  GLM-R2-LOWS.
- **obs LOW (timed_call guard misses async def)** — **CONFIRMED** (latent). FIXED →
  GLM-R2-LOWS.
- **heightmap LOW [reviewer: PLAUSIBLE] (NEP-50 float64 promotion)** — **UPGRADED to
  CONFIRMED-on-runtime**: Blender 5.1 bundles numpy 2.3.4 (live check). FIXED →
  GLM-R2-LOWS (float() pins).
- **filmstrip LOW [PLAUSIBLE/ASSUMPTION] (FS-1 needs ai_parts_active min=-1)** —
  **REFUTED as a live risk**: PatternSkin/__init__.py:1847 declares
  `IntProperty(name="Part", default=-1, min=-1, ...)`. No change; recorded here so it is
  not re-fixed.
- **keyvault safeguard note (_list_entries unknown-error → empty)** and **ai_parts
  safeguard note (download byte-cap mirror)** — noted, deliberately NOT fixed this round
  (defense-in-depth suggestions, no defect); candidates for a future quality pass.
- All 14 units' "Fixed since last review" ledgers spot-checked — consistent with the
  remediation manifest; zero stale re-reports (the REVIEW_BRIEF ledger worked).

## Review quality note
GLM 5.3 round 2: 7 findings raised, 6 confirmed (one upgraded), 1 refuted-by-fact that the
reviewer itself labeled ASSUMPTION and scoped correctly. Zero noise findings. On par with
the best sweep rounds.

## Verification
Battery tests/harness/probes/glm_r2_fixes.py 11/11 (functional repros for every fixed
class + vendored-x3 guard). Cross-regression ALL PASS: keyvault x6, grok_r2 (incl.
headless-Blender transport battery), grok_r5, grok_r6(+_bpy), grok_ai_billing. User
edition rebuilt (keyvault vendored); sync_builds green.
