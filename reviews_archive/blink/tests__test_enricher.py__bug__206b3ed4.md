# colibri review — tests/test_enricher.py (delta + test-quality hunt)

- source: `tests/test_enricher.py`
- reviewer: ZCode in-session (GLM-5.3), colibri-review v0.4.0, bug mode, test-specific classes
- sha256: 206b3ed41476f08cfbe82642ae42f2b19b19a1e286646da196826e3d29dcb5f
- date: 2026-10-05 04:40
- context pack: prior review d5152f30 (hy4, 2026-09-19); delta 73225de→c1eb108 (creative-direction
  rework, ledger, publish, static card videos — file grew to 1485 lines); contract sources =
  enricher/pipeline/config reviewed this session; fakes inventory (FakeResp, make_fake_blink_module,
  _install seam-swaps with addCleanup).

## Verdict

new: 0 — and this pass CONTRIBUTED evidence: its test_default_config_has_enrich_disabled caught a
factual error in this session's config.example.yaml artifact (now retracted and corrected there).

Test-quality hunt results:

- Assertions are real everywhere sampled: value equality against computed expectations (hashes,
  URL-encoding, slot assignment read back from the PROMPT the code actually sent — 894-905 avoids
  harness-coupling by parsing the prompt rather than assuming media duration).
- Mocks sit at the right seams (network faked at _http_json/_open_url/_songs_site_request;
  ffmpeg at _run/probe_media) — the logic under test (guard policy, funnel, archive, wallet
  clamp) is never mocked away. Negative-wiring asserts are strong: `assertNotIn("-loop")`,
  `side_effect=AssertionError("network touched")`, `probe.assert_not_called()`,
  `final_video_args side_effect=AssertionError("stills path used")` — the wrong branch fails the
  test by construction.
- Failure-economics coverage is exceptional: paid songs archived before card failure (822-828),
  IncompleteRead degraded not aborting (1021-1037), 40-song hallucination clamp (1118-1141),
  malformed-success crash guard (1227-1243), blind-archive disk guard keeping BOTH paid songs
  (907-927).
- Patch hygiene: setUp patches all carry addCleanup; the two hand-rolled try/finally restores
  (1082-1091, 1094-1107) are equivalent. No env-var leaks; temp dirs cleaned.
- No tautologies, no silent skips, no order coupling (each test builds its own store/files).

Prior findings not restated.
