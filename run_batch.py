"""Colibri headless batch code review.

Run the same reviewer the Streamlit app uses over many files, from the command line -
resumable-friendly, budget-aware, one Markdown review saved per file, running cost printed.

Reads OPENROUTER_API_KEY from the environment (never a file). See INSTRUCTIONS.md / AGENTS.md.

Examples
--------
  python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high
  python run_batch.py app.py analyzer.py --model moonshotai/kimi-k3 --budget 0.50
  python run_batch.py src --glob "*.py,*.js,*.ts" --out reviews
"""
import argparse
import os
import sys
import time
import fnmatch
import pathlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyzer   # noqa: E402

_SKIP_DIR = ("__pycache__", ".git", ".hg", "node_modules", ".venv", "venv",
             "dist", "build", ".colibri_reviews")


def gather(paths, patterns):
    files = []
    for p in paths:
        ap = os.path.abspath(p)
        if os.path.isfile(ap):
            files.append(ap)
        elif os.path.isdir(ap):
            for root, dirs, names in os.walk(ap):
                dirs[:] = [d for d in dirs if d not in _SKIP_DIR]
                for n in names:
                    if any(fnmatch.fnmatch(n, pat) for pat in patterns):
                        files.append(os.path.join(root, n))
        else:
            print("skip (not found): %s" % p)
    return sorted(set(files))


def main():
    ap = argparse.ArgumentParser(description="Colibri headless batch code review.")
    ap.add_argument("paths", nargs="+", help="files and/or folders to review")
    ap.add_argument("--model", default="z-ai/glm-5.2", help="any OpenRouter model id")
    ap.add_argument("--mode", default="bug", choices=["bug", "quality", "feature"])
    ap.add_argument("--effort", default="high",
                    choices=["off", "low", "medium", "high", "xhigh"],
                    help="reasoning effort ('off' = unbounded)")
    ap.add_argument("--max-tokens", type=int, default=0,
                    help="output+reasoning ceiling. 0 = AUTO: use the model's own max_completion_tokens "
                         "(never truncate a review - GLM-5.2 reasons past 20k and needs its full 131k).")
    ap.add_argument("--temperature", type=float, default=0.15)
    ap.add_argument("--glob", default="*.py",
                    help="comma-separated filename patterns for folder walks (default *.py)")
    ap.add_argument("--out", default="colibri_batch", help="output directory for the .md reviews")
    ap.add_argument("--budget", type=float, default=0.0,
                    help="stop before the running total would exceed this many dollars (0 = no cap)")
    ap.add_argument("--price-in", type=float, default=0.0, help="$/1M input (fallback if the API omits cost)")
    ap.add_argument("--price-out", type=float, default=0.0, help="$/1M output (fallback)")
    ap.add_argument("--no-static", action="store_true",
                    help="disable the static-analysis enrichers (ast+pyflakes, mypy, dis) appended "
                         "to each prompt (they are on by default)")
    args = ap.parse_args()

    if not analyzer.api_key():
        sys.exit("No OPENROUTER_API_KEY in the environment. See INSTRUCTIONS.md.")

    patterns = [g.strip() for g in args.glob.split(",") if g.strip()] or ["*.py"]
    files = gather(args.paths, patterns)
    if not files:
        sys.exit("No matching files.")

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cfg = {"model": args.model, "reasoning": args.effort, "max_tokens": (args.max_tokens or None),
           "temperature": args.temperature, "price_in": args.price_in, "price_out": args.price_out,
           "static_ast": not args.no_static, "static_mypy": not args.no_static,
           "static_dis": not args.no_static}

    _mt = args.max_tokens or analyzer.model_max_tokens(args.model)   # AUTO -> the model's own ceiling
    print("%d file(s) -> %s   model=%s  mode=%s  effort=%s  max_tokens=%s"
          % (len(files), out, args.model, args.mode, args.effort, _mt))
    total = 0.0
    for i, p in enumerate(files, 1):
        if args.budget and total >= args.budget:
            print("budget $%.2f reached after %d file(s); stopping." % (args.budget, i - 1))
            break
        try:
            rel = os.path.relpath(p)
        except ValueError:
            rel = p            # cross-drive on Windows (files on C:, tool on E:): relpath can't cross mounts
        t0 = time.time()
        try:
            code = open(p, encoding="utf-8", errors="ignore").read()
            md, usage = analyzer.review_code(code, rel, args.mode, cfg)
            cost = float(usage.get("cost", 0.0) or 0.0)
            total += cost
            name = rel.replace(os.sep, "__").replace("/", "__").replace(":", "") + ".%s.md" % args.mode
            (out / name).write_text(md, encoding="utf-8")
            hi = md.count("[HIGH]") + md.count("[CRITICAL]")
            med = md.count("[MEDIUM]")
            print("[%d/%d] %-48s %6.1fs  $%.4f  finish=%s  HIGH/CRIT=%d MED=%d"
                  % (i, len(files), rel[-48:], time.time() - t0, cost, usage.get("finish"), hi, med))
        except Exception as e:
            print("[%d/%d] %-48s  ERROR: %s" % (i, len(files), rel[-48:], e))
    print("DONE: %d file(s), spent $%.4f -> %s" % (len(files), total, out))


if __name__ == "__main__":
    main()
