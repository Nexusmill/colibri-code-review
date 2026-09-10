<!-- colibri review
source: src/components/DocView.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: ca53db504f4b0feb48c33567842b718d34a37552c974621db4a53771574ee722
date: 2026-09-06
mode: bug
context: E-6 wave (bundles idiom+copy, graph restore-by-timestamp+drift, palette verbs+legend, docview code+find); the stale-dist incident and its healing
-->

## Verdict
Shippable. The fenced-code parser (fence-to-fence, lang optional) renders as a pre with a per-block COPY key (copied checkmark / select-below on blocked clipboard); the FIND lens filters blocks by plain text with a spoken count in the placeholder and a named empty state. The text extractor covers every block shape.

## Bugs & vulnerabilities
(none confirmed)
