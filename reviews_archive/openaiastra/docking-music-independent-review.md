# Independent music review

Reviewer: dock_engine agent (did not author music). Date: 2026-09-08. Modes: bug/spec/quality. Scope: frozen music.js, music.test.cjs and all50 MIDI assets. Context: approved docking/music task, repo guardrails, author report/API; current mutable UI syncMusic/unlockAudio/pause/resume/finish/frame/mute/visibility callers. These caller bytes are provisional, not granted release clearance by this report. Source has no earlier production version.

## Verdict
CLEAR for the exact52 candidate hashes below. No confirmed release-blocking defects. Parent must still obtain combined frozen-UI review and browser/audio acceptance.

## Per-file source review
music.js: read end-to-end. Composition50 routes yields deterministic64-beat three-part scores with recurring sections, ten scale/root/timbre/tempo families and five route variants. Note bounds, same-pitch overlaps and phrase endings inspected. MIDI uses480PPQ, tempo plus three channel tracks, ordered note-offs and beat64 EOT. Export derives directly from compose events. Scheduler owns one music gain bus and max16 oscillators, accepts existing context only, does not resume/create a context or timers. Pause/mute/hidden/suspended stop/disconnect existing and future scheduled voices and retain elapsed beat; restart reschedules future onsets from retained position. Level change cancels and resets. Normal frames use disjoint half-open scheduling intervals; throttled frames discard backlog. Dispose is idempotent and prevents further scheduling. Cleanup handles natural endings and repeated cancellations.

music.test.cjs: read independently. Six real behavior tests cover50 unique bounded melodies, independently parsed SMF bytes with exact notes/times and tempo, fake-context lifecycle, cancellation/late frames, full-loop timing and shipped-byte parity. Fake audio models the unavailable device boundary only. Test coverage does not establish subjective beauty or actual native device playback. Existing parser counts program changes; independent reviewer separately verified exact program values for all50.

Each MIDI file: checked individually against manifest SHA256/byte count and freshly exported score. Author binary-reader tests passed for every asset including headers/lengths/channel paired on/off/timestamps/EOT and exact136note events. All50 distinct. No external sample dependency.

## Independent validation
node --test work/docking/music.test.cjs:6pass0fail, exit0. Additional standalone read-only probe:52 hashes/byte lengths match; all50 scores play two full loops at60Hz with exact event pitch/time equality,13600 note onsets, no duplicate or dropped notes. Peak concurrent live music voices6 (cap16). Dispose disconnects all oscillators after each run. Every MIDI program byte equals the corresponding score program.

## Cross-file synthesis
Provisional UI passes playing mode, level, combined sound/music mute and document.hidden in the documented shape. Existing AudioContext is constructed by unlockAudio; music module itself cannot autoplay. UI pause/mute/visibility immediately sync cancellation; garden changes are observed each frame. No API mismatch observed. Music notes omitted during pause are intentionally not reconstructed as held chords on resume, documented by author. Audible browser tone is a soft synthesized equivalent rather than actual GM patches; MIDI synth rendering differs, explicitly documented. No subjective listening conclusion claimed.

## Bugs and divergences
None confirmed. No additional safeguards required for these trusted internal score/caller inputs. toMidi accepts public score objects without a validator; current callers use compose-produced scores, so malformed third-party scores are not a reachable application defect.

## Quality
8/10. Small offline module with deterministic reusable score events and bounded scheduling; simple harmonic recurrence supports restrained background music. Musical beauty, mastering and physical audio timing remain subjective/native acceptance work, not evidence supplied by unit tests.

