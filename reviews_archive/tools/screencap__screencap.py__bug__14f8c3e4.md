# Colibri review — screencap/screencap.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\screencap\screencap.py`
- **Model:** claude-fable-5 (in-session), gating grok-4.3 findings
- **sha256:** `14f8c3e43468052b...` (grok reviewed the same bytes)
- **Date:** 2026-09-02 · **Mode:** bug
- **Context:** read-only capture tool (documented occlusion-irrelevance / PrintWindow design honored). Findings verified by reading the cited lines directly.

## Verdict
Three real robustness defects, all MEDIUM (a dev tool; no security surface). Capture core is sound.

## Bugs & vulnerabilities

**[MEDIUM] `region` command off-by-one → IndexError instead of usage** — `main()` line 562-565
- Guard is `if len(sys.argv) < 6` but the branch then reads `sys.argv[6]` (the output path). Invoking `screencap.py region x0 y0 x1 y1` (6 argv elements, no output) passes the guard and raises `IndexError`. CONFIRMED by read. Fix: guard `< 7`.

**[MEDIUM] `burst` on a title match never wakes a minimized window → black frames** — `burst()` line 476-484
- Unlike `capture_window`/`capture_pid`/`capture_process`, the `burst` title path extracts `rect` from the match but never calls `_wake_if_minimized`. A minimized target yields an off-screen rect → every frame is black/garbage. CONFIRMED by read (no wake call in the block). Fix: extract `hwnd = matches[0][0]`, `woke = _wake_if_minimized(hwnd)`, refresh rect, and `_sleep_minimized` after the loop.

**[MEDIUM] `_pids_for_process_name` ignores tasklist failure + naive CSV split** — `line 192`
- No `returncode` check after `subprocess.run(["tasklist",…])`; the `line.split('","')` hand-parse breaks on an image name containing `,` or `"`. A tasklist failure yields a silent empty PID list ("no process") with no signal. CONFIRMED by read. Fix: check returncode; parse with `csv.reader`.

## Missing safeguards
- None beyond the above.
