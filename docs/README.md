# Colibri documentation

> The complete feature reference for the colibri code-review console. Every knob, every
> mode, every file it writes, and the commit-gate machinery that guards this repo. Written
> 2026-08-30 against the code as of that date; each doc cites the module it documents -
> when a doc and the code disagree, read the module and fix the doc in the same commit.

## The product in one paragraph

Colibri is a small, fast AI code-review console (Streamlit UI + a headless batch runner).
Point it at a project; it ranks the core files, and for each file you pick it asks an
OpenRouter model to review it in one of five modes - saving one Markdown report per
file/mode, cached by content hash so re-scans only re-spend on files that changed. A live
run meter shows the maximum possible spend before you ever click. Deterministic
static-analysis output (ast+pyflakes, mypy, dis) is appended to every Python prompt so the
model corroborates facts instead of guessing.

## The docs

| Doc | Covers | Source of truth |
|---|---|---|
| [CONSOLE.md](CONSOLE.md) | The Streamlit console: every sidebar knob, scan/rank, the file table, the run meter, confirm-and-run, export, history | `app.py`, `ui.py` |
| [BATCH.md](BATCH.md) | `run_batch.py` headless runner: every flag, workers, budget, resumability, the summary file | `run_batch.py` |
| [MODES.md](MODES.md) | The five review modes (bug / quality / feature / spec / plan), delta re-review, JSON output | `analyzer.py` |
| [SPEC_AUTHORING.md](SPEC_AUTHORING.md) | **How to write a spec for ANY program** and feed it to spec mode (here, grok-review, hy4-review) | `analyzer.load_spec` + the spec template |
| [STATIC_SIGNALS.md](STATIC_SIGNALS.md) | The deterministic enrichers: ast+pyflakes, mypy, dis - when they run, their caps, how they degrade | `static_context.py` |
| [STORAGE.md](STORAGE.md) | `.colibri_reviews/` layout, the manifest schema, statuses, export, the central `reviews_archive/` + repo-memory mirror | `store.py`, `scanner.py` |
| [ADVERSARY_GATE.md](ADVERSARY_GATE.md) | The mandatory adversarial commit gate (G39) as armed in THIS repo: what it refuses, how to work under it | `Tools/adversary-gate/adversary_gate.py` |
| [GATE_INSTALLER.md](GATE_INSTALLER.md) | Installing the gate on ANY repo with `install_gate.py` - directly, or via a local/external subagent | `Tools/adversary-gate/install_gate.py` |
| [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md) | The four layers around the gate: driver check, harness guard, the git-notes audit tripwire, CI + branch protection - and the honest bypass surface | `Tools/adversary-gate/` (auditor, guard, record) |
| [GATE_ADOPTION_PLAYBOOK.md](GATE_ADOPTION_PLAYBOOK.md) | **THE OFFERING** - the complete novice-grade runbook for adopting the whole solution on any repo: exact commands, expected outputs, the daily loop, push/notes/CI/branch-protection flow, and a troubleshooting chapter where every entry actually happened | the whole `Tools/adversary-gate/` suite |
| [GATE_EVIDENCE_DOCKET.md](GATE_EVIDENCE_DOCKET.md) | **THE RUNNING CASE** - every catch the gate and its layers forced into remediation (rows of record in `gate_evidence.json`; false rebuttals, live-caught layer bugs, pre-ship CRITICALs; covenant: a row per catch, same session, never deleted) | `gate_evidence.json` |
| [EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md) | Everything that must be in place to run an external (headless) subagent that can arm the gate and drive reviews | field-verified prerequisites |

## Quick starts

- UI: `pip install -r requirements.txt`, set `OPENROUTER_API_KEY`, `streamlit run app.py`
  (full walkthrough: [../INSTRUCTIONS.md](../INSTRUCTIONS.md)).
- Headless: `python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high`
  ([BATCH.md](BATCH.md)).
- Driving colibri from a coding agent: [../AGENTS.md](../AGENTS.md) (key pickup, sweep loop).

## Repo map

| file | role |
|---|---|
| `app.py` | Streamlit console (scan, pick, meter, run, export) |
| `analyzer.py` | the reviewer: mode prompts + the OpenRouter call, fully config-driven |
| `static_context.py` | deterministic static-analysis enrichers |
| `scanner.py` | ranks a repo's core files, hides vendored/low-signal code |
| `store.py` | per-file review cache + manifest (new / changed / done) |
| `ui.py` | the visual system (CSS, masthead, run meter) |
| `run_batch.py` | headless batch runner |
| `legacy/` | retired sweep scripts kept for provenance - not part of the product |
| `reviews_archive/` | colibri's own durable copy of reviews written into other repos ([STORAGE.md](STORAGE.md)) |

Known cosmetic gap: the root `README.md` embeds `docs/screenshot.png`, which does not exist
in the repo - the image link renders broken until a real console capture is committed
(never a mockup; the capture must be of the real running app).
