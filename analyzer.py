import os
from openai import OpenAI

try:
    from static_context import build_static_context
except Exception:                                      # never let a static-pass import break reviews
    def build_static_context(code, rel, mode="bug", cfg=None):
        return ""

# ---------------------------------------------------------------------------
# Kimi K3 (or any OpenRouter model) - fully config-driven. Nothing about a run
# is hardcoded here: the UI passes every knob per call, so they are live.
# The API key still comes only from the environment, never a file.
# ---------------------------------------------------------------------------

def api_key():
    return os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")


# A run config the UI builds and hands to review_code(). These are only the
# starting values shown in the controls; the user changes them live.
DEFAULTS = {
    "api_base": os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1"),
    "model": os.getenv("MODEL_ID", "moonshotai/kimi-k3"),
    "max_tokens": None,        # None = AUTO: use the model's own max_completion_tokens (never cap
                               # below what the model needs - a low cap truncates the review to nothing)
    "temperature": 0.15,
    "reasoning": "medium",     # "off" = unbounded (no effort hint) | "low"|"medium"|"high"|"xhigh"
    "price_in": 3.0,           # $/1M input tokens (for the cost meter)
    "price_out": 15.0,         # $/1M output tokens
    # Static-analysis enrichers: deterministic tool output appended to the prompt so the model
    # corroborates instead of guessing. All default on; mypy+dis only run for bug/quality modes.
    "static_ast": True,        # ast smells + pyflakes (scope leaks / dead code)
    "static_mypy": True,       # mypy type errors
    "static_dis": True,        # dis bytecode for hot loop-bearing functions
    "static_max_chars": 8000,  # overall cap on the appended static-signals block
}

MODES = {"bug": "Bug Hunt", "quality": "Code Quality", "feature": "Feature Ideas",
         "spec": "Spec Conformance", "plan": "Remediation Plan"}


def load_spec(source, ids=None):
    """Load the feature expectations for spec mode. A path to the Nexusmill spec-harness
    registry (`controls` rows) or a features registry (`features` rows) renders to readable
    per-control contract text, optionally filtered by comma-separated row ids; a path to any
    other file (or raw text) passes through as-is."""
    import json as _json
    raw = source
    if os.path.isfile(source):
        raw = open(source, encoding="utf-8-sig", errors="ignore").read()
    try:
        d = _json.loads(raw)
    except ValueError:
        return raw.strip()
    rows = (d.get("controls") or d.get("features") or []) if isinstance(d, dict) else []
    if not rows:
        return raw.strip()
    want = {s.strip() for s in ids.split(",") if s.strip()} if ids else None
    out = []
    for r in rows:
        rid = r.get("id", "?")
        if want and rid not in want:
            continue
        out.append("### %s - %s" % (rid, r.get("label") or r.get("feature", "")))
        c = r.get("contract")
        if isinstance(c, dict):
            for k, v in c.items():
                if v:
                    out.append("  %s: %s" % (k.upper(), v))
        elif r.get("expected"):
            out.append("  EXPECTED: %s" % r["expected"])
        if r.get("status"):
            out.append("  STATUS: %s" % r["status"])
    if not out:
        raise ValueError("no matching spec rows (ids=%s)" % ids)
    return "\n".join(out)

_MODEL_MAX_CACHE = {}


def model_max_tokens(model, base_url="https://openrouter.ai/api/v1", fallback=131072):
    """The model's own output ceiling (top_provider.max_completion_tokens), cached. Used when
    max_tokens is left on AUTO so no review is ever truncated below what the model needs -
    e.g. GLM-5.2 reasons past 20k tokens at low effort and returns finish=length with 0 findings
    under a small cap; its real ceiling is 131072. Falls back high if the lookup fails."""
    if model in _MODEL_MAX_CACHE:
        return _MODEL_MAX_CACHE[model]
    val = fallback
    try:
        import json as _json, urllib.request as _u
        req = _u.Request(base_url.rstrip("/") + "/models", headers={"User-Agent": "colibri"})
        for m in _json.load(_u.urlopen(req, timeout=20))["data"]:
            if m.get("id") == model:
                val = int((m.get("top_provider") or {}).get("max_completion_tokens") or fallback)
                break
    except Exception:
        pass
    _MODEL_MAX_CACHE[model] = val
    return val

