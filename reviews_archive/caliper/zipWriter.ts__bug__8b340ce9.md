<!-- colibri review
source: zipWriter.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 8b340ce99cf6baee8687efdfbbc96f7185f21154c1a58dc976025e5428090c90
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. The guard sums per-entry overhead (30+name+data+46+name) before writing anything - a lie is refused before it is allocated; both failure shapes tested (single >4GiB entry, many entries crossing together).
