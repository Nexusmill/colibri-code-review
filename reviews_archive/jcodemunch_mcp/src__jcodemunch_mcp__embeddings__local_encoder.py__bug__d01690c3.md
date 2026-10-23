# Colibri review — src/jcodemunch_mcp/embeddings/local_encoder.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\embeddings\local_encoder.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `d01690c38556c64104995521ab0c8c456e3afdf31c4e06eb5c7fddc4e3db9d89` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `WordPieceTokenizer` 118-240 (`_wordpiece` 172-196: per-position backoff, no length cap; `encode` wraps with [CLS]/[SEP] and pads to `max_length`), the module singleton `_session`/`_tokenizer` 245-246 with `_get_session` 249-296 (fast path on `_session`, no lock, session assigned at 291 BEFORE the tokenizer at 292 - and `WordPieceTokenizer.__init__` reads `vocab.txt`, releasing the GIL in that window) and `reset_session` 299-303; the callers: `encode_batch` 329 (`session, tokenizer = _get_session()` then `tokenizer.encode_batch(...)`), dispatched by server.py through `asyncio.to_thread` for `embed_repo` and lazy semantic `search_symbols` - two overlapping tool calls are two real threads; existing `tests/test_local_encoder.py` + embedding tests (81); both RED probes re-run on these bytes (probe 1: 4.06 s for one 4,000-char token; probe 2: 2/2 FAIL). No prior `.colibri_reviews` record.

## Verdict
One long token stalled the encoder for seconds, and two overlapping first calls could hand one of them a session with no tokenizer. Both confirmed and fixed; the sub-agent's two self-refutations re-checked and kept.

## Bugs & vulnerabilities
**[HIGH] `_wordpiece` has no `max_input_chars_per_word` cap - worse-than-quadratic backoff on one long unmatched token — CONFIRMED — FIXED** - `line 172-196`
- What: for a token with no vocab match the inner loop tries every suffix length from each position - O(n^2) substring builds of O(n) each. Measured 4.06 s for a single 4,000-char token (the sub-agent measured 26.8 s at 8,000); a hex blob, a base64 line, a minified bundle or a CJK run in ordinary repository content is enough, and `embed_repo` encodes every symbol.
- Fix: `_MAX_INPUT_CHARS_PER_WORD = 100` (HuggingFace `BertTokenizer` default) - a longer token is one `[UNK]`, exactly as BERT tokenizes it. At or under the cap the pre-existing per-position behaviour is unchanged (pinned: 100 x `a` still yields 100 `[UNK]`s; 101 yields one). 4,000 chars now 1 ms.

**[HIGH] `_get_session` lazy-init race: a second thread sees `_session` set with `_tokenizer` still None — CONFIRMED — FIXED** - `line 249-296`
- What: no lock; `_session` was assigned before `_tokenizer`, and the tokenizer's constructor does file I/O in between. A concurrent `_get_session()` took the fast path on `_session is not None` and returned `(session, None)`; `encode_batch` then crashed with AttributeError. Two overlapping embed/semantic-search tool calls (real threads via `asyncio.to_thread`) are enough. Unlocked double initialisation also loaded the ONNX model twice.
- Fix: a module `_session_lock`, double-checked; `_load_session()` builds the tokenizer FIRST and the session second, under the lock, and the pair is published tokenizer-first; the fast path (and the locked re-check) returns only a COMPLETE pair, so a half-built state can never be handed out and is rebuilt under the lock if it were ever observed; `reset_session` takes the lock. The sub-agent's snippet (swap the two assignments) closed the None-pair window but kept the double load and the unlocked publish.
- Probe 2 after the fix: it SIMULATES the race by setting `_session` to a sentinel with `_tokenizer = None` and calling `_get_session()` - a state the fix makes unreachable; on these bytes that state goes to the locked rebuild, which imports onnxruntime (absent in this venv) - so the probe cannot pass here by construction. The real race is pinned instead by `test_concurrent_first_calls_never_see_a_half_built_pair` (8 threads through the real `_get_session` body with a stand-in onnxruntime and a slowed load: every thread gets the same complete pair, the model loads once) and `test_the_pair_is_published_tokenizer_first`.

## Refuted (sub-agent's own, re-checked and agreed)
- `_mean_pool` / `encode_batch` divide-by-zero on an all-zero attention mask - `encode` always emits [CLS] and [SEP] with mask 1, so the sum is >= 2.
- `_wordpiece` infinite loop when nothing matches - the `else: start += 1` branch always advances; the real defect was per-iteration cost (fixed above).

## Missing safeguards
- `download_model()` fetches from a mutable `resolve/main` HF ref with no checksum verification of the downloaded ONNX/vocab (a supply-chain hardening gap; not reproducible without network and not fixed here - a pinned revision + sha256 is the shape of the fix). Flagged.

## Adversarial verification (Phase 3)
- The cap test asserts on wall-clock (< 1 s for 4,000 chars) AND on the emitted ids ([CLS], one [UNK], [SEP], padded to `max_length`), so a fix that merely truncated would fail it.
- The concurrency test drives 8 real threads into the real `_get_session` body (stand-in `onnxruntime` in `sys.modules`, a model dir with placeholder files, a 50 ms sleep inside the fake session constructor) and asserts no exception, identical session objects, complete pairs, and exactly one load.
- `tests/test_local_encoder.py`, `test_embed_drift.py`, `test_paid_embeddings_optin.py`, `test_semantic_search.py`: unchanged, 85 passed / 1 skipped with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `93c6b862bc1bb821a25f09a2d2f09919c0cb96b823b739ea565350d758cbcabd`. TDD: `tests/test_local_encoder_reaudit.py` (4 tests) - all 4 RED on the old bytes, GREEN after; probe 1 ALL PASS; probe 2 unreachable-state, see above.
