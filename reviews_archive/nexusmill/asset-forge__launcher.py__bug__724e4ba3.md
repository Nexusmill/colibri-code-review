# Colibri Review - bug (FULL re-audit) - asset-forge/launcher.py

- **Source path:** `asset-forge/launcher.py` (twin: asset-forge-user/launcher.py (byte-identical; apply both))
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (Asset Forge tooling)
- **sha256 reviewed:** `724e4ba39e721ea8dcd7c5c0d75c5ba4e78a75bdef1486bb11ae2794f01ad760` (sha8 `724e4ba3`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling: pre-gate audits untrusted - no delta)
- **Context pack:** FULL read of the current bytes at e7be3d43 (owner ruling 2026-09-10: the file's pre-gate reviews are untrusted); jCodemunch get_file_outline + find_importers (none of the six is imported by product code - entry points/tools); tools/sync_builds.py WHITELIST (which of the six are shared twins); the remediation/deferred rows and the prior .colibri_reviews records for launcher/secrets/make_user_edition loaded as CLAIMS re-verified at the bytes; stdlib urllib proxy logic read from the buildenv's own source; the windowed-process stream state proven with pythonw.exe started without a console.

## Verdict
Shippable after two fixes. The LNCH-1 architecture holds (bind-and-hold on :0, readiness = an HTTP answer from our own socket, return-code-driven window fallbacks, temp profile always removed, durable last-resort log); the two defects are in the readiness probe's transport and in the very branch the earlier round added to report a settings failure.

## Bugs & vulnerabilities

**[MEDIUM] _wait_for_server probes loopback readiness through the system/HTTP_PROXY proxy - on a proxied machine the app refuses to start (or reads a proxy error as READY)** - `line 65`
- What: urllib.request.urlopen uses the default opener, which honours HTTP_PROXY / the Windows registry proxy; urllib bypasses a proxy only for hosts named in NO_PROXY (proxy_bypass_environment: 'don't bypass, if no_proxy isn't specified' - read from the buildenv stdlib). So the GET to http://127.0.0.1:<port>/ goes to the PROXY. Reproduced: HTTP_PROXY=http://127.0.0.1:9 -> the default opener times out, a ProxyHandler({}) opener answers 200.
- Trigger: Any machine with HTTP_PROXY/http_proxy set (corporate dev boxes, some VPN/AV setups) or a registry proxy whose bypass list lacks 127.*, and no NO_PROXY entry for loopback.
- Impact: Proxy unreachable/refusing: URLError every 100 ms for the full 20 s, then 'Asset Forge couldn't start its local server' and exit - while the server is up. Proxy answering 4xx/5xx: HTTPError is treated as READY (a false positive, benign only because WebView2 bypasses loopback proxies itself).
- Fix: A proxy-free opener (build_opener(ProxyHandler({}))) for the readiness GET. Battery LNCH_readiness_ignores_http_proxy RED (timed out after 6.7 s) -> GREEN on the fixed copy.
- Verification: CONFIRMED: stdlib logic + live reproduction with a discard-port proxy; the probe sets the proxy before urllib builds its global opener, exactly the state a real launch starts in.

**[LOW] The settings-persist failure branch writes to sys.stderr, which is None in the windowed exe - the launcher died at import on the path built to report the failure** - `line 28`
- What: AssetForge.spec builds console=False; a Windows process without a console has sys.stdout and sys.stderr == None (proven: pythonw.exe started with DETACHED_PROCESS reports (None, None); PyInstaller 6.21 installs no NullWriter). The except branch at line 27-28 (the LNCH-1 'silent settings-save' fix) does sys.stderr.write(...) -> AttributeError propagates out of the handler and out of the module import.
- Trigger: Launch from Pattern Skin with --library-dir while config.save_settings raises (settings file/dir unwritable, disk full, a malformed settings JSON).
- Impact: No window, no message box, no launcher log line - the exact silent-death class LNCH-1(4) closed elsewhere; _show_error's non-Windows stderr write has the same hazard.
- Fix: Remember the failure in _SETTINGS_ERR and let main() write it through _log_last_resort (durable without a console); guard the remaining stderr write. Battery LNCH_windowed_survives_settings_failure (child interpreter with stderr=None + save_settings raising) RED -> GREEN.
- Verification: CONFIRMED by reproduction in a child interpreter mirroring the windowed state.

## Missing safeguards / notes
- Windows 'system proxy' (registry) has the same exposure as HTTP_PROXY when its bypass list lacks 127.*; this box has none configured, so only the env form was reproduced.
- os.chdir(sys._MEIPASS) when frozen leaves relative output paths under the temp bundle dir - every product path is HOME-based, so inert today.

## Adversarial verification pass (refuted claims)
- _SRV creation at import can fail silently (no _show_error yet defined) -> refuted: binding 127.0.0.1:0 is OS-assigned; the failure needs the loopback stack itself broken - not a reachable condition on a working machine
- the chromeless profile is removed while the browser still runs -> refuted: Popen(...).wait() returns only after the browser process exits; the finally runs after
- print() to a None stdout crashes the last-resort path -> refuted: CPython's print returns silently when file is None; only the stderr .write at 28/206 raises
- --library-dir path traversal -> refuted: a CLI argument the local user passes to their own process; no privilege boundary (already refuted 07-24)
- the WebView2 host inherits no token and the app's origin guard blocks it -> refuted: the guard admits same-origin requests; the host loads the URL directly, no token needed (verified in the app.py unit)
- _SERVER_ERR cross-thread read without a lock -> refuted: single attribute rebinding under the GIL; read after the poll loop only (adjudicated 07-24)

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `9c0ce67eafc981a9a53bfb542280f02a15774e976baad2ef66bb216101f67d67`. Rows AF-LAUNCH-PROXY-READY, AF-LAUNCH-STDERR-NONE in `docs/remediation_manifest.json`, same commit.

