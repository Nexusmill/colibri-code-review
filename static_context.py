"""static_context.py - deterministic static-analysis signals appended to the review prompt.

The model reviews SOURCE TEXT; a tool can PROVE in milliseconds things the model only guesses.
This module runs three cheap, deterministic passes on the exact source under review and hands
their output to the model as HINTS to corroborate (never as gospel):

  * ast + pyflakes -> scope leaks (undefined / used-before-assignment names), dead code
                      (unused imports / variables / redefinitions), plus ast-only smells
                      (mutable default args, bare except, unreachable code after return/raise).
  * mypy           -> static type errors, surfaced before runtime (dynamic-type confusion).
  * dis            -> bytecode for the hottest (loop-bearing) functions so the model can spot
                      hidden overhead (repeated LOAD_GLOBAL / LOAD_ATTR inside loops, needless
                      work per iteration, etc.).

Everything degrades gracefully: a missing tool or a syntax error yields a short note, never a
crash. Only runs for Python source. Output is size-capped so it never dominates the input budget.
"""
import ast
import dis
import io
import os
import subprocess
import sys
import tempfile

_NONPY = (".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".h", ".cpp", ".cc",
          ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".html", ".css", ".scss",
          ".json", ".md", ".yaml", ".yml", ".toml", ".xml", ".sql", ".sh", ".ps1", ".txt")


def _looks_python(code):
    try:
        ast.parse(code)
        return True
    except Exception:
        return False


def _is_python(rel, code):
    r = (rel or "").lower()
    if r.endswith(".py") or r.endswith(".pyi"):
        return True
    if any(r.endswith(ext) for ext in _NONPY):
        return False
    return _looks_python(code)


def _cap(s, n):
    s = (s or "").rstrip()
    if len(s) <= n:
        return s
    return s[:n].rstrip() + "\n... [truncated, %d more chars]" % (len(s) - n)


# --------------------------------------------------------------- ast + pyflakes
def _pyflakes(code):
    try:
        from pyflakes import api as _api, reporter as _rep
    except Exception:
        return None                                   # not installed
    out, err = io.StringIO(), io.StringIO()
    try:
        _api.check(code, "<code>", _rep.Reporter(out, err))
    except Exception as e:
        return "(pyflakes failed: %s)" % type(e).__name__
    lines = [ln for ln in (out.getvalue() + err.getvalue()).splitlines() if ln.strip()]
    cleaned = []
    for ln in lines:
        parts = ln.split(":", 3)                       # "<code>:LINE:COL: message"
        if len(parts) >= 4 and parts[1].strip().isdigit():
            cleaned.append("L%s: %s" % (parts[1].strip(), parts[3].strip()))
        else:
            cleaned.append(ln.replace("<code>:", "L").strip())
    return "\n".join(cleaned)


