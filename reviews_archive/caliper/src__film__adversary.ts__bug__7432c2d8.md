# Colibri bug review — src/film/adversary.ts

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 7432c2d8e2e2b1226af3a3377a78cafbefdd523229ffe78f5c5321e989fa189f

### Meta
- path: src/film/adversary.ts | sha8: 7432c2d8 (matches expected) | lines: 217 | context-pack: jcodemunch outline + references (sole runtime consumer: vite.film.ts autopilot-draft loop, lines 1689-1708; tests in src/film/adversary.test.ts; Storyboard contract in src/film/autopilot.ts:68-93); git log 6 commits (e333931→49c2bd2, adversary-era commits consistent with file contents)

### Review

## Verdict
This file is the deterministic, pure core of the critique gate — no LLM call, no parsing of model output here (that lives in `extractJson`/`validateStoryboard`/`askBrain` at the call site). The two ledger-mandated invariants hold: (1) **no parse-failure→pass path exists** — `judgeStoryboard` is synchronous and pure; any throw propagates to the outer catch → HTTP 400, the draft fails closed; the redraft loop's catch (vite.film.ts:1702-1705) `break`s keeping the *last failing* verdict, so a swallowed redraft failure never reads as a pass. (2) Empty-degeneration cannot read as clean: `validateStoryboard` throws on empty beat/boardPrompt/shootPrompt upstream (autopilot.ts:281), and even a hypothetical all-empty board still racks up C/F from continuity/transition/size checks. The `worst()` fold (line 31, ORDER A<F) is correct, and shot labels are consistent (`s.index + 1` matches `index: i` 0-based at autopilot.ts:282). The real defects are two anchor-contamination fail-opens in the newer craft checks and one regex asymmetry.

## Bugs & vulnerabilities

- **[HIGH] Manifesto shorthand gate reads the mandated anchor as camera/timing spec — common anchor prose silently disables the gate** - `line 174` (regexes at 172-173, vs the file's own anchor-stripping doctrine at 150-158) — CONFIRMED mechanism, PLAUSIBLE-to-common trigger.
  What: `shorthand` tests the RAW `s.shootPrompt`, which contains the anchor block injected verbatim by `withWorldAnchor` (vite.film.ts:1691, 1699). `TIMING_TOKENS` matches bare prose words `then|first|second|until|through` and `CAMERA_TOKENS` matches `hold[s]?|static|locked|pan|tilt` — words routine in character/setting anchors ("her **first** night in the city", "she **holds** a lantern", "walks **through** the market").
  Trigger: any anchor containing one such word (or a "wide-brimmed hat", see next finding) makes `!CAMERA_TOKENS.test && !TIMING_TOKENS.test` false for EVERY shot.
  Impact: fail-open — the owner's 2026-08-30 manifesto clause ("terse prompts machine-expand into garbage") becomes inert for that film: no C finding, no redraft, director-shorthand prompts ship to costing/production with real cloud money. This is the exact opposite of the cram rule 20 lines above, which the same file carefully anchor-strips (comment at 150-154 explains why).
  Fix: apply `actionOf(s.shootPrompt)` (or the token-strip used at 113/123-124) before both regex tests.

- **[MEDIUM] Shot-size variety check counts anchor vocabulary as shot sizes** - `line 163` — CONFIRMED mechanism, PLAUSIBLE trigger.
  What: `SIZE_WORDS` scans `s.boardPrompt` unstripped; `\bwide\b` matches "wide-brimmed hat", `\bextreme\b` matches "extreme exhaustion" inside the verbatim anchor.
  Trigger: anchor contains a size word; one genuine size word elsewhere ("close-up") plus the anchor word makes `sizes.size >= 2`.
  Impact: fail-open — the "a film of one size is a security camera" C finding silently passes; no size direction reaches the engine. Same root cause and fix locus as the HIGH above.
  Fix: strip anchor tokens (reuse the 112-113 pattern) before matching SIZE_WORDS.

- **[MEDIUM] CAMERA_TOKENS inflection asymmetry yields false C findings (paid redrafts)** - `line 172` — CONFIRMED (provable regex behavior).
  What: `pan[s]?`, `tilt[s]?`, `track(?:s|ing)?`, `push(?:es|ing)?`, `pull(?:s|ing)?` are inflected, but `\bzoom\b`, `whip`, `orbit`, `dolly`, `crane` are not — "camera zooms in", "orbiting her", "the arm cranes up" all fail the test.
  Trigger: a well-formed prompt using an uninflected-variant verb with no other camera/timing token.
  Impact: fail-closed false positive — forces a redraft brain call that costs money and can churn a good storyboard, or drags the shipped verdict to C. Fix: `zoom(?:s|ing)?|whip(?:s|ping)?|orbit(?:s|ing)?|crane[s]?`.

- **[LOW] Grade "B" is unreachable; header comment says "graded A-F"** - `lines 2-3, 14` — CONFIRMED.
  Findings only emit C/F; the fold yields exactly A, C, or F. No consumer break — the redraft gate `!== "A" && !== "B"` (vite.film.ts:1693) is safe under any grade — but the docstring overstates and "B" is dead vocabulary in this judge. Fix: correct the comment or drop B from `AdversaryGrade` if no other producer exists.

- **[LOW] Hard-coded 20s engine ceiling duplicates capability knowledge** - `line 183` — CONFIRMED.
  The cap re-states engine limits that live in `maxClipSeconds` (store.ts, imported by vite.film.ts:14) and `ENGINE_CRAFT`; when an engine with a higher ceiling is added, this finding fires wrongly (fail-closed) until edited here. Fix: pass the ceiling in `opts` alongside `scenario`/`durationSec`.

## Missing safeguards
- No `seconds > 0` guard: a zero/negative-duration shot only gets caught indirectly — the 34% coverage tolerance (line 194) can absorb it, and the speech-rate check at `seconds * 2.6 + 2` with `seconds = 0` still allows up to 2 words. Add a finding for non-positive seconds.
- `actionOf` strips only the first exact copy of the anchor (line 155, `String.replace` single-occurrence): a brain that also echoed a near-copy of the anchor leaves residue that inflates the cram length/connective measures. Stripping all occurrences (or the token-set approach used at 113) is more robust.
- Call-site observation (not this file): vite.film.ts:1702-1705 swallows the redraft error into `lastErr` and ships the failing verdict with only `passes` recorded — the verdict stays truthful (never a pass), but nothing tells the owner the redraft crashed vs. simply failed to improve; consider a `redraftError` field on the verdict record.
- The transition canon here (`CANON`, line 133), the type docstring (autopilot.ts:77-79), and the correction note (line 137) agree exactly (action|match|sound|dissolve|smash|invisible|hard) — no enum drift today; worth a shared constant so the three copies cannot diverge.
