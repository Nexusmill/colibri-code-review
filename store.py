"""Persistence: remembers which files were reviewed, PER MODE (bug/quality/feature),
saves each review to .colibri_reviews/ and links it back to the source file.
Also exports every saved review into one Markdown file. Survives app restarts."""
import os, json, hashlib, time, contextlib, tempfile, uuid
try:
    import msvcrt                      # Windows advisory file lock
except ImportError:
    msvcrt = None
try:
    import fcntl                       # POSIX advisory file lock
except ImportError:
    fcntl = None


@contextlib.contextmanager
def _manifest_lock(base):
    """Cross-PROCESS lock around the manifest read-modify-write. The Streamlit console and
    run_batch (separate processes, no shared threading.Lock) both load->mutate->replace the
    same _manifest.json; without this the last writer clobbers the other's row (silent loss
    of a review record). Held across the load and the replace."""
    lockp = os.path.join(reviews_dir(base), "_manifest.lock")
    f = open(lockp, "a+")
    try:
        if msvcrt:
            f.seek(0)
            while True:
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
        elif fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if msvcrt:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            elif fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()


def reviews_dir(base):
    d = os.path.join(base, ".colibri_reviews")
    os.makedirs(d, exist_ok=True)
    return d


def _manifest_path(base):
    return os.path.join(reviews_dir(base), "_manifest.json")


def load_manifest(base):
    try:
        with open(_manifest_path(base), encoding="utf-8") as stream:
            raw = json.load(stream)
    except (OSError, ValueError, RecursionError):
        return {}
    if not isinstance(raw, dict):
        return {}
    normalized = {}
    original_keys = {path_key(path) for path in raw}
    base_key = path_key(base)
    candidates, sources, destinations = {}, {}, {}
    for path, entry in raw.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("modes", {}), dict):
            continue
        rel = entry.get("rel", "")
        if not isinstance(rel, str) or not rel or os.path.isabs(rel):
            continue
        try:
            original = path_key(path)
            candidate = path_key(os.path.join(base, rel))
            try:
                inside_base = os.path.commonpath([base_key, original]) == base_key
            except ValueError:
                inside_base = False
            if (not inside_base and candidate not in original_keys
                    and os.path.commonpath([base_key, candidate]) == base_key
                    and original.endswith(os.sep + os.path.normcase(os.path.normpath(rel)))):
                candidates[path] = candidate
                sources.setdefault(candidate, set()).add(original)
                destinations.setdefault(original, set()).add(candidate)
        except (ValueError, OSError):
            continue
    for path, entry in raw.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("modes", {}), dict):
            continue
        rel = entry.get("rel", "")
        if not isinstance(rel, str):
            rel = ""
        try:
            key = path_key(path)
            candidate = candidates.get(path)
            if (candidate and len(sources[candidate]) == 1
                    and len(destinations[key]) == 1):
                # Ambiguous relocation never merges distinct source identities.
                key = candidate
        except (ValueError, OSError):
            continue
        target = normalized.setdefault(key, {"rel": rel, "modes": {}, "attempts": []})
        attempts = entry.get("attempts", [])
        if isinstance(attempts, list):
            target["attempts"].extend(record for record in attempts if isinstance(record, dict))
        for mode, record in entry.get("modes", {}).items():
            if not isinstance(record, dict):
                continue
            previous = target["modes"].get(mode, {})
            if str(record.get("reviewed_at", "")) >= str(previous.get("reviewed_at", "")):
                target["modes"][mode] = record
    return normalized

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


def path_key(path):
    """One filesystem identity, including Windows case folding."""
    return os.path.normcase(os.path.abspath(path))


def entry_for(manifest, path):
    key = path_key(path)
    if key in manifest:
        return manifest[key]
    # In-memory legacy manifests may not have passed through load_manifest.
    entry = {"modes": {}}
    for old_path, old in manifest.items():
        if path_key(old_path) == key:
            entry["modes"].update(old.get("modes", {}))
    return entry


def read_source(path):
    """Hash and decode exactly one buffer, even if an editor saves during review."""
    with open(path, "rb") as stream:
        raw = stream.read()
    return raw.decode("utf-8", "replace"), hashlib.sha256(raw).hexdigest()


def output_path(base, output):
    """Resolve canonical references and legacy absolute paths after a project move."""
    if not os.path.isabs(output):
        return os.path.join(base, output)
    parts = os.path.normpath(output).split(os.sep)
    if ".colibri_reviews" in parts:
        index = len(parts) - 1 - parts[::-1].index(".colibri_reviews")
        relocated = os.path.join(base, *parts[index:])
        if os.path.isfile(relocated):
            return relocated
    return output


