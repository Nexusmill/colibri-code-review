# colibri gate — asset-forge/forge/secrets.py (grok round 5, security)

- **source:** asset-forge/forge/secrets.py (+ asset-forge-user twin, byte-identical G23)
- **model:** grok-4.6 security mode (external, .grok_reviews/2026-08-22_secrets_grok46.md) gated in-session by claude-fable-5
- **sha256:** a93d9f9c14c6b9af6b0b05fb55e9e63eb9f8c36a4ec2fd8c68ff3bcc7a0b7f1a (current bytes at dispatch, G36; == manifest sha8 a93d9f9c — file byte-unchanged since 2026-07-23)
- **date:** 2026-08-22 · **mode:** security (grok round 5; delta vs FOUR prior passes — 5a03f9c, glm20-7, af-secrets-robustness, af-secrets-nondict-store all pre-declared closed/accepted)
- **context pack:** module role + G18 design + the accepted-by-design RMW race + every closed robustness item pre-declared; verification traced _mac/_save/secret_set against source AND cross-checked the PatternSkin sibling keystore.py which implements the same keychain logic.
- **pre-dispatch:** literal/token scan of current bytes — NO embedded secrets (clean), confirmed before the file left the machine.

## Verdict
Shippable as-is under the tool's single-user desktop threat model, but ONE real
twin-drift worth closing. Grok's two HIGHs: the first is a REAL mechanism the PatternSkin
twin already guards (drift → downgrade to MEDIUM, self-inflicted); the second REFUTED at
its load-bearing multi-user precondition (Grok misread Unix dir permissions — the
confident-wrong-at-the-edges pattern), collapsing to the already-accepted RMW race.

## Findings after adversarial verification

**[MEDIUM, CONFIRMED — twin-drift; downgraded from Grok's HIGH] `_mac("set")` has no newline guard, so a multi-line value can inject a second `security` subcommand** — `_mac` lines 118-123
- Mechanism CONFIRMED via the repo's own evidence: the PatternSkin sibling `PatternSkin/keystore.py::_mac_keychain` implements the identical `security -i` write and ALREADY rejects it — `for fld in (name, svc, value): if ... any(ch in str(fld) for ch in "\r\n"): raise ValueError`, with the explicit comment "a newline would start a second `security` subcommand." That sibling guard is the team's own adjudication that `security -i`'s line-oriented parser breaks `shlex.quote`'s single-quote across a newline. `secrets.py` never got that guard → drift. (Runtime confirmation is macOS-only and I cannot execute it here — but the sibling precedent + comment is a first-party source, so CONFIRMED, not PLAUSIBLE.)
- **Severity downgrade rationale:** the only caller path is `config.save_provider → secret_set` with a value the USER pastes as their own API key on their own single-user machine. To trigger it a user must paste a crafted multi-line payload as their own key to attack themselves. Not remotely reachable, no second principal. Impact IF triggered is real (`add-trusted-cert` = user TLS trust root / MITM), which keeps it MEDIUM rather than LOW, and the fix is free.
- **Fix:** port the sibling's guard — reject `\r\n\0` in name/svc/value before the keychain call (and prefer a single argv vector or Security.framework over `security -i`). Apply to both twins (G23).

**[LOW, PLAUSIBLE — largely verified-stale] `_save` writes the tmp via `write_text` (follows symlinks) without O_NOFOLLOW/O_EXCL** — `_save` lines 90-104
- Grok's "no race" multi-user trigger is **REFUTED**: `HOME.mkdir(parents=True, exist_ok=True)` yields 0o777&~umask = typically **0755**, and a 0755 directory grants NO write bit to group/other, so a DIFFERENT local user cannot plant `secrets.tmp` in it. Grok's premise ("exists as 0755" → "local user plants the link") misreads the permission model — at 0755 only the owner can create/unlink entries there. The escalation to persistent symlink promotion depends on that false premise.
- What survives: `Path.write_text` does follow a pre-existing symlink / write through a hardlink — a real property — but the only principal who can pre-plant `secrets.tmp` under a 0755 owner-only dir is the OWNER, and an attacker already running as the owner can read `secrets.dat` directly (the symlink buys nothing). This collapses to the **already-accepted** "fixed-temp-name + RMW race, ACCEPTED-BY-DESIGN won't-fix (0o700 dir + single-user local tool)" decision in the remediation manifest.
- Residual actionable value is defense-in-depth only: `HOME.mkdir(mode=0o700, ...)` (create owner-only atomically instead of chmod-after-with-swallowed-failure) + `os.open(..., O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)`. Unverified as a live vulnerability (needs a genuinely group/world-writable HOME, outside the tool's threat model); logged PLAUSIBLE-LOW so Damien can accept-as-before or take the cheap hardening.

## Refuted and dropped
- Grok Finding 2's multi-user symlink-planting escalation — refuted on Unix dir-permission semantics (0755 is not writable by non-owners); retained only in the reduced defense-in-depth form above.
