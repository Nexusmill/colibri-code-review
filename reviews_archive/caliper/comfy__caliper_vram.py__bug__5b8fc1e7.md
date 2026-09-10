# colibri bug review - comfy/caliper_vram.py (delta)

source: comfy/caliper_vram.py · reviewer: ZCode GLM-5.3 in-session · sha256 5b8fc1e7 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 6fa39b24 @ f7540c3 2026-08-21)
context: no logical delta exists - git diff f7540c3..HEAD is EMPTY for this path and git status shows the file clean; the 2026-09-05 full-hunt staleness check flagged it only because the prior review hashed a pure-CRLF rendering (6fa39b24 = LF-blob with \n -> \r\n) while the on-disk file carries mixed line endings (5b8fc1e7). Same logical bytes, EOL rendering differs.

## Verdict

Cache-hit by content - the 2026-09-03 review stands unchanged. The manifest row's sha is normalized to the on-disk bytes so future freshness checks compare like with like.

## Bugs & vulnerabilities

None (no change since the reviewed content).

## Fixed since last review

- (prior review's open items - the CORS+200-zeros residual noted on the project shelf - remain open by owner decision, unchanged.)

## Verified-correct

- The sha artifact explained mechanically: CRLF-normalization of the unchanged blob reproduces the prior recorded hash exactly.