_SYS = {
    "bug": ("You are a rigorous senior staff engineer and application-security reviewer. "
            "You hunt for REAL defects and vulnerabilities, cite exact line numbers, and never "
            "pad the report with style opinions or trivia."),
    "quality": ("You are a principal engineer who cares about long-term code health: readability, "
                "structure, and maintainability. You give concrete, actionable refactors and never "
                "invent bugs that aren't there."),
    "feature": ("You are a pragmatic, product-minded staff engineer. You propose high-value feature "
                "add-ons grounded in what the code actually does, with a realistic sense of effort."),
    "spec": ("You are a rigorous senior staff engineer doing a CONFORMANCE review against the "
             "maintainer's authoritative feature expectations. You report ONLY divergences between "
             "the code and the stated expectations, quote the violated clause for every finding, "
             "and never critique the expectations themselves or report unrelated bugs."),
    "plan": ("You are a senior staff engineer writing a REMEDIATION PLAN. You plan only and never "
             "claim to execute, apply, or verify a change - the plan is executed later by someone "
             "else under strict TDD. Concrete symbols, failing-test-first, smallest viable fixes."),
}

_TEMPLATES = {
    "bug": """Hunt for BUGS and vulnerabilities in `{rel}`.

Look hard for: logic/correctness errors, off-by-one, null/None/undefined, unhandled
exceptions and error paths, edge/boundary cases, race conditions and concurrency,
resource leaks (files, handles, locks), missing input validation, injection /
deserialization / path traversal / SSRF, auth and secret handling, integer/overflow,
incorrect API or library usage, and silent failures.

Return Markdown (omit any severity with no findings):

## Verdict
1-2 sentences: is this safe to ship, and what is the single biggest risk?

## Bugs & vulnerabilities
Worst first:
**[CRITICAL|HIGH|MEDIUM|LOW] title** - `line N`
- What: the exact defect
- Trigger: the input or condition that hits it
- Impact: what breaks
- Fix: the concrete change

## Missing safeguards
Bullets: validation, error handling, or tests that should exist but don't.""",

    "quality": """Review `{rel}` for CODE QUALITY and maintainability (not bugs).

Assess: naming, readability, function length and complexity, duplication (DRY),
cohesion and coupling, abstractions, SOLID, error-handling style, comments and
docstrings, dead code, consistency, idiomatic use of the language, and testability.

Return Markdown:

## Health score
X/10 with a one-line justification.

## Improvements
Highest-impact first:
**[HIGH|MEDIUM|LOW] title** - `line N` (or symbol)
- Issue: what hurts maintainability
- Better: the concrete refactor (show a short before/after when it clarifies)

## Quick wins
A checklist of small, safe cleanups.

## What's done well
1-3 bullets.""",

    "feature": """Propose high-value FEATURE ADD-ONS and enhancements for `{rel}`.

Think about: capabilities a user would expect but are missing, robustness and
observability (logging, metrics, retries), configurability, extensibility / plugin
points, API or UX ergonomics, performance options, and integration opportunities.
Ground every idea in what the code actually does.

Return Markdown:

## What this module does
1-2 sentences.

## Suggested add-ons
Ranked by value:
**title**  -  Value: High/Med/Low  ·  Effort: S/M/L
- What: the feature
- Why: the user benefit
- How: where it hooks in (files/functions) and a sketch of the approach

## Nice-to-haves
Short bullets of smaller ideas.""",

    "spec": """Check `{rel}` for CONFORMANCE against the maintainer's feature expectations below.

FEATURE EXPECTATIONS (authoritative - the contract this code must satisfy):

{expectations}

Your ONLY job: find places where this code can produce a result NOT in line with those
expectations. Check the quiet clauses hardest: disabled/greyed states, error paths,
sentinels, cost disclosure, side effects, wrap/boundary behavior. Do NOT report generic
bugs unrelated to the expectations (Bug Hunt owns those), do NOT critique the
expectations, and a clause the code satisfies gets silence.

Return Markdown:

## Verdict
1-2 sentences: does this file conform to the judgable clauses?

## Divergences
Worst first:
**[CRITICAL|HIGH|MEDIUM|LOW] title** - `line N`
- Expectation: the violated clause, quoted
- Trigger: the input or condition that hits the divergence
- Behavior: what the code actually does vs what the contract expects
- Fix: the concrete change

## UNJUDGEABLE HERE
One line per clause whose behavior lives outside this file (name where it likely lives).""",

    "plan": """Write a REMEDIATION PLAN for `{rel}` - PLAN ONLY, never execute.

First identify the few most load-bearing REAL defects in this file (or, if a PREVIOUS
review is supplied below, plan for exactly its still-open findings - do not re-litigate,
expand, or drop them). Then, for each item:

### <id/title>
- Objective: the defect in one line
- Root cause: exact line/symbol
- Fix design: the smallest change that works (sketch the exact edit)
- Test first: the FAILING test to write BEFORE the fix - test file + concrete asserts
- Steps: ordered, bite-sized
- Verification: commands to run and their expected outcomes
- Risk & rollback: call sites affected, what could break, how to revert

Order items worst-first. End with:

## Execution order & batching
Commit-sized tranches, dependencies noted.""",
}


