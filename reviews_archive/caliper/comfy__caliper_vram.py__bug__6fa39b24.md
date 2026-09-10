# Colibri bug review — comfy/caliper_vram.py

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 6fa39b24bb914973eca95367d4601670a8dfb0e31cd56c81b78a49f5e34816a8

### Meta
- path: comfy/caliper_vram.py | sha8: 6fa39b24 (matches expected) | lines: 161 | vendored-parity: DRIFTED (canonical 6fa39b24 CRLF vs vendored E:\AI\ComfyUI\custom_nodes\caliper_vram.py 5b8fc1e7 LF; content byte-identical after EOL normalization — normalized sha8 5b8fc1e7 == vendored) | context-pack: node registers GET /caliper/vram + POST /caliper/power on `PromptServer.instance.routes`; browser polls /caliper/vram through the Vite proxy (`"/caliper": to()` → 127.0.0.1:8188, src/api/client.ts:115, StatusFooter.tsx:31); vite.power.ts:18 POSTs `{"action":"stop"}` directly to 8188 (URL/method/body both sides match); `/free` is ComfyUI's built-in purge (proxied, used by client.ts `freeVram`); launcher/start-comfyui.cmd:19 passes `--enable-cors-header` with NO origin value (→ `*`); git: f7540c3, 9b95dac, 068fc3d, d212818

### Review

## Verdict
Well-built for a local instrument. The hard parts are done right: the expensive counter read runs in an async subprocess (never blocks the loop), a single-flight lock plus stamp-at-completion caching prevents thundering-herd powershell respawns, hung counters are killed and reaped on timeout/cancel, the model snapshot is `list()`-copied with per-model try/except against load/unload races, every torch value is `int()`/`str()`-coerced for JSON, and there is no injection surface (static script, base64 `-EncodedCommand`, zero user input). The findings are process (parity invariant broken by EOLs), exposure (an unauthenticated process-kill endpoint behind `*` CORS), and truthfulness (degraded reads return 200 with zeroed data whose error marker the client never reads). No CRITICAL or HIGH defects.

## Bugs & vulnerabilities

- **[MEDIUM] Vendored byte-parity is broken (CRLF vs LF) — the repo's own sync invariant no longer checks anything** - `E:\AI\ComfyUI\custom_nodes\caliper_vram.py` vs `E:\AI\Caliper\comfy\caliper_vram.py` — CONFIRMED.
  What: AGENTS.md declares this file "sha-synced (byte-parity)" into custom_nodes, but `git config core.autocrlf=true` checks the canonical out as CRLF (161 CRLFs, 6465 B, sha8 6fa39b24) while the vendored copy holds the repo's LF bytes (161 LFs, 6304 B, sha8 5b8fc1e7). Content is identical after normalization; only line endings differ.
  Trigger: every byte-level comparison, forever, starting from whenever the vendored copy was placed.
  Impact: no runtime difference (Python ignores EOL), but drift detection is permanently red — and vite.power.ts:61's restart-failure path explicitly depends on a human asking "is the caliper_vram custom node current?". A permanently-alarming check trains the operator to ignore it, which is exactly how a real stale-node divergence gets missed.
  Fix: add `.gitattributes` (`comfy/*.py text eol=lf`) or sync the CRLF working-tree bytes, so canonical and vendored hashes compare equal; re-sync and record both sha8s.

