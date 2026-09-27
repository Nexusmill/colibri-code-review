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
import pathlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scanner    # noqa: E402
import analyzer   # noqa: E402
import store      # noqa: E402  (shared sha cache: batch + app never re-bill unchanged files)
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def gather(paths, patterns):
    files = []
    for p in paths:
        ap = os.path.abspath(p)
        if os.path.isfile(ap):
            files.append(ap)  # explicit files are a deliberate opt-in
        elif os.path.isdir(ap):
            files.extend(row["path"] for row in scanner.scan(ap, patterns=patterns))
        else:
            print("skip (not found): %s" % p)
    return sorted(set(files))


def cache_root(paths, explicit=None):
    if explicit:
        root = os.path.abspath(explicit)
        if not os.path.isdir(root):
            raise ValueError("--root must name an existing directory")
        return root
    roots = []
    for value in paths:
        path = pathlib.Path(os.path.abspath(value))
        if not path.exists():
            continue
        directory = path if path.is_dir() else path.parent
        repo = next((p for p in (directory, *directory.parents) if (p / ".git").exists()), None)
        roots.append(str(repo or directory))
    try:
        return os.path.commonpath(roots)
    except ValueError:
        raise ValueError("Paths span drives; run each project separately or supply --root") from None


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
    ap.add_argument("--root", help="project cache root (default: repository or requested directory)")
    ap.add_argument("--out", default="colibri_batch", help="output directory for the .md reviews")
    ap.add_argument("--budget", type=float, default=0.0,
                    help="stop new calls once billed spend reaches this amount; in-flight calls can exceed it (0 = no cap)")
    ap.add_argument("--force", action="store_true",
                    help="review even files whose current sha already has an up-to-date review "
                         "in .colibri_reviews (default: skip them - true resumability)")
    ap.add_argument("--workers", type=int, default=1,
                    help="parallel review calls (network-bound; 4 is ~4x wall clock). Budget is "
                         "enforced under a lock before each dispatch.")
    ap.add_argument("--format", default="md", choices=["md", "json"],
                    help="review output: md (default) or validated machine-readable json "
                         "(one corrective retry; falls back to .md on double parse failure)")
    ap.add_argument("--delta", action="store_true",
                    help="stale files: inject the previous saved review so the model reports "
                         "only NEW/changed findings (cheaper convergence rounds)")
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

    # Cache identity comes from the requested project, not matching-file distribution.
    try:
        base = cache_root(args.paths, args.root)
        if any(os.path.commonpath([base, p]) != base for p in files):
            ap.error("All files must be inside --root; run separate projects separately")
    except ValueError as error:
        ap.error(str(error))
    manifest = store.load_manifest(base)
    mlock = threading.Lock()

    _mt = args.max_tokens or analyzer.model_max_tokens(args.model)   # AUTO -> the model's own ceiling
    print("%d file(s) -> %s   model=%s  mode=%s  effort=%s  max_tokens=%s  workers=%d"
          % (len(files), out, args.model, args.mode, args.effort, _mt, max(1, args.workers)))
    state = {"total": 0.0, "stopped": False, "done": 0, "skipped": 0, "errors": 0}
    summary = []

    def _one(i, p):
        try:
            rel = os.path.relpath(p, base)
        except ValueError:
            rel = p            # cross-drive on Windows: relpath can't cross mounts
        # sha/status ran OUTSIDE the review try, so a file deleted between gather() and
        # here (or a manifest read error) crashed the whole batch and skipped the summary.
        try:
            code, sha = store.read_source(p)
            with mlock:
                st_ = store.status(manifest, os.path.abspath(p), sha, args.mode)
        except Exception as e:
            with mlock:
                state["errors"] += 1
            print("[%d/%d] %-48s  ERROR (pre-review): %s" % (i, len(files), rel[-48:], e))
            summary.append({"rel": rel, "status": "error", "error": str(e)[:300]})
            return
        if st_ == "reviewed" and not args.force:
            with mlock:
                state["skipped"] += 1
            print("[%d/%d] %-48s  SKIP (already reviewed at this sha; --force to redo)"
                  % (i, len(files), rel[-48:]))
            summary.append({"rel": rel, "status": "skipped"})
            return
        prior = None
        if args.delta and st_ == "stale":
            with mlock:
                e = store.entry_for(manifest, p)
                md_e = (e.get("modes") or {}).get(args.mode) or {}
            try:
                if md_e.get("output"):
                    with open(store.output_path(base, md_e["output"]), encoding="utf-8", errors="replace") as stream:
                        prior = stream.read()
            except OSError:
                prior = None
        t0 = time.time()
        cost = 0.0
        received = False
        md = None
        saved = None
        try:
            with mlock:
                if state["stopped"]:
                    return
            md, usage = analyzer.review_code(code, rel, args.mode, cfg,
                                             prior_md=prior, fmt=args.format)
            cost = float(usage.get("cost", 0.0) or 0.0)
            received = True
            with mlock:
                state["total"] += cost  # billed even if every persistence operation fails
            complete = usage.get("complete", usage.get("finish") == "stop") is True
            ok_json = args.format == "json" and not usage.get("json_error")
            ext = (".%s.json" if ok_json else ".%s.md") % args.mode
            name = store._safe_name(rel) + ext
            (out / name).write_text(md, encoding="utf-8")
            with mlock:
                saved = store.save_review(base, p, rel, sha, args.mode, md, usage, args.model)
                manifest.update(store.load_manifest(base))
            with mlock:
                state["done" if complete else "errors"] += 1
            hi = md.count("[HIGH]") + md.count("[CRITICAL]") + md.count('"HIGH"') + md.count('"CRITICAL"')
            med = md.count("[MEDIUM]") + md.count('"MEDIUM"')
            print("[%d/%d] %-48s %6.1fs  $%.4f  finish=%s  HIGH/CRIT=%d MED=%d%s%s"
                  % (i, len(files), rel[-48:], time.time() - t0, cost, usage.get("finish"), hi, med,
                     "  json_error->md" if usage.get("json_error") else "",
                     "  (delta)" if prior else ""))
            summary.append({"rel": rel, "status": "ok" if complete else "incomplete", "cost": cost, "finish": usage.get("finish"),
                            "high_crit": hi, "medium": med, "output": str(out / name),
                            "delta": bool(prior), "json_error": bool(usage.get("json_error"))})
        except Exception as e:
            with mlock:
                state["errors"] += 1
                if received:
                    state["stopped"] = True  # storage failure: do not bill more work
            print("[%d/%d] %-48s  ERROR: %s" % (i, len(files), rel[-48:], e))
            row = {"rel": rel, "status": "error", "error": str(e)[:300], "cost": cost}
            if received:
                row.update({"review": md, "usage": usage, "saved_output": saved})
            summary.append(row)

    workers = max(1, int(args.workers))
    if workers == 1:
        for i, p in enumerate(files, 1):
            if state["stopped"]:
                break
            if args.budget and state["total"] >= args.budget:
                print("budget $%.2f reached after %d file(s); stopping." % (args.budget, i - 1))
                break
            _one(i, p)
    else:
        # Bound in-flight dispatch on COMPLETION so --budget is actually enforced: the old
        # single-pass loop submitted every file before any worker finished (state["total"]
        # rises only on completion), so the budget check never tripped and the whole list
        # was billed regardless. Keep at most `workers` in flight; re-check budget as
        # completions accrue.
        from concurrent.futures import wait, FIRST_COMPLETED
        with ThreadPoolExecutor(max_workers=workers) as ex:
            pending = set()
            for i, p in enumerate(files, 1):
                with mlock:
                    over = state["stopped"] or (bool(args.budget) and state["total"] >= args.budget)
                if over:
                    if state["stopped"]:
                        print("persistence failure; not dispatching further files.")
                    else:
                        print("budget $%.2f reached; not dispatching further files." % args.budget)
                    state["stopped"] = True
                    break
                pending.add(ex.submit(_one, i, p))
                if len(pending) >= workers:
                    done, pending = wait(pending, return_when=FIRST_COMPLETED)
                    for f in done:
                        f.result()
            for f in as_completed(pending):
                f.result()
    import json as _json
    result = {"model": args.model, "mode": args.mode, "format": args.format,
              "done": state["done"], "skipped": state["skipped"], "errors": state["errors"],
              "spent": round(state["total"], 6), "files": summary}
    try:
        (out / "_batch_summary.json").write_text(_json.dumps(result, indent=1), encoding="utf-8")
    except OSError as error:
        state["errors"] += 1
        result["errors"] = state["errors"]
        print("ERROR saving batch summary: %s" % error)
        # The terminal remains a recovery destination when every file write fails.
        print("RECOVERY SUMMARY:\n" + _json.dumps(result, indent=1))
    print("DONE: %d reviewed, %d skipped, %d error(s), spent $%.4f -> %s"
          % (state["done"], state["skipped"], state["errors"], state["total"], out))
    return 1 if state["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
