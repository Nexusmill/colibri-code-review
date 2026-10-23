# Colibri review — src/jcodemunch_mcp/tools/get_changed_symbols.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_changed_symbols.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `fa98ac8600efb26a11bf375dc61e9f2f09f914f0b0f8a23a25cf6698469813f9` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's PARTIAL review (an UNVERIFIED question about the rename branch; 2 refuted argument-injection claims, kept); `_parse_symbols_from_content` 52-85 (keyed `qualified_name#kind`, last-wins), the per-file diff 246-284, `_meta.tip` 311-315; `parser/symbols.Symbol` (`id` = `file::qualified_name#kind`, the extractor suffixes same-named siblings `~N` - seen live: `src/cfg.py::GIT#constant~2`); `parser/extractor` 818 (`content_hash` over `source_bytes[start:end]` of the WHOLE node, signature included); a census probe over the default store (27 indexes, 130,710 symbols: `qualified_name` ends with `name` for every symbol but one toml array-table; 1,890 duplicate `(file, qualified_name#kind)` keys across 8 languages); `tests/test_get_changed_symbols.py`, `tests/test_branch_following.py`. No prior `.colibri_reviews` record.

## Verdict
Two real LOWs settled from the sub-agent's open question: same-named siblings collapsed into one row (a change to the first was invisible), and the tool promised a `renamed` outcome it could not produce. Both fixed; the injection claims stay refuted.

## Bugs & vulnerabilities
**[LOW] Per-file diff keyed by `qualified_name#kind`, last-wins — a change to the first of two same-named siblings was invisible — CONFIRMED — FIXED** - `line 66`
- Trigger (RED on these bytes): `GIT = "one"` / `GIT = "two"` → the dict held one `GIT#constant` (the second); editing the first reported nothing.
- Fix: the key is the parser's own `sym.id`, which already carries the `~N` ordinal for siblings. Same file on both sides, so the ids align.
- The ordinals are positional and present only when there ARE siblings (`~1`/`~2`; none when unique - verified live), so deleting, inserting or editing one re-numbers the rest, and a key-by-key diff read a deletion as "2 removed + 1 added" (over-reported, not hidden). The diff is now aligned per sibling GROUP - the id without its ordinal, qualified name and kind included: byte-identical bodies pair off as unchanged whatever their number, as many edited rows as remain on both sides pair positionally as `modified` (the unique-symbol case is exactly one and one), and the surplus on either side is what really went or came.
- **Gate round 1 (gate_20260913-232653) caught my first form of this, twice - EV-082.** The first pair-off keyed on `(name, kind, content_hash)` with no qualified name, so a byte-identical body moved into another parent (`A.f` → `B.f`, an id-changing, reference-breaking move) was paired off and hidden where the old keying reported removed + added; and it only caught renumbering that crossed the added/removed boundary, so deleting the first of three read as 1 removed + 2 spurious `modified` - contradicting my own "exactly one removal" claim in the context. Both shapes were RED on the round-1 bytes and are pinned now.

**[LOW] The `renamed` branch was unreachable and `_meta.tip` promised it — CONFIRMED — FIXED** - `line 268-276, 313`
- Why unreachable, twice over: the key embeds the name, so a renamed symbol is never in `before_keys & after_keys`; and `content_hash` covers the signature, so a renamed body never hashes the same. The 130,710-symbol census confirms the first (one toml array-table aside, `qualified_name` ends with `name` everywhere).
- Fix: the branch is removed with a comment saying why; the tip now reads "a rename shows as removed + added". A real detector needs a name-agnostic body hash - a design item, not a fix for this pass.

## Refuted (kept from the sub-agent, re-traced)
- `since_sha`/`until_sha` flag injection into `git rev-parse --verify` (8 payloads → rc 128; `--verify` needs a real revision); `git show sha:path` with a `-`-leading path (the token is always `<hex>:<path>`). List-form argv throughout, no shell.

## Adversarial verification (Phase 3)
- Pinned end to end on real git repos: the sibling edit → `modified` at line 1, no added/removed; deleting the first of two → exactly one `removed` (line 1); deleting the first of THREE → exactly one `removed`, no `modified`; inserting before one and before two → exactly one `added`, no `modified`; editing both of two → two `modified`; `A.f` → `B.f` with identical bytes → removed {A, A.f} + added {B, B.f} (fixture validity asserted: same hash, different qualified name); an untouched pair reports nothing while a real change in another file still does; `foo`→`bar` → removed {foo} + added {bar}, no `renamed`, tip text pinned. Unit pin on `_parse_symbols_from_content` (two rows, lines 1 and 2). `tests/test_get_changed_symbols.py` + branch-following unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `db0b2b93ac04b3f3250f8d32968170a25b67db2ef7753c1ee8fa3eae08046877`. TDD: `tests/test_get_changed_symbols_reaudit.py` - 10 tests: 3 RED on the old bytes + 1 control green throughout; the two-sibling renumbering shapes (RED on the key-only form); the first-of-three, insert-before-two and scope-move shapes (RED on the round-1 pair-off, the gate's catches); both-edited as a control, GREEN after.
