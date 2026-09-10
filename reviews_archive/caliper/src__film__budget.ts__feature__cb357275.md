# Colibri review — src/film/budget.ts (feature)

- **Source:** `src/film/budget.ts` · **sha256:** cb357275
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the bill's arithmetic (owner 2026-08-23: nothing paid before APPROVE; unpriced legs widen the band, never invent); consumed by vite.film's autopilot-bill and the produce gate; the R1 price-provenance add-on's code home; last touch a8dfbfd (2026-09-05).

## What this module does

137 pure lines: `parseTiers` (per-resolution rates out of a scraped pricing blob, two format patterns, absent tiers stay absent), `BillPrices` (draft/finish rates and tiers as separate fields), `computeBill` — the tier-aware shoot line (draft-mode rate for draft-720p, stated tier for native, unknown tier widens the band), the finishing pass as its own full-timeline line, board/score/voice/transcribe lines with null-means-unknown discipline, the ±20%-per-unknown band, the explicit 15% retry-margin line item (the owner's itemized-contingency ruling), and a null total the moment any leg cannot say. `gateStep` is the produce gate's ceiling check.

## Suggested add-ons

**Price provenance on every line** — Value High · Effort S-M
- What: thread `source: "owner" | "page" | "estimate"` from the builder (vite.film computes priceSource per engine and drops it before `computeBill`) through `BillPrices` fields onto `BillLine`.
- Why: this file is where the lines are BUILT — the R1/R2 finding (priceSource computed, rendered nowhere; BillLine cannot carry it) lands here first, then autopilot.ts's type and the wizard's display. An estimate-priced line and an owner-verified line are indistinguishable at APPROVE SPEND today.
- How: optional `source` fields on BillPrices entries, copied onto each line at push time; band logic unchanged.

**A window count on the bill** — Value Low-Med · Effort S
- The bill prices whole-film lines; the checkpoint doctrine spends in 20s windows and THE ENGINES already shows per-window money. A `windows` count (ceil(seconds/20)) in the Bill — or a per-window column beside the shoot line — aligns the bill with how the run actually halts.

**Tunable retry margin** — Value Low · Effort S
- The 15% contingency is a fixed literal (the owner's ruling named the mechanism, not the number); `opts.retryPct` with 15 as default lets a nervous run approve 25% up front.

## Nice-to-haves

- `parseTiers` handles two blob shapes; a third ("$X/s at 1080p" suffix form) would widen coverage — data-driven, add when a real page needs it.
