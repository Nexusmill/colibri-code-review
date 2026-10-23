# Colibri review — src/jcodemunch_mcp/agent_selector.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\agent_selector.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `7345dd40cfc9afae75f7d736eaa2288f0caa5ea22b7e2c8c0d075abe89c440cb` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `DEFAULT_PROVIDERS` 20-31 (google maps medium and high to the same string), `AgentSelectorConfig.from_config` 96-119 (`providers`/`thresholds`/`weights` taken from the raw block with no type check; `**raw.get("thresholds", {})` raises on a non-dict as surely as the providers subscript), `resolve_provider_models` 121-131, `_model_tier` 236-241 (first match), `route` 249-380 (manual mode: tier lookup at 304 before any equality check), `extract_signals_from_index` 426-435 (bare `startswith`); the config path: `config.py` `_PROJECT_CONFIGS` / the repo-committed `.jcodemunch.jsonc` feed `config_module.get("agent_selector", {})`, and server.py:6641 isinstance-checks only the OUTER block, wrapping the whole selector in `except Exception: logger.debug` - a raise inside is a silent, permanent feature outage; server.py builds `ComplexitySignals` directly from result-dict keys, so `extract_signals_from_index` has no live caller today (dormant); existing `tests/test_agent_selector.py` (39); all three RED probes re-run on these bytes (1/2, 1/1, 1/2 FAIL). No prior `.colibri_reviews` record.

## Verdict
Repo-controlled config could silently switch the feature off, the highest-weighted signal could be missed on a path prefix, and the shipped google defaults made the router ask you to switch to the model you were already on. All three confirmed and fixed; the first more broadly than reported.

## Bugs & vulnerabilities
**[MEDIUM] a non-dict `providers` (and `thresholds`, `weights`) block from repo config raised inside scoring and was swallowed into a silent outage — CONFIRMED (broader than reported) — FIXED** - `line 99-106, 127-128`
- What: `"providers": "anthropic-models-here"` passes `activeProvider in self.providers` (substring) and then `[...]` raises TypeError; a list raises the same way. The sub-agent reported `providers` only; `{**DEFAULT_THRESHOLDS, **raw.get("thresholds", {})}` and the `weights` merge raise on the same shapes one line lower - same class, same source. The server's `except Exception: logger.debug` turned every such raise into the selector silently doing nothing, per request, forever.
- Fix: `_dict_block()` returns `{}` with a `logger.warning` naming the offending key for any of the three blocks that is not an object (`None` is treated as absent); `resolve_provider_models` additionally warns and falls back to the defaults when the active provider's own entry is not a non-empty tier->model object. The feature degrades to its defaults, loudly.

**[MEDIUM] `extract_signals_from_index` decided cross-project by a bare string prefix — CONFIRMED — FIXED (dormant path)** - `line 426-435`
- What: `/repo/proj2/x.py` "starts with" `/repo/proj`, so a genuinely different project was scored as inside - `crossProjectReferences` is the single highest-weighted signal (25.0). Dormant today: server.py builds the signals itself and never calls this function (the sub-agent noted the same); fixed against the function's own contract and its tests.
- Fix: exact match or `root + "/"` after separator normalisation on both sides (a Windows root against a forward-slash path is inside, pinned).

**[LOW] `route` prompted a step-up to the model already running when two tiers share a model string — CONFIRMED — FIXED** - `line 304-308`
- What: `_model_tier` returns the FIRST tier whose model matches; `DEFAULT_PROVIDERS["google"]` maps medium and high to `gemini-2.5-pro`, so a caller on that model at tier high was read as medium and told to "switch" to the same string. The fix is provider-agnostic (an equality check on the recommended model before any tier arithmetic); it happens to be triggered by the google defaults, which the owner is retiring from his own fleet - that is why it stays LOW and why the defaults table itself is left alone here.

## Adversarial verification (Phase 3)
- The config tests parametrise all three blocks x string/list, assert the warning NAMES the block, then drive `resolve_provider_models` AND `score_complexity` through the degraded config (a fix that only guarded `providers` fails the thresholds/weights rows).
- Cross-project: three sibling-prefix rows (POSIX, a shorter root, Windows) must be cross-project; four inside rows (trailing slash, nested, backslashes, mixed separators) must not.
- Router: the google shared-string case must `proceed` with the current model; a real anthropic low->high step-up must still `prompt` and name the recommended model in the prompt text (the control - so the fix cannot be "never prompt").
- `tests/test_agent_selector.py` (39) unchanged: 52 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `ed1b3073bdfaa12e2d9f673634eb1d8254df71868ce268f6a718aab889c6cb83`. TDD: `tests/test_agent_selector_reaudit.py` (13 tests) - 9 RED on the old bytes (4 controls green throughout), GREEN after; all three probes ALL PASS.
