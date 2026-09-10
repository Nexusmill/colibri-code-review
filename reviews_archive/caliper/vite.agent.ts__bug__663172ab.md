# colibri bug review - vite.agent.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 663172ab - 2026-08-25
mode: bug - context: sole consumer vite.caliper.ts; src/llm/tools.ts validateToolCall read in full (the deterministic core); git 1e8181c..af12a90 (flag-write + multi-brain era); applyProposal/chat/apply handler traced end to end

## Verdict

Shippable - no confirmed defects. The write path is disciplined: validateToolCall gates every tool call, applyProposal is the only writer, validation-before-write on bundles.json, honest live-flag reporting against the running server's own argv, fixed local addresses (no request input reaches a URL).

## Bugs & vulnerabilities

None confirmed. Refuted in the adversarial pass:

- NaN/Infinity poisoning bundles.json via set_param: validateToolCall enforces typeof number + isFinite + > 0 (tools.ts line 105) and JSON cannot carry NaN - dead end.
- describeProposal's FLAG_ALLOWLIST[...]! non-null assertion: every call site validates first, so the allowlist hit is guaranteed.
- currentState spread order (config flags override server flags): correct for the no-op filter's semantics - a config value already equals the post-restart truth.

## Missing safeguards

- A crafted /api/agent/apply with a "bench" call passes validation and reaches applyProposal's "unknown action" fallthrough instead of an explicit 400 like read_kb gets - harmless (no write) but asymmetric.
- caliper.config.json read-modify-write is last-write-wins across concurrent applies; single-user console tempo makes it theoretical.
