# DEBUG: PatternSkin named scan "FAILED: ...output(s) but none could be fetched/decoded"

- **Source path:** PatternSkin/ai_parts.py (root cause) + PatternSkin/__init__.py (PATTERNSKIN_OT_ai_parts_semantic) + PatternSkin/replicate_client.py (hardening)
- **Model:** claude-fable-5 (in-session)
- **sha256 (post-fix, first 16):** ai_parts.py be1ea09f6dac379a · __init__.py e7b4c37fbc2cde2b · replicate_client.py eb311bdf798d22be
- **Date:** 2026-08-27 · **Mode:** debug (Phase D ladder)
- **Context pack:** jCodemunch outline + symbol sources (sam3_mask, _load_mask, _decode_mask_red, _check_fetch_url, _replicate_create, _poll_prediction, _sam2_masks, grounded_sam_mask), modal operator source read, remediation manifest consulted (GROK-AI #4 / GROK-AIP2 #1 lineage), obs.py contract read. Version verified live in Blender (loaded module = blender_dev junction = repo bytes, v1.12.0; PIL 12.2.0 present; numpy 2.3.4).

## 1. Failure signal (captured, not guessed)
User report: named scan shows "1/6" repeatedly per piece, ends "Named scan FAI...tput(s) but none".
Replicate account trail (2026-08-27 18:14–18:16 UTC): 3× qwen2-vl captions succeeded; sam3
'wings'→1 mask, 'tail'→1, 'legs'→7, 'head'→1 all succeeded; **'body' (prediction
yfpjqq20tnrmt0d08hr9ekksmw) succeeded with output = 22-byte EMPTY ZIP (PK\x05\x06 EOCD, zero
entries)** → sam3_mask: outs=1, decoded=0 → RuntimeError "…succeeded with 1 output(s) but none
could be fetched/decoded - transient delivery failure…" → modal aborted the whole scan.

## 2. Hypothesis ledger
- **H-UA (delivery fetch bot-blocked)** — REFUTED for replicate.delivery: UA-less probe fetched
  fine. CONFIRMED for api.replicate.com (Cloudflare error 1010 on python-urllib UA) but the addon
  sends UA on all api calls → hardening only.
- **H-PIL (decode dead)** — REFUTED: PIL 12.2.0 live in his Blender 5.1.2.
- **H-EMPTY-ZIP** — **CONFIRMED**: control call prompt 'giraffe' (prediction
  61795jwatdrmw0d08j4tw2gp7w) deterministically returns a 22-byte empty ZIP. SAM-3 packages
  genuine no-match as an empty ZIP; the guard misreads it as delivery failure. Systematic: any
  named scan with one unmatched noun in view 1 dies and discards prior paid votes.

## 3. Fix (root cause, minimal)
- sam3_mask: three outcomes — clean empty ZIP → `clean_empty` (real empty answer, all-False mask,
  cacheable); real fetch/zip/png failures → captured per-output via obs.swallow, raise only when
  `decoded==0 and failures`, message carries reasons. Zip-bomb budget break now recorded as failure.
- Modal: failed grounding call = missed vote (skip+continue; `_covis_done` keeps per-view covis
  honest even when the first noun fails); abort only at 3-in-a-row streak, without caching.
- `_urlopen`/`_rc_urlopen`: inject `User-Agent: patternskin/1.0` when absent (class-closing).

## 4. Verification
- Battery tests/harness/probes/sam3_emptyzip_fixes.py: RED on unfixed code 3/8 (A reproduced the
  exact production failure string), GREEN post-fix **8/8**.
- Live in-Blender (module reloaded): sam3_mask('giraffe') → empty mask, no raise;
  sam3_mask('circle', 256px) → 18,354 true px decoded (expected circle area ≈18.5k). $0.005 total spend.
- Cross-regression ALL PASS: glm_r2_fixes, grok_r2..r6_fixes, glm_sp_fixes.
- G35: remediation manifest row PSK-SAM3-EMPTYZIP + harness row PS-SAM3-EMPTYZIP same commit.

## Refuted findings deleted per Phase 3; H-UA recorded as hardening, not cause.
