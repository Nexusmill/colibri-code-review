"""agent_error_rates.py - the error-introduction-rate ledger (owner order 2026-09-21).

Tabulates, PER AUTHORING AGENT (the git AUTHOR of the anchored commit - the identity
that wrote the code under review; the committer can differ after amend/rebase, so
attribution is by authorship), the defects adversarial reviews found in commits -
counting ONLY commit-anchored reviews (the review header sha line carries
"= commit <sha>"); on-demand bug hunts / feature-mode scan-ladder passes with no such
anchor are excluded by design.

Source of truth chain: each reviews_archive/<repo>/_manifest.json enumerates the
reviewed files and their outputs; the OUTPUT .md headers carry reviewer/sha/date/mode
and the commit anchor; the anchor resolves the authoring agent via the target repo's
git. Every enumeration anomaly reconciles in totals (missing outputs, unreadable
files, unmapped archive folders) - nothing drops silently.

Metric integrity: a review whose header has no parseable "new: N" line is counted as
a commit review and flagged no_count_line, but is EXCLUDED from the rate denominator
(the rate is new_findings / counted reviews) - it can deflate coverage, never a rate.

Outputs (both rewritten whole each run):
  docs/agent_error_rates.json - machine ledger
  docs/AGENT_ERROR_RATES.md   - human table + method notes

Usage:  python agent_error_rates.py [--repo-root-map k=v ...]   (map overridable)
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
DEFAULT_REPO_MAP = {
    "blink": r"C:\Users\User\source\repos\Blink",
    "caliper": r"E:\AI\Caliper",
    "fleet": r"C:\Users\User\source\repos\fleet",
    "nexusmill": r"C:\Users\User\source\repos\Nexusmill",
    "openaiastra": r"C:\Users\User\source\repos\OpenAIAstra",
}
GIT = r"C:\Program Files\Git\cmd\git.exe"
SHA_RE = re.compile(r"sha256:\s*([0-9a-f]{8,64})\s*\((.*?)\)")
# the documented anchor form only - a parenthetical that merely MENTIONS a commit is
# not a commit-triggered review (gate r2 finding 2)
COMMIT_RE = re.compile(r"=\s*commit\s+([0-9a-f]{7,40})")
NEW_RE = re.compile(r"(?<![\w])new:\s*(\d+)")
REVIEWER_RE = re.compile(r"reviewer:\s*(.+)")
DATE_RE = re.compile(r"date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
UNREADABLE = "UNREADABLE"


def git_author(repo_root, sha):
    """Author + FULL normalized sha (abbreviated archive anchors and 40-char note
    shas must collide as the same episode - gate r7 finding 1)."""
    try:
        r = subprocess.run([GIT, "-C", repo_root, "rev-parse", sha],
                           capture_output=True, text=True, timeout=15)
        full = r.stdout.strip() if r.returncode == 0 else sha
        r2 = subprocess.run([GIT, "-C", repo_root, "log", "-1",
                             "--format=%an|||%ae", full],
                            capture_output=True, text=True, timeout=15)
        if r2.returncode == 0 and "|||" in r2.stdout:
            name, email = r2.stdout.strip().split("|||", 1)
            return name, email, full
    except Exception:
        pass
    return None, None, sha


def parse_review(md_path):
    """Parse a review .md header.

    Returns: dict for a commit-anchored review; None for an on-demand scan (no
    '= commit' anchor); the sentinel UNREADABLE for a file that cannot be read
    (routed to the missing bucket, never counted as an on-demand scan)."""
    try:
        full = open(md_path, encoding="utf-8", errors="replace").read()
    except OSError:
        return UNREADABLE
    # anchor search: the header block only (through the first section heading); count
    # search: header + the Verdict section, where "new: N" canonically lives - a fixed
    # small window would misread long headers (gate r5 F2)
    cut = full.find("\n## ", 1)
    head = full[:cut] if cut > 0 else full
    m = SHA_RE.search(head)
    if not m:
        return None  # no sha line at all (gate r4 F4: distinct from sha-without-anchor)
    anchor = COMMIT_RE.search(m.group(2) or "")
    if not anchor:
        return None
    nm = None
    vm = full.find("## Verdict")
    if vm >= 0:
        nm = NEW_RE.search(full[vm:])   # canonical position; quoted diffs cannot preempt
    elif head is not full:
        nm = NEW_RE.search(head)
    return {
        "path": md_path,
        "commit": anchor.group(1),
        # None = no parseable "new: N" line - excluded from rate denominators, never
        # treated as zero-findings evidence (gate r3 finding 1)
        "new_findings": int(nm.group(1)) if nm else None,
        "reviewer": (REVIEWER_RE.search(head).group(1).strip()
                     if REVIEWER_RE.search(head) else "unknown"),
        "date": DATE_RE.search(head).group(1) if DATE_RE.search(head) else "",
    }


def git_gate_reviews(repo_root):
    """Commit-anchored GATE reviews for a repo, via the adversary notary notes.

    Every notarized commit's note (refs/notes/adversary) carries its review
    artifacts; a commit with MULTIPLE artifacts was a multi-round episode - only
    the EARLIEST artifact (the initial denial) counts (owner order 2026-09-21).
    Returns {commit: {"artifact": path, "when": ts}} for the initial artifact."""
    out, anomalies = {}, []
    try:
        lst = subprocess.run([GIT, "-C", repo_root, "notes", "--ref=adversary", "list"],
                             capture_output=True, text=True, timeout=60)
        if lst.returncode != 0:
            return out, anomalies
        for line in lst.stdout.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            commit = parts[1]
            try:
                show = subprocess.run([GIT, "-C", repo_root, "notes", "--ref=adversary",
                                       "show", commit], capture_output=True, text=True,
                                      timeout=15)
                note = json.loads(show.stdout) if show.returncode == 0 else None
            except Exception:
                note = None
            if not isinstance(note, dict):
                anomalies.append({"commit": commit[:12],
                                  "reason": "note unreadable or non-JSON"})
                continue
            arts = []
            if isinstance(note, dict):
                arts = [a for a in (note.get("artifacts") or [])
                        if isinstance(a, dict) and a.get("path")]
                if not arts:
                    for finfo in (note.get("files") or {}).values():
                        if isinstance(finfo, dict) and finfo.get("artifact"):
                            arts.append({"path": finfo["artifact"],
                                         "when": finfo.get("when", "")})
            # gate artifact paths are recorded absolute or repo-relative
            fixed = []
            for a in arts:
                p = a.get("path", "")
                if not os.path.isabs(p):
                    p = os.path.join(repo_root, p)
                fixed.append({"path": p, "when": a.get("when", "")})
            fixed = [a for a in fixed if os.path.isfile(a["path"])]
            if not fixed:
                anomalies.append({"commit": commit[:12],
                                  "reason": "note lists no on-disk review artifact"})
                continue
            fixed.sort(key=lambda a: a["when"] or "9999")  # empty never wins "earliest" (r8 F4)
            out[commit] = fixed[0]
    except Exception:
        pass
    return out, anomalies


GATE_FINDING_RE = re.compile(r"(?im)^(?:\s|\*)*(?:FINDING|Finding)\s*\d+"
                             r"|^(?:\s|\*)*\d+\.\s+(?:HIGH|MEDIUM|LOW)")


def parse_gate_artifact(path):
    """Finding count + reviewer from a gate review artifact; BLOCK with unnumbered
    prose findings counts as 1 (the denial itself), CLEAR counts 0."""
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    n = len(GATE_FINDING_RE.findall(text))
    if n == 0 and re.search(r"(?m)^VERDICT:\s*BLOCK", text):
        n = 1
    model = ""
    m = re.search(r"(?m)^model:\s*(\S+)", text)  # search, not match (r8 F5)
    if m:
        model = m.group(1)
    return {"new_findings": n, "reviewer": model}


def main(argv=None):
    ap = argparse.ArgumentParser(description="error-introduction-rate ledger (commit-anchored reviews only)")
    ap.add_argument("--repo-root-map", nargs="*", default=[],
                    help="archive-subfolder=repo-root overrides, e.g. blink=C:/repos/Blink")
    a = ap.parse_args(argv)
    repo_map = dict(DEFAULT_REPO_MAP)
    for kv in a.repo_root_map:
        k, _, v = kv.partition("=")
        repo_map[k] = v

    rows, skipped_ondemand, unresolved, unmapped, missing = [], 0, [], [], []
    for sub in sorted(os.listdir(ARCHIVE)):
        sub_dir = os.path.join(ARCHIVE, sub)
        if not os.path.isdir(sub_dir):
            continue
        if sub not in repo_map:
            unmapped.append(sub)
            continue
        # enumerate via the repo's _manifest.json (the index); a malformed ROW is
        # quarantined per-row (gate r3 finding 2), never allowed to truncate the
        # enumeration silently; only a wholly unparseable manifest falls back to *.md
        outputs = []
        man = os.path.join(sub_dir, "_manifest.json")
        man_ok = True
        if os.path.isfile(man):
            try:
                data = json.load(open(man, encoding="utf-8"))
                if not isinstance(data, dict):
                    missing.append({"repo": sub, "reason":
                                    "manifest valid JSON but not an object - disk glob substituted"})
                    data, man_ok = {}, False
            except Exception:
                data, man_ok = {}, False
                missing.append({"repo": sub, "reason":
                                "manifest unparseable - disk glob substituted"})
            for key, entry in (data.items() if isinstance(data, dict) else []):
                if key.startswith("_"):
                    continue  # _doc and kin are manifest metadata, not rows (gate r5 F1)
                if not isinstance(entry, dict):
                    missing.append({"repo": sub, "manifest_key": str(key),
                                    "reason": "entry not an object"})
                    continue
                modes = entry.get("modes")
                if not isinstance(modes, dict) or not modes:
                    missing.append({"repo": sub, "manifest_key": str(key),
                                    "reason": "no modes table"})
                    continue
                try:
                    for mode_rec in modes.values():
                        out = mode_rec.get("output", "") if isinstance(mode_rec, dict) else ""
                        if out:
                            outputs.append(os.path.basename(out))
                        else:
                            missing.append({"repo": sub, "manifest_key": str(key),
                                            "reason": "mode record without output"})
                except Exception:
                    missing.append({"repo": sub, "manifest_key": str(key)})
        if not man_ok or not outputs:
            outputs = [f for f in os.listdir(sub_dir)
                       if f.endswith(".md") and not f.startswith("_")]
        else:
            # reviews on disk that a parseable manifest failed to index must not be
            # invisible (gate r5 F3): union them in and record the reconciliation
            disk = {f for f in os.listdir(sub_dir)
                    if f.endswith(".md") and not f.startswith("_")}
            unindexed = len(disk - set(outputs))
            if unindexed:
                missing.append({"repo": sub, "reason": "present on disk, unindexed by manifest",
                                "count": unindexed})
                outputs = list(set(outputs) | disk)
        for name in sorted(set(outputs)):
            if "__SYNTHESIS__" in name or not name.endswith(".md"):
                continue  # synthesis files and non-review artifacts are not reviews
            p = os.path.join(sub_dir, name)
            if not os.path.isfile(p):
                missing.append({"repo": sub, "file": name})
                continue
            parsed = parse_review(p)
            if parsed == UNREADABLE:
                missing.append({"repo": sub, "file": name, "unreadable": True})
                continue
            if parsed is None:
                skipped_ondemand += 1
                continue
            author, email, full = git_author(repo_map[sub], parsed["commit"])
            if author is None:
                unresolved.append({"repo": sub, "commit": parsed["commit"], "file": name})
                continue
            parsed.update({"repo": sub, "author": author, "email": email,
                           "commit": full, "source": "archive"})
            rows.append(parsed)

        # SOURCE B: the commit-anchored GATE reviews, via the target repo's adversary
        # notary notes - every notarized commit, initial (earliest) artifact only.
        # NO skip on archive-covered commits: by_episode's gate-notes-wins rule below
        # performs the cross-source reconciliation (the gate artifact IS the initial
        # denial; archive re-reviews are remediation rounds) - gate r8 finding 2.
        gate_eps, gate_anoms = git_gate_reviews(repo_map[sub])
        missing.extend({"repo": sub, **a} for a in gate_anoms)
        for commit, art in gate_eps.items():
            ga = parse_gate_artifact(art["path"])
            if ga is None:
                missing.append({"repo": sub, "file": art["path"], "unreadable": True})
                continue
            author, email, full = git_author(repo_map[sub], commit)
            if author is None:
                unresolved.append({"repo": sub, "commit": commit,
                                   "file": os.path.basename(art["path"])})
                continue
            rows.append({"path": art["path"], "commit": full,
                         "new_findings": ga["new_findings"], "reviewer": ga["reviewer"],
                         "date": art["when"] or "", "repo": sub, "author": author,
                         "email": email, "source": "gate-notes"})

    # ONE row per (repo, FULL-sha commit) episode - the INITIAL denial, never the
    # remediation rounds (owner order 2026-09-21). When both sources cover an
    # episode the GATE-NOTES row wins by construction: its earliest artifact IS the
    # initial denial with a sub-day timestamp, while archive dates are day-granular
    # and cannot order same-day rounds (gate r7 finding 2).
    by_episode = {}
    for r in rows:
        k = (r["repo"], r["commit"])
        cur = by_episode.get(k)
        if cur is None:
            by_episode[k] = r
        elif r["source"] == "gate-notes" and cur["source"] != "gate-notes":
            by_episode[k] = r
        elif r["source"] == cur["source"] and (r["date"] or "9999") < (cur["date"] or "9999"):
            by_episode[k] = r
    rows = list(by_episode.values())

    agents = {}
    for r in rows:
        g = agents.setdefault(r["author"], {"commit_reviews": 0, "counted": 0,
                                            "new_findings": 0, "reviews_with_findings": 0,
                                            "no_count_line": 0, "repos": set()})
        g["commit_reviews"] += 1
        if r["new_findings"] is None:
            g["no_count_line"] += 1
        else:
            g["counted"] += 1
            g["new_findings"] += int(r["new_findings"])
            if r["new_findings"]:
                g["reviews_with_findings"] += 1
        g["repos"].add(r["repo"])
    ledger = {
        "_doc": ("error-introduction rate per authoring agent - COMMIT-ANCHORED adversarial "
                 "reviews only (on-demand bug hunts / scan-ladder passes excluded); generated "
                 "by agent_error_rates.py, owner order 2026-09-21"),
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "method": ("TWO sources, reconciled semantics: (A) archive .md reviews whose sha "
                   "line carries '= commit <sha>' (on disk, manifest-indexed or not); "
                   "(B) commit-anchored GATE reviews via each target repo's adversary "
                   "notary notes. ONE row per (repo, commit) episode - the INITIAL "
                   "denial (earliest artifact/review), never the remediation rounds. "
                   "The anchor resolves the git AUTHOR; rate = new findings / counted "
                   "reviews, counted excluding no-parseable-count archive reviews "
                   "(flagged no_count_line; they can deflate coverage, never a rate)"),
        "agents": [],
        "totals": {"commit_reviews": len(rows), "on_demand_excluded": skipped_ondemand,
                   "unresolved_commits": len(unresolved), "unmapped_archives": unmapped,
                   "missing_or_unreadable": sum(1 for m in missing if "file" in m),
                   "recovered_unindexed": sum(m.get("count", 0) for m in missing
                                              if "unindexed" in str(m.get("reason", ""))),
                   "enumeration_anomalies": len(missing)},
        "unresolved": unresolved, "missing": missing,
    }
    for name, g in sorted(agents.items(), key=lambda kv: -kv[1]["new_findings"]):
        ledger["agents"].append({
            "author": name, "email": next(r["email"] for r in rows if r["author"] == name),
            "commit_reviews": g["commit_reviews"], "counted": g["counted"],
            "new_findings": g["new_findings"],
            "reviews_with_findings": g["reviews_with_findings"],
            "no_count_line": g["no_count_line"],
            "error_introduction_rate": (round(g["new_findings"] / g["counted"], 3)
                                        if g["counted"] else None),
            "repos": sorted(g["repos"]),
        })

    json_path = os.path.join(HERE, "docs", "agent_error_rates.json")
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ledger, f, indent=1, ensure_ascii=False)
        f.write("\n")

    md = ["# AGENT_ERROR_RATES — error-introduction rate per authoring agent",
          "",
          "> Commit-anchored adversarial reviews ONLY, TWO sources under reconciled "
          "semantics (owner orders 2026-09-21): (A) archive reviews whose sha line "
          "carries `= commit <sha>` — on disk, manifest-indexed or not; (B) GATE "
          "reviews recovered from each target repo's adversary notary notes. ONE row "
          "per (repo, commit) episode — the INITIAL denial, never the remediation "
          "rounds. On-demand bug hunts and scan-ladder passes are excluded. "
          "Attribution = git AUTHOR. `rate` divides by **counted** reviews; reviews "
          "with no parseable `new: N` are flagged and excluded from the denominator — "
          "they can deflate coverage, never a rate.",
          "",
          "| agent | commit reviews | counted | new findings | reviews w/ findings | no count line | findings/counted | repos |",
          "|---|---|---|---|---|---|---|---|"]
    for ag in ledger["agents"]:
        rate = "%.2f" % ag["error_introduction_rate"] if ag["error_introduction_rate"] is not None else "n/a"
        md.append("| %s | %d | %d | %d | %d | %d | %s | %s |" % (
            ag["author"], ag["commit_reviews"], ag["counted"], ag["new_findings"],
            ag["reviews_with_findings"], ag["no_count_line"], rate,
            ", ".join(ag["repos"])))
    t = ledger["totals"]
    md += ["", "Totals: %d commit-anchored episodes (%d counted), %d on-demand scans "
           "excluded, %d commits unresolved, %d outputs missing/unreadable, %d reviews "
           "RECOVERED from disk beyond the manifest index, %d enumeration anomalies "
           "(all itemized in the JSON), %d archive folders unmapped. Same-source "
           "archive ties break by filename order (deterministic residual)."
           % (t["commit_reviews"],
              sum(x["counted"] for x in ledger["agents"]),
              t["on_demand_excluded"], t["unresolved_commits"],
              t["missing_or_unreadable"], t["recovered_unindexed"],
              t["enumeration_anomalies"], len(t.get("unmapped_archives", [])))]
    with open(os.path.join(HERE, "docs", "AGENT_ERROR_RATES.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print("episodes: %d | on-demand excluded: %d | unresolved: %d | missing/unreadable: %d | recovered-unindexed: %d | anomalies: %d | agents: %d"
          % (t["commit_reviews"], t["on_demand_excluded"], t["unresolved_commits"],
             t["missing_or_unreadable"], t["recovered_unindexed"],
             t["enumeration_anomalies"], len(ledger["agents"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
