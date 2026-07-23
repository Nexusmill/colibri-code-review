"""Headless review sweep: run a batch of reviews through the same scanner/store the
console uses, so results land in .colibri_reviews/ with identical tracking.

    python sweep.py <project_dir> [--mode bug] [--count 20] [--max-cost 5.0]

Skips files already reviewed (current sha, same mode). Writes progress to
<project>/.colibri_reviews/_sweep_log.txt so a long run can be watched.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyzer
import scanner
import store


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--mode", default="bug", choices=sorted(analyzer.MODES))
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--max-cost", type=float, default=5.0,
                    help="stop the batch once actual spend crosses this")
    ap.add_argument("--min-score", type=float, default=40.0)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--max-tokens", type=int, default=8000)
    ap.add_argument("--only-new", action="store_true",
                    help="review only files never reviewed in this mode (skip 'changed' too)")
    a = ap.parse_args()

    if not analyzer.api_key():
        sys.exit("No OPENROUTER_API_KEY in the environment.")
    base = os.path.abspath(a.project)
    log_path = os.path.join(store.reviews_dir(base), "_sweep_log.txt")
    lg = open(log_path, "a", encoding="utf-8", buffering=1)

    def log(msg):
        line = time.strftime("%H:%M:%S ") + msg
        print(line)
        lg.write(line + "\n")

    cfg = {"reasoning": a.effort, "max_tokens": a.max_tokens}
    rows = scanner.scan(base)
    manifest = store.load_manifest(base)
    want = {"new"} if a.only_new else {"new", "stale"}
    todo = [r for r in rows if r["score"] >= a.min_score
            and store.status(manifest, os.path.abspath(r["path"]), r["sha"], a.mode) in want]
    todo = todo[: a.count]
    est_in = sum(r["tokens"] for r in todo)
    log(f"SWEEP start: mode={a.mode} files={len(todo)} est_input={est_in:,} tok "
        f"ceiling<=${est_in * 3 / 1e6 + len(todo) * a.max_tokens * 15 / 1e6:.2f} "
        f"budget=${a.max_cost:.2f}")

    spent = 0.0
    done = 0
    for i, r in enumerate(todo, 1):
        if spent >= a.max_cost:
            log(f"BUDGET reached (${spent:.2f}) - stopping at {done}/{len(todo)}")
            break
        rel = r["rel"]
        try:
            with open(r["path"], encoding="utf-8", errors="ignore") as fh:
                code = fh.read()
            t0 = time.time()
            md, usage = analyzer.review_code(code, rel, a.mode, cfg)
            out = store.save_review(base, r["path"], rel, r["sha"], a.mode, md, usage,
                                    cfg.get("model") or analyzer.DEFAULTS["model"])
            spent += usage.get("cost", 0)
            done += 1
            log(f"[{i}/{len(todo)}] {rel}  ${usage.get('cost', 0):.4f}  "
                f"{int(time.time() - t0)}s  finish={usage.get('finish')}  -> {os.path.basename(out)}")
        except Exception as e:
            log(f"[{i}/{len(todo)}] {rel}  FAILED: {e}")
    log(f"SWEEP done: {done} reviews, ${spent:.4f} actual spend")


if __name__ == "__main__":
    main()
