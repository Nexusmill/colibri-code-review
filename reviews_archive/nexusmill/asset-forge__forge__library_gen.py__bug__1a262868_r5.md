# colibri gate — asset-forge/forge/library_gen.py (grok round 5)

- **source:** asset-forge/forge/library_gen.py
- **model:** grok-4.6 (external, .grok_reviews/2026-08-22_library_gen_grok46.md) gated in-session by claude-fable-5
- **sha256:** 1a26286806a441808f90b9544f5a81c7e0113833e4ed510037c903bedd86810f (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** bug, billing-honesty doctrine pre-declared (grok round 5; delta vs many prior reviews — GROK-CC/OO, tranche-1, LG-4..LG-9, COLIBRI-LIB-1 closures all pre-declared, zero stale rediscoveries)
- **context pack:** module role + invariants + closed/deferred items in the dispatch context file; verification traced _work, _attempt (975-1197), the coordinator consume loop (1242-1330), todo construction (932-933), Stop allocation (941), _billed_generations, build_plan seam_feather stamp (385-392), build_regen_plan, and a repo-wide listing check for .black/.rgba filtering.

## Verdict
NOT clean — the strongest round-5 file. All FOUR raw findings CONFIRMED against source
(no refutations; one severity downgraded for class consistency). The HIGH is a genuine
resume double-charge window in the same family as the already-fixed LG-4.

## Findings after adversarial verification

**[HIGH, CONFIRMED — billing honesty] unguarded quality floor after a billed generate → failed-not-billed item → resume re-bills** — `_attempt` ~1075-1078 (`_quality.check` / `prompt_wants_colour` / `"; ".join(why)` / `metrics.items()`)
- Traced end to end: it is the ONLY post-generate step in `_attempt` with no try/except (the seamless blend above it and every alpha/vector step below are each guarded). A raise (PIL on a truncated/corrupt PNG is the credible path; contract-shape breaks the paranoid one) propagates through `imap_bounded` → coordinator `exc` branch (1243-1247) sets `status="failed"` with `billed_failure` only for `_BilledFailure` → `_billed_generations` counts **0** for a generation that WAS billed (spent_est understates, G19) → the resume queue `todo = [... status != "done" and not billed_failure]` (932-933) re-runs it → `provider.generate` again = **double charge** (the first PNG is overwritten at the same deterministic path, so the money — not the file — is what's lost).
- Fix shape (Grok's, verified sound against the coordinator): wrap the floor in try/except; on raise treat as floor failure (`upd["quality_warning"] = "quality floor crashed: ..."`) and return `(png, hp, upd)` — item lands `done`, billed once, file moves to flagged/ for the user-priced regen menu. Never re-raise after a successful billed generate.

**[MEDIUM, CONFIRMED — post-cancel charge window; downgraded from Grok's HIGH for class consistency with GROK-CC #1] control cancel/pause not consulted inside `_attempt`'s billing loops** — `_work` 970-972 vs the retry ladders (1054+, 429 up to `max_429` with backoff sleeps) and the dual-pass black-frame create (1101+)
- Verified: `Stop` is local to the run (941); `control` is read at run start, at `_work` entry (trips stop), and post-loop — NOWHERE mid-item. After the user cancels, every in-flight worker continues: a 429/transient backoff wakes and issues a NEW paid create, and the dual-pass path STARTS its second paid black-frame generation. Up to `workers` extra billed generations post-cancel; sequential mode included. "Let the in-flight request finish" is recorded doctrine; *starting new creates after cancel* is not.
- Fix shape (verified minimal): beside the two `stop.is_set()` checks at the loop heads, `if control.get("cancelled") or control.get("paused"): stop.trip("control", "paused or cancelled by user")` and take the existing abort path.

**[MEDIUM, CONFIRMED] `build_regen_plan` drops the `seam_feather` stamp** — 737-766
- Verified: `build_plan` stamps `it["seam_feather"] = max(0.004, min(_sf, 0.2))` from the catalog (388-392); `build_regen_plan` performs the SAME type lookup for `expect_colour` (761) but never copies seam_feather, so `_attempt` uses `it.get("seam_feather") or 0.035` (1057) — a PAID fur regen re-applies the wide feather that LIB-SEAM-FUR (3e322fa) exists to prevent, re-introducing the ghosted gutter on exactly the flagged types most likely to be regenerated.
- Fix: apply the identical clamp/stamp after the type lookup in build_regen_plan.

**[MEDIUM, CONFIRMED — narrow trigger] dual-pass failure paths orphan `.black.png`/`.rgba.png` in the flat library** — `_attempt` 1101-1165
- Verified: `os.remove(black)` runs only inside the success path after `os.replace(rgba, png)`. On a solve exception (the "never lose a PAID image" branch) black remains; on an `os.replace` failure rgba remains too; on billed-failure/credit/auth/rate breaks a partially-written black can remain. `search_text` across asset-forge: NOTHING filters `.black.png`/`.rgba.png` from listings — the keying frames surface in the two-folders-images-only flat library (Damien's product contract). Requires dual-pass output + a failure there, hence narrow.
- Fix shape: try/finally around the black-frame work unlinking black (and a leftover rgba) once the deliverable png is decided.

## Refuted and dropped
None this file — first round-5 unit with a 4/4 confirm rate.
