# Iris voice author handoff — 2026-09-08

Frozen candidates: voice.js, voice.test.cjs and319 WAV files in voice/. Exact hashes and metadata: voice-manifest.json. Full textual new-file diff: voice.diff. Production untouched; no commit or independent review claimed by author.

## Voice and assets

Installed Windows voices inspected through System.Speech; Microsoft Zira Desktop is Female/en-US. All319 clips were actually synthesized locally using that voice, rate1, volume100, directly to PCM16 mono16000Hz. No browser voice selection or external service; Iris is an original navigator role, with no attempt to imitate a named actor.

Full sentences avoid awkward number splicing:85 dock inventories (five pads times counts0..16),80 single-removal/remaining messages (five colors times0..15),144 actual-addition messages (nine colors times1..16),nine restrained effect tips andone ten-second warning. Some insertion counts exceed current packet size; bounded supported counts are intentionally covered without new synthesis if packet rules later change.

SAPI adds about0.66s silence at the tail. Rendered audio was trimmed using amplitude threshold80 with40ms leading/100ms trailing safety margin, then peak-normalized to0.68. Every file is standard PCM WAV. Total21,759,952bytes. Longest removal2.8276875s fits the existing3-second interval. All319 clips have nonzero audible samples and no clipped sample. They have not been human-listened by this author. Representative actual clips for parent listening: voice/dock-black-16.wav, voice/reset-blue-3.wav, voice/added-gold-2.wav, voice/teleport-10.wav.

## Frozen API

UMD global EmberVoice/CommonJS exports createPlayer(options) and immutable clips map of clip IDs to text. options: assetBase (default voice/), onCaption(text), onDuck(active); optional audioFactory exists for deterministic tests. API: update({playing,muted,hidden,unlocked,time,teleport,violetCount,dockedColor,counts}), handleEvent(event), stop(), dispose(), stats(). UI supplies actual simulation time and current shield/docking values. Update state before consuming events; call lifecycle updates immediately on pause/mute/visibility. UI owns trusted gesture tracking, independent Voice mute OR global Sound mute. Voice owns one lazily created HTMLAudioElement; no AudioContext/fetch dependency, preserving offline relative-file playback. Optional duck callback requires no music.js changes and can be omitted.

Engine contracts accepted with author: dock {color,count}; reset {color,removed:1,remaining}; shieldchange {color,added}. Pickup spectrum and generic recycle events never announce additions. Negative/fractional/out-of-range counts are rejected. Dock inventory includes zero. Every actual reset is eligible to announce its real remaining count; higher-priority warnings/lifecycle cancellation may preempt.

## Queue and timing

Maximum six queued clips plus one active element. Priorities: warning100, reset80, dock70, actual additions50, advice10. Higher priority interrupts lower priority; identical active/queued phrases deduplicate. Undock drops previous pad inventory/removal. Violet dock cancels stale teleport warning and previous chatter. Teleport/garden/end/complete clear queue and current audio. Audio completion/error/rejection callbacks carry a sequence guard against cancelling a later utterance. Eight-second simulation watchdog releases a stalled element. All pauses/mutes/hidden/end lifecycle events discard queued speech; they do not shift deadlines and replay old inventory later.

Warnings require a witnessed actual remaining-time crossing from above10 to9.75..10, with violet cells and no violet docking. Restored timers already below10, throttled frames skipping below9.75, resumed countdowns below10, or inactive voice cannot assert a delayed false ten-second warning. Actual teleport and violet-dock snapshots cancel an in-progress warning. Effect advice uses current counts, including restored shields. Recent actual insertions can nominate an effect for30s; otherwise idle advice rotates through currently present effects, starting at20s session time with45s minimum subsequent spacing. Clearing/expiring a color prunes pending, queued and active advice for that effect.

## Test evidence

First RED: five tests failed on missing createPlayer API. Implementation: four behavior tests passed, asset validation failed on missing WAV. First actual synthesis: same test failed because reset-black-0 lasted3.105s; analysis measured0.661s trailing silence. Trim/normalization retained speech margins and yielded GREEN5/5. Final command: node --test work/iris/voice.test.cjs. Independent review subsequently identified a stale/current-inventory advice gap. New sixth regression failed with a black tip after full cleansing; current-count pruning and bounded periodic restored-inventory advice fixed it. Final GREEN6/6; original319WAV bytes unchanged.

Tests exercise exact dock/add/remove captions and asset IDs, rejection of queued-only/zero insertion, priority preemption, six-item cap, expired advice/queue deadlines, true threshold versus short restored/skipped threshold, dock/teleport warning cancellation, gesture/global/voice-state gates, pause discarding deadlines, stale completion callbacks, disposal, malformed counts, and every WAV's RIFF/chunk lengths/PCM format/duration/peak. Audio element is faked only at media boundary; real WAV files are parsed. Browser playback and human listening remain parent acceptance, as do exact-byte independent pre-write review and normal armed Git review.
