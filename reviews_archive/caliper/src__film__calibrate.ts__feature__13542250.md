# Colibri review — src/film/calibrate.ts (feature)

- **Source:** `src/film/calibrate.ts` · **sha256:** 13542250
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the calibration battery (owner 2026-08-23: "video is unranked — test and score ourselves"); the live loop in vite.film runs prompts[0] only (R1 finding); the OWNER'S TWO-PROMPT STANDARD (memory, owner-requested 2026-08-30: shot 58 = the people/faces wall — two persistent characters trading a beat; shot 1 = the action axis) — verified ABSENT from BATTERY_PROMPTS; last touch 8508c3d (2026-08-24).

## What this module does

The battery's data and math: three fixed prompts probing continuity/i2v/audio (harbor-night, paper-boat, lamp-turns — all landscape/object shots, no people), the budget plan (cheapest engines that fit the ~$5 cap, unpriced riding last at a conservative $0.05 estimate so they cannot crowd the known-cheap), and `serviceTiers` — per-service win rates from rated runs folded into S/A/B tiers with sample counts.

## Suggested add-ons

**The owner's two-prompt standard INTO the battery** — Value High · Effort S
- What: add the two standard prompts as first-class battery entries — the faces wall (two persistent characters trading a beat in 5s, working smiles, i2v from a shared reference) probing a new `faces` axis, and the action axis ("dives toward the child; camera pans") probing `action`. The standing rule: an engine failing EITHER axis fails the brief.
- Why (verified): BATTERY_PROMPTS contains zero people and zero multi-character action — the two hardest classes in the corpus (The Super Man condemned on exactly the two-character brief; p-video's card admits "cannot render faces"). A battery that never tests faces ranks engines blind on the class that matters most. Combined with R1's finding (the live loop runs prompts[0] only), the full fix is: both standards in the plan, all prompts executed, both axes graded.
- How: two prompt entries + the `probes` union gains "faces"|"action"; the vite.film loop iterates plan.prompts (R1 add-on); results append per-axis.

**Sample-count honesty on tiers** — Value Med · Effort S
- `serviceTiers` computes `n` but nothing gates on it — a single 5★ run stamps a service S. Mirror the R1 win-rates finding: tiers with n<3 render provisional (or sort below settled ones).

## Nice-to-haves

- Battery results → ENGINE_HEALTH writes (R1's persisted-health add-on): an engine failing an axis lands in the denylist with the battery run as evidence.
