<!-- source: src/install/catalog.ts | reviewer: glm-5.3-zai-in-session | sha256: a3dd0c50685410d5a8460a0121722c37289746f22ea32ab083b9e093795e12e4 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

## Verdict
Not shippable as-is: the 2026-09-15 gate that made `bytes` an enforced exact-match pin retroactively hardened five MiB-rounded display values into hard pins, and those pins do not equal the artifacts their URLs serve — every affected brain download now completes and then deletes itself, forever. (Systemic pattern confirmed with live ground truth; the only entry that survives is the sha-pinned qwen3-4b — its byte pin 2,497,280,736 matches the tree API exactly, proving the author's exact-size discipline was applied only there.)

## Bugs & vulnerabilities

**[HIGH] MiB-rounded `bytes` pins are enforced as exact sizes — five catalog brains can never install** - `lines 68, 77, 86, 95, 112`
- What: Six `LLM_MODELS` entries pin `bytes: N * 2**20` (whole-MiB roundings authored 2026-09-06 as approximate shelf listings, commit 1ea5c7a). The 2026-09-15 remediation made `bytes` a hard post-landing check (`sizeVerdict` strict `===` in `vite.caliper.ts:629`, file deleted + thrown on mismatch) fed directly from these entries at `vite.llm.ts:372` (`{ bytes: entry.bytes, sha256: entry.sha256 }`). Verified live against the HF tree API today: `gemma-3-4b-it-Q4_K_M.gguf` serves **2,489,757,856** bytes but line 68 pins 2374 MiB = **2,489,319,424** (438,432 off); `LFM2-8B-A1B-Q4_K_M.gguf` serves **5,044,779,712** but line 77 pins 4811 MiB = **5,044,699,136** (80,576 off). Lines 86, 95, 112 are the same construction and near-certainly wrong too (real GGUFs almost never land on exact MiB boundaries; the one grounded entry, line 58, uses a non-round exact byte count 2,497,280,736 — confirmed exact — plus a sha256).
- Trigger: User picks any of gemma-3-4b-chat, lfm2-8b-fast-chat, qwen25-coder-7b, nemotron-nano-4b, or qwen3-coder-30b in MORE MODELS (all pass `isCatalogBrain`, `vite.llm.ts:366`).
- Impact: A multi-GB download (16.6 GB for the coder-30b) runs to completion, is deleted by the verifier, and the job errors with a false "truncated or substituted transfer" sentence — a truthful-status violation and an unretryable-out install loop. Side effect: `totalBytes: entry.bytes` (`vite.llm.ts:367`) also under-reports the progress denominator past 100%.
- Fix: Re-pin exact tree-API byte sizes for lines 68/77/86/95/112 (and 104/121, same rounding, currently off the enforced path) — or, better, ground them with sha256 pins like line 59 so the pin class has a second factor. A test asserting no enforced `bytes` pin is exactly divisible by 2**20 would hold the line.

## Missing safeguards
- `serveCtx` (line 255) has no floor: a future entry with `contextTokens: 0` or negative serves `-c 0` to llama-server (`Math.min` passes it through); clamp the low side too.
- `isCatalogBrain` (lines 128-130) filters on free-text `role` substrings — a brain whose role copy later contains "rerank"/"embeddings" is silently hidden from the picker; a structural field (e.g. `seat: "brain" | "service"`) would not rot.
- Every upper-register render file (lines 157-160, 167-170, 177-179, 186-188, 195, 206) carries no `bytes`/`sha256` at all — the exact clean-looking-truncation class the 2026-09-15 gate closed on the LLM side stays open for the largest downloads in the catalog (doctrine-blessed as "verify-what-is-pinned", but the motive applies equally).
- Nothing validates pins against ground truth at authoring time — no test or script cross-checks `LLM_MODELS[].bytes` against the HF tree API, which is precisely how five wrong pins survived a review gate focused on the clamp arithmetic.

context-pack: catalog.ts pins enforced end-to-end via vite.llm.ts:367-374 -> vite.caliper.ts:627-640 (sizeVerdict + sha, delete on mismatch); HF tree API grounded 2026-09-15 (gemma/LFM2 mismatch, qwen3-4b exact); prior review covered only the KV-clamp fix.
new-findings: 1
