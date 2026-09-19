# civilizations.js — Colibri feature review

Source: C:/Users/User/source/repos/OpenAIAstra/implementations/emberline/civilizations.js
Reviewer: GPT-6 Codex, in-session primary reviewer
SHA-256: 888c03d5043e7c64f02181869b7075fc45d86b9dc88f91ef92af6c1890538bfb
Bytes: 4729
Date: 2026-09-16
Mode: feature
Context: native jCodemunch module outlines; exact current runtime dependencies and callers; README, AGENT_STATE, ACTIVITY, FEATURES, REMEDIATION, DEFERRED and progression/combat task; relevant test assertions inspected where available. No prior feature-mode cache entry. Existing bug/spec/quality clearances are not feature reviews or current gameplay acceptance.

## What this module does
Ten civilization identities and materials, atlas frame/orientation metadata, asynchronous local artwork loading, and sprite drawing with reduced-motion support.

## Suggested add-ons
### An automatically unlocked civilization field journal — Value Med · Effort M
- What: Add a read-only journal of encountered civilizations and their craft/ecology, revealed as the sequential campaign reaches each region.
- Why / evidence: Lines 4–15 already provide names and materials; keys/frame() lines 16–19 and draw() lines 42–53 provide illustration hooks. game.js selectPreview() line 555 currently displays the selected civilization, while index.html line 36 hides the atlas selection controls.
- How / hook points: Extend metadata with concise original lore/craft descriptions and stable IDs; have game.js record discoveries on actual garden entry and expose a separate read-only journal. Reuse the existing art/status fallback instead of loading another atlas set. Keep discovery state separate from the expedition checkpoint and document its reset policy.

## Adversarial verification
CONFIRMED static foundation, PLAUSIBLE retention value. Re-read exports and UI call sites: basic names/material descriptions already exist; persistent discoveries and journal entries do not. Do not re-enable route selection, vehicle choice or level skipping. Future tests should unlock only encountered regions, preserve discoveries across resume, and remain usable with failed artwork.

The complete file was read, then re-read through native read_file; SHA-256 was unchanged. Calls, existing functionality and recorded decisions were checked separately. CONFIRMED describes the static code basis, not proven player benefit. Proposed behavior has not been implemented or runtime-tested. No bug/spec clearance is issued in this feature review.

## Nice-to-haves
An illustrated enemy reference could reuse existing frames, but behavior descriptions must use engine encounter roles as well as species; a spore sprite alone does not imply a spore-ring attack.