## Exact review units
| File | SHA256 | Verdict |
|---|---|---|
| music.js | aaa191ad12f4739b5567b5f5efee1f6ab366d38bf541851c1cde17f06cb5a57a | CLEAR |
| music.test.cjs | 3fec6ad9e0d4f479dbc4a53545eb4021a176aedebb9c22a8513de40e6d0cf277 | CLEAR |
| music/garden-01.mid | 1d7a8f6fe0f635d7388b1179f5508d352a04017fa2a1aaecd9b61f3f356aec99 | CLEAR |
| music/garden-02.mid | 0c7ff84146a328ed48ef855f5973f105c8c0134e384b6fb37646408b265f67bb | CLEAR |
| music/garden-03.mid | ce561e52e7cb7df763cea649b1515a1e8d4a4889330f256fdd70ff3afff0f8de | CLEAR |
| music/garden-04.mid | 08b4654ccb89936d2f4d81c80fd87b69c6680c39c22cc5fbbae78e34c3b90cdb | CLEAR |
| music/garden-05.mid | 93fab876fbe36c97e750a126f388c38118b758b89e0d36dae8f7e74856304396 | CLEAR |
| music/garden-06.mid | 37a493441e0a3f76658bafca12523e2e301bf6d6cb44dca19ca3ad3cbaa2523b | CLEAR |
| music/garden-07.mid | 01b78f15c282dfa7835a2fb44911069d9cd0182a710e2153bb9f2e9e2898a67a | CLEAR |
| music/garden-08.mid | ede52f9e3d82081d4e6769833d6b12df3604558bf56076d90ea55f12ddfdf212 | CLEAR |
| music/garden-09.mid | 1401f576a1518be08ffd39dc041c3f6e35d5033c9241a5c77094f0a1ebd83a20 | CLEAR |
| music/garden-10.mid | 1d5232f3b9207a6de5955df3dac35db54c7296ef0beb108f99ba4fc3b7b733aa | CLEAR |
| music/garden-11.mid | c69fcaaf57bc289cb5d05553d2bf99e9e4dc6042517d72be35a0d53aae0ce4d6 | CLEAR |
| music/garden-12.mid | 3608437def3d99bb663c493ccea74af17841e59cff5f7efbaac40bcd92f50cd8 | CLEAR |
| music/garden-13.mid | 73873cf2b22aa5b8ebf104ec30d1f8b0df513e107f25ec27b6ca5d981a9f966a | CLEAR |
| music/garden-14.mid | 70d59bacb93cf3181b2df9fb5ebec827137c7f7109e995634333799b04be26b1 | CLEAR |
| music/garden-15.mid | 2d9ac5a5d9f1038690700c64d56b85dfe5047d2541ab19606f53a72757a3bf76 | CLEAR |
| music/garden-16.mid | e2c56d1d15b50207167c206e19df019bb14fd2475599a05c91cbc7740b8e22dd | CLEAR |
| music/garden-17.mid | d5446ac7abba11f21470479e200b58f90b15bc9459485891b620ded05239aeac | CLEAR |
| music/garden-18.mid | c2160e9e969087e1ae2088ceb261c1269b0eafd298e3b3eca234e65975c5d516 | CLEAR |
| music/garden-19.mid | c1fe7098e5f5000c43de9434480971622e86d3e66cb5ae39ad16efa7150cef9a | CLEAR |
| music/garden-20.mid | 687384937a1828cba901edbde48d115d2cd8f9633ba49dc4b383497c785a84f5 | CLEAR |
| music/garden-21.mid | 3ea2534aac2227b631e8c85822507b848366dd9c0a18855a91605341dfa4b386 | CLEAR |
| music/garden-22.mid | 63f2543235c2c6c15987ab4bc22dca18b886c4a414b9d0406eb55bff560d9e2b | CLEAR |
| music/garden-23.mid | c03c1c5953c318e7c073627e34e10310b92eca8a3369c09d4835bcd9ec843754 | CLEAR |
| music/garden-24.mid | 0426fd07e4d1e55a14b538514624c59ac1d3cecf7392a9c2c405718a1a5ae1fa | CLEAR |
| music/garden-25.mid | 53afecb711608ef991bcc759d8b7dc4ec880ecd5c522ee70e9053d0919d930e3 | CLEAR |
| music/garden-26.mid | 937bd0d2fd70b42c7d19e02f97e6c2e21df5b9100c7344aaaf5e832b0fc9bfbb | CLEAR |
| music/garden-27.mid | 3a9a117d972f30bb4fe036c9b1af3fa4852c0c3302f8ca4fed91e6a9e4b5641a | CLEAR |
| music/garden-28.mid | dd81b1ffcd6e5b726cd96dc121c01b328040bab9c9c862cc7585b447d57b74f6 | CLEAR |
| music/garden-29.mid | 25cb99089b780e612dd1a6c03c6064880457ce9a42b94ed9decfaee2d0e1a036 | CLEAR |
| music/garden-30.mid | bb44a4abcf73f6baf8fde2c85da8543287b299f342d032d6aa70f47284628e26 | CLEAR |
| music/garden-31.mid | 47dff58e1a108c97bbf766e46e372caf9380add8a38a0925767306834c2d5113 | CLEAR |
| music/garden-32.mid | 11b356e39cb827b94ecadece81d4b6b40c6210e236000a23e849258264b09bcb | CLEAR |
| music/garden-33.mid | dfabdfc14164f7c1e6485ef4c71106e33a885255d7c43f80b2d100e51c68bfe5 | CLEAR |
| music/garden-34.mid | 83908b0216791b818c621e21f870ea17d6abd8cfa188a1e6f26970a61d184d67 | CLEAR |
| music/garden-35.mid | cab0fb938caf4c2617d07d0cee2c8d5b2b67c1c362ddfbe601537a23cfb824a9 | CLEAR |
| music/garden-36.mid | 08f35b2b99c3c147cf186c990caa7b84cf920fa0eb3a663e0f465a2a4de707dd | CLEAR |
| music/garden-37.mid | bb4d7c84264de2023b940bab34d94b20f37db8e0e06910175653e4315b70450c | CLEAR |
| music/garden-38.mid | 247aaaab86641fc49713a3f718f8f3d79e4c96d617c92f11a22633b006585006 | CLEAR |
| music/garden-39.mid | 78cca08c225202fd08a6d74b3f80024546c88e60add7ba72b0d67e68d2f31e9c | CLEAR |
| music/garden-40.mid | a5e17f587c407b32dcfbdefa7810e543f52190ba284fab0346c33271dc26216b | CLEAR |
| music/garden-41.mid | 5df01cd4912841d8de83f30f34e0ad9eadb31c5226d5c24151f7242cf0012712 | CLEAR |
| music/garden-42.mid | 009ac77a93c6248463b654e8bcec96b6a6e32e8a7bb6c79d7d21ddda85af3d0e | CLEAR |
| music/garden-43.mid | ca540baada7f1597c7dab87ef3dfc227e774f416ffc3922ac7591dd6ec834ad0 | CLEAR |
| music/garden-44.mid | 31fe83c85e6f7bdb481bbe05d3019c31d6f9bcc149db101187abdd0beb82fc67 | CLEAR |
| music/garden-45.mid | d9076f0b9b0eaccb52a10f197832ba779dd59d9a6690b1d5aaa790b9006ae146 | CLEAR |
| music/garden-46.mid | 33b275276bba5f542fd6265e720b61541d7750d1db2b4c302b77811a41e40557 | CLEAR |
| music/garden-47.mid | f08583da2cd8de41fa45c396a3ed5756b76186d3debb7985bb13cd17c130173e | CLEAR |
| music/garden-48.mid | 11a90a9dfe3869a852bfda16a74d3f8a7f60edab2cdb7bd74f8557b8b7e82ca9 | CLEAR |
| music/garden-49.mid | 19b5f8bbc4fbec9ef054a3ab86fa1cb4089dddb32b60b1c1ec8558b9af379d81 | CLEAR |
| music/garden-50.mid | 076f1e90d0b427d2923513f130680b7a933eee2ac440c4ec59aa22ceeb97e9bf | CLEAR |