def _numbered(code):
    return "\n".join(f"{i+1:>5}| {ln}" for i, ln in enumerate(code.splitlines()))


def _merge(cfg):
    c = dict(DEFAULTS)
    if cfg:
        c.update({k: v for k, v in cfg.items() if v is not None})
    return c


_JSON_INSTR = """
Return ONLY a JSON object (no prose, no code fences) with this shape:
{"verdict": "<1-2 sentences>",
 "findings": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW", "line": <int or null>,
               "title": "...", "detail": "...", "fix": "..."}],
 "notes": ["<missing safeguards / quick wins / nice-to-haves as strings>"]}
Findings worst-first. Use the same rigor as the Markdown contract."""


def _parse_json_review(text):
    """Tolerant parse: strip code fences / leading prose, take the outermost object."""
    import json as _json
    t = (text or "").strip()
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b <= a:
        raise ValueError("no JSON object in response")
    d = _json.loads(t[a:b + 1])
    if not isinstance(d, dict) or "findings" not in d:
        raise ValueError("missing 'findings'")
    return d
def review_code(code, rel_path, mode="bug", cfg=None, prior_md=None, fmt="md", spec_text=None):
    """Returns (markdown_review, usage). Config-driven: model, max_tokens, temperature,
    reasoning effort (or 'off' for unbounded), base URL and prices all come from cfg.
    Always returns a string review and a usage dict with the real billed cost."""
    c = _merge(cfg)
    if mode not in MODES:
        mode = "bug"
    key = api_key()
    if not key:
        return "**No API key.** Set `OPENROUTER_API_KEY` and restart the app.", {"cost": 0}

    if mode == "spec":
        if not spec_text:
            return ("**Spec Conformance requires the feature expectations.** Load them first "
                    "(spec-harness registry JSON or hand-written contracts) - no API call was "
                    "made."), {"cost": 0}
        body = _TEMPLATES["spec"].format(rel=rel_path, expectations=spec_text)
    else:
        body = _TEMPLATES[mode].format(rel=rel_path)
    prompt = f"{body}\n\nSource (shown as `N| code`):\n\n```\n{_numbered(code)}\n```\n"
    try:
        static = build_static_context(code, rel_path, mode, c)
    except Exception:
        static = ""                                    # a broken enricher must never block a review
    if static:
        prompt += "\n" + static + "\n"
    if prior_md:
        # DELTA mode: the iterate-until-clean loop stops re-paying to re-hear known findings.
        prompt += ("\n---\nA PREVIOUS review of an EARLIER version of this file is below. "
                   "Report ONLY findings that are NEW or CHANGED since that review. Add a "
                   "'## Fixed since last review' section confirming previously-reported findings "
                   "that no longer apply. Do not restate unchanged findings.\n\n"
                   + prior_md[:20000] + "\n---\n")
    if fmt == "json":
        prompt += "\n" + _JSON_INSTR + "\n"

    client = OpenAI(
        api_key=key, base_url=c["api_base"],
        default_headers={"HTTP-Referer": "http://localhost", "X-Title": "Colibri Code Review"},
    )
    # bounded reasoning -> effort hint; unbounded ('off') -> omit so the model reasons freely
    extra = {}
    eff = str(c.get("reasoning", "off")).lower()
    if eff in ("low", "medium", "high", "xhigh"):
        extra = {"reasoning": {"effort": eff}}

    _mt = c.get("max_tokens")                          # AUTO (None/<=0) -> the model's own ceiling
    max_tokens = int(_mt) if _mt else model_max_tokens(c["model"], c["api_base"])
    messages = [{"role": "system", "content": _SYS[mode]},
                {"role": "user", "content": prompt}]

    def _call(msgs):
        return client.chat.completions.create(
            model=c["model"], messages=msgs, temperature=float(c["temperature"]),
            max_tokens=max_tokens, extra_body=extra)

    resp = _call(messages)
    ch = resp.choices[0]
    fin = ch.finish_reason
    content = ch.message.content

    if not content:
        reasoning = getattr(ch.message, "reasoning", None)
        if fin == "length":
            content = ("_The model hit the output token limit before finishing. Raise **Max output "
                       "tokens** in Run Config (or split the file), then retry._")
        elif reasoning:
            content = "_(Model returned only reasoning, no final answer. Raw reasoning below.)_\n\n" + reasoning
        else:
            content = f"_Model returned no content (finish_reason={fin}). Try again._"
    elif fin == "length":
        content += "\n\n_[Note: output hit the token limit and may be truncated. Raise Max output tokens.]_"

    def _usage_of(r):
        u = getattr(r, "usage", None)
        pin = getattr(u, "prompt_tokens", 0) or 0
        pout = getattr(u, "completion_tokens", 0) or 0
        cost = getattr(u, "cost", None)
        if cost is None:
            cost = pin * c["price_in"] / 1_000_000 + pout * c["price_out"] / 1_000_000
        return pin, pout, (cost or 0.0)

    pin, pout, cost = _usage_of(resp)
    usage = {"prompt_tokens": pin, "completion_tokens": pout, "cost": cost,
             "finish": fin, "model": c["model"]}

    if fmt == "json" and content:
        import json as _json
        try:
            usage["parsed"] = _parse_json_review(content)
            content = _json.dumps(usage["parsed"], indent=1)
        except Exception:
            try:                                  # ONE corrective retry (the 10/194 parse-error class)
                r2 = _call(messages + [{"role": "assistant", "content": content[:8000]},
                                       {"role": "user", "content":
                                        "That was not valid JSON. Reply again with ONLY the JSON "
                                        "object, exactly the shape specified."}])
                c2 = r2.choices[0].message.content or ""
                p2, o2, cost2 = _usage_of(r2)
                usage["prompt_tokens"] += p2
                usage["completion_tokens"] += o2
                usage["cost"] += cost2
                usage["parsed"] = _parse_json_review(c2)
                content = _json.dumps(usage["parsed"], indent=1)
            except Exception:
                usage["json_error"] = True        # keep the raw text - never lose a paid review
    return content, usage
