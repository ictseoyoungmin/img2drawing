# img2drawing vNext planning

This directory is the current planning authority for img2drawing vNext. The product is
a general drawing framework, and implementation always follows **Production WIP Limit =
1**.

## Current summary

```text
B00–B16 plus B01-R1/B07-R1 hardening are CLOSED.
B17–B18 complete the remaining product surface.
No fresh visual dogfood starts before the B18 freeze.
B17 package, public API, and release-candidate truth is the sole production WIP.
```

Earlier dogfood exposed enough foundation defects to drive B01-R1 subject-boundary
observation hardening and B07-R1 compact value-region authoring. The plan now completes
B09→B18 in order before running one integrated dogfood campaign. Historical HTML or
temporary plans are design input, not status authority; current HEAD, `STATUS.md`, and
the active slice win.

## Reading order

1. [`STATUS.md`](STATUS.md) — sole WIP and immediate next gate.
2. [`CONTRACT.md`](CONTRACT.md) — architecture invariants and implementation/validation boundary.
3. [`ROADMAP.md`](ROADMAP.md) — implementation order and later dogfood/release phases.
4. [`slices/`](slices/) — B09–B18 execution cards.
5. [`VALIDATION_RELEASE.md`](VALIDATION_RELEASE.md) — D01–D06 and R01–R04 after B18.
6. [`capsules/`](capsules/) — compressed authoritative context for closed work.
7. [`archive/`](archive/) — historical execution cards and reopen history.

Read these only when needed:

- [`BASELINE.md`](BASELINE.md): read-only R23 baseline.
- [`failure-dossier/`](failure-dossier/): evidence that justified the reset.
- [`path-sanitization-GATES.md`](path-sanitization-GATES.md): completed repository-path hygiene.

## Authority order

Resolve conflicts in this order:

1. Current user direction and actual HEAD.
2. `STATUS.md` and the one active `slices/Bxx.md` card.
3. `CONTRACT.md`.
4. `ROADMAP.md` and `VALIDATION_RELEASE.md`.
5. Closed capsules.
6. Archives, failure dossiers, and temporary planning artifacts.

Historical documents remain evidence but cannot override current state. Reopen a closed
slice explicitly before changing its contract.

## Planning invariants

- B09–B18 is a product-surface implementation phase, not a fresh visual-dogfood phase.
- Each implementation slice closes with deterministic fixtures, unit/integration tests,
  preserved evidence, direct review, a capsule, and one dedicated commit.
- B18 freezes the dogfood-ready system. D01–D06 defects reopen the responsible B-slice;
  they do not create parallel workflows.
- `DrawingIntent`, `ModeGuide`, `FinishGuide`, and `StyleGuide` are plain-data authoring
  guidance, not lifecycle cursors or renderer pipelines.
- `StyleGuide` and `RenderProfile` remain separate.
- Tests and schemas do not issue artistic verdicts.
- Mode or style never justifies a second session/history/renderer/inspection tree.
- Physical R23 retirement occurs only at R03 after integrated dogfood and regression.

## Product target

One `DrawingSession`, explicit action/stroke history, renderer, inspection, residual
correction, checkpoint, and replay core serves:

- observed, imaginative, and hybrid reference authority;
- croquis, figure drawing, tonal study, line study, and free-draw modes;
- pose, subject, form-light, and expressive finish intent;
- preset, override, and structured custom style guidance.

```text
observe or declare intent
→ draw
→ render and inspect
→ choose the highest-impact residual
→ correct the responsible authored representation
→ inspect again
→ finish for the declared intent
```
