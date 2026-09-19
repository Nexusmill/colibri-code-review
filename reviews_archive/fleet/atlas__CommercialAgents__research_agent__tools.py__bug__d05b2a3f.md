# Colibri review - atlas/CommercialAgents/research_agent/tools.py (bug, lead Phase-3 verification + remediation)

- source: `C:\Users\User\source\repos\fleet\atlas\CommercialAgents\research_agent\tools.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report under `_external_raw/` is INPUT)
- sha256 reviewed: `d05b2a3fe1b50b0f262e6bb47bcf3ab3fab966fd8e8743a0cdf6265103b94351` (172 lines, CRLF; identical to the bytes the fork reviewed)
- sha256 after remediation: `0b4ee6e355b1da7c36f5981dcc97ca8698c36e39ed715074e3adb7a68fbe167e`
- date: 2026-09-15
- mode: bug (Phase 3 lead pass over the 2026-09-10 re-audit's claim, then TDD remediation in the same tranche)
- context pack: full file (172 lines) read; `find_importers` -> only `research_agent/agent.py`, whose `agent_tools = [scrape_webpage, arxiv_search, submit_finding_for_review]` (line 88) binds the tool to the model - `save_research_file` is NOT bound (the deferred path-traversal row stays unreachable); `research_agent/prompts.py:27` tells the model to use scrape_webpage "to read deep technical specs or articles"; deferred rows TAVILY-EAGER-IMPORT / ARXIV-EAGER-IMPORT / RESEARCH-SAVE-FILE-PATH-TRAVERSAL / RESEARCH-CONFIDENCE-RECURSION re-verified present; Nexusmill's remediation manifest precedent (Asset Forge `replicate_flux._download` `_host_ok` allowlist) for the class; the fork's review + RED probe.

## Verdict
The fork's single CONFIRMED finding held: a model-chosen URL was fetched with no scheme, address or redirect check - textbook SSRF from a tool the prompt actively steers the model toward. Fixed fail-closed; the practical attack surface (metadata, loopback, private ranges, scheme smuggling, open-redirect bounce) is closed, with one documented residual (DNS rebinding). Retirement test: the scrape tool is provider-neutral and survives the Phase 3 provider factory - fix.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] `scrape_webpage` fetches any URL the model names - CONFIRMED, FIXED - `line 44-57` (pre-fix)
- What: `urllib.request.urlopen(Request(url, ...), timeout=10)` on the raw tool argument; no scheme check, no address check, default redirect following.
- Trigger (traced): the tool is bound (`agent.py:88`) and recommended by the system prompt; a prompt-injected page, a hallucinated URL, or a public page that 302s to an internal host puts `http://169.254.169.254/...`, `http://localhost:PORT/...`, `file:///...` in front of `urlopen`. Reproduced on the pre-fix bytes by `tests/test_research_scrape_guard.py`: 11 of 11 internal/non-http targets reached the (stubbed) network layer.
- Impact: the first 8000 bytes of the response return into the model's context and flow into research output that other agents upload (AssetManager) - credential/metadata exfiltration path; also a port-scan/side-channel against the workstation's loopback services.
- Fix applied: `_fetch_refusal(url)` - http(s) only; literal IP checked directly, otherwise `socket.getaddrinfo` and EVERY address must satisfy `ipaddress.is_global` (IPv4-mapped IPv6 unwrapped, zone id stripped; unresolvable -> refused); `_GuardedRedirectHandler.redirect_request` runs the same check on every redirect target and raises `URLError`; the tool fetches through a module-level `_OPENER = build_opener(_GuardedRedirectHandler)`. Refusals are the tool's normal error string (the model sees the reason), never exceptions.
- Why not the fork's snippet verbatim: it checked `is_private/loopback/link_local/reserved/multicast` (misses unspecified 0.0.0.0, shared 100.64/10, IPv4-mapped forms) and left redirects unguarded; `is_global` + the redirect handler cover those.
- Tests: 16 cases, 15 RED before the fix (the 16th, "public host fetched once", passed on both - the pre-fix tool also fetched public hosts, which is the point). Suite 51 passed.
- Manifest: remediation `FLEET-SCRAPE-SSRF`.

### Residual - DNS rebinding TOCTOU - DEFERRED
The guard resolves, checks, then urllib resolves again to connect. Deferred `FLEET-P0-SCRAPE-DNS-REBIND` (pin the connection to the validated address). The fork flagged the same gap.

## Deferred rows re-verified PRESENT on these bytes (not re-fixed)
FLEET-P0-TAVILY-EAGER-IMPORT (module-level Tavily construction under a broad except), FLEET-P0-ARXIV-EAGER-IMPORT (`arxiv_search = ArxivQueryRun()` at import), FLEET-P0-RESEARCH-SAVE-FILE-PATH-TRAVERSAL (`save_research_file` still unbound - unreachable), FLEET-P0-RESEARCH-CONFIDENCE-RECURSION (`submit_finding_for_review` builds a fresh Confidence Agent per call).

## Adversarial pass on the fix
- `build_opener` with a `HTTPRedirectHandler` subclass drops the default handler (`issubclass` skip) - asserted by `test_the_tool_uses_the_guarded_opener`.
- A `URLError` raised inside `redirect_request` propagates out of `opener.open` into the tool's `except` -> error string; traced through `HTTPRedirectHandler.http_error_302`.
- Userinfo smuggling (`http://public@169.254.169.254/`) -> `urlparse().hostname` is the address -> refused. Decimal/short IPv4 forms (`2130706433`, `127.1`) fail `ip_address`, go to the resolver, and are refused either as loopback or as unresolvable - fail closed both ways.
- Not changed (adjacent, out of scope): `submit_finding_for_review`'s stale "Using default config (Anthropic)" comment (the bare default is Google - a Phase 3 provider-factory item), the 8000-byte cap on a non-UTF-8 page raising into the error string.

## Files
- `atlas/CommercialAgents/research_agent/tools.py` (imports + `_fetch_refusal` + `_GuardedRedirectHandler` + `_OPENER`; the tool body gains the refusal check and uses the opener), `tests/test_research_scrape_guard.py` (new), `docs/remediation_manifest.json` (+1 row, +1 source), `docs/deferred_manifest.json` (+1 row), this record + `_external_raw/atlas__CommercialAgents__research_agent__tools.py__fork-2026-09-10.md`.
