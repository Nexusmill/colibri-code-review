# Colibri review — src/jcodemunch_mcp/redact.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\redact.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `86a1e34effcbb0f7a825d2d0f78e4a2796b459e5a79f82578e58716c637eadf8` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `_PATTERNS` (55-112), `_redact_string` (131-168: the `secret` group is replaced by `[REDACTED:<label>]`, prefix/suffix kept), `redact_dict` (171-230: dict / list / str-over-16 / depth cap); `runtime/redact.py` is a re-export of this module; `tests/test_redact.py` (the F9 "bare Bearer in prose" rule, kept); the audit probe re-run on these bytes (5/8 RED). No prior `.colibri_reviews` record.

## Verdict
The private-key rule redacted the banner and left the key. Four real defects, all fixed in the commit carrying this record; the existing suite's expectations (including the prose-Bearer exemption) unchanged.

## Bugs & vulnerabilities
**[HIGH] `private_key` matched only the `-----BEGIN … PRIVATE KEY-----` banner — the base64 body and END banner passed through — CONFIRMED — FIXED** - `line 95-97`
- What: `_redact_string` replaces the `secret` group only, so a PEM block came out as `[REDACTED:private_key]` followed by the entire key material. Every consumer of a redacted tool response (get_symbol_source over a checked-in key, redacted runtime records, the `_meta` scan) received the key.
- Fix: the pattern now spans banner-to-END with a lazy `.*?` under `DOTALL` (linear against a fixed literal end anchor; verified on a multi-KB body). A block with no END banner is deliberately NOT matched by this rule (it would otherwise swallow the rest of the text) and falls to the generic patterns.

**[HIGH] PKCS#8 `ENCRYPTED PRIVATE KEY` and PGP `PRIVATE KEY BLOCK` not matched at all — CONFIRMED — FIXED** - `line 96`
- `ENCRYPTED ` added to the banner alternation; a separate `pgp_private_key` rule for `gpg --export-secret-keys --armor` output (the same export shape the secret classifier tranche `5923fe8` stopped exempting as documentation).

**[MEDIUM-HIGH] JSON / dict-quoted `Authorization` headers slipped the bearer rule — CONFIRMED — FIXED** - `line 67-69`
- `"Authorization": "Bearer …"` has a quote between the key and the colon and another before `Bearer`; `\s*[:=]\s*Bearer` required none. Optional `["']` on both sides now; the F9 rule (the word Bearer without the header key is prose) is preserved and re-pinned by `test_bare_bearer_in_prose_still_not_redacted`.

**[MEDIUM] `redact_dict` never scanned tuples — CONFIRMED — FIXED** - `line 217-223`
- A tuple value passed through as a scalar (the fall-through `return data, 0`). Tuples are now walked like lists and returned as tuples so callers that type-check keep their shape.

## Refuted (sub-agent's own, re-checked and agreed)
- `azure_client_secret` unbounded class as a runaway match — `re.sub` stops at the first character outside the class.
- The new lazy `.*?` + `DOTALL` as catastrophic backtracking — no nested repetition, so no exponential case. **This refutation was too narrow and the gate caught what it missed (round 2, below): linear per attempt is not linear per `sub()`.**

## Adversarial verification (Phase 3)
- Key material in the tests is synthesized at runtime from a formula (never a literal that a secret scanner could trip on), and each test asserts the body string is ABSENT from the output, not merely that a label is present.
- Checked that widening the bearer rule cannot re-open F9: the header key is still mandatory; only quoting between it and the value is tolerated.
- Ran every redaction test in the suite (50) after the change - unchanged.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `5dec1d04ac64d6c776376d29318660bde4cb24b8380a8a22444fe69f3c4f6daa`. TDD: `tests/test_redact_reaudit.py` (8 tests) - 4 RED on the old bytes for exactly the four findings, GREEN after (the prose control green throughout); `tests/test_redact.py` unchanged; probe `probe_jcm_redact_1.py` ALL PASS.

**Gate catch (round 1, gate_20260913-142436, MEDIUM, accepted):** teaching `redact_dict` to walk tuples left the depth-cap sentinel enumerating `(str, dict, list)` - a tuple sitting past depth 20 was returned RAW (`return data, 0`), secrets and all, while a list at the same depth collapsed to `[REDACTED:depth_exceeded]`; the cap's own comment (audit finding F10) declares the invariant the new branch broke. This reviewer had checked the tuple branch's return shape and missed the sibling guard. Fixed (`tuple` added to the cap guard) and pinned by `test_depth_cap_collapses_a_tuple_like_any_container` - a 26-deep tuple nest, RED on the round-1 bytes (the token came back in the output), GREEN after. Docketed as EV-072.

**Gate catch (round 2, gate_20260913-143014, MEDIUM, accepted):** the whole-block span `.*?-----END ...` is linear per ATTEMPT only. Every BEGIN banner lacking an END walked to end of text, so a file of repeated banners - which `get_file_content`/`get_symbol_source` hand to the redactor whole - cost O(banners x length): measured 5.4 s for 224 KB of bare banners on the round-2 bytes, minutes for 1 MB, repeatable per tool call. The same unbounded span also let a stray BEGIN (a banner quoted in prose) swallow everything up to the next real key's END - 200 legitimate lines collapsed into one marker in the probe. Both were the exact claim this review's own refuted-list had waved through ("a lazy span to a fixed literal is linear"). Fixed with a tempered span, `(?:(?!-----).)*?`: the body may not contain the start of a banner, so an attempt stops at the next `-----` (1 MB of banners now 0.09 s; a 150 KB real block still redacted whole) and a stray banner cannot reach past the next one. No size cap - a cap that a large PGP export exceeded would leak the whole key, worse than over-redaction. Pinned by `test_unterminated_banners_do_not_go_quadratic` (8000 banners under 1 s; 4.7 s RED) and `test_a_stray_banner_does_not_swallow_the_text_up_to_a_later_key` (RED: 0 of 200 lines kept). Docketed as EV-073.