- **[MEDIUM] /caliper/power is a CORS-wide-open, unauthenticated process-kill endpoint** - `line 143-157` — CONFIRMED (mechanism verified end-to-end).
  What: the route accepts any POST with `{"action":"stop"}` and hard-exits ComfyUI via `os._exit(0)`. The launcher runs `--enable-cors-header` with no origin (start-comfyui.cmd:19; ComfyUI's argparse uses `const="*"`), so the CORS middleware allows any origin on 127.0.0.1:8188.
  Trigger: any webpage visited by the user issues a preflighted `fetch('http://127.0.0.1:8188/caliper/power', {method:'POST', ...})`. Chrome's Private Network Access increasingly blocks public→local requests, but Firefox/Safari do not.
  Impact: drive-by shutdown of the backend — a killed in-flight render (lost work) and DoS on the local tool. `GET /caliper/vram` under the same posture also discloses the process table (names/pids/bytes) and full `sys.argv`. Context that bounds severity: ComfyUI's own `/prompt`, `/free`, `/interrupt` are equally exposed once that flag is on, so this node enlarges the blast radius (whole-process exit) rather than opening the hole; listen is loopback-only.
  Fix: pass an explicit origin (`--enable-cors-header http://localhost:4173`) in the launcher, and/or have the node require a shared-secret header (or check `Origin`/`Host`) before scheduling `os._exit`.

- **[MEDIUM] Failed counter read returns HTTP 200 with zeroed data and an error key the client never reads — silent fallback to a different source** - `line 102`, `line 140` (node) with `src/components/StatusFooter.tsx:103-106` (consumer) — CONFIRMED.
  What: on subprocess/JSON failure the route returns 200 with `{"adapter_bytes":0,"processes":[],"error":<type>}`. The frontend contract declares `error?` (src/api/types.ts) but `VramDiagnostic` never reads it: `counterUsed = vram.adapter_bytes > 0 ? ... : null` silently falls back to `/system_stats` VRAM numbers and the process list renders empty.
  Trigger: powershell spawn failure, 15s counter timeout, or malformed stdout.
  Impact: the status instrument shows plausible numbers from a different source while the requested measurement failed — a silent lie under the project's own "status text must be truthful: report what the SERVER says" rule.
  Fix (node side, this file): return 503 (or a machine-checkable `"ok": false`) when the process table errored, instead of 200-with-zeros; the client then can't mistake degradation for data.

- **[LOW] English-only counter names fail silently to a zero payload with no error marker** - `lines 37-46` — CONFIRMED.
  What: `Get-Counter '\GPU Adapter Memory(*)\Dedicated Usage'` uses localized counter paths on non-English Windows; with `$ErrorActionPreference='SilentlyContinue'` a failure leaves `$adapters` empty and line 46 prints `{"adapter_bytes":0,"processes":[]}` — valid JSON, so the Python side never sets `error`.
  Trigger: non-English locale, or GPU perf counters disabled.
  Impact: indistinguishable from "no dedicated usage" — same silent-lie class as above, one layer deeper (even the error key is absent). Low on this owner's English single-machine deployment; a portability trap.
  Fix: use counter GUID paths or `$ErrorActionPreference='Stop'` with a try/catch that prints an explicit `{"error":...}` object the Python side can propagate.

- **[LOW] Deprecated `asyncio.get_event_loop()` for the exit timer** - `line 156` — CONFIRMED.
  What/Trigger: inside a running coroutine it returns the running loop today, but on Python 3.12+ the call is deprecated for anything but a running loop and is the documented foot-gun.
  Impact: none currently; a warning/future break on Python upgrades.
  Fix: `asyncio.get_running_loop().call_later(0.5, os._exit, 0)`.

## Missing safeguards
- `torch` stats use a blanket `except Exception: pass` (lines 138-139): a CUDA query failure yields `"torch": {}`, indistinguishable from "no CUDA installed" — set an `error` marker like the process table does.
- Per-model `except Exception: continue` (lines 125-126) silently omits models whose introspection failed mid-race; report a skipped count so "what's resident" stays a complete ground truth.
- Error results are cached for the full 4s TTL (line 105) — a transient powershell hiccup suppresses retries for 4s; acceptable, but stamping error entries with a shorter TTL would recover faster.
- No `.gitattributes` pinning `comfy/*.py` EOL, leaving the byte-parity invariant unenforceable (root cause of the DRIFTED finding).
- `_lock = asyncio.Lock()` at module import (line 68) is loop-lazy only on Python ≥3.10; if this carrier ever targets older Pythons, create the lock lazily inside the server's loop.
