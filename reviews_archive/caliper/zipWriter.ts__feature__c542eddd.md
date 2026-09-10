# Colibri review — zipWriter.ts (feature)

- **Source:** `zipWriter.ts` · **sha256:** c542eddd
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the dependency-free STORE zip writer behind library export (vite.library); the honesty note (media doesn't compress; byte-exact copies ARE the contract); consumed only by vite.library + tests; unchanged since 2026-08-25-era.

## What this module does

86 lines of PKZip spec: table-driven CRC-32, local file headers with the UTF-8 name flag, the central directory, end-of-central-directory, DOS datetime encoding — enough for every OS unzipper, zero dependencies, STORE method by doctrine (no re-encode, no compression theater on media).

## Suggested add-ons

**A zip64 marker comment** — Value Low · Effort S
- Films can exceed 4 GB of footage; the classic EOCD caps at 4 GiB/65,535 entries with no error — a silently corrupt archive at the boundary. A build-time guard (throw when total > 4 GiB − 1) turns a silent corruption into an honest refusal until zip64 is ever needed. One length check in buildZip.

## Nice-to-haves

- DEFLATE is deliberately absent and correct (media); directory entries for empty folders are unrepresented — exports never contain empty folders. Nothing to add; the file is exactly its size.
