Source: PatternSkin/accel_ipc.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 743b5f4acaa63dda55e7c8983e69170095ed8b0e20d4f35c3fbe37c74132443c
Date: 2026-08-06
Mode: bug (FIRST review - never in .colibri_reviews/_manifest.json or _hunt_plan.json)
Context pack: full 127-line file read; find_importers=0 (dynamic `import accel_ipc as ipc`, not
statically resolved) so cross-referenced via search_text: sole consumers are accel_worker.py
(server side) and accel.py's _WorkerClient.request()/close() (client side, lines ~1176-1201);
read _WorkerClient in full to see the actual timeout values passed in (10.0s default) and the
threat-model docstring ("Deliberately NOT pickle... a raw-bytes-plus-declared-shape/dtype payload
can only ever produce an array, never execute code"); checked docs/remediation_manifest.json and
docs/deferred_manifest.json for prior art on this file - none found (confirms first-ever review).

## Verdict
Shippable, and unusually well-hardened for a brand-new module: every untrusted-length field
(header_len, per-array shape/dtype-derived nbytes) is bounds-checked with plain Python ints
(no fixed-width overflow) BEFORE any read or allocation is attempted, and the frame format
deliberately avoids pickle to keep a local-socket peer from being a code-execution boundary.

## Bugs & vulnerabilities
None confirmed. Adversarially traced and refuted:
- np.dtype(spec["dtype"]) with a malicious/crafted string (e.g. attempting dtype="O" to get raw
  bytes reinterpreted as object pointers): numpy itself refuses to construct an object array from
  a raw buffer via frombuffer, so this can't be used to smuggle pointer reinterpretation across
  the wire even before this file's own MAX_PAYLOAD_BYTES cap is considered.
- A crafted huge single dimension (e.g. shape=[10**18]): nbytes is accumulated in a plain Python
  int (no wraparound, per the code's own comment at line 116) and checked against
  MAX_PAYLOAD_BYTES BEFORE any read_exact() call for that array - confirmed by tracing recv_frame
  end to end, the total>cap check runs inside the spec-building loop, strictly before the
  read-arrays loop.
- header["arrays"] not a list (e.g. a dict/string): `for spec in header["arrays"]` would iterate
  wrong-shaped items, but `spec["name"]` etc. raise inside the existing try/except Exception ->
  FrameError wrapper; no unhandled crash.

## Missing safeguards
- read_exact()'s `timeout` resets per sock.recv() call inside its while loop rather than bounding
  the whole read, so REQUEST_TIMEOUT (used by the caller) is really an idle-timeout, not a
  hard total-frame deadline. Traced against the actual threat model in this module's own
  docstring ("if this process dies or hangs, the caller falls back") - a full hang produces zero
  bytes on the very first recv(), which the idle-timeout catches immediately; a slow-but-alive
  trickle over a loopback socket to a subprocess this code itself spawned is not a realistic
  failure mode. Noted, not reported as a finding.
