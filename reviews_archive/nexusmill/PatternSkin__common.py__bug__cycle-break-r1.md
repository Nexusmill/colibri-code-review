# Colibri Review - bug (FIRST review) - PatternSkin/common.py + the cycle-break tranche

- **Source path:** `PatternSkin/common.py` (new 2026-10-02; the whole tranche diff audited: __init__, filmstrip, apply_core, projections, heightmap, keystore, keyvault x3, accel, ai_parts + 2 test retargets)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37
- **sha256 reviewed:** recorded at commit (353 lines: 22-symbol helper closure + 13-member preview/enum cluster + _dispose_previews)
- **Date:** 2026-10-02 · **Mode:** bug, first review of the new unit + the tranche diff

## Verdict
CLEAN at battery-verified state. 31 of 35 moved symbols are AST-identical to their __init__ originals (proven at edit time, before any file replacement); the 3 function-local import re-homes are documented and behavior-preserving (name imports / importlib for module objects); _dispose_previews is the unregister teardown verbatim in a function. The tranche's four defects were all introduced AND caught pre-land by the batteries (never shipped): the late-rebind class-body NameError, one comment-filtered missed call site, the `global`-rebinding preview caches split across namespaces, and the math battery's source scrape.

## Bugs & vulnerabilities
None at the verified state. Design notes: the shared mutable caches (_PREVIEWS/_ENUM_CACHE/_ENUM_SIG/_BRAND/_LIB_EMPTY_CACHE/_HM_CACHE) have ONE owning module each (common/common/common/common/common/heightmap) - every cross-module consumer either imports the object (mutation-safe, no rebinding anywhere outside the owner) or calls the owner's reset (_previews_reset/_dispose_previews). The keystore<->keyvault call-time mutual reference (legacy migration bridge) is lazy, guarded, and import-time-acyclic by construction.

## Notes
- __init__ keeps EARLY assignment re-exports (line ~85): class-body-time consumers (PatternSkinSettings) and every historical patch seam bind correctly; pyflakes' remaining signal there is the documented projections public re-export block.
- The blender_dev twin "cycle" row in jCodemunch is a stale pre-symlink index artifact; the twin directory is a symlink to PatternSkin/ (same inodes).
