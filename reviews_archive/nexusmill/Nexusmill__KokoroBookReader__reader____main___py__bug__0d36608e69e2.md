# scan 0d36608e69e2 (batch batch-1790108168-DvQpbUet9uEcAXD4QsVf via z-ai/glm-5.3:batch)

Scanned all three files. `__main__.py` is a trivial entry point — clean. `library.py`: the import transaction (temp copy → digest re-verify → atomic `os.replace` → insert with rollback-unlink), dedup, suffix/identity validation, position bounds, voice/rate validation, and payload reconstruction all check out; the except-path unlink condition is correct for every single-process failure mode (only a multi-process, different-extension, identical-hash concurrent import could strand an orphan file — too contrived to block on). `playback.py`: I traced session/serial token guards, `_invalidate` ordering (session bump → cancel → stop → release), offset clamping in every branch, the look-ahead window, fresh vs. non-fresh activation, pause/seek/voice-change/rate flows, and `ended` advancement — all correct. One real defect remains in the error path:

**Finding 1 — synthesis failures are completely silent; the error message is discarded.**
- **File:** `KokoroBookReader/reader/playback.py`
- **Line:** 136–147 (`failed()`; the `message` parameter is never used anywhere in the body)
- **Trigger:** The speech service reports a synthesis failure (engine/model error, voice-resolution failure for `index:cast`, resource exhaustion) for the current sentence or a look-ahead sentence, invoking `failed(session, request, message)`.
- **Impact:** The user gets zero feedback. `message` is dropped, and `self.notice` — the controller's only user-facing feedback channel, which `audio_ready()` uses even for the far milder "audio regenerated" case — is never set, so playback just pauses (current-sentence failure) or stalls mid-book with silence when it reaches a failed look-ahead gap. Additionally, when only a look-ahead request fails, neither `pause()` branch executes, so `changed()` is never called: any UI state derived from the controller (pending/buffering indicators) goes stale, and the failure stays invisible until playback hits the gap. The retry that eventually occurs (on `play()`/`ended` → `_request`) only happens after the user notices the unexplained stop and intervenes.
- **Concrete fix:** Route the failure through the notice channel and always notify observers:

```python
def failed(self, session, request, message):
    if session != self.session:
        return
    indices = [i for i, r in self.pending.items() if r.request == request]
    for i in indices:
        del self.pending[i]
    hit_active = request == self.active
    if hit_active:
        self.active = None
        self.loaded_result = None
    if hit_active or self.sentence in indices:
        self.notice = message or "Speech synthesis failed."
        self.pause()      # pause() already invokes changed()
    else:
        self.changed()    # look-ahead pending state changed; refresh UI
```

VERDICT: BLOCK
