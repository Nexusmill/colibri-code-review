# Colibri Code Review Console -> Kimi K3 via OpenRouter

## 1. Set your OpenRouter key (one time)
In PowerShell, paste YOUR key:

    setx OPENROUTER_API_KEY "sk-or-v1-...your-key..."

Then **close that terminal and open a new one** (setx only affects new shells).
The key is read from the environment; it is never stored in these files.

## 2. Run
    cd E:\colibri-analyzer
    & "C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run app.py

## 3. Use it
- **Run Config (left sidebar)** — everything about a run is live here:
  - **Model** (any OpenRouter id)
  - **Reasoning**: Bounded (low/medium/high effort) or Unbounded (thinks freely up to your ceiling)
  - **Max output tokens** — YOU set the cost ceiling; thinking + the review share this budget
  - **Temperature**
  - **Endpoint & pricing** (advanced) — base URL and $/1M rates for the cost meter
- **Main panel** — point at a directory, Scan (core files rank first, vendored code hidden),
  pick a review type (Bug Hunt / Code Quality / Feature Ideas / All three), check files,
  and the **Run Meter** shows the max spend at your settings before you Confirm.
- Reviews save to `.colibri_reviews/` and are tracked as new / done / changed per mode.
  "Review all changed + new" batches; "Export all reviews" makes one Markdown file.

## Notes
- Cost is metered per file and capped by your Max output tokens. The Run Meter shows the ceiling.
- Speed/cost tradeoff: low effort + smaller token cap = fast & cheap; high effort = deeper & pricier.
- Privacy: text is sent to OpenRouter -> Moonshot. Never paste secrets or the legal/formation files.
- A key pasted in plaintext anywhere should be rotated at openrouter.ai/keys.