def _ast_smells(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ["SYNTAX ERROR at L%s: %s (the file does not parse)" % (e.lineno, e.msg)], True
    smells = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in list(node.args.defaults) + list(node.args.kw_defaults):
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    smells.append("L%s: mutable default argument in `%s` "
                                  "(one object shared across all calls)" % (d.lineno, node.name))
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            smells.append("L%s: bare `except:` (also swallows KeyboardInterrupt/SystemExit)"
                          % node.lineno)

    def scan(body):
        terminated_at = None
        for st in body:
            if terminated_at is not None:
                smells.append("L%s: unreachable code (follows the return/raise/break/continue "
                              "at L%s)" % (st.lineno, terminated_at))
                terminated_at = None                   # flag once per block
            if isinstance(st, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                terminated_at = st.lineno
        for st in body:
            for field in ("body", "orelse", "finalbody"):
                b = getattr(st, field, None)
                if isinstance(b, list) and b:
                    scan(b)
            for h in getattr(st, "handlers", []) or []:
                scan(h.body)

    scan(tree.body)
    return smells, False


def ast_section(code):
    smells, _syntax = _ast_smells(code)
    pf = _pyflakes(code)
    chunks = []
    if smells:
        chunks.append("ast smells:\n" + "\n".join("  - " + s for s in smells))
    if pf is None:
        chunks.append("pyflakes: NOT INSTALLED (pip install pyflakes) - "
                      "undefined-name / unused-import / unused-var checks were skipped.")
    elif pf.strip():
        chunks.append("pyflakes (undefined names = scope leaks; unused = dead code):\n"
                      + "\n".join("  " + ln for ln in pf.splitlines()))
    else:
        chunks.append("pyflakes: clean (no undefined names, unused imports, or unused locals).")
    return "\n".join(chunks) if chunks else "no findings."


# --------------------------------------------------------------------- mypy
def mypy_section(code, rel, timeout=60):
    try:
        import mypy  # noqa: F401
    except Exception:
        return "NOT INSTALLED (pip install mypy) - type check skipped."
    tmpdir = tempfile.mkdtemp(prefix="colibri_mypy_")
    base = os.path.basename(rel or "") or "module.py"
    if not base.endswith(".py"):
        base += ".py"
    p = os.path.join(tmpdir, base)
    try:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(code)
        cmd = [sys.executable, "-m", "mypy", "--no-error-summary", "--show-error-codes",
               "--no-color-output", "--hide-error-context", "--follow-imports=skip",
               "--ignore-missing-imports", "--no-pretty", p]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = ((r.stdout or "") + (r.stderr or "")).replace(p, rel or base)
        out = out.replace(tmpdir + os.sep, "").strip()
        return out if out else "clean (no type errors)."
    except subprocess.TimeoutExpired:
        return "timed out after %ds (skipped)." % timeout
    except Exception as e:
        return "failed (%s) - skipped." % type(e).__name__
    finally:
        try:
            os.remove(p)
            os.rmdir(tmpdir)
        except Exception:
            pass


# ---------------------------------------------------------------------- dis
def _loop_depth(node):
    best = 0
    for child in ast.iter_child_nodes(node):
        d = _loop_depth(child)
        if isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            d += 1
        best = max(best, d)
    return best


def _hot_functions(tree):
    hot = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            depth = _loop_depth(node)
            if depth >= 1:
                loops = sum(isinstance(n, (ast.For, ast.AsyncFor, ast.While))
                            for n in ast.walk(node))
                hot.append((depth, loops, node.name))
    hot.sort(reverse=True)
    return [name for _d, _l, name in hot]


def _code_objects(co):
    yield co
    for const in co.co_consts:
        if hasattr(const, "co_code"):
            yield from _code_objects(const)


def dis_section(code, rel, max_funcs=3, per_cap=2500):
    try:
        tree = ast.parse(code)
        module_co = compile(code, rel or "<module>", "exec")
    except SyntaxError:
        return "skipped (file does not parse)."
    names = _hot_functions(tree)[:max_funcs]
    if not names:
        return "no loop-bearing functions - nothing hot to disassemble."
    by_name = {}
    for co in _code_objects(module_co):
        by_name.setdefault(co.co_name, co)             # first (outermost) wins
    chunks = []
    for nm in names:
        co = by_name.get(nm)
        if co is None:
            continue
        buf = io.StringIO()
        try:
            dis.dis(co, file=buf)
        except Exception as e:
            chunks.append("# %s(): dis failed (%s)" % (nm, type(e).__name__))
            continue
        chunks.append("# %s()\n%s" % (nm, _cap(buf.getvalue(), per_cap)))
    return "\n\n".join(chunks) if chunks else "no disassembly available."


# ------------------------------------------------------------------- assemble
def build_static_context(code, rel, mode="bug", cfg=None):
    """Return a Markdown block of deterministic static-analysis signals for `code`, or "" when
    it isn't Python or every pass is disabled. Config keys (all default True):
      static_ast, static_mypy, static_dis, and static_max_chars (int, overall cap)."""
    cfg = cfg or {}
    if not _is_python(rel, code):
        return ""
    want_ast = cfg.get("static_ast", True)
    want_mypy = cfg.get("static_mypy", True) and mode in ("bug", "quality")
    want_dis = cfg.get("static_dis", True) and mode in ("bug", "quality")
    total_cap = int(cfg.get("static_max_chars", 8000) or 8000)

    sections = []
    if want_ast:
        sections.append(("Scope leaks & dead code (ast + pyflakes)", ast_section(code)))
    if want_mypy:
        sections.append(("Static type check (mypy)", mypy_section(code, rel)))
    if want_dis:
        sections.append(("Bytecode of hot loop-bearing functions (dis)", dis_section(code, rel)))
    if not sections:
        return ""

    body = [
        "---",
        "## Static-analysis signals (deterministic tooling, not the model)",
        "_Generated by running real tools on this exact source. Treat as HINTS: corroborate each "
        "against the code, act on the true ones, and ignore any that don't hold. Line numbers "
        "match the `N| code` gutter above._",
        "",
    ]
    for title, content in sections:
        body.append("### %s" % title)
        body.append((content or "").strip() or "none.")
        body.append("")
    return _cap("\n".join(body), total_cap)
