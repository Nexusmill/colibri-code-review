# colibri bug review - src/components/ModelPicker.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 2cc3289b - 2026-08-25
mode: bug - context: consumers SettingsConsole + CloudPane (SchemaField re-exported); api/modelRoutes + api/catalog contracts read; MediaView branches checked for the artifact-open path; git f9c5a4d/3f395f0 (price-truth + picker-fix era)

## Verdict

Shippable after the two fixes below. The schema-field mapping is thorough and the escape stacking is correct; both defects are value-plumbing races between what the UI shows and what it sends.

## Fixed since this review (same session)

- [MEDIUM] A required enum field without a schema default RENDERED enum[0] as the selected option (SchemaField's value fallback) while values[k] stayed undefined - missingRequired kept RUN disabled with the form looking complete, and the status line named no culprit. FIX: the default-seeding loops (both the replicate detail path and the catalog-schema path) now seed enum[0] when no default exists - the shown value is the sent value.
- [LOW-MEDIUM] The catalog effect had no cancellation: flipping services quickly races two getCloudModels fetches and the stale one could resolve last, replacing the fresh list under the new service's header (rows would OPEN with the wrong service captured). FIX: an alive flag in the effect discards stale resolutions.

## Missing safeguards

- MediaView has no audio-solo branch (`if (!video) return null`), so music-type runs from ModelScreen open as black <video> windows - the current code is the working path; a solo-audio player is a design change, not a fix.
- Multi-image FileReader loop stalls silently if a reader errors mid-batch (onload never fires, onChange never called).

## Verified-correct (adversarial passes, findings deleted)

- Escape stacking (picker's useEscape deactivated while the schema screen is open - no double-close).
- Overlay backdrop click guards (target === currentTarget), route-save error surfacing, canRun gating, price-truth fallbacks (pending/unpublished).