def status(manifest, abspath, current_sha, mode):
    """Only a completed review of the current bytes grants cache credit."""
    md = entry_for(manifest, abspath).get("modes", {}).get(mode)
    if not md or md.get("complete") is False:
        return "new"
    return "reviewed" if md.get("sha") == current_sha else "stale"


def modes_done(manifest, abspath, current_sha):
    """Count only bug, quality and feature for the All three view."""
    return sum(status(manifest, abspath, current_sha, mode) == "reviewed"
               for mode in ("bug", "quality", "feature"))


def _safe_name(rel):
    normalized = os.path.normcase(os.path.normpath(rel)).replace("\\", "/")
    identity = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    flat = normalized.replace("/", "__").replace(":", "_")
    return flat[-48:] + "__" + identity


def save_review(base, path, rel, sha, mode, review_md, usage, model):
    rd = reviews_dir(base)
    finishes = [usage[key] for key in ("finish", "finish_reason") if key in usage]
    complete = (usage.get("complete", "stop" in finishes) is True
                and all(finish == "stop" for finish in finishes)
                and isinstance(review_md, str) and bool(review_md.strip()))
    attempt = "__attempt_" + uuid.uuid4().hex
    out = os.path.join(rd, f"{_safe_name(rel)}__{mode}__{sha[:8]}{attempt}.md")
    header = (f"# {mode.upper()} review: {rel}\n\n"
              f"- source: `{path}`\n"
              f"- model: {model}\n"
              f"- completion: {'complete' if complete else 'incomplete'}\n"
              f"- reviewed: {time.strftime('%Y-%m-%d %H:%M')}\n"
              f"- tokens: in {usage.get('prompt_tokens', 0)} / out {usage.get('completion_tokens', 0)}\n"
              f"- est cost: ${usage.get('cost', 0):.4f}\n\n---\n\n")
    fd, tmp = tempfile.mkstemp(prefix=".review-", suffix=".tmp", dir=rd)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(header + (review_md if isinstance(review_md, str) and review_md
                              else repr(review_md) if review_md is not None
                              else "_(empty review)_"))
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    #                        # atomic: never leave a half-written review

    with _manifest_lock(base):           # cross-process: re-read INSIDE the lock, then replace
        m = load_manifest(base)
        ap = path_key(path)
        entry = m.get(ap) or {"rel": rel, "modes": {}}
        entry.setdefault("modes", {})
        entry["rel"] = rel
        previous = entry["modes"].get(mode)
        record = {
            "sha": sha, "output": os.path.relpath(out, base), "complete": complete, "mode": mode,
            "reviewed_at": time.strftime("%Y-%m-%d %H:%M"),
            "tokens_in": usage.get("prompt_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0),
            "cost": usage.get("cost", 0),
        }
        if previous and previous.get("complete") is not False and not complete:
            # A failed retry cannot erase a paid completed review or its cache credit.
            entry.setdefault("attempts", []).append(record)
        else:
            if previous:
                entry.setdefault("attempts", []).append(previous)
            entry["modes"][mode] = record
        m[ap] = entry
        save_manifest(base, m)
    return out


def total_cost(manifest):
    tot = 0.0
    for e in manifest.values():
        for md in list((e.get("modes") or {}).values()) + e.get("attempts", []):
            tot += md.get("cost", 0) or 0
    return tot


def export_all(base):
    """Concatenate every saved review into one Markdown file. Returns (path, text)."""
    m = load_manifest(base)
    parts = [f"# Colibri Code Reviews - {os.path.basename(base.rstrip(os.sep))}",
             f"_exported {time.strftime('%Y-%m-%d %H:%M')} - {len(m)} file(s) - "
             f"${total_cost(m):.4f} total_\n", "## Contents\n"]
    for _, e in sorted(m.items(), key=lambda kv: kv[1].get("rel", "")):
        modes = e.get("modes") or {}
        done = ", ".join(sorted(mode for mode, md in modes.items()
                               if md.get("complete") is not False)) or "none"
        incomplete = sum(md.get("complete") is False
                         for md in list(modes.values()) + e.get("attempts", []))
        parts.append(f"- {e.get('rel', '?')}  (completed: {done}; incomplete attempts: {incomplete})")
    parts.append("\n---\n")
    for _, e in sorted(m.items(), key=lambda kv: kv[1].get("rel", "")):
        records = sorted((e.get("modes") or {}).items())
        records += [(md.get("mode", "previous attempt"), md) for md in e.get("attempts", [])]
        for mode, md in records:
            try:
                with open(output_path(base, md["output"]), encoding="utf-8") as f:
                    parts.append("\n" + f.read() + "\n\n---\n")
            except Exception:
                parts.append(f"\n*(missing output for {e.get('rel')} / {mode})*\n\n---\n")
    text = "\n".join(parts)
    out = os.path.join(reviews_dir(base), "_all_reviews.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    return out, text
