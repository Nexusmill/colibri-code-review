<!-- colibri review
source: vite.caliper.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 6e01a0ac04220a995001829254a9869ae369aaaee3d21a48ea5ccf2eae4911ac
date: 2026-09-06
mode: bug
context: E-6 wave (bundles idiom+copy, graph restore-by-timestamp+drift, palette verbs+legend, docview code+find); the stale-dist incident and its healing
-->

## Verdict
Shippable. Delta confined to the two graph handlers: backups GET answers drifted (live workflow vs newest backup, Buffer.equals); restore accepts an optional file which must be a member of THAT graph's rotation (membership refusal 400), restoring backs up current first, and the response names what was restored.

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: a foreign file value could traverse - the file is never joined into a path; it is only matched against the rotation's own readdir listing, so no caller-supplied path segments reach the filesystem.
