# colibri bug review - src/components/StatusFooter.tsx (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 c345b763 - 2026-08-26
mode: bug (delta on 64a42466, 2026-08-19) - context: CaliperVram/SystemStats/LlmStatus shapes from api/types; the custom node's 4s counter cache; git b1f6a1a/e8dd8ef (truthful-residency era)

## Verdict

Shippable - the delta is clean.

## New findings

None confirmed. Single-source-of-truth VRAM used-figure (adapter counter over CUDA free arithmetic), artifact process values as em-dashes (never fact), the optimizer sidecar's resident-model line, the 4.5s post-purge cache wait, and the three poll intervals' cleanup all re-verified.

## Missing safeguards

- `free = total - used` mixes the adapter counter with the CUDA total; a hypothetical adapter_bytes above vram_total would print a negative free - not physically reachable for the same card today.
