# Iris engine independent review

Source: C:/Users/User/source/repos/OpenAIAstra/work/iris/engine.js
Target: implementations/emberline/engine.js
Reviewer: GPT-6 Codex /root/dock_music, independent engine reviewer
SHA-256: c7ee052410977cc94870a6c496614cb2c8f4a05d633c99ebb00a3ca202c4b876
Date:2026-09-08
Mode:spec
Context: current iris-worlds task; engine-manifest/report/diff; previous docking-engine review; native JCodemunch resolve/engine outline/caller context; actual spectrum serial/recycling implementation; frozen voice event API and terrain renderer interface.

## Verdict

CLEAR for exact bytes. No blocking contract divergence confirmed.

## Review evidence

Delta reviewed against previously cleared docking engine plus current exact call paths. Common setup creates terrain and player altitude before entry cargo. Actual player movement routes through terrain.move after bounded mode acceleration and before teleport/stations. No-input station overlap stops residual inertia/current while deliberate input restores movement; this directly addresses measured black-pad submarine drift. Teleport rejects occupied footprints, retains existing safe-landing rules, uses12..20second cycles and preserves already-running/restored shorter timers. Dock count and reset remaining are sampled from actual shield cells; inserted counts use new cell serials rather than net color change or queued packets. Validated shield cycles and capped simulation dt permit at most one packet per step. Current checkpoint semantics intentionally recreate garden-entry terrain. Existing FIFO/save/damage paths retain behavior.

## Divergences

None confirmed after rechecking candidate paths against call order, shield serial semantics, dt bounds and fresh tests.

## UNJUDGEABLE HERE

Actual3D projection/depth ordering, audible voice playback, and finalUI lifecycle are separate files/parent browser acceptance. Fullhuman50garden balance is not claimed.

## Validation

Independent node --test work/iris/engine.test.cjs work/iris/spectrum.test.cjs work/iris/terrain.test.cjs:93tests93pass0fail. Exact hashes reverified against frozen author manifest. No production modifications or commit. This is pre-write evidence, not additional armed Git clearance.
