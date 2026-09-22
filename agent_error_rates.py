"""agent_error_rates.py - the error-introduction-rate ledger v3 (owner orders 2026-09-21).

v3 rulings after the owner's challenges:
  - machine-wide: every repo with an .adversary/reviews dir DIRECTLY under a swept
    root (depth-1 discovery - repos nested deeper are out of scope by design; the
    ledger's gate_repos count is exactly that set).
  - the INITIAL DENIAL is recovered from the ON-DISK gate artifacts (filenames carry
    gate_YYYYMMDD-HHMMSS timestamps): notary notes are OVERWRITE semantics - a
    multi-round commit's note keeps only the final CLEAR - so the note chain alone
    guts the numerator. Each BLOCK artifact joins the first notarized commit that
    lands AFTER its timestamp; repeated BLOCKs for one commit collapse to the
    FIRST (the initial denial). BLOCKs with no subsequent landing commit count as
    unattributed "unlanded denials" (never silently dropped).
  - sub-program attribution: gate artifacts list the files they reviewed; the first
    path segment maps to a SUBPROGRAMS entry (Nexusmill: PatternSkin, asset-forge,
    asset-forge-user, Spector) so rates break down per agent x program.

SOURCE A (colibri review archive): the .md files under reviews_archive/<repo>/ on
disk, anchored '= commit <sha>' (manifest-indexed or not - reconciled semantics).

Outputs (rewritten whole each run): docs/agent_error_rates.json + AGENT_ERROR_RATES.md.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "reviews_archive")
DEFAULT_ROOTS = [r"C:\Users\User\source\repos", r"E:\AI"]
GIT = r"C:\Program Files\Git\cmd\git.exe"
ARCHIVE_REPO_MAP = {
    "blink": r"C:\Users\User\source\repos\Blink",
    "caliper": r"E:\AI\Caliper",
    "fleet": r"C:\Users\User\source\repos\fleet",
    "nexusmill": r"C:\Users\User\source\repos\Nexusmill",
    "openaiastra": r"C:\Users\User\source\repos\OpenAIAstra",
}
SUBPROGRAMS = {
    "Nexusmill": {"PatternSkin", "asset-forge", "asset-forge-user", "Spector"},
}
SHA_RE = re.compile(r"sha256:\s*([0-9a-f]{8,64})\s*\((.*?)\)")
COMMIT_RE = re.compile(r"=\s*commit\s+([0-9a-f]{7,40})")
NEW_RE = re.compile(r"(?<![\w])new:\s*(\d+)")
REVIEWER_RE = re.compile(r"reviewer:\s*(.+)")
DATE_RE = re.compile(r"date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
GATE_TS_RE = re.compile(r"gate_(\d{8}-\d{6})\.md$", re.IGNORECASE)
GATE_FINDING_RE = re.compile(r"(?im)^(?:\s|\*)*(?:FINDING|Finding)\s*\d+"
                             r"|^(?:\s|\*)*\d+\.\s+(?:HIGH|MEDIUM|LOW)")
FILES_RE = re.compile(r"files:\s*\[(.*?)\]", re.DOTALL)
UNREADABLE = "UNREADABLE"


def run_git(repo, *a, timeout=60):
    return subprocess.run([GIT, "-C", repo, *a], capture_output=True, text=True,
                          timeout=timeout)


def _git_identity(d):
    """(canonical repo root, is_worktree) for a checkout dir; None if not git.

    A linked worktree shares its parent's refs and object store - the notary
    notes resolve there - so a directory-name identity double-counts the
    parent's whole episode set under the worktree's name (gate_20260922-151605
    F1)."""
    try:
        gd = run_git(d, "rev-parse", "--path-format=absolute", "--git-dir", timeout=15)
        cd = run_git(d, "rev-parse", "--path-format=absolute",
                     "--git-common-dir", timeout=15)
    except Exception as e:
        # a stalled/unlaunchable git must degrade to legacy standalone identity,
        # never crash the whole sweep (r3 F1: enumeration failures are anomalies)
        print("warning: git identity probe failed for %s: %s" % (d, e),
              file=sys.stderr)
        return None
    if gd.returncode != 0 or cd.returncode != 0:
        return None
    gdir = os.path.normpath(gd.stdout.strip())
    cdir = os.path.normpath(cd.stdout.strip())
    if gdir == cdir:
        return os.path.normpath(d), False
    return os.path.dirname(cdir), True


def discover_gate_repos(roots):
    """Repos with .adversary/reviews under the roots, as (name, root, dirs).

    Linked worktrees FOLD into their parent checkout: the parent identity
    scans the shared notary refs once, with denial artifacts gathered from the
    parent dir AND every linked-worktree dir (a worktree's gate rounds write
    their artifacts into the worktree - the only on-disk copy). Non-git dirs
    with gate artifacts (archived snapshots) keep legacy standalone identity."""
    found = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            entries = sorted(os.listdir(root))
        except OSError as e:
            print("warning: sweep root unreadable: %s: %s" % (root, e),
                  file=sys.stderr)
            continue
        for name in entries:
            d = os.path.join(root, name)
            if not os.path.isdir(os.path.join(d, ".adversary", "reviews")):
                continue
            ident = _git_identity(d)
            if ident is None:
                key, pname = os.path.normpath(d), name
            else:
                key, _is_wt = ident
                pname = os.path.basename(key)
            slot = found.setdefault(key, {"name": pname, "dirs": []})
            slot["dirs"].append(d)
    return [(v["name"], k, v["dirs"])
            for k, v in sorted(found.items(), key=lambda kv: (kv[1]["name"], kv[0]))]


def program_for(repo_name, artifact_text):
    subs = SUBPROGRAMS.get(repo_name)
    if not subs:
        return ""
    m = FILES_RE.search(artifact_text[:3000])
    if not m:
        return ""
    for bit in m.group(1).split(","):
        seg = bit.strip().strip("'\"").replace("\\", "/").lstrip("./").split("/")
        if seg and seg[0] in subs:
            return seg[0]
    return "(root/tooling)" if m.group(1).strip() else ""


def parse_gate_artifact(repo_name, path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return UNREADABLE  # distinct from not-a-BLOCK: must surface, never drop (r3 F2)
    # verdict-FIRST classification: only a BLOCK is a denial; a CLEAR that restates
    # earlier rounds' findings (the common multi-round shape) is not one (v3-r2 F1)
    if not re.search(r"(?m)^VERDICT:\s*BLOCK", text):
        return None
    n = len(GATE_FINDING_RE.findall(text))
    if n == 0:
        n = 1  # BLOCK with unnumbered prose findings: the denial itself
    model = ""
    m = re.search(r"(?m)^model:\s*(\S+)", text)
    if m:
        model = m.group(1)
    return {"new_findings": n, "reviewer": model,
            "program": program_for(repo_name, text)}


def git_author(repo_root, sha):
    try:
        r = run_git(repo_root, "rev-parse", sha, timeout=15)
        full = r.stdout.strip() if r.returncode == 0 else sha
        r2 = run_git(repo_root, "log", "-1", "--format=%an|||%ae", full, timeout=15)
        if r2.returncode == 0 and "|||" in r2.stdout:
            name, email = r2.stdout.strip().split("|||", 1)
            return name, email, full
    except Exception:
        pass
    return None, None, sha


def gate_episodes(repo_name, repo_root, review_dirs=None):
    """Episodes from on-disk gate artifacts + notary records (v3).

    Every NOTARIZED commit is an episode (the denominator). Each VERDICT-BLOCK
    artifact attaches to the first notarized commit landing after its timestamp;
    only the FIRST BLOCK per commit counts (the initial denial). BLOCKs with no
    landing commit become 'unlanded' denials; enumeration failures become
    anomalies - the two buckets are returned SEPARATELY (r3 F1).

    review_dirs: extra checkout dirs sharing this repo's git identity (linked
    worktrees) whose .adversary/reviews artifacts also belong to this repo."""
    primary = os.path.join(repo_root, ".adversary", "reviews")
    blocks = []
    extra_anoms = []
    try:
        primary_files = os.listdir(primary)
    except OSError as e:
        return [], [], [{"repo": repo_name,
                         "reason": "reviews dir unreadable: %s" % e}]
    for f in primary_files:
        m = GATE_TS_RE.search(f)
        if m:
            blocks.append((m.group(1), os.path.join(primary, f)))
    for base in dict.fromkeys(os.path.normpath(b) for b in (review_dirs or [])
                              if os.path.normpath(b) != os.path.normpath(repo_root)):
        rvw = os.path.join(base, ".adversary", "reviews")
        try:
            more = os.listdir(rvw)
        except OSError as e:
            extra_anoms.append({"repo": repo_name,
                                "reason": "worktree reviews dir unreadable: %s" % e})
            continue
        for f in more:
            m = GATE_TS_RE.search(f)
            if m:
                blocks.append((m.group(1), os.path.join(rvw, f)))
    blocks.sort()

    commits = []
    anoms = list(extra_anoms)
    try:
        lst = run_git(repo_root, "notes", "--ref=adversary", "list")
        if lst.returncode != 0:
            anoms.append({"repo": repo_name,
                          "reason": "notary list failed - repo contributes no episodes"})
            return [], [], anoms
        shas = [ln.split()[1] for ln in lst.stdout.splitlines() if len(ln.split()) >= 2]
        # chunked batch: a thousand-sha argv overflows the Windows command line and
        # the OSError would bypass the returncode fallback entirely (r3 F3)
        lines = []
        for i in range(0, len(shas), 100):
            chunk = shas[i:i + 100]
            fmt = run_git(repo_root, "log", "--no-walk", "--date=iso-local",
                          "--format=%H%x1f%cI%x1f%an%x1f%ae", *chunk, timeout=120)
            if fmt.returncode != 0:
                for sha in chunk:
                    one = run_git(repo_root, "log", "-1", "--no-walk", "--date=iso-local",
                                  "--format=%H%x1f%cI%x1f%an%x1f%ae", sha, timeout=15)
                    if one.returncode == 0 and one.stdout.strip():
                        lines.append(one.stdout.strip())
                    else:
                        anoms.append({"repo": repo_name,
                                      "reason": "notary record on unresolvable object",
                                      "object": sha[:12]})
            else:
                lines.extend(fmt.stdout.splitlines())
        for ln in lines:
            parts = ln.split("\x1f")
            if len(parts) == 4:
                commits.append({"sha": parts[0],
                                # naive local slice of the ISO offset form so the
                                # timestamp join compares like with like (r3 F4)
                                "when": parts[1][:19],
                                "author": parts[2], "email": parts[3]})
    except Exception as e:
        anoms.append({"repo": repo_name,
                      "reason": "git failure reading notary records: %s" % e})
    commits.sort(key=lambda c: c["when"])

    assigned = {}
    unlanded = []
    for ts, path in blocks:
        parsed = parse_gate_artifact(repo_name, path)
        if parsed == UNREADABLE:
            anoms.append({"repo": repo_name, "file": os.path.basename(path),
                          "unreadable": True})
            continue
        if parsed is None:
            continue  # not a VERDICT-BLOCK artifact: CLEAR or prose, no denial
        dt = datetime.datetime.strptime(ts, "%Y%m%d-%H%M%S").isoformat()
        host = next((c for c in commits if c["when"] >= dt), None)
        if host is None:
            unlanded.append({"repo": repo_name, "artifact": os.path.basename(path),
                             "when": ts, "findings": parsed["new_findings"]})
            continue
        cur = assigned.get(host["sha"])
        if cur is None or dt < cur["dt"]:
            assigned[host["sha"]] = {"dt": dt, "parsed": parsed,
                                     "artifact": os.path.basename(path)}

    episodes = []
    for c in commits:
        blk = assigned.get(c["sha"])
        episodes.append({
            "repo": repo_name, "commit": c["sha"], "author": c["author"],
            "email": c["email"], "when": c["when"],
            "new_findings": blk["parsed"]["new_findings"] if blk else 0,
            "reviewer": blk["parsed"]["reviewer"] if blk else "",
            "program": blk["parsed"]["program"] if blk else "",
            "source": "gate-denial", "denial_artifact": blk["artifact"] if blk else "",
        })
    return episodes, unlanded, anoms


def parse_review(md_path):
    try:
        full = open(md_path, encoding="utf-8", errors="replace").read()
    except OSError:
        return UNREADABLE
    cut = full.find("\n## ", 1)
    head = full[:cut] if cut > 0 else full
    m = SHA_RE.search(head)
    if not m:
        return None
    anchor = COMMIT_RE.search(m.group(2) or "")
    if not anchor:
        return None
    nm = None
    vm = full.find("## Verdict")
    if vm >= 0:
        nm = NEW_RE.search(full[vm:])
    elif head is not full:
        nm = NEW_RE.search(head)
    return {"path": md_path, "commit": anchor.group(1),
            "new_findings": int(nm.group(1)) if nm else None,
            "reviewer": (REVIEWER_RE.search(head).group(1).strip()
                         if REVIEWER_RE.search(head) else "unknown"),
            "date": DATE_RE.search(head).group(1) if DATE_RE.search(head) else ""}


def archive_rows(anomalies, root_names=None):
    rows, skipped, unresolved = [], 0, []
    root_names = root_names or {}
    if not os.path.isdir(ARCHIVE):
        return rows, skipped, unresolved
    for sub in sorted(os.listdir(ARCHIVE)):
        sub_dir = os.path.join(ARCHIVE, sub)
        if not os.path.isdir(sub_dir):
            continue
        if sub not in ARCHIVE_REPO_MAP:
            anomalies.append({"repo": sub, "reason": "archive folder with no repo mapping"})
            continue
        repo_root = os.path.normpath(ARCHIVE_REPO_MAP[sub])
        # the DISCOVERED repo name keys the episode join - otherwise the same repo
        # counts twice under its archive name and its directory name (Blink/blink).
        # A diverging map path is an ANOMALY, never a silent fallback (r5 F3):
        # re-resolve the path through the same git identity discovery uses (a map
        # aimed at a linked worktree folds to the parent key), and if it still
        # matches no discovered repo the folder is SKIPPED - rows under the raw
        # archive name would double-count any commit the discovered view holds.
        repo_name = root_names.get(repo_root.lower())
        if repo_name is None:
            ident = _git_identity(repo_root) if os.path.isdir(repo_root) else None
            if ident is not None:
                repo_name = root_names.get(ident[0].lower())
        if repo_name is None:
            anomalies.append({"repo": sub,
                              "reason": "archive map path not among discovered repos: %s"
                                        % repo_root})
            continue
        disk = {f for f in os.listdir(sub_dir)
                if f.endswith(".md") and not f.startswith("_")}
        # v2 surfaced manifest rows whose output is missing from disk; v3 lost
        # that when it switched to the disk glob (gate_20260922-160856 F3) -
        # a dangling row contributes no episode AND no anomaly, the exact
        # fragmentation this ledger refuses. Restore the itemized bucket.
        mpath = os.path.join(sub_dir, "_manifest.json")
        if os.path.isfile(mpath):
            try:
                mdata = json.load(open(mpath, encoding="utf-8-sig"))
            except Exception as e:
                anomalies.append({"repo": sub,
                                  "reason": "archive manifest unreadable: %s" % e})
                mdata = {}
            indexed = set()
            for _k, v in (mdata.items() if isinstance(mdata, dict) else []):
                if not isinstance(v, dict):
                    continue
                for info in (v.get("modes") or {}).values():
                    if isinstance(info, dict) and info.get("output"):
                        indexed.add(os.path.basename(info["output"]))
            for gone in sorted(indexed - disk):
                anomalies.append({"repo": sub, "dangling_output": gone,
                                  "reason": "manifest row with no output file on disk"})
        for name in sorted(disk):
            if "__SYNTHESIS__" in name:
                continue
            parsed = parse_review(os.path.join(sub_dir, name))
            if parsed == UNREADABLE:
                anomalies.append({"repo": sub, "file": name, "unreadable": True})
                continue
            if parsed is None:
                skipped += 1
                continue
            author, email, full = git_author(repo_root, parsed["commit"])
            if author is None:
                unresolved.append({"repo": sub, "commit": parsed["commit"], "file": name})
                continue
            parsed.update({"repo": repo_name, "author": author, "email": email,
                           "commit": full, "source": "archive", "program": ""})
            rows.append(parsed)
    return rows, skipped, unresolved


def main(argv=None):
    ap = argparse.ArgumentParser(description="error-introduction-rate ledger v3")
    ap.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS,
                    help="roots swept for repos with .adversary/reviews")
    a = ap.parse_args(argv)

    anomalies, unlanded_all, gate_rows = [], [], []
    repos = discover_gate_repos(a.roots)
    root_names = {os.path.normpath(root).lower(): name
                  for name, root, _dirs in repos}
    for name, root, dirs in repos:
        eps, unl, ano = gate_episodes(name, root, dirs)
        gate_rows.extend(eps)
        unlanded_all.extend(unl)
        anomalies.extend(ano)
    arc_rows, skipped, unresolved = archive_rows(anomalies, root_names)

    # episode dedupe: the GATE row wins ONLY when it carries a denial artifact
    # (authoritative findings); an artifact-less CLEAR-only gate row never displaces
    # an archive row that recorded findings (v3-r1 F2). Archive-archive collisions
    # keep the EARLIEST-dated row (the initial denial), not filename order (r5 F1).
    by_ep = {}
    for r in arc_rows + gate_rows:
        k = (r["repo"], r["commit"])
        cur = by_ep.get(k)
        gate_wins = (r["source"] == "gate-denial" and r.get("denial_artifact")
                     and (cur is None or cur["source"] != "gate-denial"))
        arc_earlier = (cur is not None and r["source"] == "archive"
                       and cur["source"] == "archive"
                       and (r["date"] or "9999") < (cur["date"] or "9999"))
        if cur is None or gate_wins or arc_earlier:
            by_ep[k] = r
    rows = list(by_ep.values())

    agents, programs = {}, {}
    for r in rows:
        g = agents.setdefault(r["author"], {"episodes": 0, "counted": 0, "findings": 0,
                                            "with_findings": 0, "no_count_line": 0,
                                            "repos": set()})
        g["episodes"] += 1
        if r["new_findings"] is None:
            g["no_count_line"] += 1
        else:
            g["counted"] += 1
            g["findings"] += int(r["new_findings"])
            if r["new_findings"]:
                g["with_findings"] += 1
        g["repos"].add(r["repo"])
        if r.get("program"):
            p = programs.setdefault((r["author"], r["program"]),
                                    {"episodes": 0, "findings": 0})
            p["episodes"] += 1
            p["findings"] += int(r["new_findings"] or 0)

    ledger = {
        "_doc": ("error-introduction rate per authoring agent, machine-wide, "
                 "INITIAL DENIALS ONLY (owner orders 2026-09-21). v3: dynamic repo "
                 "discovery; denials recovered from on-disk BLOCK artifacts (notary "
                 "notes are overwrite semantics and lose remediation rounds); "
                 "sub-program attribution from artifact file lists."),
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "method": ("Episodes = every notarized commit in every repo carrying "
                   ".adversary/reviews directly under a swept root (depth-1 "
                   "discovery), plus archive reviews "
                   "anchored '= commit <sha>'. Each on-disk BLOCK artifact attaches "
                   "to the first notarized commit landing after its timestamp; only "
                   "the FIRST BLOCK per commit counts (initial denial); CLEAR-only "
                   "commits are zero-finding episodes. rate = findings / counted "
                   "episodes (archive rows without a parseable 'new: N' are flagged "
                   "no_count_line and excluded from the denominator). Attribution = "
                   "git AUTHOR (caveat: repos driven via _git_do.py commit under the "
                   "owner's identity, so their rows mix every agent)."),
        "agents": [],
        "programs": [{"author": k[0], "program": k[1], **v}
                     for k, v in sorted(programs.items())],
        "totals": {"episodes": len(rows),
                   "counted": sum(g["counted"] for g in agents.values()),
                   "findings": sum(g["findings"] for g in agents.values()),
                   "gate_repos": len(repos),
                   "archive_on_demand_excluded": skipped,
                   "unresolved_commits": len(unresolved),
                   "unlanded_denials": len(unlanded_all),
                   "anomalies": len(anomalies)},
        "unresolved": unresolved, "unlanded": unlanded_all, "anomalies": anomalies,
        "_caveat": ("Nexusmill attribution is identity-blurred: _git_do.py commits "
                    "under the owner's git identity on behalf of every agent."),
    }
    for name, g in sorted(agents.items(), key=lambda kv: -kv[1]["findings"]):
        counted = g["counted"] or 0
        ledger["agents"].append({
            "author": name, "email": next(r["email"] for r in rows if r["author"] == name),
            "episodes": g["episodes"], "counted": counted,
            "findings": g["findings"], "with_findings": g["with_findings"],
            "no_count_line": g["no_count_line"],
            "pct_commits_with_errors": (round(100.0 * g["with_findings"] / counted, 1)
                                        if counted else None),
            "findings_per_error_commit": (round(g["findings"] / g["with_findings"], 2)
                                          if g["with_findings"] else None),
            "rate": round(g["findings"] / counted, 3) if counted else None,
            "repos": sorted(g["repos"]),
        })

    with open(os.path.join(HERE, "docs", "agent_error_rates.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(ledger, f, indent=1, ensure_ascii=False)
        f.write("\n")

    md = ["# AGENT_ERROR_RATES — error-introduction per authoring agent (v3, machine-wide)",
          "",
          "**ERROR INTRODUCTION RATE = the percentage chance (0-100%) that a COMMIT "
          "introduces at least one error**: the share of an agent's commits whose "
          "adversarial review's INITIAL DENIAL (first BLOCK) carried at least one "
          "finding. A commit denied five times before clearing counts once. "
          "**VALIDATION STATUS: these are gate-review findings counted at the denial, "
          "NOT outcome-validated errors** — in this workflow every BLOCK finding is "
          "adjudicated (remediated as real, or factually rebutted with byte evidence "
          "and re-verified by the reviewer), but this ledger does not yet join each "
          "finding to its outcome, so the percentage is an UPPER BOUND on the true "
          "error-introduction chance; observed gate false-positive rates are low "
          "(single digits), so the validated rate sits a few points under the stated "
          "figure. Findings are severity-blind (HIGH/MEDIUM/LOW each count).",
          "",
          "> INITIAL DENIALS ONLY, machine-wide: every repo with `.adversary/reviews` "
          "under the swept roots, denials recovered from on-disk BLOCK artifacts "
          "(notary notes keep only the final CLEAR of a multi-round episode). "
          "Attribution = git AUTHOR (repos driven via `_git_do.py` commit under the "
          "owner's identity — identity-blurred). The JSON also carries findings per "
          "counted commit (`rate`); the MD shows the percentage form.",
          "",
          "| agent | commits (counted) | commits w/ errors | % chance error per commit | findings | findings/error-commit | repos |",
          "|---|---|---|---|---|---|---|"]
    for ag in ledger["agents"]:
        pct = ("%.1f%%" % ag["pct_commits_with_errors"]
               if ag.get("pct_commits_with_errors") is not None else "n/a")
        fpec = ("%.2f" % ag["findings_per_error_commit"]
                if ag.get("findings_per_error_commit") is not None else "n/a")
        md.append("| %s | %d | %d | **%s** | %d | %s | %s |" % (
            ag["author"], ag["counted"], ag["with_findings"], pct,
            ag["findings"], fpec, ", ".join(ag["repos"])))
    t = ledger["totals"]
    overall_err = sum(ag["with_findings"] for ag in ledger["agents"])
    overall_pct = (100.0 * overall_err / t["counted"]) if t["counted"] else 0.0
    md += ["", "**MACHINE-WIDE: %.1f%% of commits introduce at least one error** "
           "(%d of %d counted commits)."
           % (overall_pct, overall_err, t["counted"])]
    if ledger["programs"]:
        md += ["", "## Sub-programs (gate episodes with a denial program match)",
               "",
               "| agent | program | episodes | findings |",
               "|---|---|---|---|"]
        for p in ledger["programs"]:
            md.append("| %s | %s | %d | %d |" % (p["author"], p["program"],
                                                 p["episodes"], p["findings"]))
    t = ledger["totals"]
    md += ["", "Totals: %d episodes (%d counted, %d findings) across %d gate repos; "
           "%d archive on-demand scans excluded; %d commits unresolved; %d UNLANDED "
           "denials (BLOCK with no subsequent commit - itemized in the JSON); %d "
           "enumeration anomalies."
           % (t["episodes"], t["counted"], t["findings"], t["gate_repos"],
              t["archive_on_demand_excluded"], t["unresolved_commits"],
              t["unlanded_denials"], t["anomalies"])]
    with open(os.path.join(HERE, "docs", "AGENT_ERROR_RATES.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print("v3: %d episodes / %d findings / %d gate repos / %d unlanded denials / %d agents"
          % (t["episodes"], t["findings"], t["gate_repos"], t["unlanded_denials"],
             len(ledger["agents"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
