# img2drawing planning index

This directory contains the **current planning control point plus historical vNext execution evidence**.
It is not a second product specification. The deployable drawing authority remains
`skills/img2drawing/SKILL.md` and its `references/` graph.

## Read first

1. [`STATUS.md`](STATUS.md) — current mutable repository truth and open work.
2. [`ROADMAP.md`](ROADMAP.md) — current near-term sequence.
3. [`CONTRACT.md`](CONTRACT.md) — durable architecture invariants for current main.
4. [`../../../CHANGELOG.md`](../../../CHANGELOG.md) — unreleased public changes and known issues.

## Historical records

The rest of this tree is primarily evidence from the B/A vNext buildout and earlier validation planning:

- `slices/`, `capsules/`, and `archive/` — closed implementation/reopen history;
- `A*_*.md`, `B18_IMPLEMENTATION_INVENTORY.md`, `BASELINE.md`, and `R03_RUNTIME_OWNERSHIP_INVENTORY.md` — dated planning/audit records;
- `failure-dossier/` and path-sanitization records — evidence that motivated earlier corrections;
- `VALIDATION_RELEASE.md` — retained validation design, updated so it no longer claims that R23 retirement or v1.0.2 release work is still pending.

Historical records may describe a state that was true at the time they closed. They must not be read as current package/support/runtime truth. When a historical statement conflicts with current `STATUS.md`, current source, or the immutable release record for its version, the historical statement stays historical.

## Current product invariants

- one stage-free `DrawingSession` owns orchestration;
- one authoritative action history feeds render, inspection, replay, and provenance;
- the Agent owns visual judgment; tests do not issue artistic PASS/FAIL;
- construction is provisional and must be revalidated against reference authority or declared intent;
- correction routes by cause and can escalate upstream when a local hypothesis fails;
- instruction routing is dynamically checked from the actual `references/**/*.md` tree;
- current `src` contains no installable R23 runtime/legacy namespace;
- immutable released evidence is never rewritten to describe later `main` changes.

## Current work

See `ROADMAP.md`. The immediate sequence is fresh-worker gesture validation, coordinated inspect/final/replay parity closure, then release/version hardening for the post-v1.0.2 main state.

## Authority order

1. current user direction and actual repository state;
2. `STATUS.md`;
3. deployable skill/runtime source and active tests;
4. `ROADMAP.md` and `CONTRACT.md`;
5. immutable release records for the version they describe;
6. closed slices, capsules, audits, baselines, and archived plans.
