# Music author handoff

Frozen scratch files: music.js and music.test.cjs; 50 assets in music/garden-01.mid through garden-50.mid. Full new-file textual diff: music.patch. Exact hashes/byte counts plus per-score metadata: music-manifest.json. No production writes, commits, or independent review claims.

## Public contract

UMD window.EmberMusic / CommonJS exports compose(index), toMidi(scoreOrIndex), createPlayer(existingAudioContext). Garden indexes are zero based, 0..49, matching the existing five-routes-per-biome order. Player update({playing,level,muted,hidden}) is driven by the game's animation frame; stop() cancels scheduled notes and preserves position; dispose() disconnects all owned nodes. stats() exposes level/playing/voices/beat/disposed for inspection. No timer, context creation, context resume or autoplay. UI supplies global sound mute and page visibility and owns gesture unlock.

Level changes cancel all old voices and reset musical position. Menu, pause, mute, hidden or suspended context cancels all notes and freezes musical position. Restart schedules future note onsets from that position (it does not reconstruct a partially held chord). At most 16 music oscillators, 150ms lookahead, late frames skip missed notes. Music bus gain .28 with lower per-note gains than SFX; each note has soft attack and exponential decay. No effects nodes or external dependencies.

## Composition

Original deterministic 16-bar/64-beat miniatures, three parts: bass, rolled open harmony, restrained melody. A/A-prime/B/A-cadence structure. Ten named biome families use major, Dorian, minor or Lydian scales, distinct roots/tempos, sine/triangle colours and MIDI program families. Five routes vary motif, chord progression and tempo; melody recurrence is intentional. Scores contain 136 events each. No random note selection. All 50 melody event streams are distinct. Audible patches are intentionally simple synthesizer equivalents; MIDI playback uses the receiving synth's General MIDI instruments and will differ in timbre.

MIDI is SMF type 1, four tracks (tempo plus three instruments), 480 PPQ, complete note-offs and end-of-track at beat 64. Bytes derive directly from the same score events used by the browser sequencer. The final quarter-beat leaves a soft breathing space before the repeat.

## Actual validation

TDD RED: four behavioral tests failed on missing composition/MIDI/player APIs. First implementation reached 3/4; pitch bounds caught two sub-C2 bass roots, corrected by octave choice. GREEN 4/4. Added asset test RED on absent garden-01.mid, generated all 50 files, GREEN 6/6. The complete-loop duplicate scheduling test was added after implementation as additional verification, not claimed as a failed-first test.

Final command: node --test work/docking/music.test.cjs. Six tests pass: deterministic/distinct/bounded scores; independent binary SMF parsing with exact score equality; unlock/menu/mute/hidden/pause/disposal; garden cancellation and bounded late-frame catch-up; every note once across a normal full loop; all 50 assets byte-identical to exports. Fake WebAudio context is used only at the unavailable native audio boundary; tests inspect scheduled note frequencies/times/cancellations and owned node cleanup. Browser hearing and real audio-device timing remain root acceptance work.

## Preview

music-preview.wav is a 40-second mono 22050Hz PCM approximation of gardens 1, 13, 36: 12 seconds each with one-second gaps, using the same notes, sine/analytic triangle shapes, gain and envelope. Peak 0.02820, RMS 0.00439; no clipping. It is not OfflineAudioContext output and has not been human-listened by the author. The preview is scratch QA, not a shipping asset. Root should inspect audibility and musical taste in the live browser.
