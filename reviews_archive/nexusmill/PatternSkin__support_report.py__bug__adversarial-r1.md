# Colibri Review - bug (FULL pass, adversarial-era FIRST review) - PatternSkin/support_report.py

- **Source path:** `PatternSkin/support_report.py` (+ ui_text.py reviewed in the same pass - see below)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37 postures A-D
- **sha256 reviewed:** pre-wave sha (6267 B, 177 lines); post-wave restamp below
- **Date:** 2026-10-02 · **Mode:** bug, FULL pass - the file's FIRST adversarial-era review (owner-ordered item 2 of the open-items program; prior art = the 2026-08-27 hy4 spec tranche + ps_support_report_fixes probe battery, both green on entry)
- **Context pack:** full read; obs.py's RotatingFileHandler verified LIVE in source (maxBytes=1_000_000, backupCount=3 - the roll the docstring references is real machinery); the 2026-08-27 spec rulings (one-click-per-incident, payload disclosed, scrub rules) loaded as claims; the probe's pins cross-checked.

## Verdict
Shippable after a 2-finding wave. The transport/scrub/store core honors its recorded rulings (scrub verified live for tokens/bearer/user-paths/home; G20 never-raise on reply polling; atomic record writes; consent flows live in the UI layer per spec).

## Bugs & vulnerabilities

**[LOW-MED] SR-ROLLED-TAIL - read_log_tail never read the rolled sibling its own docstring promised** - `line 77`
- What: the docstring promised "plus rolled sibling if the live file is tiny"; the code read ONLY the live file. obs.py rolls at 1 MB x 3 backups - right after a roll the live log is tiny and the incident context lives entirely in patternskin.log.1, i.e. the report loses its tail exactly when it matters most.
- Trigger: any support report sent shortly after a log rotation.
- Fix (W1): budget the cap live-first; when the live tail is under cap and a .1 sibling exists, prepend its tail within the remaining budget.
- Verification: CONFIRMED (obs rotation verified at the bytes; battery W1a RED pre-fix -> GREEN post; mutation m1 caught).

**[LOW] SR-PAYLOAD-FIT - the trim was single-shot with no guaranteed fit** - `build_report line 106`
- What: one overshoot slice (+4096 slack) and no re-check - a payload still over the cap after trimming (or oversized by an untrimmable error field) shipped oversized to a server that enforces the same cap, converting a local guard into a remote rejection.
- Fix (W2): after the trim, log_tail drops to empty if still over, and a STILL-oversized payload raises ValueError (loud, caller-owned - the operator owns the user-facing message).
- Verification: CONFIRMED (battery W2b RED pre-fix -> GREEN post; mutation m2 caught).

## Adjudications (L2.5)
- One-click-per-incident dedup lives in the UI layer per the 2026-08-27 rulings (verified in __init__'s operator) - not re-litigated here.
- The scrub scope (r8_ tokens, bearer values, /Users/<name> paths, home) matches the recorded ruling; platform.platform() carries no username (verified).
- `check_replies`' per-id try/except catches the malformed-record KeyError path too (the rec["id"] concat sits inside the try).

## ui_text.py (same pass)
CLEAN - one pure function; the FS-1 sentinel (-1 -> "Part - / N"), str-key tolerance, 1-based display and face-count formatting all verified at the bytes. No findings; no record row needed beyond this note.

## Remediation postscript
W1/W2 applied same session; post-wave sha8 recorded at commit. Battery tests/test_perfection_support_report.py 9 rows (RED-first proven, 2/2 mutants caught); prior probe ps_support_report_fixes.py still green; FULL SUITE 36/36 ALL PASSED under the battery venv (2026-10-02).
