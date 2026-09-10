# colibri bug review - src/llm/tools.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 84daa792 - 2026-08-26
mode: bug - context: the deterministic core every agent path flows through (validateToolCall traced in rounds 2-3 from vite.agent.ts; parseFlagTokens feeds activeServerFlags; filterNoopProposals gates chat AND apply)

## Verdict

Shippable - no defects. The allowlist discipline holds end to end.

## Bugs & vulnerabilities

None confirmed. Every validator rejects on type, range, finiteness, and integrality; JSON-parse failures are caught; the bench contract is closed (two positive finite values, seed bounds, 1-2 repeats); filterNoopProposals' undefined-vs-value comparison correctly KEEPS proposals for unset flags/params; parseFlagTokens handles --flag=value, --flag value, valueless, and junk tokens.

## Missing safeguards

None material. FLAG_ALLOWLIST is a single entry today (vram-headroom) - additions should keep the min/max/plain/cite shape.
