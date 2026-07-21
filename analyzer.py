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
    "max_tokens": 8000,        # hard ceiling on output (reasoning + review share it)
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

MODES = {"bug": "Bug Hunt", "quality": "Code Quality", "feature": "Feature Ideas"}

_SYS = {
    "bug": ("You are a rigorous senior staff engineer and application-security reviewer. "
            "You hunt for REAL defects and vulnerabilities, cite exact line numbers, and never "
            "pad the report with style opinions or trivia."),
    "quality": ("You are a principal engineer who cares about long-term code health: readability, "
                "structure, and maintainability. You give concrete, actionable refactors and never "
                "invent bugs that aren't there."),
    "feature": ("You are a pragmatic, product-minded staff engineer. You propose high-value feature "
                "add-ons grounded in what the code actually does, with a realistic sense of effort."),
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
}


def _numbered(code):
    return "\n".join(f"{i+1:>5}| {ln}" for i, ln in enumerate(code.splitlines()))


def _merge(cfg):
    c = dict(DEFAULTS)
    if cfg:
        c.update({k: v for k, v in cfg.items() if v is not None})
    return c


def review_code(code, rel_path, mode="bug", cfg=None):
    """Returns (markdown_review, usage). Config-driven: model, max_tokens, temperature,
    reasoning effort (or 'off' for unbounded), base URL and prices all come from cfg.
    Always returns a string review and a usage dict with the real billed cost."""
    c = _merge(cfg)
    if mode not in MODES:
        mode = "bug"
    key = api_key()
    if not key:
        return "**No API key.** Set `OPENROUTER_API_KEY` and restart the app.", {"cost": 0}

    body = _TEMPLATES[mode].format(rel=rel_path)
    prompt = f"{body}\n\nSource (shown as `N| code`):\n\n```\n{_numbered(code)}\n```\n"
    try:
        static = build_static_context(code, rel_path, mode, c)
    except Exception:
        static = ""                                    # a broken enricher must never block a review
    if static:
        prompt += "\n" + static + "\n"

    client = OpenAI(
        api_key=key, base_url=c["api_base"],
        default_headers={"HTTP-Referer": "http://localhost", "X-Title": "Colibri Code Review"},
    )
    # bounded reasoning -> effort hint; unbounded ('off') -> omit so the model reasons freely
    extra = {}
    eff = str(c.get("reasoning", "off")).lower()
    if eff in ("low", "medium", "high", "xhigh"):
        extra = {"reasoning": {"effort": eff}}

    resp = client.chat.completions.create(
        model=c["model"],
        messages=[{"role": "system", "content": _SYS[mode]},
                  {"role": "user", "content": prompt}],
        temperature=float(c["temperature"]),
        max_tokens=int(c["max_tokens"]),
        extra_body=extra,
    )
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

    u = getattr(resp, "usage", None)
    pin = getattr(u, "prompt_tokens", 0) or 0
    pout = getattr(u, "completion_tokens", 0) or 0
    cost = getattr(u, "cost", None)
    if cost is None:
        cost = pin * c["price_in"] / 1_000_000 + pout * c["price_out"] / 1_000_000
    usage = {"prompt_tokens": pin, "completion_tokens": pout, "cost": cost or 0.0,
             "finish": fin, "model": c["model"]}
    return content, usage
