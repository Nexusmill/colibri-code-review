# Colibri review — src/install/tiers.ts (feature)

- **Source:** `src/install/tiers.ts` · **sha256:** e622496b
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the GPU ladder (owner rulings 2026-09-02: floors 15/8 + the 32/64 GB packages from the open-weights landscape); fmtGb's truncating rule is display doctrine; the LADDER-RULING approval context in [[caliper-era51-shelf-wave]]; last touch fe8f967 (2026-09-02).

## What this module does

161 pure lines: the five-rung ladder (video-max 64: Wan fp16 + FLUX.2 dev 32B; video-pro 32: Wan fp8 + Qwen-Image-2512 fp8; video 15: distilled LTX + Anima; image 8: Anima-Turbo; cloud-only), each rung with its reason-sentence naming the GPU's own numbers, `fmtGb` (TRUNCATES — a 7.9992 GiB boundary never reads 8.0), `judgeTier` (probe in / verdict out / null when the backend never answered — no verdict beats an invented one), and the catalogIds consistency check.

## Suggested add-ons

**Non-CUDA device branches** — Value Low-Med · Effort S (blocked on owner direction)
- `judgeTier` matches `type === "cuda"`; a rocm/MPS device falls to cloud-only with "no CUDA device answered" — accurate-but-blunt for the non-nvidia-mac deferral. When the Mac port un-parks, the rungs need device-type awareness (rocm reports its own type; MPS has its own memory accounting). Recorded so the ladder's next edit knows the seam.

**Free-headroom note on the verdict** — Value Low · Effort S
- The reason sentences state VRAM total; a machine where Windows+desktop eats 3 GB of a 16 GB card still hears "holds local video" (the card does; the working set shrank). An optional free-at-probe line (the stats carry it) would make the wizard's verdict one degree more checkable. Owner call — the card-class framing may be the intent.

## Nice-to-haves

- The rung reasons are beautiful copy; nothing to add. Thresholds as exports for tests = the THRESHOLDS pattern from the adversary review.
