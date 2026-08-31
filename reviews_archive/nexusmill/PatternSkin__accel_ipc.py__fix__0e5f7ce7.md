# Colibri fix-pass record - PatternSkin/accel_ipc.py + accel_worker.py + accel.py (GLM-IPC)
- source: PatternSkin/accel_ipc.py (sha256 0e5f7ce7951824df19ff606d133395090a294bfdcc69ce4684bcbc580fc8621a) + accel_worker.py main + accel.py _spawn
- model: claude-fable-5 (in-session)
- date: 2026-08-15
- mode: fix (GLM-IPC finding + handshake safeguard)
- context pack: GLM 5.3 reviews (.glm_reviews ipc/worker units, colibri-gated same day, zero
  refuted); parent request() flow read (broad except made parent crash survivable, contract
  fix still owed); worker containment model preserved (die -> parent falls back).

## Verdict
Contract sealed and handshake shipped; battery 6/6 with a live worker subprocess (real kNN
round-trip after auth, imposter dropped, worker survives). Windows lesson recorded in the
probe: a dropped connection reads as RST (ConnectionResetError), not clean EOF.

## Fixed since last review
- GLM-IPC (a) non-list arrays TypeError escape -> FrameError
- GLM-IPC (b) object-dtype ValueError escape -> FrameError
- safeguard: one-shot accept token (argv + first line), legacy path intact
