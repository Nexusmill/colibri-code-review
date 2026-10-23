# Colibri review — sign/install_cert.ps1 (bug)

- **Source:** `C:\Users\User\source\repos\Tools\sign\install_cert.ps1`
- **Model:** claude-fable-5 (in-session), gating grok-4.3 (smoke-run) findings
- **sha256:** `364bee75b628ce4f779819bf0d0a63ea99dd807c4e8eb12b8a5e234f7a7433d9`
- **Date:** 2026-09-02 · **Mode:** bug
- **Context:** one-shot YubiKey PIV cert-import helper, run by hand with a human PIN. Signing is verified working ([[nexusmill-release-signing]]).

## Verdict
Sound. The external HIGH is refuted; one genuine LOW.

## Fixed / refuted since external review

**[REFUTED — was flagged HIGH] "`Start-Process -ArgumentList "…$Der…"` breaks ykman on a path with spaces"**
- Line 54 uses ARRAY-form `-ArgumentList @("piv","certificates","import",$Slot,"`"$Der`"")`. `Start-Process` space-JOINS array elements (it does not do the call-operator's smart per-arg quoting), so the manual `` `"$Der`" `` quotes are exactly what keeps a spaced path as one argument — they are correct, not harmful. Decisive evidence: the default `$Der` is `"…\nexusmill llc.der"` (contains a space) and signing has succeeded via this script. The external finding assumed call-operator quoting semantics, and also mis-cited the line (42 vs 54) and mis-rendered the backtick-escapes as backslashes. Refuted.

## Bugs & vulnerabilities

**[LOW] Step 3/4 `piv info` exit code is discarded** — `line 60` `Start-Process … -ArgumentList @("piv","info") -NoNewWindow -Wait | Out-Null`
- `-Wait` but no `-PassThru`/exit check; a failure of the informational slot-state display is silently ignored. The import step (line 54-56) correctly checks `$p.ExitCode`; only this cosmetic display step doesn't. Fix: `-PassThru` + check, or accept as intentionally-informational.

## Missing safeguards
- None material; the pre-flight (EKU + pubkey match) is thorough.
