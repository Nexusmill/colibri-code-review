#!/usr/bin/env python3
"""Offline regression net for analyzer.py - the engine all six importers depend on.

Pins the money-relevant and offline-testable behaviors of the review engine at
sha 8afa3ca9 (perfection wave 1 / tranche 1, 2026-09-26): config merge semantics,
key/spec refusals before any spend, the mode vocabulary, tolerant JSON parsing,
spec registry rendering, usage/cost math incl. the corrective-retry accumulation
precedent, content normalization, reasoning-effort and max-tokens AUTO mapping,
delta-prompt embedding, and fail-soft static enrichment.

Standalone script (repo convention); run with `python tests/test_analyzer.py`.
No network, no real key: the OpenAI client is faked, API keys are runtime-built
dummies; AUTO cases prime the model-ceiling cache per call and every other case passes
explicit max_tokens, so no lookup is attempted.
"""
import importlib.util, inspect, json, os, shutil, sys, tempfile, types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
_results = {}


def check(name, ok):
    _results[name] = bool(ok)
    print(("PASS " if ok else "FAIL ") + name)


def _load(mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(ROOT, mod + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


an = _load("analyzer")
_DUMMY = "k" + "ey-" + "1" * 20          # runtime-built, obviously fake (never a real secret)
_ORIG_OPENAI = an.OpenAI
_ORIG_STATIC = an.build_static_context
_ORIG_CACHE = dict(an._MODEL_MAX_CACHE)
_J = json.dumps
_OBJ = {"verdict": "fine", "findings": [{"severity": "LOW", "line": 1, "title": "t",
                                         "detail": "d", "fix": "f"}], "notes": []}


class _Resp:
    def __init__(self, content, fin="stop", reasoning=None, usage=None):
        msg = types.SimpleNamespace(content=content, reasoning=reasoning)
        self.choices = [types.SimpleNamespace(message=msg, finish_reason=fin)]
        self.usage = usage


def _usage(pin, pout, cost=None):
    return types.SimpleNamespace(prompt_tokens=pin, completion_tokens=pout, cost=cost)


class _FakeClient:
    def __init__(self, script):
        self.calls, self._script = [], list(script)
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls.append(kw)
        if not self._script:
            raise AssertionError("unexpected API call (script exhausted)")
        nxt = self._script.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


class _KeyEnv:
    """Dummy OPENROUTER key in; previous env restored on exit."""
    def __enter__(self):
        self._saved = {k: os.environ.pop(k, None) for k in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
        os.environ["OPENROUTER_API_KEY"] = _DUMMY

    def __exit__(self, *exc):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class _NoKeyEnv(_KeyEnv):
    def __enter__(self):
        out = super().__enter__()
        os.environ.pop("OPENROUTER_API_KEY", None)
        return out


def _restore_module():
    an.OpenAI = _ORIG_OPENAI
    an.build_static_context = _ORIG_STATIC
    an._MODEL_MAX_CACHE.clear(); an._MODEL_MAX_CACHE.update(_ORIG_CACHE)


def _run(script, cfg=None, static="", **kw):
    """review_code under the fake seam: dummy key, deterministic (empty) enrichment,
    ctor-recording client factory. Returns (content, usage, fake, ctor_calls)."""
    cfg = dict({"model": "fake/auto-model", "max_tokens": 5000}, **(cfg or {}))
    fake = _FakeClient(script)
    ctor = []

    def _ctor(**ck):
        ctor.append(ck)
        return fake

    an.OpenAI = _ctor
    an.build_static_context = (lambda *a, **k: static) if isinstance(static, str) else static
    code = kw.pop("code", "x = 1\n")
    rel = kw.pop("rel", "pkg/mod.py")
    try:
        with _KeyEnv():
            content, usage = an.review_code(code, rel, cfg=cfg, **kw)
        return content, usage, fake, ctor
    finally:
        _restore_module()


def test_merge():
    c = an._merge({"model": None, "temperature": 0})
    check("merge_none_filtered", c["model"] == an.DEFAULTS["model"])
    check("merge_zero_kept", c["temperature"] == 0)
    check("merge_none_cfg_is_defaults", an._merge(None)["price_in"] == an.DEFAULTS["price_in"])
    c2 = an._merge({})
    c2["model"] = "MUTATED-MODEL"
    check("merge_copy_isolated", an.DEFAULTS["model"] != "MUTATED-MODEL")


def test_api_key():
    saved = {k: os.environ.get(k) for k in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
    try:
        os.environ.pop("OPENROUTER_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
        check("apikey_empty_when_unset", an.api_key() == "")
        os.environ["OPENAI_API_KEY"] = "sk-" + "alt"
        check("apikey_openai_fallback", an.api_key() == "sk-" + "alt")
        os.environ["OPENROUTER_API_KEY"] = "sk-" + "main"
        check("apikey_openrouter_wins", an.api_key() == "sk-" + "main")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_refusals():
    def _boom(**ck):
        raise AssertionError("client constructed on a refusal path")
    an.OpenAI = _boom
    try:
        with _NoKeyEnv():
            content, usage = an.review_code("x = 1\n", "pkg/mod.py")
        check("nokey_message", content.startswith("**No API key.**"))
        check("nokey_zero_cost", usage == {"cost": 0})
        with _KeyEnv():
            content, usage = an.review_code("x = 1\n", "pkg/mod.py", mode="spec", spec_text=None)
        check("spec_refusal_text", "Spec Conformance requires" in content)
        check("spec_refusal_zero_cost", usage == {"cost": 0})
        check("spec_refusal_no_spend_call", "no API call was" in content)
    finally:
        _restore_module()


def test_parse_json():
    ok = '{"verdict": "v", "findings": [], "notes": []}'
    check("pj_happy", an._parse_json_review(ok)["verdict"] == "v")
    check("pj_fenced", an._parse_json_review("```json\n" + ok + "\n```")["findings"] == [])
    check("pj_prose_wrapped", an._parse_json_review("Here:\n" + ok + "\nDone")["notes"] == [])
    for name, bad in (("pj_missing_findings", '{"verdict": "v"}'),
                      ("pj_no_object", "no braces at all"),
                      ("pj_empty", "")):
        try:
            an._parse_json_review(bad)
            check(name, False)
        except ValueError:
            check(name, True)


_REG = {"controls": [
    {"id": "c1", "label": "L1", "contract": {"expected": "does X", "error": ""}, "status": "draft"},
    {"id": "c2", "label": "L2", "expected": "does Y"}]}
_FEAT = {"features": [{"id": "f1", "feature": "F1", "expected": "e"}]}


def test_load_spec():
    out = an.load_spec(_J(_REG))
    check("spec_render_controls", "### c1 - L1" in out and "### c2 - L2" in out)
    check("spec_contract_upper", "EXPECTED: does X" in out)
    check("spec_empty_contract_value_skipped", "ERROR:" not in out)
    check("spec_status", "STATUS: draft" in out)
    check("spec_expected_fallback", "EXPECTED: does Y" in out)
    filt = an.load_spec(_J(_REG), ids="c2")
    check("spec_ids_filter", "### c2" in filt and "### c1" not in filt)
    try:
        an.load_spec(_J(_REG), ids="zzz")
        check("spec_nomatch_raises", False)
    except ValueError:
        check("spec_nomatch_raises", True)
    check("spec_features_variant", "### f1 - F1" in an.load_spec(_J(_FEAT)))
    check("spec_nonjson_passthrough", an.load_spec("  plain text  ") == "plain text")
    check("spec_no_rows_passthrough", an.load_spec('{"a": 1}') == '{"a": 1}')
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "reg.json")
        with open(p, "w", encoding="utf-8-sig") as f:
            f.write(_J(_REG))
        check("spec_file_load_bom", "### c1 - L1" in an.load_spec(p))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_review_gates_and_prompt():
    content, usage, fake, ctor = _run([_Resp("ok")], mode="quaity")
    check("mode_coercion_pins_bug", fake.calls[0]["messages"][0]["content"] == an._SYS["bug"])
    msgs = fake.calls[0]["messages"]
    check("prompt_roles", len(msgs) == 2 and msgs[0]["role"] == "system" and msgs[1]["role"] == "user")
    check("prompt_renders_rel", "pkg/mod.py" in msgs[1]["content"])
    check("prompt_numbered_gutter", "    1| x = 1" in msgs[1]["content"])
    check("guard_model_kwarg", fake.calls[0]["model"] == "fake/auto-model")
    check("guard_temperature_float", fake.calls[0]["temperature"] == 0.15)
    check("guard_max_tokens_kwarg", fake.calls[0]["max_tokens"] == 5000)
    check("client_ctor_recorded", len(ctor) == 1)


def test_reasoning_and_auto():
    _, _, fake, _ = _run([_Resp("ok")], cfg={"reasoning": "high"})
    check("effort_high_mapped", fake.calls[0]["extra_body"] == {"reasoning": {"effort": "high"}})
    _, _, fake, _ = _run([_Resp("ok")], cfg={"reasoning": "off"})
    check("effort_off_empty", fake.calls[0]["extra_body"] == {})

    def _prime():
        an._MODEL_MAX_CACHE["fake/auto-model"] = 4321
    try:
        _prime()
        _, _, fake, _ = _run([_Resp("ok")], cfg={"max_tokens": None})
        check("auto_none_uses_ceiling", fake.calls[0]["max_tokens"] == 4321)
        _prime()                                    # _run's teardown clears the cache - re-prime per call
        _, _, fake, _ = _run([_Resp("ok")], cfg={"max_tokens": 0})
        check("auto_zero_uses_ceiling", fake.calls[0]["max_tokens"] == 4321)
        _prime()
        _, _, fake, _ = _run([_Resp("ok")], cfg={"max_tokens": 5000})
        check("explicit_tokens_win", fake.calls[0]["max_tokens"] == 5000)
    finally:
        _restore_module()


def test_usage_math():
    c, u, fake, _ = _run([_Resp("hello", usage=_usage(100, 10, None))])
    check("usage_fallback_math", abs(u["cost"] - (100 * 3.0 / 1e6 + 10 * 15.0 / 1e6)) < 1e-12)
    check("usage_tokens_recorded", u["prompt_tokens"] == 100 and u["completion_tokens"] == 10)
    check("usage_finish_model", u["finish"] == "stop" and u["model"] == "fake/auto-model")
    c, u, _, _ = _run([_Resp("hello", usage=_usage(1, 2, 0.5))])
    check("usage_cost_verbatim", u["cost"] == 0.5)
    c, u, _, _ = _run([_Resp("hello")])            # usage=None -> zero-fill guard
    check("usage_missing_zero", u["cost"] == 0 and u["prompt_tokens"] == 0)


def test_json_fmt():
    c, u, fake, _ = _run([_Resp(_J(_OBJ))], fmt="json")
    check("json_parsed", u["parsed"] == _OBJ)
    check("json_redumped", c == json.dumps(_OBJ, indent=1))

    # corrective retry: invalid then valid - usage ACCUMULATES across attempts (the :369-374 precedent)
    c, u, fake, _ = _run([_Resp("not json at all", usage=_usage(100, 10, None)),
                          _Resp(_J(_OBJ), usage=_usage(50, 5, 0.25))], fmt="json")
    check("retry_attempted_once", len(fake.calls) == 2)
    check("retry_tokens_accumulated", u["prompt_tokens"] == 150 and u["completion_tokens"] == 15)
    check("retry_cost_accumulated", abs(u["cost"] - (100 * 3.0 / 1e6 + 10 * 15.0 / 1e6 + 0.25)) < 1e-12)
    check("retry_parsed", u["parsed"] == _OBJ)
    check("retry_corrective_user_msg", "not valid JSON" in fake.calls[1]["messages"][-1]["content"])

    # both invalid - the paid review is never lost
    raw = "definitely { not json"
    c, u, fake, _ = _run([_Resp(raw), _Resp("still { nope")], fmt="json")
    check("json_error_flag", u.get("json_error") is True)
    check("json_error_keeps_raw_content", c == raw)


def test_content_normalization():
    c, _, _, _ = _run([_Resp(None, fin="length")])
    check("empty_length_hint", "output token limit" in c and "Max output tokens" in c)
    c, _, _, _ = _run([_Resp(None, fin="stop", reasoning="chain-of-thought")])
    check("reasoning_only_echoed", c.startswith("_(Model returned only reasoning") and "chain-of-thought" in c)
    c, _, _, _ = _run([_Resp(None, fin="stop")])
    check("no_content_soft_msg", "finish_reason=stop" in c)
    c, _, _, _ = _run([_Resp("answer", fin="length")])
    check("truncation_note_appended", c.startswith("answer") and c.endswith("Raise Max output tokens.]_"))


def test_prior_and_static():
    prior = "SENTINEL-PRIOR-" + "z" * 40
    _, _, fake, _ = _run([_Resp("ok")], prior_md=prior)
    user = fake.calls[0]["messages"][1]["content"]
    check("prior_embedded", "SENTINEL-PRIOR-" in user and "PREVIOUS review" in user)
    _, _, fake, _ = _run([_Resp("ok")], prior_md="A" * 25000)
    user = fake.calls[0]["messages"][1]["content"]
    check("prior_truncated_20000", "A" * 20000 in user and "A" * 20001 not in user)

    def _enrich(code, rel, mode, cfg):
        return "STATIC-X-BLOCK"
    c, _, fake, _ = _run([_Resp("ok")], static=_enrich)
    check("static_block_in_prompt", "STATIC-X-BLOCK" in fake.calls[0]["messages"][1]["content"])

    def _raise(*a, **k):
        raise RuntimeError("enricher boom")
    c, _, fake, _ = _run([_Resp("ok")], static=_raise)
    check("static_failure_failsoft", c == "ok")


class _CloseProbe:
    """Context-manager proxy standing in for open()/urlopen() results; records closing."""

    def __init__(self, payload=None, fail_read=False):
        self.closed = False
        self._payload, self._fail = payload, fail_read

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False                                # never swallow

    def read(self):
        if self._fail:
            raise RuntimeError("read blew up")
        return self._payload

    def close(self):
        self.closed = True


def test_handle_teardown():
    import builtins, urllib.error, urllib.request
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "reg.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write(_J(_REG))
        probe = _CloseProbe(payload=_J(_REG))
        orig_open = builtins.open
        builtins.open = lambda *a, **k: probe
        try:
            out = an.load_spec(p)
        finally:
            builtins.open = orig_open
        check("loadspec_handle_closed", probe.closed is True)
        check("loadspec_content_intact", "### c1 - L1" in out)

        probe = _CloseProbe(payload=_J(_REG), fail_read=True)
        builtins.open = lambda *a, **k: probe
        try:
            try:
                an.load_spec(p)
                propagated = False
            except RuntimeError:
                propagated = True
        finally:
            builtins.open = orig_open
        check("loadspec_readfail_propagates", propagated is True)
        check("loadspec_readfail_still_closes", probe.closed is True)

        models = _J({"data": [{"id": "fake/ceiling-model",
                               "top_provider": {"max_completion_tokens": 7777}}]})
        probe = _CloseProbe(payload=models.encode("utf-8"))
        orig_urlopen = urllib.request.urlopen
        urllib.request.urlopen = lambda *a, **k: probe
        try:
            val = an.model_max_tokens("fake/ceiling-model")
        finally:
            urllib.request.urlopen = orig_urlopen
        check("mmt_value_parsed", val == 7777)
        check("mmt_response_closed", probe.closed is True)

        def _down(*a, **k):
            raise urllib.error.URLError("down")
        urllib.request.urlopen = _down
        try:
            an._MODEL_MAX_CACHE.pop("fake/ceiling-model", None)
            check("mmt_fetchfail_fallback", an.model_max_tokens("fake/ceiling-model") == 131072)
        finally:
            urllib.request.urlopen = orig_urlopen
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_auto_negative():
    an._MODEL_MAX_CACHE["fake/auto-model"] = 4321    # _run's teardown clears it after the call
    try:
        _, _, fake, _ = _run([_Resp("ok")], cfg={"max_tokens": -5})
        check("auto_negative_uses_ceiling", fake.calls[0]["max_tokens"] == 4321)
    finally:
        _restore_module()


def test_single_json_import():
    src = inspect.getsource(an)
    check("no_local_json_imports", "import json as _json" not in src)
    check("no_json_alias_left", "_json." not in src)   # _parse_json_review contains _json legitimately


def main():
    for t in (test_merge, test_api_key, test_refusals, test_parse_json, test_load_spec,
              test_review_gates_and_prompt, test_reasoning_and_auto, test_usage_math,
              test_json_fmt, test_content_normalization, test_prior_and_static,
              test_handle_teardown, test_auto_negative, test_single_json_import):
        try:
            t()
        except Exception as exc:                     # a crashing test must not kill the run
            _results["EXCEPTION:" + t.__name__] = False
            print("FAIL EXCEPTION:%s: %r" % (t.__name__, exc))
        finally:
            _restore_module()
    bad = [k for k, v in _results.items() if not v]
    print("\n%d/%d PASS" % (len(_results) - len(bad), len(_results)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
