# Colibri review — src/jcodemunch_mcp/secret_classifier.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\secret_classifier.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `491b8b86709c54a1708604aa0df56fc9b51b349b1b71ab31d0307dd6bb807249` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline of the classifier and of `tests/test_secret_classifier.py` (the ORACLE table idiom); the pattern tables and `classify_secret_file` (lines 76-171, 215-310) read in full; `SECURITY.md` "Secret Exclusion" (the sub-agent's no-drift claim re-checked: it mirrors the tables exactly, so every table change must land in the doc in the same commit); the single consumer `security.is_secret_file` (fan-out to index_file/index_folder/index_repo); the audit probe re-run on these bytes (18/20 checks RED). No prior `.colibri_reviews` record.

## Verdict
The classifier is a filename/path deny-table by design and its tables missed several of the best-known plaintext credential files, so those files were indexed and made searchable. Fixed in the commit carrying this record (tables + SECURITY.md + oracle rows). The sub-agent's "5 HIGH + 1 MEDIUM" is ONE finding class counted per filename; recorded here as one MEDIUM-HIGH plus one MEDIUM, which is what it is.

## Bugs & vulnerabilities
**[MEDIUM-HIGH] Well-known plaintext credential files absent from `EXACT_CREDENTIAL_NAME_PATTERNS` — CONFIRMED — FIXED** - `line 80-90` (pre-fix numbering)
- What: `.git-credentials` (git credential-store, PATs in clear), `.pgpass` (PostgreSQL passwords), `.my.cnf` (`[client] password=`), `.s3cfg` / `.boto` (AWS keys, s3cmd/legacy boto), and Terraform CLI credentials (`credentials.tfrc.json`, plus `.terraformrc` / `terraform.rc`, whose `credentials` blocks carry the same token) were not in the table, while their peers `.netrc` / `.npmrc` / `.pypirc` were.
- Trigger: any indexed tree containing one of these files (home-directory-shaped repos, dotfiles repos, ops repos, container build contexts).
- Impact: the file's contents are indexed and retrievable through every search tool — the exact outcome the classifier exists to prevent. Confirmed via both the classifier and the `security.is_secret_file` wrapper (probe checks 1-14 RED).
- Fix: the eight names added to `EXACT_CREDENTIAL_NAME_PATTERNS` (group `exact_credential_names`, confidence high); `SECURITY.md` updated in the same commit so doc and code stay byte-consistent; 11 oracle rows + 4 negative controls (`my.cnf`, `boto.py`, `docs/secrets-overview.adoc`, `release.tar.gz.asc`).
- Judgement call recorded: `.terraformrc` / `terraform.rc` can be pure provider-mirror config with no credentials; excluding them from the index is the same conservative trade the table already makes for `.npmrc`.

**[MEDIUM] `.asc` in `DOCUMENTATION_EXTENSIONS` waves PGP-armoured private-key exports past the broad `secret` basename group — CONFIRMED — FIXED** - `line 165-168, 299-308` (pre-fix numbering)
- What: `gpg --export-secret-keys --armor > secret-key.asc` is the canonical export shape; group 6 would flag `secret-key.asc` / `secrets.asc` by the `secret` token, but the doc-extension exemption fired first because `.asc` was listed as legacy AsciiDoc.
- Fix: `.asc` removed from the doc set (comment explains why). Detached signatures (`release.tar.gz.asc`) stay not-secret — they carry no `secret` token — pinned by a control row. Genuine AsciiDoc named with a `secret` token now gets excluded from indexing; acceptable for an ambiguous legacy extension.
- Limitation (not fixable by a filename-only classifier, recorded so it is not re-reported): a private-key export named without the token (`mykey.asc`) is still indexed. Adding `*.asc` to the extension group would exclude every detached signature and AsciiDoc file; rejected.

## Refuted (sub-agent's own, re-checked and agreed)
- "`_is_template_name` exemption applied inconsistently across groups" — the exemption only ever forces not-secret; its absence in groups 1/3/5 makes them strictly more conservative.
- "SSH patterns miss `id_ed25519_prod`" — `ssh-keygen` never produces that shape; `id_ed25519.*` covers the real renames (`.old`, `.bak`).

## Adversarial verification (Phase 3)
- Verified each missing name against the tool's own documentation of the file's role (git credential-store, libpq `.pgpass`, MySQL option files, s3cmd, boto2, Terraform CLI config) rather than the sub-agent's assertion; all carry credentials in clear by design.
- Checked precedence: the new exact names sit in group 2 and cannot be shadowed by group 1 path patterns; `home/.git-credentials` resolves through the basename path like `.npmrc` does.
- Ran the full secret/security suites (279) and the probe (20/20) after the change.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `e714530dc44552cd2acce9f34dd2ba2d216bd771ad445ecc36b16f2afe3a2899`. TDD: 11 ORACLE rows RED on the old bytes (all `not_secret`), GREEN after; 4 new negative controls green throughout; `tests/test_secret_classifier.py` 97/97.
