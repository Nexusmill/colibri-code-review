# colibri bug review - zipWriter.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 c542eddd - 2026-08-26
mode: bug - context: the Library's SAVE ZIP (byte-exact export promise); zipWriter.test.ts; local/central/EOCD headers verified field-by-field against the PKZip APPNOTE

## Verdict

Shippable - no defects. CRC-32 table is the standard IEEE polynomial; STORE method with compressed==uncompressed; UTF-8 name flag 0x0800; central-directory offsets track exactly; leading-slash names stripped. DOS date/time limits (pre-1980, >2047) would wrap, but entries always pass now().

## Missing safeguards

- zip32 ceilings (65535 entries, 4GB offset) unguarded - the library's selection sizes are far below both.
