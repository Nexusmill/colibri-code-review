# Engine author handoff

Frozen candidates: engine.js, engine.test.cjs, spectrum.test.cjs in this directory. Production untouched; gardens.js and spectrum.js are byte-identical scratch dependencies. engine-manifest.json gives production old and candidate new SHA256; engine.diff is normalized-line review diff (candidate exact bytes are authoritative).

Root cause: updateSpectrum previously decremented and teleported before movement and before updateStations. A violet cell could therefore interrupt its own three-second cleansing. Teleport processing now runs after movement and checks actual violet station overlap before decrement/teleport, covering entry frame. Leaving resumes on the same frame once outside. No forced movement or input lock.

Contract: s.docked is null or {color,x,y}; dock/undock edges use {type,color,x,y} with station centers. Direct station change emits undock before dock. Existing bounded spectrumEvent queue is used. setupSpectrum resets docked on create/garden/restore. UI author received contract.

Guardian measured baseline first actual hit 4.4833333333s. Candidate warning begins 1.0s, first actual hit 1.4166666667s. Warning value 0.4s (discrete countdown duration 0.4167s). Locked aim/footprint preserved; ordinary flight movement dodges. Repeat strikes at 2.9333,4.45,5.9667,7.4833,9.0s; alert capped3, radius86/life1.8 max. Ten-second stationary long-life QA fixture takes seven actual hits.

TDD: eight new tests and one updated old guardian timing expectation. Corrected regression suite against original production engine: 82 tests,73pass9fail, exit1 (engine-red.txt). Candidate:82pass0fail exit0 (engine-green.txt). Initial violet fixture used two packets incorrectly assuming two cells; corrected to one packet/two cells and reran production red. Old five-second exact-life assertion updated to 1.5-second window because intentional repeat pressure kills sooner. Existing other expectations unchanged. Engine and shield production baseline74 tests, plus8 new=82; parent's UI baseline adds2 to previous76.

Files frozen for independent review; no commits or production writes. Remaining parent work: independent review, exact safe application, full combined suite/browser acceptance and release.
