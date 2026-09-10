# world3d.js — bug
Source: C:/Users/User/source/repos/OpenAIAstra/work/iris/world3d.js
Reviewer: /root/dock_music (independent UI reviewer)
SHA256: 534f6a83a48c72ab9656213967cc362f8a14c898a5f553514a9eb1014ef3c966
Date: 2026-09-08
Mode: bug
Context: Iris task contract, current UI report/diffs, prior docking UI review, exact engine/terrain contracts, current voice integration API. Native indexed navigation context previously resolved; ignored exact candidates read directly.

## Verdict
CLEAR for exact source bytes; no remaining confirmed source defect. Real-browser visual/FPS acceptance stays with root.

## Bugs & vulnerabilities
None remaining.

## Missing safeguards
Actual xyz vertices and computed face normals provide projected geometry within terrain conservative AABBs. Material atlas tiles use correct integer 5x2 inset crops and bounded cached patterns. Foundation draws before organic faces. Static mesh rendering now caches at most64 sprites per context/scene; geometry, damage quarter, destruction, texture identity/readiness and garden keys invalidate correctly. Warm-frame geometry is not rerasterized. Fallback remains functional when canvas/texture is absent. No dependency or voice ownership expansion. Performance must still be accepted in real browser.
