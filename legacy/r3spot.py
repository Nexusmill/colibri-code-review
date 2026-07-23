import os, sys, time, re
sys.path.insert(0, r"E:\colibri-analyzer")
import analyzer
REPO = r"C:\Users\User\source\repos\Nexusmill"
OUT = os.path.join(REPO, "junk", "round3")
os.makedirs(OUT, exist_ok=True)
if not analyzer.api_key():
    sys.exit("no key")
tot = 0.0
for rel in ("Spector/warehouse.py", "PatternSkin/accel.py"):
    path = os.path.join(REPO, rel)
    code = open(path, encoding="utf-8", errors="ignore").read()
    t0 = time.time()
    md, u = analyzer.review_code(code, rel.replace("/", "\\"), "bug", {"reasoning": "medium", "max_tokens": 8000})
    tot += u.get("cost", 0)
    open(os.path.join(OUT, rel.replace("/", "__") + "__r3med.md"), "w", encoding="utf-8").write(md)
    with open(os.path.join(OUT, "_r3spot_log.txt"), "a", encoding="utf-8") as f:
        f.write("%s findings=%d crit_high=%d $%.4f %ds finish=%s\n" % (
            rel, len(re.findall(r"(?m)^\*\*\[", md)),
            len(re.findall(r"(?m)^\*\*\[(?:CRITICAL|HIGH)", md)),
            u.get("cost", 0), int(time.time() - t0), u.get("finish")))
with open(os.path.join(OUT, "_r3spot_log.txt"), "a", encoding="utf-8") as f:
    f.write("done $%.4f\n" % tot)
