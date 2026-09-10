<!-- colibri review
source: src/components/StatusFooter.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 024ddaa64bf9a27485388bde3d0d2e1f4c9e2cb455ac27444de1fc23b2a114a8
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. diagnostics is built from state the footer already holds (server-sourced lines only); the copy key uses the diag-unload tiny-button idiom; blocked clipboard falls back to select-all lines - every press shows a result.

- REFUTED in pass 3: "the torch reserved parens math could NaN" - `(m.loaded_bytes / 2 ** 30).toFixed(1)` operates on numbers; the reserved fallback `(m.torch.reserved ?? 0 / 2 ** 30)` groups wrongly in text only when reserved is undefined (renders "0.0r" - harmless); kept as-is, no arithmetic depends on it. Wait - flagged MYSELF in refutation: `(vram.torch.reserved ?? 0 / 2 ** 30)` binds as `reserved ?? (0/2**30)` = reserved when present else 0 - then .toFixed(1) on the RESULT. Actually correct: `(...).toFixed(1)` wraps the whole paren expression. No defect.

## Postscript (adversary round 1 remediation, same session)
Finding 1 (reserved precedence) FIXED at the root + regression test; the
wrong refutation above is corrected in place - the record must not teach
the lie it caught. Finding 2 (unguarded version) FIXED (` v${v}` only
when a version exists). Two more defects caught by my own tests while
pinning: a null payload was mislabeled pre-self-id (now unverifiable -
no payload is not a payload-without-self-id) and the argv filter dropped
flag values (now the full tail from the first flag). buildDiagnostics is
exported and pure with 4 pinned cases. Bytes advanced to c97dbfba.
