# CONSOLE.md - the Streamlit console, every control documented

> Source of truth: `app.py` (behavior) and `ui.py` (visual system). Launch:
> `streamlit run app.py`. Nothing about a run is decided for you - every knob below is
> live per run, and the sidebar config is rebuilt into `st.session_state.cfg` on every
> rerun.

## Sidebar

### Model
- **Model picker** - `z-ai/glm-5.2` (GLM-5.2) and `moonshotai/kimi-k3` (Kimi K3) are
  pinned to the top (`PINNED_MODELS`); below them the **entire live OpenRouter catalogue**
  (fetched from `https://openrouter.ai/api/v1/models`, no key needed, cached 1 hour via
  `st.cache_data`). Last entry **"Custom (type an id)..."** opens a text input accepting
  any model id.
- **Offline fallback**: if the catalogue fetch fails the list silently degrades to the two
  pins + Custom, with the caption "Live model list unavailable - pinned models + Custom
  still work." Reviews are unaffected.

### Reasoning
- **Bounded / Unbounded** radio.
  - *Bounded* exposes an **effort** selectbox `low | medium | high` (default `medium`) -
    sent to OpenRouter as `extra_body={"reasoning": {"effort": ...}}`.
  - *Unbounded* sends **no** effort hint (`reasoning = "off"`): the model thinks freely,
    capped only by the output ceiling.
  (The batch runner additionally accepts `xhigh`; the console deliberately stops at
  `high`.)

### Limits
- **Auto output ceiling** toggle (default ON). ON = `max_tokens` is `None` and the call
  uses **the model's own `top_provider.max_completion_tokens`** (looked up for the selected model and endpoint
  via `analyzer.model_max_tokens`, cached in-process, fallback 131072). This exists
  because reasoning models truncated by a low cap return `finish=length` with ZERO
  findings - a paid empty review. The caption shows the resolved ceiling.
- OFF = a **Max output tokens** number input (256-64,000, default 8,000). Thinking and
  the written review share this budget; the displayed cost is an estimate, not a spending cap.
- **Temperature** slider 0.0-1.0, default **0.15**.
- **Delta re-review for changed files** toggle (default ON): a file whose review is
  *stale* (content changed since its last review in this mode) gets its previous saved
  review injected into the prompt, and the model is instructed to report **only NEW or
  CHANGED findings** plus a "Fixed since last review" section. Cheaper convergence
  rounds; see [MODES.md](MODES.md#delta-re-review).

### Endpoint & pricing (Advanced expander)
- **Base URL** (default `https://openrouter.ai/api/v1`; env `API_BASE_URL` overrides the
  default). Any OpenAI-compatible endpoint works.
- **Price in / Price out** ($/1M tokens, defaults 3.0 / 15.0) - used by the file table, meter and confirmation estimates,
  and as a cost fallback when the API omits real billing; OpenRouter normally reports
  actual cost, which is what gets saved.

### Static signals
Three checkboxes, all default ON - deterministic tool output appended to the prompt
(details: [STATIC_SIGNALS.md](STATIC_SIGNALS.md)):
- **AST + pyflakes** (scope leaks / dead code / ast smells)
- **mypy type check** (bug/quality modes only)
- **dis bytecode of hot loops** (bug/quality modes only)

## Main surface

### API-key banner
If neither `OPENROUTER_API_KEY` nor `OPENAI_API_KEY` is in the environment, a red error
banner shows and reviews return a no-key message without spending anything.

### Project directory + Scan
Text input (default: last scanned dir, else env `COLIBRI_DIR`, else the cwd) + **Scan**
button. Scan walks and ranks the tree (`scanner.scan`, see
[STORAGE.md](STORAGE.md#scanner-ranking)) and loads the review manifest. A non-directory
path errors inline.

### Review type
Radio: **Bug Hunt · Code Quality · Feature Ideas · Spec Conformance · Remediation Plan ·
All three**. "All three" = bug + quality + feature per selected file (spec and plan are
NOT part of it).

**Spec Conformance prerequisite panel** (appears only for spec): an **Expectations file**
path (a spec-registry JSON or any hand-written contract text file - format in
[SPEC_AUTHORING.md](SPEC_AUTHORING.md)) and an optional comma-separated **Row ids**
filter. On success the caption shows how many characters of expectations loaded; errors
render inline. With no expectations loaded, a spec run returns a message and **makes no
API call** ($0).

### Filters
- **Hide vendored / low-signal** (default ON): hides files with scanner score < 40.
- **Only outstanding (new / changed)** (default OFF): hides files whose current sha is
  already reviewed in the selected mode(s).

### The file table
One row per surviving file, ranked core-first:
- **Select** - the only editable column.
- **Status** - single mode: `new` (never reviewed in this mode) / `done` (reviewed at the
  current sha) / `changed` (file edited since its review). "All three": `n/3` modes up to
  date at the current sha.
- **File** - path relative to the scanned root.
- **in tok** - estimated input tokens (`chars / 3.5`).
- **Source est $** - the source-only estimate for every selected mode:
  `n_modes x (in_tok x price_in/1M + max_out x price_out/1M)`.
  Full prompt overhead is included later in the confirmation estimate.

### The run meter
The meter estimates source-token cost and an output allowance for every selected
(file, mode) call. Selecting All three sends each file three times. This source-only
estimate excludes prompt overhead; the confirmation estimate includes it. Neither
display is a guaranteed maximum because tokenization and provider prices can vary.

### Actions
- **Review selected (n)** - queues selected files x selected mode(s).
- **Review all changed + new** - queues every outstanding row in the current view.
- **Export all reviews** - concatenates every saved review for this project into
  `.colibri_reviews/_all_reviews.md` and offers a download button.

### Confirm & run
The confirmation shows the call count and estimates every actual prompt, including
system instructions, specifications, prior reviews and static signals, plus each
call's selected output allowance. The first estimate can run the selected static tools;
unchanged queue items reuse their estimates within the session. Source, settings, prior-review
or specification changes refresh the affected estimates. AUTO uses the selected model and endpoint together.
Confirm is disabled if the queue cannot be estimated. Prices and token counts remain
estimates, not a spending cap.

Each response appears with its saved path and recorded cost (provider-reported billing
when available, otherwise a configured token-price estimate). Empty, refused, truncated
or invalid-JSON responses are incomplete and do not grant completed-cache credit.
A paid save failure retains the cost, displays the response and stops further calls.
The progress message reports how many calls completed successfully.

### Previously reviewed in this project
An expander listing every manifest entry (file + completed modes and incomplete-attempt count) and the project's
total recorded spend.

## Visual system (`ui.py`)

Hummingbird-throat palette (teal `#24C6AD` -> violet `#7C6BFF`) on cool near-black;
Space Grotesk (headings) / Inter (body) / JetBrains Mono (numbers, labels). Streamlit
chrome is hidden **granularly** - never the whole toolbar: in Streamlit 1.59+ the
sidebar-reopen button lives inside the toolbar, and blanket-hiding it once left a
collapsed sidebar with no way back (the CSS keeps `stExpandSidebarButton` /
`stSidebarCollapseButton` visible). The masthead shows the wordmark, "code review
console", a gradient rule, and the active model id (HTML-escaped).
