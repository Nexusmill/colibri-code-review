# Colibri review — src/components/MediaView.tsx (feature)

- **Source:** `src/components/MediaView.tsx` · **sha256:** 5dc0e38c
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the media router inside every asset window + Outputs cards; FEATURES.md `sound-plate` (audio shape + DocView words); ruling 38's mute doctrine lives at the callers; verified absence: no frame capture; last touch c9bb3bb (2026-09-05).

## What this module does

Routes one asset to its viewer: images object-fit; text artifacts fetch and render through DocView with panel images resolved against the document's own film folder (and honest moved/recycled error states); audio alone gets the sound plate — the decaying phosphor-bar silhouette over native controls; video plays with an optional HIDDEN synced audio track that follows play/pause/seek/rate — the dual-track marriage for engine-audio clips.

## Suggested add-ons

**Frame capture from video windows** — Value Med-High · Effort S-M
- What: a capture key on video windows writing the current frame to a PNG — through `autopilot-ref` into the open run's refs (or the generic asset path for one-offs), then a status line naming where it landed.
- Why: reference images are the film flow's consistency mechanism (References ride every image-accepting engine call) and the best references are frames from your own footage — "this look, held." Today the round trip is: screenshot externally → find the file → attach at THE IDEA. One press closes it. Verified absent.
- How: canvas drawImage at currentTime → toBlob → the existing ref-upload endpoint; the window already holds the video element.

**Sound plate: real waveform** — Value Low-Med · Effort M
- The bars are a fixed decorative profile; a rendered waveform (decode + peaks) would show song structure — where the drops are. Decoding audio client-side per window is the cost. Cosmetic-leaning; commission.

## Nice-to-haves

- Playback rate chips (0.5/1/2×) on video windows — reviewing footage at 2× is the grading workflow's natural speed. Low, small.
