# Colibri Review - bug (FIRST review + extraction verification) - PatternSkin/apply_core.py

- **Source path:** `PatternSkin/apply_core.py` (new in the 2026-10-01 extraction tranche; blender_dev twin via the PatternSkin symlink)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37
- **sha256 reviewed:** (recorded at commit; 466 lines) - the file comprises the module header/imports + `_apply_pattern_rest` + `_live_build`
- **Date:** 2026-10-01 · **Mode:** bug, first review of the new unit + the extraction diff on `__init__.py`

## Verdict
CLEAN. The extraction is behavior-preserving by construction and by proof: both function bodies are AST-identical to the `__init__` originals (ast.dump equality asserted at edit time, before any file was replaced), `__init__` re-binds both names at the late-import site beside filmstrip, and the two functions' external references resolve to immutable names (the one mutable-global scare - `_m` - resolved as a function-local `import math as _m` riding verbatim inside `_live_build`). The seam breakage the move DID cause lived entirely in four hunt batteries' patch/source-pin targeting, all retargeted in the same tranche (each was RED on the moved code and GREEN after - the RED was the mutation proof).

## Bugs & vulnerabilities
None. The module imports: stdlib (os, math-as-_math), bpy, numpy, `from . import accel` (G21 optional-GPU surface unchanged), `from .heightmap import _save_gray_png`, `from .projections import` the six kernels it uses, and `from . import` the four __init__-resident helpers under the filmstrip late-import contract.

## Notes for future readers
- `_LIVE_UV` stays defined in `__init__` (other live-mode operators use it); apply_core imports it from the package root at load.
- The projections import block remaining in `__init__` is a documented public re-export surface - deliberately NOT swept.
- The follow-up cycle-break tranche (re-homing leaf modules' package-root imports) is recorded in CODE_RATING_2026-10-01 §Work program.
