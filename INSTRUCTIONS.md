# Colibri — setup & running jobs

Colibri is a small Streamlit console that runs **AI code reviews** over a project. Point it
at a folder, it ranks the "core" files first, and for each file you choose it asks a model
(via [OpenRouter](https://openrouter.ai)) to hunt for **bugs**, **quality** issues, or
**feature** ideas — then saves a Markdown report per file. It shows a live "run meter" with
the **maximum** possible spend before you click, so a run never surprises you.

It works with **any OpenRouter model**. Two are pinned to the top of the model dropdown
because they're strong and cheap for review work: **GLM‑5.2** (`z-ai/glm-5.2`) and
**Kimi K3** (`moonshotai/kimi-k3`).

---

## 1. Install

You need **Python 3.10+**. From the project folder:

```bash
pip install -r requirements.txt
```

## 2. Get an OpenRouter API key

1. Make an account at <https://openrouter.ai>.
2. Add a little credit (reviews are cheap — a GLM‑5.2 review of a small file is ~1–3¢).
3. Create a key at <https://openrouter.ai/keys>. It looks like `sk-or-v1-...`.

## 3. Set the key as an environment variable

Colibri reads the key from the environment variable **`OPENROUTER_API_KEY`** — it is never
stored in a file or in the app.

**Windows (PowerShell)** — set it permanently for your user, then open a NEW terminal:

```powershell
setx OPENROUTER_API_KEY "sk-or-v1-your-key-here"
```

`setx` writes it for future terminals; your *current* window won't see it until you reopen it
(or run `$env:OPENROUTER_API_KEY = "sk-or-v1-..."` just for this session).

**macOS / Linux (bash/zsh)** — add to `~/.zshrc` or `~/.bashrc`, then reopen the terminal:

```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

If the key isn't set, the app shows a red banner and won't run reviews.

## 4. Run the app

```bash
streamlit run app.py
```

Your browser opens the console. Then:

1. **Model** (sidebar) — pick one. GLM‑5.2 and Kimi K3 are at the top; the rest of
   OpenRouter's live catalogue follows; or choose **Custom** to type any id.
2. **Reasoning / Limits / Pricing** (sidebar) — bounded vs unbounded thinking, the output‑token
   ceiling (this sets your cost ceiling), and the $/1M prices used by the meter. (OpenRouter also
   reports the *real* billed cost after each call, which is what gets saved.)
3. **Project directory** — type a path and click **Scan**. Core files rank first; vendored/low‑signal
   code is hidden by default.
4. Tick the files you want, choose **Bug Hunt / Code Quality / Feature Ideas / All three**, watch the
   **run meter** show the max spend, then **Confirm & run**.
5. Each review appears inline and is saved under `.colibri_reviews/` in the project you scanned.
   **Export all reviews** bundles them into one Markdown file.

Re‑scanning is cheap: Colibri remembers what it already reviewed (by file hash) and marks files
**new / changed / done**, so you only re‑spend on what actually changed.

---

## 5. Running reviews without the UI (batch)

`run_batch.py` runs the exact same reviewer over many files from the command line — handy for
sweeping a whole repo or scripting it from a coding agent. It reads `OPENROUTER_API_KEY` from the
environment, writes one Markdown review per file, and prints a running cost total.

```bash
# every .py under a folder, GLM-5.2, bug hunt, high effort
python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high

# specific files, Kimi K3, with a hard $ budget
python run_batch.py app.py analyzer.py --model moonshotai/kimi-k3 --budget 0.50

# other languages / patterns
python run_batch.py path/to/repo --glob "*.py,*.js,*.ts"
```

Key options: `--model`, `--mode {bug,quality,feature}`, `--effort {off,low,medium,high,xhigh}`,
`--max-tokens`, `--glob`, `--out`, `--budget`. Run `python run_batch.py -h` for all of them.

> **Gotcha — `--max-tokens` on high effort.** Reasoning tokens count against `max-tokens`. The
> default `32000` is plenty for a normal source file and finishes in ~40–120s. If you set it very
> high (e.g. 128000) on `--effort high`, the model can reason for *many minutes* on a single file.
> Only raise it for genuinely huge files.

See **AGENTS.md** if you want a coding agent (Claude, etc.) to drive `run_batch.py` for you —
it documents how the agent should pick up the key once you've set it.

---

## Costs, briefly

There is no free lunch — every review is a paid model call on your own OpenRouter credit. The
app's meter shows the **ceiling**; the number saved with each review is the **actual** billed
cost OpenRouter reports. GLM‑5.2 and Kimi K3 are chosen as pins because they're inexpensive and
strong for this. Start with one file to calibrate, then sweep.
