"""Round-3 convergence test: re-review the remediated crown jewels at BOTH high and
medium effort (owner's locked strategy). Saves each to junk/round3/ so neither
overwrites the other, and logs finding counts. -> junk/round3/_round3_log.txt"""
import os, sys, time, re
sys.path.insert(0, r"E:\colibri-analyzer")
import analyzer

REPO = r"C:\Users\User\source\repos\Nexusmill"
OUTDIR = os.path.join(REPO, "junk", "round3")
os.makedirs(OUTDIR, exist_ok=True)
LOG = os.path.join(OUTDIR, "_round3_log.txt")

TARGETS = [
    ("PatternSkin/ai_parts.py", "PatternSkin\\ai_parts.py"),
    ("PatternSkin/accel.py", "PatternSkin\\accel.py"),
    ("Spector/warehouse.py", "Spector\\warehouse.py"),
]
EFFORTS = ["high", "medium"]


def log(m):
    line = time.strftime("%H:%M:%S ") + m
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


if not analyzer.api_key():
    sys.exit("no key")

spent = 0.0
for rel, winrel in TARGETS:
    path = os.path.join(REPO, rel)
    with open(path, encoding="utf-8", errors="ignore") as fh:
        code = fh.read()
    for eff in EFFORTS:
        t0 = time.time()
        cfg = {"reasoning": eff, "max_tokens": 16000 if eff == "high" else 8000}
        md, usage = analyzer.review_code(code, winrel, "bug", cfg)
        spent += usage.get("cost", 0)
        nfind = len(re.findall(r"(?m)^\*\*\[", md))
        hi = len(re.findall(r"(?m)^\*\*\[(?:CRITICAL|HIGH)", md))
        safe = rel.replace("/", "__")
        out = os.path.join(OUTDIR, "%s__%s.md" % (safe, eff))
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        log("%-28s %-6s findings=%2d (crit/high=%d) $%.4f %ds finish=%s"
            % (rel, eff, nfind, hi, usage.get("cost", 0), int(time.time() - t0), usage.get("finish")))
log("ROUND-3 done: total $%.4f" % spent)
