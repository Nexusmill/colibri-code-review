# colibri debug record - tools/skill_census.py

- source: `tools/skill_census.py` (Nexusmill)
- model: claude-fable-5-1 (in-session, Phase D debug modality)
- sha256 reviewed (pre-fix): `15520559557ee958985828939cf3706d264eac27686528d686d70f17a2e6a182`
- sha256 after fix: `c95f46e1e1a47fd9a3f6bf9731bb410d196c46acb31d431cde155aba76a0672d`
- date: 2026-09-04
- mode: debug
- context pack: new module (this session, TDD from the 2026-09-03 plan); single caller = its own `main` /
  `collect_events`; test suite `tests/test_skill_census.py` (8 cases green on synthetic stores before the
  failure); no manifest rows on this file (never committed); real stores = CLI `~/.claude/projects`
  (92 files) + Cowork `local-agent-mode-sessions` (361 audit.jsonl).

## Failure signal (captured, not inferred)
First run against the real stores (`--since 2026-08-12 --until 2026-09-03`):
```
File "tools\skill_census.py", line 72, in extract_events
    content = (rec.get("message") or {}).get("content")
AttributeError: 'str' object has no attribute 'get'
```
Reproducible every run; the synthetic fixtures never triggered it.

## Hypothesis ledger
1. Some real records carry `message` as a non-dict (string). Kill/confirm: scan both stores for records
   whose `message` is present and not a dict, bucket by (store, type, python type). **CONFIRMED** by probe
   (`scratchpad/probe_msg.py`): exactly one shape, 14 records, all Cowork `type: "system"`,
   `subtype: "permission_denied"`, `message` = str ("Permission for tool ... denied"). No CLI hits.
2. A malformed JSON line parsed to a non-dict. Killed: `iter_records` already drops non-dict records; the
   probe shows the parent record is a well-formed dict.

## Fix (root cause, one variable)
`extract_events`: read `message` once; take `content` only when it is a dict, else `None` (the record then
falls through both the `user` and `assistant` branches, which is right - a permission event is neither a
turn nor a tool call). Regression test written FIRST (`test_string_message_system_record_is_tolerated`:
a string-message system record inside the Cowork fixture session; 7 of 9 tests errored on the pre-fix
bytes), then the one-line guard; 9 of 9 green.

## Verification
- `python -m unittest tests.test_skill_census` -> `Ran 9 tests ... OK`.
- Real-store run completes: window 51 Skill invocations / 19 skills; all-time 129 / 31; both stores listed.
- Cross-check: CLI-only run over the 2026-09-03 hand census's window gives 78 / 23 against its 79 / 23; the
  CLI store dropped from 94 to 92 files between the runs (retention churn), same skill set.

## G35 note
No `docs/remediation_manifest.json` row: the defect never reached a commit (caught between the module's
first write and its first commit, in the same session). The features_manifest row for the tool records the
string-message tolerance as part of the shipped behaviour.
