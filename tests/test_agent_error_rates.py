"""True-rate STEP 2 (owner orders 2026-09-21 + 2026-09-23): the ledger joins
gate adjudications to episodes, computes VALIDATED error rates (not denial-time
upper bounds), and breaks results down by CALLING AGENT (the gate's new
caller field) alongside git author. Pure-function rows, no network."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import agent_error_rates as aer  # noqa: E402


def _write(tmp, name, text):
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def test_gate_ts_regex_accepts_collision_suffix():
    # the gate emits -<n> suffixed artifacts on same-second collisions (Tools
    # c2a89df); the ledger regex must match them or those denials vanish
    assert aer.GATE_TS_RE.search("gate_20260923-163305-2.md")
    assert aer.GATE_TS_RE.search("gate_20260923-163305.md")
    assert not aer.GATE_TS_RE.search("gate_x.md")


def test_parse_gate_artifact_reads_caller():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "gate_20260923-120000.md",
                   "model: m | provider: p | usage: 1 | scrubbed: 0 | "
                   "files: ['a.py'] | caller: zcode\n\n"
                   "FINDING 1 HIGH a.py:1 x\n\nVERDICT: BLOCK\n")
        row = aer.parse_gate_artifact("r", p)
        assert row and row.get("caller") == "zcode"


def test_parse_gate_artifact_old_header_has_no_caller():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "gate_20260923-120000.md",
                   "model: m | provider: p | usage: 1 | scrubbed: 0 | "
                   "files: ['a.py']\n\nFINDING 1 HIGH a.py:1 x\n\nVERDICT: BLOCK\n")
        row = aer.parse_gate_artifact("r", p)
        assert row and row.get("caller") in (None, "")


def test_join_adjudications_by_commit():
    eps = [{"repo": "r", "commit": "c1", "author": "A", "new_findings": 2,
            "caller": "zcode"},
           {"repo": "r", "commit": "c2", "author": "A", "new_findings": 0,
            "caller": "codex"}]
    with tempfile.TemporaryDirectory() as tmp:
        adj = _write(tmp, os.path.join(".adversary", "adjudications.json"),
                     json.dumps({
                         "version": 1,
                         "episodes": [{"commit": "c1",
                                       "findings": [{"outcome": "fixed"},
                                                    {"outcome": "rebutted-upheld"}]}]}))
        joined = aer.join_adjudications(eps, tmp)
    assert joined[0]["adjudicated"] is True
    assert [f["outcome"] for f in joined[0]["outcomes"]] == ["fixed",
                                                             "rebutted-upheld"]
    # no adjudication recorded -> flagged, never silently counted as validated
    assert joined[1]["adjudicated"] is False
    assert joined[1]["outcomes"] == []


def test_join_adjudications_missing_file_flags_all():
    eps = [{"repo": "r", "commit": "c1", "new_findings": 1, "caller": "unknown"}]
    with tempfile.TemporaryDirectory() as tmp:
        joined = aer.join_adjudications(eps, tmp)   # no adjudications.json at all
    assert joined[0]["adjudicated"] is False


def test_validated_stats_math_and_caller_breakdown():
    eps = [
        # zcode: two adjudicated episodes, one validated (fixed), one pure FP
        {"commit": "c1", "author": "A", "new_findings": 2, "caller": "zcode",
         "adjudicated": True,
         "outcomes": [{"outcome": "fixed"}, {"outcome": "rebutted-upheld"}]},
        {"commit": "c2", "author": "A", "new_findings": 1, "caller": "zcode",
         "adjudicated": True,
         "outcomes": [{"outcome": "cleared-unedited"}]},
        # codex: one adjudicated, validated via rebuttal_rejected corroboration
        {"commit": "c3", "author": "A", "new_findings": 1, "caller": "codex",
         "adjudicated": True,
         "outcomes": [{"outcome": "rebutted-upheld", "rebuttal_rejected": True}]},
        # unrecorded history: NEVER mixed into the measured columns
        {"commit": "c4", "author": "A", "new_findings": 3, "caller": "unknown",
         "adjudicated": False, "outcomes": []},
    ]
    s = aer.validated_stats(eps)
    assert s["adjudicated_episodes"] == 3
    assert s["validated_episodes"] == 2            # c1 (fixed) + c3 (rejected rebuttal)
    assert abs(s["validated_pct"] - 66.7) < 0.1
    # FP findings = rebutted-upheld + cleared-unedited MINUS findings whose
    # rebuttal was REJECTED (corroborated real - the numerators are disjoint,
    # gate r1 catch): c1 (1) + c2 (1) + c3 (1, but rejected -> NOT FP) = 2 of 4
    assert s["fp_findings"] == 2
    assert s["adjudicated_findings"] == 4
    by_caller = {r["caller"]: r for r in s["by_caller"]}
    assert by_caller["zcode"]["adjudicated"] == 2
    assert by_caller["zcode"]["validated"] == 1
    assert by_caller["codex"]["validated"] == 1
    assert by_caller["unknown"]["adjudicated"] == 0   # measured columns EMPTY


def test_validated_stats_empty_data_never_fabricates():
    s = aer.validated_stats([])
    assert s["adjudicated_episodes"] == 0
    assert s["validated_pct"] is None              # None, not 0.0 - no data yet
