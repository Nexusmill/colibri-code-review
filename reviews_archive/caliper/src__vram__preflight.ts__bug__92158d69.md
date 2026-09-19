source: src/vram/preflight.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: 92158d69408f5d763f51b300d06c496fee0645281ed725e1d7fb71059fe86b6e
date: 2026-09-19 12:15
mode: bug
context: VRAM preflight estimate; /caliper/vram ground truth; silence-over-guess law excluded the unreachable case

Finding 1 [MEDIUM] REFUTED by the repo's own pinned doctrine: preflight.test.ts line 61-63 ("a degraded read (free zeroed) is not data either") adjudicates free=0 as a DEGRADED sensor reading, not a full card - an initial one-character "fix" (`>= 0`) was applied and then REVERTED after the pinned test went red (the verification gate catching the scan's wrong premise). The guard keeps `> 0`; a doctrine comment now names the adjudication. The file's remaining findings (see %TEMP%/hunt1/vram__preflight.md Finding 2+) are OPEN for the next session.
