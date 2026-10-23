# colibri review — birdcam/cli.py (delta + security hunt)

- source: `birdcam/cli.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: f458611257d1bd3873b254245c3e6843567cf16a72d9927f53a1b0e4b4bd6c24
- date: 2026-10-05 03:50
- context pack: prior bug reviews 95ff22ad/c0a0713b (hy4, delta-clean lineages); git delta
  45d9ca0→c88d8b6 (excluded-clip status sections, check-setup person-detector block, unpublish
  always-note fix per remediation 2026-09-23); state.retry_batch contract (takedown refusal);
  launcher surface (numbered .bat files call these commands).

## Verdict

Clean delta; no new findings. The takedown path is correctly ordered end to end, and the
resurrection guard the 2026-09-23 remediation prescribed is verifiably in place.

## Bugs & vulnerabilities (new findings only)

None. Verified clean, by trace:

- `cmd_unpublish` (294-339): YouTube deletion happens BEFORE any state mutation (a failed deletion
  leaves no false "removed" note); the note is written even when an earlier error string was
  present (331-334), `youtube_video_id` is cleared so recheck/retry ignore it, and state.py's
  retry_batch refuses batches carrying the note — the full takedown-safety chain holds.
- `cmd_retry --vanished` enforces the state-layer contract at the CLI: archive existence + byte
  hash verified before any reset (251-264).
- `cmd_check_setup` reports secrets as set/EMPTY only — no value ever printed (verified every
  print in the function); the person-detector block fails loudly with the fail-closed consequence
  spelled out.
- Exit-code ladder in main() maps every module error family; argparse SUPPRESS-flag handling
  (349-355, 410-411) keeps both flag positions working.

Adversarial pass: the unpublish ordering was re-traced against youtube_client.delete_video's error
branches (403-misroute finding lives there); the excluded-status grouping (56-76) was checked
against pipeline's reason-string formats. Prior findings not restated.
