# Colibri bug review — src/components/FirstRun.tsx

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 6f236b82c3384eda005a7d51aaf85e43899fa99e9d175dc084533a8f2dfccc8e

### Meta
- path: src/components/FirstRun.tsx | sha8: 6f236b82 | lines: 409 | context-pack: jcodemunch outline + importers (ScreenStage.tsx:67 mount `{firstRunOpen && <FirstRun onClose={() => setFirstRunOpen(false)} />}`, FirstRun.test.tsx, App.tsx boot gate); read src/install/client.ts, src/install/plan.ts, src/install/tiers.ts (contract only), src/api/{keys,firstrun,modelRoutes}.ts; git log -6 (single commit 91620a1)

### Review
## Verdict
Shippable. The exit-recording semantics (mount-generation guard vs StrictMode, any-unmount-is-an-exit) and secret handling are engineered correctly and match their comments; the biggest real risk is the `/api/install/recommend` failure path, where the wizard's copy promises a cloud-key affordance that renders zero rows.

## Bugs & vulnerabilities
**[MEDIUM] Cloud-keys section promises a key row that does not exist when recommend fails** - `lines 37, 106-107, 255-259, 318` — CONFIRMED
- What: `services` starts `[]` and is only populated by a successful `installRecommend()` (line 105). On failure (`load()` catch), `rec` stays null, so step 2 renders the `!v` copy "no verdict while the backend is away - a key below lights every cloud engine anyway" (line 258) and step 3 says "needs a cloud key - THE PACKAGE (step 2) saves one in place" (line 388) — but the CLOUD KEYS field (line 318) maps an empty array and renders no inputs at all, with no error or retry inside that section. Trigger: `/api/install/recommend` fails (stale preview build missing the route, middleware restart race) and the user proceeds to THE PACKAGE. Impact: the one affordance the copy points to is absent with no next click — violates the project's "empty/error states are invitations" rule; the user's only recovery is returning to step 1 and noticing PROBE AGAIN. Fix: when `load()` fails, fall back to `getKeys()` (`src/api/keys.ts:12`, already exists) to seed `services`, or render an explicit empty state in the keys field ("the key list did not load — PROBE AGAIN") instead of the promising copy.
- Trace note: verified the success path is unaffected (services retained on later `load()` failures since `setServices` only runs in `try`), so this bites only the never-loaded case — hence MEDIUM, not HIGH.

**[LOW] applyProfile conflates a failed routes-store refresh with a failed profile write** - `lines 139-152` — CONFIRMED
- What: `setProfile()` and `useRoutesStore.getState().refresh()` share one try/catch. If the POST succeeds but `refresh()` throws (transient `/api/model-routes` failure), the catch shows the refresh error as the status, `profileApplied` stays false, and the button still reads "APPLY THE VERDICT" — implying a write that actually landed did not. Trigger: profile POST 200 followed by refresh fetch failure. Impact: user re-applies or distrusts a done write; mild truthfulness drift on the status line. Fix: wrap `refresh()` separately — set `profileApplied(true)` immediately after the successful `setProfile`, and report a refresh failure as its own message ("profile set - the deck list did not refresh; reopen or check MODEL ROUTES").

**[LOW] watch() can state an unverified success for a superseded job record** - `lines 81-84` — PLAUSIBLE
- What: exit branch fires when `s.job.id !== id`; if another client (second tab) started job B after A's record was replaced, the else-branch announces "`${id}` fetched" without ever seeing A's own done record. Trigger: two browser tabs racing the single-job install server inside a 1.5 s poll gap. Impact: status text claims success the server never confirmed — against the "report what the SERVER says" invariant. Fix: when `s.job.id !== id` and the incoming state is not an A-error, say "the record for ${id} was replaced by ${s.job.id} - its outcome is unknown" instead of "fetched". PLAUSIBLE because the middleware's single-job serialization and the timing window could not be verified within this review's scope.

**[LOW] Persistent installStatus failure is swallowed silently for up to 10 minutes** - `lines 68-90` — PLAUSIBLE
- What: the poll loop's `catch { /* hiccuped - keep watching */ }` treats persistent failures (404 from a stale preview build — a documented incident class in AGENTS.md) identically to hiccups: no status update while the progress row freezes and every INSTALL button stays disabled on the stale `running` snapshot (`job?.state === "running"` at lines 274/305); after 400 iterations it asserts "still fetching ${id}" — itself unverified if the endpoint, not the download, is down. Fix: count consecutive catch failures and surface one after, say, 5 ("the status endpoint is not answering - progress is stale") so the frozen UI is explained. PLAUSIBLE: requires the status route to fail while `recommend` still works.

## Missing safeguards
- `install()` and the mount-adoption effect leave a ~1.5 s window (before the first poll sets `job`) where INSTALL buttons are enabled while the server already runs a job; the server's refusal path (`!r.ok` → thrown message) is the only guard — acceptable, but a brief "checking for a running fetch…" disable on mount would close it client-side.
- No double-click guard on INSTALL before `job` state lands; same server-side refusal covers it.
- The two-tab scenario above has no client fingerprinting of who started a job; a "started elsewhere" hint would make adoption messaging honest.
