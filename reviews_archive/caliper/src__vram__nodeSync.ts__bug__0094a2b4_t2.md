source: src/vram/nodeSync.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: 0094a2b48f14179ac8183d16bc194b1ed422c81e3b5c1388a0da74a0c6c1e1ca
date: 2026-09-19 13:16
mode: bug
context: node sync verdict; silence-over-a-guess law

1 finding, REFUTED at current bytes: [HIGH] "!deployed returns pre-self-id even when the backend is away" - the finding assumed deployed=undefined means backend-away, but BOTH production callers (StatusFooter lines 57 and 231) call nodeSyncVerdict only after the CaliperVram union narrow from THIS session's T1 fix: a backend-away answer never reaches the function (the caller yields null verdict itself). At the call sites, undefined means exactly "backend answered, pre-self-id node" - which pre-self-id correctly names. The T1 union removed the confusion the finding describes.
Scan log: %TEMP%/hunt2/vram__nodeSync.md
