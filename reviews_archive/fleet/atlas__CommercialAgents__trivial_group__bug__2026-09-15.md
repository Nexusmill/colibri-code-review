# Colibri review - CommercialAgents trivial group (bug, lead confirmation of the 2026-09-10 fork's zero-finding group review)

- model: claude-opus-5 (in-session lead; fork report `_external_raw/group__ca_trivial_group__fork-2026-09-10.md` is INPUT)
- date: 2026-09-15 · mode: bug
- context pack: every file re-hashed today (identical to the fork's bytes); the `__init__.py` files are one-line docstrings; the two `ontology.json` files are static data no code path consumes; `confidence_agent/prompts.py` and `cinematographer_agent/prompts.py` follow the `_get_instructions() -> get_or_push_prompt()` Hub pattern already covered by FLEET-P0-HUB-HARD-DEP; `composer_agent/prompts.py` likewise.

## Verdict
No findings in any of the eleven files (fork and lead agree). sha256 per file:

- `atlas/CommercialAgents/__init__.py` - `fa39eb527c1d2fec24989641ffc8b2b1d617d5a2a713620a73381e26f1da8b44`
- `atlas/CommercialAgents/composer_agent/__init__.py` - `0056e0f8976f2b28d280189362d90f845974b7c7b60ec19bdae895e7125f63c9`
- `atlas/CommercialAgents/composer_agent/prompts.py` - `53c832821bc6a843092a43d3250ca5cb687130b9f6f7177e53dd1f5c64419b93`
- `atlas/CommercialAgents/cinematographer_agent/__init__.py` - `32c577fcc3c3e10c20b1a2f335d7be7c1a34cbd022aa68b1c232ca5629328096`
- `atlas/CommercialAgents/cinematographer_agent/prompts.py` - `fa0128a596ca74dce134f13ff6d453e5b1e1741974621a8e2f5c335644823c40`
- `atlas/CommercialAgents/confidence_agent/__init__.py` - `b3e058631c01a6f8922e6fc5696260126db41099277a6f98848d748da75f4d5c`
- `atlas/CommercialAgents/confidence_agent/prompts.py` - `7f6152db90765a991c408d8a8311b4912797a84714d55dd2ed0952c1af23714e`
- `atlas/CommercialAgents/confidence_agent/ontology.json` - `f9c17a1a62f24d6088cabc17c4d89484c39110fd57348c06ea95fecc33bba11f`
- `atlas/CommercialAgents/director_agent/__init__.py` - `5ddbbc2e1e3fa4a46ce6391e730eec53008bc55ad513a50788b513bcf8683649`
- `atlas/CommercialAgents/research_agent/__init__.py` - `8260a4aba5914db7311af06b746caf625ffa47401d23196bca6df31c9da2639b`
- `atlas/CommercialAgents/research_agent/ontology.json` - `c6be695ed28104eb808208dbb1d9a52e0a64f1bd3c01346eb84fd3b2b62be8af`
