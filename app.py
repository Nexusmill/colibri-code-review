import os
import hashlib
import marshal
import streamlit as st
import pandas as pd
from analyzer import review_code, MODES, DEFAULTS, api_key, model_max_tokens, load_spec, _build_prompt, _PROMPTS
import json
import urllib.request
import scanner
import store
import ui

PINNED_MODELS = ["z-ai/glm-5.2", "moonshotai/kimi-k3"]   # pinned to the top of the dropdown


@st.cache_data(ttl=3600, show_spinner=False)
def openrouter_models():
    """Every model id from OpenRouter's public catalogue (no API key needed). Cached 1h;
    returns [] on any failure so the two pinned models + Custom still work offline."""
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/models",
                                     headers={"User-Agent": "colibri/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        return sorted(m["id"] for m in data.get("data", []) if m.get("id"))
    except Exception:
        return []

st.set_page_config(page_title="Colibri Code Review", page_icon="C", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject()

# ------------------------------------------------------------------ run config
# Every knob is live here. Nothing about a run is decided for the user.
with st.sidebar:
    st.markdown("### Model")
    _all_models = openrouter_models()
    _rest = [m for m in _all_models if m not in PINNED_MODELS]
    _opts = PINNED_MODELS + _rest + ["Custom (type an id)..."]
    _labels = {"z-ai/glm-5.2": "GLM-5.2  |  z-ai/glm-5.2",
               "moonshotai/kimi-k3": "Kimi K3  |  moonshotai/kimi-k3"}
    _pick = st.selectbox("Model", _opts, index=0, label_visibility="collapsed",
                         format_func=lambda m: _labels.get(m, m),
                         help="Any OpenRouter model. GLM-5.2 and Kimi K3 are pinned on top; the "
                              "rest of the live catalogue (%d models) follows." % len(_all_models))
    if _pick == "Custom (type an id)...":
        model = st.text_input("Custom model id", DEFAULTS["model"])
    else:
        model = _pick
    if not _all_models:
        st.caption("Live model list unavailable - pinned models + Custom still work.")

    st.markdown("### Reasoning")
    bounded = st.radio("Reasoning bound", ["Bounded", "Unbounded"], horizontal=True,
                       label_visibility="collapsed",
                       help="K3 thinks before it writes. Bounded caps the effort; "
                            "unbounded lets it think freely up to your output ceiling.")
    if bounded == "Bounded":
        reasoning = st.selectbox("Effort level", ["low", "medium", "high"], index=1,
                                 help="How hard the model thinks before writing. "
                                      "low = fast/cheap, high = deep/slower.")
    else:
        st.caption("Model reasons freely, capped only by Max output tokens.")
        reasoning = "off"

    st.markdown("### Endpoint & pricing")
    with st.expander("Advanced", expanded=False):
        api_base = st.text_input("Base URL", DEFAULTS["api_base"])
        price_in = st.number_input("Price in ($/1M)", value=3.0, step=0.5, min_value=0.0)
        price_out = st.number_input("Price out ($/1M)", value=15.0, step=0.5, min_value=0.0)

    st.markdown("### Limits")
    auto_out = st.toggle("Auto output ceiling (model max - never truncate)", value=True,
                         help="Reasoning models truncated by a low cap return finish=length with "
                              "ZERO findings. AUTO uses the model's own max_completion_tokens "
                              "(the ff626b1 fix, now reachable from the console).")
    if auto_out:
        _model_ceiling = model_max_tokens(model, api_base)
        st.caption("Output capped at the model's own ceiling: {:,} tokens.".format(_model_ceiling))
        max_tokens = None
        eff_max_out = _model_ceiling
    else:
        max_tokens = st.number_input("Max output tokens", min_value=256, max_value=64000,
                                     value=8000, step=256,
                                     help="Hard ceiling on output. Thinking + the written review "
                                          "share this budget. YOU set the cost ceiling here.")
        eff_max_out = int(max_tokens)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.15, 0.05)
    delta_rr = st.toggle("Delta re-review for changed files", value=True,
                         help="Stale files get their previous review injected so the model "
                              "reports only NEW/changed findings (cheaper convergence rounds).")

    st.markdown("### Static signals")
    st.caption("Deterministic tool output appended to the prompt so the model corroborates "
               "instead of guessing.")
    static_ast = st.checkbox("AST + pyflakes (scope leaks / dead code)", value=True,
                             help="Undefined names, unused imports/vars, mutable defaults, "
                                  "bare excepts, unreachable code.")
    static_mypy = st.checkbox("mypy type check", value=True,
                              help="Static type errors surfaced before runtime (bug/quality modes).")
    static_dis = st.checkbox("dis bytecode of hot loops", value=True,
                             help="Disassembly of loop-bearing functions so the model spots "
                                  "per-iteration overhead (bug/quality modes).")

    cfg = {"model": model, "api_base": api_base,
           "max_tokens": (int(max_tokens) if max_tokens else None),
           "temperature": float(temperature), "reasoning": reasoning,
           "price_in": float(price_in), "price_out": float(price_out),
           "static_ast": static_ast, "static_mypy": static_mypy, "static_dis": static_dis}
    st.session_state.cfg = cfg

ui.masthead(model)
if not api_key():
    st.error("No API key found. Set OPENROUTER_API_KEY (see INSTRUCTIONS.md), then restart the app.")

MODE_CHOICES = {"Bug Hunt": ["bug"], "Code Quality": ["quality"],
                "Feature Ideas": ["feature"], "Spec Conformance": ["spec"],
                "Remediation Plan": ["plan"],
                "All three": ["bug", "quality", "feature"]}


def per_file_ceiling(tokens_in, n_modes):
    return n_modes * (tokens_in * cfg["price_in"] / 1e6 + eff_max_out * cfg["price_out"] / 1e6)


def process(base, items):
    prog = st.progress(0.0, text="Starting...")
    spent = 0.0
    completed = 0
    for i, (rel, mode) in enumerate(items, 1):
        prog.progress((i - 1) / len(items), text=f"{MODES[mode]}: {rel}")
        path = os.path.abspath(os.path.join(base, rel))
        received = False
        try:
            code, sha = store.read_source(path)
            prior = None
            if delta_rr:
                mf = st.session_state.get("manifest") or {}
                if store.status(mf, os.path.abspath(path), sha, mode) == "stale":
                    md_e = (store.entry_for(mf, path).get("modes") or {}).get(mode) or {}
                    try:
                        if md_e.get("output"):
                            with open(store.output_path(base, md_e["output"]), encoding="utf-8", errors="replace") as _pf:
                                prior = _pf.read()
                    except OSError:
                        prior = None
            md, usage = review_code(code, rel, mode, cfg, prior_md=prior,
                                    spec_text=(st.session_state.get("spec_text")
                                               if mode == "spec" else None))
            received = True
            spent += usage.get("cost", 0) or 0
            out = store.save_review(base, path, rel, sha, mode, md, usage, cfg["model"])
            complete = usage.get("complete", usage.get("finish") == "stop") is True
            completed += int(complete)
            note = "" if complete else "  ·  incomplete; retry required"
            with st.expander(f"[{MODES[mode]}] {rel}   ${usage.get('cost', 0):.4f}{note}",
                             expanded=len(items) == 1):
                st.markdown(md)
                st.caption("saved -> " + out)
        except Exception as e:
            st.error(f"{rel} [{mode}]: {e}")
            if received:
                st.markdown(md)  # retain the paid response visibly if saving failed
                break
    prog.progress(1.0, text=f"Finished: {completed}/{len(items)} completed. Spent ${spent:.4f}")
    st.session_state.manifest = store.load_manifest(base)
    return spent


def queue_tokens(base, items):
    """Estimate every actual prompt, including system, spec, prior and static text."""
    tokens = 0
    builder_version = hashlib.sha256(marshal.dumps(_build_prompt.__code__)).hexdigest()
    cached = st.session_state.get("prompt_estimates", {})
    current = {}
    manifest = store.load_manifest(base)
    for rel, mode in items:
        path = os.path.abspath(os.path.join(base, rel))
        code, sha = store.read_source(path)
        prior = None
        if delta_rr and store.status(manifest, path, sha, mode) == "stale":
            record = store.entry_for(manifest, path).get("modes", {}).get(mode, {})
            if record.get("output"):
                try:
                    with open(store.output_path(base, record["output"]), encoding="utf-8", errors="replace") as stream:
                        prior = stream.read()
                except OSError:
                    pass
        spec = st.session_state.get("spec_text") if mode == "spec" else None
        key = (path, mode)
        signature = (sha, rel, tuple(sorted(cfg.items())), _PROMPTS[mode], builder_version,
                     hashlib.sha256((prior or "").encode("utf-8")).hexdigest(),
                     hashlib.sha256((spec or "").encode("utf-8")).hexdigest())
        previous = cached.get(key)
        if previous is not None and previous[0] == signature:
            estimate = previous[1]
        else:
            prompt = _build_prompt(code, rel, mode, cfg, prior_md=prior, spec_text=spec)
            estimate = max(1, int((len(prompt) + len(_PROMPTS[mode][0])) / 3.5) + 1)
        current[key] = (signature, estimate)
        tokens += estimate
    # Keep only the current queue: reruns reuse expensive enrichment without accumulating history.
    st.session_state.prompt_estimates = current
    return tokens


# ------------------------------------------------------------------ scan
c1, c2 = st.columns([5, 1])
with c1:
    dir_in = st.text_input("Project directory",
                           value=st.session_state.get("dir", os.environ.get("COLIBRI_DIR", os.getcwd())))
with c2:
    st.write("")
    st.write("")
    if st.button("Scan", use_container_width=True, type="secondary"):
        if not os.path.isdir(dir_in):
            st.error("Not a directory: " + dir_in)
        else:
            with st.spinner("Scanning + ranking core files..."):
                st.session_state.dir = dir_in
                st.session_state.scan = scanner.scan(dir_in)
                st.session_state.manifest = store.load_manifest(dir_in)
                st.session_state.pop("pending", None)

# ------------------------------------------------------------------ review surface
if st.session_state.get("scan"):
    base = st.session_state.dir
    manifest = st.session_state.get("manifest") or {}
    rows = st.session_state.scan

    mode_label = st.radio("Review type", list(MODE_CHOICES), horizontal=True)
    modes = MODE_CHOICES[mode_label]
    if "spec" in modes:
        st.info("Spec Conformance PREREQUISITE: the feature expectations - a spec-harness "
                "registry file (tests/harness/specs/<product>/<surface>.json) or any "
                "hand-written contract text.")
        sp1, sp2 = st.columns([3, 2])
        _spec_path = sp1.text_input("Expectations file", value=st.session_state.get("spec_path", ""))
        _spec_ids = sp2.text_input("Row ids (comma-separated, optional)",
                                   value=st.session_state.get("spec_ids", ""))
        st.session_state.spec_path = _spec_path
        st.session_state.spec_ids = _spec_ids
        st.session_state.spec_text = None
        if _spec_path.strip():
            try:
                st.session_state.spec_text = load_spec(_spec_path.strip(),
                                                       _spec_ids.strip() or None)
                st.caption(f"expectations loaded: {len(st.session_state.spec_text):,} chars")
            except Exception as e:
                st.error(f"expectations: {e}")
    is_all = len(modes) > 1

    f1, f2 = st.columns(2)
    hide = f1.checkbox("Hide vendored / low-signal", value=True)
    only_out = f2.checkbox("Only outstanding (new / changed)", value=False)

    def row_status(r):
        ap = os.path.abspath(r["path"])
        if is_all:
            n = store.modes_done(manifest, ap, r["sha"])
            return f"{n}/3", n < 3
        s = store.status(manifest, ap, r["sha"], modes[0])
        return {"new": "new", "reviewed": "done", "stale": "changed"}[s], s != "reviewed"

    disp = []
    for r in rows:
        label, outstanding = row_status(r)
        if only_out and not outstanding:
            continue
        if hide and r["score"] < 40:
            continue
        disp.append({"Select": False, "Status": label, "File": r["rel"],
                     "in tok": r["tokens"], "Source est $": round(per_file_ceiling(r["tokens"], len(modes)), 3),
                     "_out": outstanding, "_tok": r["tokens"]})

    st.write(f"**{len(disp)}** files shown · {len(rows)} scanned · core first · **{mode_label}**")
    edited = st.data_editor(
        pd.DataFrame([{k: v for k, v in d.items() if not k.startswith("_")} for d in disp]),
        hide_index=True, use_container_width=True, height=360, key="editor",
        column_config={"Select": st.column_config.CheckboxColumn(required=False),
                       "Source est $": st.column_config.NumberColumn(format="$%.3f")},
        disabled=["Status", "File", "in tok", "Source est $"],
    )
    recs = edited.to_dict("records")
    picked = [d["File"] for d, e in zip(disp, recs) if e["Select"]]
    sel_tok = sum(d["_tok"] for d, e in zip(disp, recs) if e["Select"])

    ui.meter(len(picked) * len(modes), sel_tok * len(modes), eff_max_out, cfg["price_in"], cfg["price_out"],
             unbounded=(reasoning == "off"), auto_out=auto_out)

    b1, b2, b3 = st.columns(3)
    if b1.button(f"Review selected ({len(picked)})", type="primary", disabled=not picked,
                 use_container_width=True):
        st.session_state.pending = {"items": [(rel, m) for rel in picked for m in modes],
                                    "why": f"{len(picked)} selected · {mode_label}"}
    if b2.button("Review all changed + new", use_container_width=True):
        outs = [d["File"] for d in disp if d["_out"]]
        if outs:
            st.session_state.pending = {"items": [(rel, m) for rel in outs for m in modes],
                                        "why": f"all {len(outs)} outstanding · {mode_label}"}
        else:
            st.session_state.pop("pending", None)
            st.info("Nothing outstanding — every shown file is already reviewed at its current sha.")
    if b3.button("Export all reviews", use_container_width=True):
        path, text = store.export_all(base)
        st.session_state.export = (path, text)

    pend = st.session_state.get("pending")
    if pend and pend["items"]:
        try:
            tok = queue_tokens(base, pend["items"])
        except Exception as error:
            tok = None
            st.error(f"Cannot estimate this queue: {error}")
        estimate = ((tok or 0) * cfg["price_in"] / 1e6
                    + len(pend["items"]) * eff_max_out * cfg["price_out"] / 1e6)
        st.warning(f"Queued: **{len(pend['items'])}** review call(s) — {pend['why']}. "
                   f"Estimated spend at the output ceiling: **${estimate:.2f}**. "
                   "Includes prompt overhead; token counts and prices are estimates, not a spending cap.")
        cc1, cc2, _ = st.columns([2, 1, 3])
        if cc1.button(f"Confirm & run  (est. ${estimate:.2f})", type="primary",
                      disabled=tok is None, use_container_width=True):
            st.session_state.pop("pending", None)
            spent = process(base, pend["items"])
            st.info(f"Run finished; spent ${spent:.4f}. Completion counts and errors are shown above.")
        if cc2.button("Cancel", use_container_width=True):
            st.session_state.pop("pending", None)

    exp = st.session_state.get("export")
    if exp:
        path, text = exp
        st.download_button("Download all_reviews.md", data=text,
                           file_name="all_reviews.md", mime="text/markdown")
        st.caption("also saved -> " + path)

    with st.expander("Previously reviewed in this project"):
        m = store.load_manifest(base)
        if m:
            st.write(f"{len(m)} file(s) · ${store.total_cost(m):.4f} total")
            for _, e in sorted(m.items(), key=lambda kv: kv[1].get("rel", "")):
                records = e.get("modes") or {}
                done = ", ".join(sorted(mode for mode, md in records.items()
                                       if md.get("complete") is not False)) or "none"
                incomplete = sum(md.get("complete") is False for md in
                                 list(records.values()) + e.get("attempts", []))
                st.write(f"- **{e.get('rel')}** · completed: {done} · incomplete attempts: {incomplete}")
        else:
            st.write("Nothing reviewed yet.")
else:
    st.caption("Point at a directory and Scan. Core files rank first; vendored code is hidden.")
