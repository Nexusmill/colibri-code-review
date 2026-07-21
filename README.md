# colibri

A small, fast **AI code-review console**. Point it at a project, it ranks the core files,
and for each file you pick it asks an [OpenRouter](https://openrouter.ai) model to hunt for
**bugs**, **quality** issues, or **feature** ideas — saving a Markdown report per file. A live
"run meter" shows the **maximum** possible spend before you ever click, so a run can't surprise
you, and re-scans only re-spend on files that actually changed.

Works with **any OpenRouter model**. **GLM‑5.2** (`z-ai/glm-5.2`) and **Kimi K3**
(`moonshotai/kimi-k3`) are pinned to the top of the picker — both are cheap and strong for
review work.

![console](docs/screenshot.png)

## Quick start

```bash
pip install -r requirements.txt
setx OPENROUTER_API_KEY "sk-or-v1-..."   # Windows; macOS/Linux: export in your shell rc
streamlit run app.py
```

Full walkthrough (getting a key, running jobs, batch mode) is in **[INSTRUCTIONS.md](INSTRUCTIONS.md)**.

## Batch / headless

```bash
python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high
```

One Markdown review per file, a running cost total, a `--budget` cap. Driving it from a coding
agent? See **[AGENTS.md](AGENTS.md)**.

## Static-analysis signals (Python)

Before asking the model, colibri runs three **deterministic** tools on the exact source and
appends their output to the prompt as *hints to corroborate* — so the model verifies facts a
tool already proved instead of guessing:

- **ast + pyflakes** — scope leaks (undefined / used-before-assignment names), dead code (unused
  imports / variables), and ast smells (mutable default args, bare `except:`, unreachable code).
- **mypy** — static type errors surfaced before runtime (stops dynamic-type confusion).
- **dis** — bytecode of the hottest loop-bearing functions, so the model can spot per-iteration
  overhead (e.g. a `LOAD_GLOBAL` / `LOAD_ATTR` that should be hoisted out of the loop).

On by default; toggle them in the sidebar (**Static signals**) or with `--no-static` in batch.
`pyflakes` and `mypy` are optional — if not installed, that pass just prints a one-line note.
Only runs for Python; other languages are skipped.

## What's in here

| file | role |
|------|------|
| `app.py` | Streamlit console (scan, pick, meter, run, export) |
| `analyzer.py` | the reviewer: prompts + OpenRouter call, fully config-driven |
| `static_context.py` | deterministic static-analysis enrichers (ast+pyflakes, mypy, dis) |
| `scanner.py` | ranks a repo's core files, hides vendored/low-signal code |
| `store.py` | per-file review cache + manifest (new / changed / done) |
| `ui.py` | the visual system (CSS, masthead, run meter) |
| `run_batch.py` | headless batch runner |

## Notes

- Every review is a **paid** model call on your own OpenRouter credit. The meter shows the
  ceiling; the saved cost is the real billed amount OpenRouter reports.
- The key is read only from `OPENROUTER_API_KEY` — never stored in the app or the repo.
- Reviews are written to `.colibri_reviews/` in the scanned project (git-ignored here).

## License

MIT — see [LICENSE](LICENSE).
