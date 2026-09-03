# img2drawing vNext status

Updated: 2026-09-03

```text
SYSTEM:          vNext product/API/schema/package contract frozen through B18 + A2 root alignment
PACKAGE:         0.6.0rc2 · DrawingSession/0.6.0-vnext
SKILL SURFACE:   stage-free instruction graph; deployable examples removed
ACTIVE ON MAIN:  none
NEXT ENGINEERING: instruction routing-edge hardening
NEXT VALIDATION: D01 difficult observed croquis, after the pre-D01 alignment pass
DOGFOOD:         D01–D06 not started
CLOSED:          B00–B18 + A1 repository truth + A2 public-root alignment + A3 runtime isolation audit
```

## Current decision

B18 remains the frozen implementation/release-candidate boundary. A2 intentionally realigned
the package-root discoverability contract without changing the `DrawingSession` methods,
persisted schemas, intent axes, renderer contract, or R23 checkpoint support. The aligned
candidate is `0.6.0rc2`.

A3 then audited physical runtime ownership. The canonical vNext route does not import the
historical `run/stages/exemplar/review/registration` cluster. Current registration and bounded
measurement live under `img2drawing.inspection`; the generic historical modules remain only as
R23 compatibility implementation. Renaming/deleting that cluster before dogfood would add
migration risk without improving the current drawing path, so the bounded retirement decision
remains R03 work.

This is a **pre-D01 alignment pass**, not a second architecture and not a return to Pn/R23
development:

```text
A1 repository truth reconciliation      CLOSED
→ A2 public root API alignment          CLOSED
→ A3 runtime physical-isolation audit   CLOSED
→ A4 instruction routing-edge hardening NEXT
→ A5 high-value drawing-leaf gaps
→ D01 → D02 → D03 → D04 → D05 → D06
→ R01 → R02 → R03 → R04
```

## Current canonical truths

- New work uses one stage-free `DrawingSession` orchestration route.
- `img2drawing.__all__` is intentionally narrow: normal root discovery exposes session,
  declarative intent/reference/render inputs, and the small observed-construction facade.
- Specialized inspection/observation/vNext/core capability remains importable from explicit
  owning namespaces; pre-rc2 root names survive only as deprecated lazy compatibility shims.
- Canonical root import and `DrawingSession` resolution do not activate `img2drawing.run`,
  `stages`, `exemplar`, the historical `review` package, or the historical `registration`
  package.
- `img2drawing.inspection` owns current stage-free inspection, measurement, and registration.
- The Python package `img2drawing.review` is R23 stage-review compatibility machinery; it is
  not the same thing as the current instruction-graph `references/review/` concept.
- `skills/img2drawing/SKILL.md` is the deployable instruction router.
- `skills/img2drawing/references/INDEX.md` is a progressive-disclosure routing graph, not a lifecycle.
- Croquis economizes marks, not observed geometry; construction abstractions are hypotheses,
  not final forms.
- `skills/img2drawing/examples/` is intentionally absent until a representative example is
  good enough to teach from.
- The frozen vNext control-plane contract lives at `dev/release/vnext/CONTRACT_FREEZE.json`.
- R23 remains explicit compatibility/history material. Physical retirement is deferred to the
  release-hardening path unless D-case evidence requires a narrower earlier fix.
- Mechanical CI proves package/API/persistence/integration contracts, not artistic quality or
  unseen-subject generalization.

## Closed implementation truth — B00 through B18

| Slice | State | Durable result |
|---|---|---|
| B00 | CLOSED | frozen R23 baseline and failure dossier |
| B01 | CLOSED | vNext architecture cut; preserve capabilities, remove ceremony |
| B01-R1 | CLOSED | subject observation/boundary hardening |
| B02+B03 | CLOSED | immutable inspection + bounded measurement foundation |
| B04 | CLOSED | stage-free `DrawingSession`, checkpoint/resume |
| B05 | CLOSED | construction grammar without runtime stage gate |
| B06 | CLOSED | Agent-owned residual/correction loop with provenance |
| B07 | CLOSED | bounded evidence budget + telemetry |
| B07-R1 | CLOSED | value-region authoring, compaction, form-before-value |
| B08 | CLOSED | orthogonal intent/mode/style scaffold |
| B09 | CLOSED | finish / relational recognition authoring |
| B10 | CLOSED | intent/state/inspection-bound completion |
| B11 | CLOSED | canonical `RenderProfile`, replay, PNG/GIF parity contract |
| B12 | CLOSED | explicit legacy compatibility boundary |
| B13 | CLOSED | observed/imaginative/hybrid reference authority |
| B14 | CLOSED | drawing-mode capability completion |
| B15 | CLOSED | style authoring completion |
| B16 | CLOSED | authored-element lookup/edit ergonomics |
| B17 | CLOSED | package/public API/release-candidate integration |
| B18 | CLOSED | dogfood-ready machine-readable contract freeze |

Detailed closure evidence remains in `capsules/`, slice records, tests, `dev/evidence/`, and
`dev/release/`. This status file is the current control-plane summary, not a duplicate archive.

## Pre-D01 alignment ownership

### A1. Repository truth reconciliation — CLOSED

Root handoff/gates, this status, roadmap, validation plan, package notes, and changelog are
aligned to the current main-line product model. Stale R21 package-root records are historical
and do not own current package truth.

### A2. Public root API surface — CLOSED

Normal users and Agents now discover one package-root mental model centered on
`DrawingSession`. Low-level/history/schema/inspection names remain available in explicit
public namespaces and through deprecated pre-rc2 root shims for compatibility, but are not
advertised in `__all__` or normal `dir(img2drawing)` discovery. See
`A2_PUBLIC_ROOT_API_AUDIT.md` and `dev/release/vnext/SUPPORT.md`.

### A3. Runtime physical-isolation audit — CLOSED

The canonical vNext import path is mechanically isolated from the historical R23 orchestration
cluster. `run.py`, `stages/`, `exemplar/`, the old runtime `review/`, and the old runtime
`registration/` are compatibility implementation; current registration is owned by
`inspection`. See `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md` and
`dev/tests/test_runtime_physical_isolation.py`.

Physical retirement is intentionally deferred to R03 because those paths still back explicit
R23 compatibility. A3 closes ownership ambiguity, not the compatibility window.

### A4. Instruction routing-edge hardening — NEXT

Goal: make common residual escalation explicit, e.g. local foot mismatch → leg chain/ground
premise when needed, rather than treating the reference tree as a flat taxonomy.

### A5. Drawing-leaf gaps

Goal: add only evidence-backed leaves that materially improve worker behavior, with hands/grip
and foreshortening currently the clearest candidates. Do not grow a comprehensive anatomy textbook.

## Post-alignment validation

`VALIDATION_RELEASE.md` owns D01–D06. D01 is the first fresh visual validation after the
alignment pass. It must start from a newly sealed input and may reopen the responsible
implementation/guidance premise when it exposes a real defect.

No current document should claim D01–D06 quality, cross-agent reproducibility, or final release
readiness before that evidence exists.

## Authority map

- deployable drawing behavior: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
- current project state: this file
- sequence: `ROADMAP.md`
- A3 ownership evidence: `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md`
- D01–D06 / release contracts: `VALIDATION_RELEASE.md`
- current program gates: `/GATES.md`
- frozen vNext release-candidate contract: `dev/release/vnext/`
- historical release/compatibility evidence: `dev/release/r23/`, older release records, and Git history
