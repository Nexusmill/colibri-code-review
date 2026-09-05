# colibri debug record - tools/session_grounding_hook.ps1

- source: `tools/session_grounding_hook.ps1` (Nexusmill)
- model: claude-fable-5-1 (in-session, Phase D debug modality)
- sha256 reviewed (pre-fix): `69c3825fa8d1c4ab931e07ff6fadee6bcaf9179b6f128306093a3ee1f47ff2a5`
- sha256 after fix: `2348056a89abb1a00289d901c222369ca573d383fe604a58001fae6d5e5361f8`
- date: 2026-09-03
- mode: debug
- context pack: `.claude/settings.json` hook registration (only caller; SessionStart, no matcher = startup/compact/resume);
  jCodemunch search_text `session_grounding_hook` (1 reference, the settings row); remediation/deferred/features manifests
  (0 prior rows on this file); no prior colibri review; no prior test; session transcripts 982cc771 (fail, CC 2.1.258)
  and 1d34e71b (success, CC 2.1.234) for the harness-captured stdout bytes.

## Failure signal (captured, not inferred)
Transcript attachment `hook_non_blocking_error` for `SessionStart:startup`, exitCode 0, 677 ms, stderr:
"Hook output looks like a JSON object but is not valid JSON - JSON Parse error: Unterminated string."
Effect: the Nexusmill grounding context (AGENT_STATE head slice) was DROPPED from the session; only the
superpowers + episodic-memory hooks reached context.

## Hypothesis ledger
1. Script errors / non-zero exit -> KILLED: rc 0 in harness and by hand, stderr empty.
2. Timeout -> KILLED: 677 ms in harness, 0.27 s by hand.
3. additionalContext over the 10,000-char cap -> KILLED: 8.8 KB payload, ctx ~8.3k chars.
4. Console code page corrupts the payload -> CONFIRMED (bytes): stdout position 2444 = 0x82 (cp437 e-acute,
   invalid UTF-8 lead byte) where AGENT_STATE has `cafe.py` with e-acute; positions 3727/4035/4366/7390/8157/8388
   = 0x1A (SUB) where AGENT_STATE has U+2192 arrows ("30->32") - .NET best-fit maps U+2192 to cp437 0x1A.
   0x1A inside a JSON string is an illegal control character -> strict parsers reject ("Unterminated string"
   in the harness's parser; "Invalid control character" in Python). PS 5.1 ConvertTo-Json does NOT escape
   non-ASCII, and powershell.exe writes stdout in the OEM code page, not UTF-8.
5. Why now: yesterday's transcript (CC 2.1.234) shows the SAME corrupt bytes accepted as `hook_success`
   (raw text passed through); CC 2.1.258 validates JSON-looking stdout strictly. The defect was latent
   since the hook was written (2026-07-24); the harness upgrade made it visible.

## Fix (one variable, at the root)
After `ConvertTo-Json -Compress`, `[regex]::Replace($json, '[^\x20-\x7E]', ...)` escapes every UTF-16 code unit
outside printable ASCII as `\uXXXX` (surrogate halves separately - legal JSON). The payload is pure ASCII and
therefore immune to any console code page. `NEXUSMILL_AGENT_STATE` env override added for the test.

## Verification
- `tests/test_session_grounding_hook.py` (runs the REAL hook under powershell.exe): RED on the pre-fix bytes
  (fails on byte 0x82 at position 2444), GREEN after (2/2): pure ASCII, no raw control chars, strict
  `json.loads`, hookEventName, ctx <= 10,000, and hostile content (arrow, e-acute, emoji+VS16, \x01, quotes,
  backslash path) round-trips through the escape.
- Byte probe after fix: non-ASCII bytes 0, control bytes none.

## Phase 3 (adversarial) on the fix
- Could the escape damage structure? No: JSON structural chars and ConvertTo-Json's own escapes are all in
  0x20-0x7E and are never touched. CONFIRMED by the strict-parse test.
- Lone/paired surrogates: `[char]` cast on a one-unit string is total; escaping each half is valid JSON;
  emoji round-trip CONFIRMED by test.
- Cost: regex evaluator over ~9 KB - hook now 0.79 s for two runs incl. process spawn.

## Manifest
- remediation_manifest.json row `HOOK-JSON-CODEPAGE` (same commit).
