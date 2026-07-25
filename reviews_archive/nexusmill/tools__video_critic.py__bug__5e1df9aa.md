# BUG review: tools\video_critic.py

- source: `C:\Users\User\source\repos\Nexusmill\tools\video_critic.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:10
- tokens: in 2810 / out 2582
- est cost: $0.0472

---

## Verdict
Not safe to ship as-is: it mostly "works," but several silent-failure paths mean the quality gate can pass (or mislead the vision pass) without actually checking what it claims. Biggest single risk: the contact sheet silently drops beat flags (dead code at line 95) and substitutes grey placeholder frames on keyframe failure, so the mandatory vision pass judges fabricated/blank content without any warning.

## Bugs & vulnerabilities

**[HIGH] Beat flags are never drawn on the contact sheet (dead code)** - `line 95`
- What: `bad=[f for f in b.get("_flags",[])]` reads a key `_flags` that is never set anywhere (flags are stored in the local `flags` list and in `report["beats"][i]["flags"]`, never back into `b`), and `bad` is never used. No flag text is ever rendered onto the sheet.
- Trigger: any beat with a P0 flag (STATIC, JITTER, STILL SOURCE).
- Impact: the docstring (lines 7-9) promises the sheet is labelled for the vision pass to judge sync/quality; reviewers/vision model see a clean sheet while `critique.json` says FAIL. The "mandatory quality gate" visually contradicts its own verdict.
- Fix: draw the beat's flags (from the `flags` list computed at lines 49-55) onto the cell, e.g. `dr.text((x+10, yy+60), "FLAGS: "+"; ".join(flags), font=fb, fill=(220,60,60))`, and delete the dead line 95.

**[HIGH] Missing ffmpeg/ffprobe causes an opaque crash; missing video causes an unhandled ValueError** - `lines 16, 21-22, 26`
- What: `FF`/`FP` are `shutil.which(...)` results with no None check. If absent, `subprocess.run([None, ...])` raises `TypeError`. If ffprobe runs but returns empty stdout (unreadable/missing video file), `float("")` raises `ValueError`. Neither is caught; `analyze` has no top-level error handling and `__main__` (line 114) doesn't either.
- Trigger: ffmpeg not on PATH, or a corrupt/missing video path passed as argv[1].
- Impact: the gate crashes with a traceback instead of a clear FAIL, and any pipeline calling this treats the exception ambiguously (crash ≠ FAIL verdict).
- Fix: at startup, `if not FF or not FP: sys.exit("ffmpeg/ffprobe not on PATH")`; wrap `dur()` in try/except and emit a hard FAIL report rather than raising.

**[MEDIUM] Keyframe failure is silently replaced with a grey placeholder** - `lines 85-86`
- What: on any exception from `keyframe()` (e.g. `t=(t0+t1)/2` beyond video duration, which makes ffmpeg exit non-zero and `check=True` raise), a blank grey image is pasted with no annotation.
- Trigger: a beat whose midpoint exceeds the video duration, or any ffmpeg hiccup.
- Impact: the vision pass judges a fabricated grey frame as if it were real content; nothing in the sheet or report records the failure — a true silent failure in a quality gate.
- Fix: record the failure in the report (`be["keyframe_error"]=...`, add a p1_flag) and render "KEYFRAME FAILED" text on the placeholder.

**[MEDIUM] No validation of beats.json — KeyError/TypeError crash mid-run** - `lines 44, 56, 84, 91, 112`
- What: `b["t0"]`/`b["t1"]` are required but never validated; non-numeric or missing values raise `TypeError`/`KeyError` deep inside `analyze` (after expensive full-video frame extraction at line 39). `json.load` at line 112 has no error handling. Non-list JSON (e.g. a dict) iterates over keys and crashes confusingly.
- Trigger: malformed beats.json: missing `t0`, string times, or top-level object instead of array.
- Impact: wasted minutes of ffmpeg extraction followed by a crash; no actionable error message.
- Fix: validate up front: `assert isinstance(beats, list)`; per beat, coerce/check `float(b["t0"]) < float(b["t1"])`, clamp to `[0, D]`, and fail fast with the beat index in the message.

**[MEDIUM] Spurious STRUCTURE P0 on empty beats list** - `lines 62-64`
- What: `k0 = ""` when `beats` is empty, and `"" not in ("card","bumper")` is True, so an empty beats file produces a P0 failure about "opens on ''".
- Trigger: `beats.json` = `[]`.
- Impact: misleading failure message; also `rows = 0` at line 79 produces a 0-height image — `Image.new("RGB",(1440,0))` and `sheet.save` behavior is fragile across PIL versions.
- Fix: explicitly reject empty beats with a clear error before analysis.

**[MEDIUM] Whole video loaded into RAM as float64 numpy frames** - `lines 28, 39`
- What: every downscaled frame is converted to a Python `float` (float64) array and kept in a list for the entire video. At 12 fps, 100 s → 1200 frames × 160×~90 px × 8 B ≈ 140 MB; longer or wider inputs scale linearly with no cap.
- Trigger: long/high-resolution input video.
- Impact: memory exhaustion; also the `Image.open` objects in the list comprehension are never explicitly closed, and `shutil.rmtree(..., ignore_errors=True)` can silently leave the temp dir behind on Windows due to open handles (resource leak that is then hidden).
- Fix: stream frames (process pairwise diffs without retaining all frames, or use `ffmpeg` pipe to rawvideo), use `np.float32`/`uint8`, use `with Image.open(...)`, and don't ignore rmtree errors.

**[LOW] ebur128 loudness failure is silent** - `lines 73-75`
- What: `r.returncode` is never checked; if ffmpeg fails or the video has no audio stream, `il` is empty and `report["audio_tail"]=[]` with no flag.
- Trigger: video without an audio track.
- Impact: the audio check appears to have run but produced nothing; no flag raised.
- Fix: check `r.returncode` and add a p1_flag when no loudness summary is parsed.

**[LOW] File handles leaked via `open()` without context manager; double JSON write** - `lines 97, 101`
- What: `json.dump(report, open(...))` never closes the file explicitly (relies on refcounting), and the file is written twice — once without `auto_verdict`, once with. The first write is pure waste and briefly leaves an incomplete report on disk that a concurrent reader could pick up.
- Fix: delete the dump at line 97 and write once with `with open(...) as f:` after setting `auto_verdict`.

**[LOW] Segment slicing is off-by-one/fragile at boundaries** - `line 44`
- What: `seg=diff[max(0,a-1):max(a,z)]` — for a beat where `int(t0*FPS)==int(t1*FPS)` (very short beat < 1/12 s) or `t1<=t0`, the slice is empty and the beat silently reports motion 0.0, which then triggers a STATIC P0 for a measurement that never happened.
- Fix: guard `z <= a` and mark the beat as unmeasurable (distinct flag) instead of motion=0.

## Missing safeguards
- Startup check that ffmpeg/ffprobe exist; top-level try/except in `__main__` mapping any failure to a non-zero exit + FAIL artifact.
- Schema validation for beats.json (types, `t0 < t1`, times within duration, `kind` in the documented enum).
- No check that `frames()` produced a non-empty list before computing diffs (line 40 only guards `len>1`; `len==0` yields `diff=[0.0]` and a fake "all static" analysis).
- Keyframe timestamps should be clamped to `[0, D]`.
- Temp-dir cleanup should not use `ignore_errors=True`; failures should surface.
- No tests at all: no fixture video, no test that flags render on the sheet, no test for malformed beats.json or missing ffmpeg.