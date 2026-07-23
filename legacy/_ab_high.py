import sys, time
sys.path.insert(0, r"E:\colibri-analyzer")
import analyzer
SRC = r"C:\Users\User\source\repos\Nexusmill\PatternSkin\filmstrip.py"
code = open(SRC, encoding="utf-8", errors="ignore").read()
t0 = time.time()
md, usage = analyzer.review_code(code, "PatternSkin/filmstrip.py", "bug",
                                 {"reasoning": "high", "max_tokens": 16000})
hdr = ("# A/B HIGH-effort bug review: filmstrip.py\n"
       f"- elapsed: {int(time.time()-t0)}s  cost: ${usage.get('cost',0):.4f}  "
       f"out_tokens: {usage.get('completion_tokens')}  finish: {usage.get('finish')}\n\n---\n\n")
open(r"C:\Users\User\source\repos\Nexusmill\junk\ab_high_filmstrip.md", "w",
     encoding="utf-8").write(hdr + md)
