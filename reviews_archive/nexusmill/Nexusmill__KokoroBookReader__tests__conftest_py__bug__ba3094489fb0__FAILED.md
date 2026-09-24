# scan ba3094489fb0 FAILED (empty-batch-output)

batch output carried no VERDICT line

unit: {
 "kind": "bug",
 "files": [
  "KokoroBookReader/tests/conftest.py",
  "KokoroBookReader/tests/test_acceptance.py",
  "KokoroBookReader/tests/test_analysis_activity.py",
  "KokoroBookReader/tests/test_audio_onset.py",
  "KokoroBookReader/tests/test_book_index_edges.py",
  "KokoroBookReader/tests/test_cast_flow.py",
  "KokoroBookReader/tests/test_cast_refine.py",
  "KokoroBookReader/tests/test_cast_scan.py",
  "KokoroBookReader/tests/test_imports.py",
  "KokoroBookReader/tests/test_index_narration.py",
  "KokoroBookReader/tests/test_kindle.py",
  "KokoroBookReader/tests/test_playback.py",
  "KokoroBookReader/tests/test_refine_boundaries.py",
  "KokoroBookReader/tests/test_refine_retry_cache.py",
  "KokoroBookReader/tests/test_runtime.py",
  "KokoroBookReader/tests/test_speech.py",
  "KokoroBookReader/tests/test_style_scan.py"
 ],
 "prompt": "Cross-family TEST-surface scan (colibri bug mode, batch ladder) - the KokoroBookReader test suite. Tests are review units: hunt TEST-SPECIFIC defects - assertions that cannot fail (tautologies, value compared to itself, assert True), a stale or wrong target (a stub or fixture shadowing the real symbol, a mock that mocks away the behavior under test), runners reporting PASS on exception or exit 0 on failure, silent skips masquerading as passes, order or shared-state coupling between tests, fixture and environment leaks (temp dirs, env vars, monkeypatches never restored), hard-coded machine paths, non-deterministic inputs without a seed - AND any real production defect the tests visibly betray while you read them. The production sources were scanned separately; findings here must cite test behavior. End your reply with a final line exactly 'VERDICT: CLEAR' if no real defects, or 'VERDICT: BLOCK' followed by the numbered findings (each with file, line, trigger, impact, concrete fix).\n\n===== FILE: KokoroBookReader/tests/conftest.py =====\n\"\"\"Isolate ReaderWindow settings in per-test temporary INI files.\"\"\"\nimport pytest\nfrom PySide6.QtCore import QSettings\n\n@pytest.fixture(autouse=True)\ndef isolated_settings(tmp_path, monkeypatch):\n    import reader.ui.window as window\n    filename = str(tmp_path / \"settings.ini\")\n    monkeypatch.setattr(window, \"QSettings\", lambda *args: QSettings(filename, QSettings.Format.IniFormat))\n\n\n===== FILE: KokoroBookReader/tests/test_acceptance.py =====\n\"\"\"Regression probes for review findings and end-to-end UI boundaries.\"\"\"\nimport json\nimport subprocess\nimport sys\nimport zipfile\nfrom pathlib import Path\nfrom types import SimpleNamespace\nimport pytest\nfrom reader.domain import AudioReady, ReadingPosition\nfrom tests.test_playback import setup_controller, ready\nfrom tests.test_imports import epub\n\ndef test_dialogue_quotes_are_not_relocated():\n    from reader.importers.text import sentences\n    source = 'She entered the room. \"Hello?\" she said. The clock struck. \\'Twas midnight.'\n    assert \" \".join(sentences(source)) == source\n\ndef test_cancel_reentry_cannot_pause_new_position():\n    c, player, speech, _ = setup_controller()\n    c.play()\n    old = speech.requests[0]\n    speech.cancel = lambda session: c.failed(old.session, old.request, \"cancelled\")\n    c.seek(2)\n    assert c.playing and c.sentence == 2\n    assert any(r.sentence == 2 and r.session == c.session for r in speech.requests)\n\ndef test_out_of_order_lookahead_and_pause_at_end():\n    c, player, speech, _ = setup_controller()\n    c.play()\n    first, second = speech.requests[:2]\n    c.audio_ready(ready(second))\n    assert player.play_calls == 0\n    c.audio_ready(ready(first))\n    c.pause()\n    c.ended(first.session, first.request)\n    assert c.sentence == 0 and not c.playing\n\ndef test_duplicate_archive_entries_rejected(tmp_path):\n    from reader.importers.epub import read_epub, InvalidBook\n    path = epub(tmp_path / \"book.epub\")\n    with zipfile.ZipFile(path, \"a\") as archive:\n        archive.writestr(\"OEBPS/book.opf\", \"<package/
