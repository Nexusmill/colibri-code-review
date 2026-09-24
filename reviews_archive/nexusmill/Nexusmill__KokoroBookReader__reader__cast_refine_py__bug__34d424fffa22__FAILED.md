# scan 34d424fffa22 FAILED (batch-exhausted)

all batch rungs failed to submit: z-ai/glm-5.3:batch+deepseek/deepseek-v4-pro-0813:batch+z-ai/glm-5.3-flash:batch

unit: {
 "kind": "bug",
 "files": [
  "KokoroBookReader/reader/cast_refine.py",
  "KokoroBookReader/reader/cast_ui.py",
  "KokoroBookReader/reader/style_scan.py",
  "KokoroBookReader/reader/speech/voices.py",
  "KokoroBookReader/reader/speech/client.py",
  "KokoroBookReader/reader/speech/worker.py",
  "KokoroBookReader/reader/index_client.py",
  "KokoroBookReader/reader/index_worker.py",
  "KokoroBookReader/reader/process_priority.py",
  "KokoroBookReader/tests/test_final_review.py"
 ],
 "prompt": "M2 scan-ladder cross-family review (colibri bug mode, new-findings-only). These files were modified in the KokoroBookReader adoption (Nexusmill 1a713344): app-relative data root + migration, scan-progress persistence (progress.json per batch, v3-aware status), orphan pruning, atomic_json PermissionError retry, BELOW_NORMAL priority for helper processes, thread caps, bundled Kokoro runtime paths. Two gate reviews already passed (BLOCK gate_20260922-065440 findings fixed; CLEAR gate_20260922-071710) - hunt NEW defects only; verified-fixed items need no re-raising.",
 "id": "34d424fffa22",
 "repo": "Nexusmill",
 "requested_at": "2026-09-22T08:02:29",
 "status": "failed(batch-exhausted)",
 "last_error": "HTTP Error 400: Bad Request",
 "failure": {
  "code": "batch-exhausted",
  "detail": "all batch rungs failed to submit: z-ai/glm-5.3:batch+deepseek/deepseek-v4-pro-0813:batch+z-ai/glm-5.3-flash:batch",
  "at": "2026-09-22T08:02:35"
 }
}
