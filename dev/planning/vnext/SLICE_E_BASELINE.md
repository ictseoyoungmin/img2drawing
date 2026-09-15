# Slice E attention-architecture baseline

Date: 2026-09-15
Scope: structural CI only; no drawing semantics, runtime/renderer behavior, package version, or dogfood verdict changes.

The Slice D cleaned deployable graph establishes the baseline used to select bounded structural ceilings:

- `skills/img2drawing/SKILL.md`: 9,066 bytes on Slice D main; Slice E ceiling 12,000 bytes.
- `skills/img2drawing/references/INDEX.md`: 7,692 bytes on Slice D main; Slice E ceiling 10,000 bytes.
- `SKILL.md` direct reference-leaf routes, excluding `references/INDEX.md`: 13 on the Slice D router; Slice E ceiling 16.

The ceilings intentionally leave bounded maintenance headroom without allowing the root router or index map to regrow into policy textbooks.

Slice E structural gates also require:

- slash-qualified deployable Markdown routes to resolve inside the reference graph;
- canonical policy-owner leaves to remain present and reachable;
- deployable worker guidance to remain independent of `dev/`, `.github/`, and release-control-plane documents;
- the existing sole-entrypoint, direct visual-quality route, direct INDEX map row, reachability, and Slice D ownership tests to remain green.

These budgets are architecture guardrails, not drawing rules. Raising a ceiling later requires an explicit attention-architecture decision rather than incidental instruction growth.
