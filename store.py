"""Persistence: remembers which files were reviewed, PER MODE (bug/quality/feature),
saves each review to .colibri_reviews/ and links it back to the source file.
Also exports every saved review into one Markdown file. Survives app restarts."""
import os, json, hashlib, time


def reviews_dir(base):
    d = os.path.join(base, ".colibri_reviews")
    os.makedirs(d, exist_ok=True)
    return d


def _manifest_path(base):
    return os.path.join(reviews_dir(base), "_manifest.json")


def load_manifest(base):
    p = _manifest_path(base)
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_manifest(base, m):
    # atomic: a crash mid-dump previously corrupted the manifest -> load_manifest returned {}
    # and the WHOLE project's sha cache + cost ledger silently reset (every file re-billed as new).
    p = _manifest_path(base)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    os.replace(tmp, p)


def file_sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return ""


def status(manifest, abspath, current_sha, mode):
    """'new' (this mode never run), 'reviewed' (up to date), 'stale' (file changed since)."""
    e = manifest.get(abspath) or {}
    md = (e.get("modes") or {}).get(mode)
    if not md:
        return "new"
    return "reviewed" if md.get("sha") == current_sha else "stale"


def modes_done(manifest, abspath, current_sha):
    """How many of the 3 modes are up to date for this file (for the 'All three' view)."""
    e = manifest.get(abspath) or {}
    return sum(1 for md in (e.get("modes") or {}).values() if md.get("sha") == current_sha)


def _safe_name(rel):
    # keep filenames sane on Windows (260-char path limit): flatten + cap, keep it unique via sha
    flat = rel.replace(os.sep, "__").replace("/", "__")
    return flat[-120:]


def save_review(base, path, rel, sha, mode, review_md, usage, model):
    rd = reviews_dir(base)
    out = os.path.join(rd, f"{_safe_name(rel)}__{mode}__{sha[:8]}.md")
    header = (f"# {mode.upper()} review: {rel}\n\n"
              f"- source: `{path}`\n"
              f"- model: {model}\n"
              f"- reviewed: {time.strftime('%Y-%m-%d %H:%M')}\n"
              f"- tokens: in {usage.get('prompt_tokens', 0)} / out {usage.get('completion_tokens', 0)}\n"
              f"- est cost: ${usage.get('cost', 0):.4f}\n\n---\n\n")
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(header + (review_md or "_(empty review)_"))
    os.replace(tmp, out)                        # atomic: never leave a half-written review

    m = load_manifest(base)
    ap = os.path.abspath(path)
    entry = m.get(ap) or {"rel": rel, "modes": {}}
    entry.setdefault("modes", {})
    entry["rel"] = rel
    entry["modes"][mode] = {
        "sha": sha, "output": out,
        "reviewed_at": time.strftime("%Y-%m-%d %H:%M"),
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost": usage.get("cost", 0),
    }
    m[ap] = entry
    save_manifest(base, m)
    return out


def total_cost(manifest):
    tot = 0.0
    for e in manifest.values():
        for md in (e.get("modes") or {}).values():
            tot += md.get("cost", 0) or 0
    return tot


def export_all(base):
    """Concatenate every saved review into one Markdown file. Returns (path, text)."""
    m = load_manifest(base)
    parts = [f"# Colibri Code Reviews - {os.path.basename(base.rstrip(os.sep))}",
             f"_exported {time.strftime('%Y-%m-%d %H:%M')} - {len(m)} file(s) - "
             f"${total_cost(m):.4f} total_\n", "## Contents\n"]
    for _, e in sorted(m.items(), key=lambda kv: kv[1].get("rel", "")):
        done = ", ".join(sorted((e.get("modes") or {}).keys()))
        parts.append(f"- {e.get('rel', '?')}  ({done})")
    parts.append("\n---\n")
    for _, e in sorted(m.items(), key=lambda kv: kv[1].get("rel", "")):
        for mode, md in sorted((e.get("modes") or {}).items()):
            try:
                with open(md["output"], encoding="utf-8") as f:
                    parts.append("\n" + f.read() + "\n\n---\n")
            except Exception:
                parts.append(f"\n*(missing output for {e.get('rel')} / {mode})*\n\n---\n")
    text = "\n".join(parts)
    out = os.path.join(reviews_dir(base), "_all_reviews.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    return out, text
