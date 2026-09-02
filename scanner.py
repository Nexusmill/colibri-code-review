"""Directory scanner + core-file ranker.
Walks a project, hard-excludes secrets/legal/vendored/binary trees, then scores
each source file so authored 'core' files rank above bundled dependencies."""
import os, hashlib

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".hpp", ".cpp",
            ".cc", ".html", ".css", ".glsl", ".sh", ".ps1", ".rs", ".go", ".java", ".rb"}

# Directory names never worth reviewing (secrets/legal/binaries/deps/scratch).
DENY_DIRS = {".git", ".hg", ".svn", ".secrets", "secrets", "legal", "media",
             "junk", "build", "dist", "out", "__pycache__", "node_modules",
             ".venv", "venv", "site-packages", ".vs", ".idea", ".vscode",
             "vendor", "third_party", "thirdparty", ".mypy_cache", ".pytest_cache",
             ".ruff_cache", "coverage", "htmlcov", "obj", ".tox", ".eggs", "dist-info"}
DENY_SUBSTR = ("site-packages", "node_modules", "dist-info", ".egg-info",
               os.sep + "vendor" + os.sep, os.sep + "venv" + os.sep, os.sep + ".venv" + os.sep)
SKIP_FILE = (".min.js", ".min.css", ".map", "-lock.", ".bundle.")
MAX_BYTES = 2_000_000     # skip huge generated blobs


def _is_vendor(rel):
    low = rel.lower()
    return any(s in low for s in DENY_SUBSTR)


def scan(root):
    root = os.path.abspath(root)
    cand = []            # (path, rel, ext, dirpath)
    dir_count = {}
    for dp, dirs, fns in os.walk(root):
        if "pyvenv.cfg" in fns:          # a bundled virtualenv -> prune whole subtree
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs
                   if d.lower() not in DENY_DIRS
                   and not d.endswith(".egg-info") and not d.endswith(".dist-info")]
        for fn in fns:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in CODE_EXT:
                continue
            if any(s in fn.lower() for s in SKIP_FILE):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            if _is_vendor(rel):
                continue
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
            except OSError:
                continue
            dir_count[dp] = dir_count.get(dp, 0) + 1
            cand.append((p, rel, ext, dp))

    rows = []
    CORE_NAMES = {"__init__.py", "app.py", "main.py", "__main__.py", "cli.py",
                  "core.py", "server.py", "index.js", "index.ts"}
    for p, rel, ext, dp in cand:
        try:
            with open(p, "rb") as fh:
                raw = fh.read()
        except OSError:
            continue
        data = raw.decode("utf-8", "ignore")   # decoded text is used for scoring only
        chars = len(data)
        depth = rel.count(os.sep)
        sib = dir_count.get(dp, 1)
        score = 100.0
        score -= depth * 6                       # shallower = more likely core
        if sib > 150:   score -= 80              # very dense dir = vendored bundle
        elif sib > 60:  score -= 40
        elif sib > 30:  score -= 15
        if os.path.basename(p).lower() in CORE_NAMES:
            score += 15
        if ext in (".py", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cpp"):
            score += 8
        elif ext in (".css", ".html"):
            score -= 6
        if chars < 80:
            score -= 20
        head = data[:200].lstrip()
        if head.startswith(('"""', "'''", "#!", "# ", "/*", "//", "import ", "from ", "package ")):
            score += 4
        rows.append({
            "path": p, "rel": rel, "ext": ext, "chars": chars,
            "tokens": int(chars / 3.5), "dir_siblings": sib,
            "score": round(score, 1),
            "sha": hashlib.sha256(raw).hexdigest(),   # RAW bytes: must equal store.file_sha() (binary), or CRLF files read as perpetually "stale" and get re-billed
        })
    rows.sort(key=lambda r: (-r["score"], -r["tokens"]))
    return rows
