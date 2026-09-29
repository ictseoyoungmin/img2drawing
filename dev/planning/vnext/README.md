# img2drawing planning index

This directory contains the **current planning control point plus historical vNext execution evidence**.
It is not a second product specification. The deployable drawing authority remains
`skills/img2drawing/SKILL.md` and its `references/` graph.

## Read first

1. [`STATUS.md`](STATUS.md) — current mutable repository truth and open work.
2. [`ROADMAP.md`](ROADMAP.md) — current near-term sequence and closed release-cycle handoff.
3. [`CONTRACT.md`](CONTRACT.md) — durable architecture invariants for current main.
4. [`../../../CHANGELOG.md`](../../../CHANGELOG.md) — released public history and maintenance notes.

## Historical records

The rest of this tree is primarily evidence from the B/A vNext buildout and earlier validation planning:

- `slices/`, `capsules/`, and `archive/` — closed implementation/reopen history;
- `A*_*.md`, `B18_IMPLEMENTATION_INVENTORY.md`, `BASELINE.md`, and `R03_RUNTIME_OWNERSHIP_INVENTORY.md` — dated planning/audit records;
- `failure-dossier/` and path-sanitization records — evidence that motivated earlier corrections;
- `VALIDATION_RELEASE.md` — retained historical/reusable validation design from the published v1.0.3 baseline; it is not current release authority.

Historical records may describe a state that was true at the time they closed. They must not be read as current package/support/runtime truth. When a historical statement conflicts with current `STATUS.md`, current source, or the immutable release record for its version, the historical statement stays historical.

## Current product invariants

- one stage-free `DrawingSession` owns orchestration;
- one authoritative action history feeds render, inspection, replay, and provenance;
- the Agent owns visual judgment; tests do not issue artistic PASS/FAIL;
- construction is provisional and must be revalidated against reference authority or declared intent;
- correction routes by cause and can escalate upstream when a local hypothesis fails;
- instruction routing is dynamically checked from the actual `references/**/*.md` tree;
- current `src` contains no installable R23 runtime/legacy namespace;
- current `src/**/*.py` module basenames are semantic rather than renderer-generation tagged;
- immutable released evidence is never rewritten to describe later `main` changes.

## Current work

The v1.0.3 and v1.1.0 release cycles are closed. M01 closes the post-v1.1.0 public-contract/release-hygiene maintenance as **GitHub Release v1.1.1** with its additive freeze, release notes, wheel, and sdist. No next bottleneck is selected; later work must begin from new evidence or a new product requirement in `ROADMAP.md`.

## Authority order

1. current user direction and actual repository state;
2. `STATUS.md`;
3. deployable skill/runtime source and active tests;
4. `ROADMAP.md` and `CONTRACT.md`;
5. immutable release records for the version they describe;
6. closed slices, capsules, audits, baselines, and archived plans.
