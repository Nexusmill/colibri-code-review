# E-3 synthesis - POWER ON from the app (2026-09-06)

Chain: socketState (the ws's own truth) -> the seat set (start when down,
restart when connected, a busy key pins its seat) -> comfyStart -> the
launcher's own start tail (flags pipeline by construction) -> observed
port poll. The feature cannot drift from a cold start because it IS the
cold start door.

Ranked findings: none above LOW; two refuted in pass 3 (double-start
guard chain; connecting-state seat truth). Live e2e recorded in HISTORY:
stop -> [START, POWER] -> two-press -> port back 15s with
--enable-cors-header and the optimizer's --vram-headroom 4, node self-ID
answering across the cycle.

Tier 62/0/4 exit 0; vitest 456/456.
