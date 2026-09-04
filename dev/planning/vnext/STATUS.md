# img2drawing vNext status

Updated: 2026-09-05

```text
SYSTEM:          vNext product/API/schema/package contract frozen through B18 + post-freeze alignment through A8
PACKAGE:         0.6.0rc2 · DrawingSession/0.6.0-vnext
SKILL SURFACE:   stage-free instruction graph with cause-based routing, structural orientation/specificity, and explicit occlusion-inference boundary
ACTIVE ON MAIN:  none
NEXT ENGINEERING: none before fresh validation
NEXT VALIDATION: D01 difficult observed croquis
DOGFOOD:         D01–D06 not started
CLOSED:          B00–B18 + A1 repository truth + A2 public-root alignment + A3 runtime isolation + A4 residual routing + A5 drawing-leaf gaps + A6 structural orientation + A7 structural specificity/inheritance + A8 occlusion inference
```

## Current decision

B18 remains the frozen implementation/release-candidate boundary. A2 intentionally realigned
the package-root discoverability contract without changing the `DrawingSession` methods,
persisted schemas, intent axes, renderer contract, or R23 checkpoint support. The aligned
candidate is `0.6.0rc2`.

A3 audited physical runtime ownership. The canonical vNext route does not import the historical
`run/stages/exemplar/review/registration` cluster. Current registration and bounded measurement
live under `img2drawing.inspection`; historical modules remain R23 compatibility implementation
until the bounded R03 retirement decision. A detailed module-level R03 baseline is now frozen in
`R03_RUNTIME_OWNERSHIP_INVENTORY.md`; it is planning evidence only and does not reopen runtime
engineering before D01.

A4 made the deployable instruction graph operational rather than merely taxonomic: visible
residuals route by the relationship that must change and escalate upstream when a local part is
only a symptom.

A5 closed two high-value guidance gaps with focused leaves for local hands/grip and
foreshortening/depth compression.

A6 responds to repeated exploratory visual evidence that clean local contours can coexist with a
flattened whole pose. The instruction graph now separates tilt from turn, owns head/ribcage/pelvis
orientation and relative twist explicitly, requires a reversible structural read before local
description, and keeps broad croquis value off by default until structure survives without tone.

A7 generalizes the next failure class beyond figures: “defer detail” may not mean “defer structural
specificity,” construction primitives remain provisional rather than geometry authority, and each
descriptive pass must revalidate the parent structure before inheriting it. Detail is classified by
structural role rather than physical size.

A8 closes a distinct ambiguity around occlusion. Hidden structure may be inferred when continuity,
pose, topology, contact, depth, or a downstream visible anchor depends on it, but that provisional
inference must stay separate from visible evidence and from final rendered contour/detail. A
measurement still stops at the occluder; Agent structural reasoning does not have to stop there. No
runtime/API/schema contract changed.

The pre-D01 alignment pass is now complete:

```text
A1 repository truth reconciliation      CLOSED
→ A2 public root API alignment          CLOSED
→ A3 runtime physical-isolation audit   CLOSED
→ A4 instruction routing-edge hardening CLOSED
→ A5 high-value drawing-leaf gaps       CLOSED
→ A6 structural orientation hardening   CLOSED
→ A7 structural specificity/inheritance CLOSED
→ A8 occlusion inference boundary       CLOSED
→ D01 NEXT → D02 → D03 → D04 → D05 → D06
→ R01 → R02 → R03 → R04
```

## Current canonical truths

- New work uses one stage-free `DrawingSession` orchestration route.
- `img2drawing.__all__` is intentionally narrow around session/declarative/construction facade
  names; specialized capabilities live in explicit owning namespaces and old root names are
  deprecated compatibility shims.
- Canonical root import and `DrawingSession` resolution do not activate historical R23
  `run/stages/exemplar/review/registration` orchestration.
- `img2drawing.inspection` owns current stage-free inspection, measurement, and registration.
- Python `img2drawing.review` is historical runtime compatibility machinery; it is not the
  current instruction-graph `references/review/` concept.
- `skills/img2drawing/SKILL.md` is the deployable instruction router and
  `skills/img2drawing/references/INDEX.md` is the progressive-disclosure graph index.
- `references/foundation/structural-specificity.md` owns the cross-subject rule: defer secondary
  detail, not structural specificity; earlier construction is provisional and must be revalidated
  before downstream description inherits it.
- `references/foundation/occlusion-inference.md` owns the cross-subject occlusion boundary:
  visible evidence, provisional hidden structure, and rendered visible description are distinct;
  infer the minimum hidden continuity only when it materially constrains the visible relation.
- `references/review/residual-routing.md` routes symptoms by cause and upstream responsibility,
  including the difference between an occlusion-continuity failure and a local visible-edge
  failure.
- `references/construction/orientation-and-twist.md` owns major-mass turn, near/far planes,
  counter-rotation, and whole-pose flattening/symmetry drift without becoming a runtime stage.
- `references/figure/hands-and-grip.md` owns local visible hand/grip geometry only after the
  parent arm relation is credible; exact hidden digits are not fabricated, while a needed hidden
  hand/contact relation may still be inferred provisionally.
- `references/construction/foreshortening-and-depth.md` owns projected spacing, depth order,
  overlap, and terminal orientation without unfolding expected hidden length into visible contour.
- Measurement tools stop at occlusion. They may constrain visible entry/reappearance anchors but
  cannot prove an exact hidden path; Agent inference remains relational and provisional.
- Croquis economizes marks, not observed geometry, and broad value/dense hatch is off by default
  until the structural read remains credible without tone.
- A small feature may be structurally necessary when it decides orientation, contact, scale,
  identity, topology, or another high-impact relation; detail is not classified by size alone.
- `skills/img2drawing/examples/` remains intentionally absent until a representative example
  earns instructional authority.
- The frozen vNext control-plane contract lives at `dev/release/vnext/CONTRACT_FREEZE.json`.
- R23 physical retirement remains R03 work; its pre-D01 module ownership baseline is
  `R03_RUNTIME_OWNERSHIP_INVENTORY.md`.
- Mechanical CI proves package/API/persistence/integration/instruction-surface contracts, not
  artistic quality or unseen-subject generalization.

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

Detailed closure evidence remains in capsules, slice records, tests, `dev/evidence/`, and
`dev/release/`; this file is the current control-plane summary.

## Pre-D01 alignment ownership

### A1. Repository truth reconciliation — CLOSED

Current handoff/gates/status/roadmap/validation/package notes tell one route.

### A2. Public root API surface — CLOSED

Normal discovery is centered on `DrawingSession`; specialized public capability is explicit and
pre-rc2 root imports are compatibility shims. See `A2_PUBLIC_ROOT_API_AUDIT.md`.

### A3. Runtime physical-isolation audit — CLOSED

Current runtime ownership is isolated from the historical R23 orchestration cluster without
cosmetic file moves. See `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md`. The detailed retirement
inventory is `R03_RUNTIME_OWNERSHIP_INVENTORY.md` and remains dormant until post-D01–D06/R02.

### A4. Instruction routing-edge hardening — CLOSED

Residuals route by cause, with explicit upstream escalation signals. See
`A4_RESIDUAL_ROUTING_HARDENING.md`.

### A5. Drawing-leaf gaps — CLOSED

Two focused leaves remain: local hands/grip and cross-cutting foreshortening/depth. See
`A5_DRAWING_LEAF_GAP_HARDENING.md`.

### A6. Structural orientation hardening — CLOSED

Exploratory visual evidence showed repeated whole-pose flattening despite locally plausible
contours. The graph now owns turn/near-far/counter-rotation explicitly, requires a reversible
structural read before description, and prevents broad croquis value from hiding unresolved
structure. See `A6_STRUCTURAL_ORIENTATION_HARDENING.md`.

### A7. Structural specificity and construction inheritance — CLOSED

The graph now generalizes structure-before-detail across subject classes. Secondary detail may be
deferred; placement/orientation/proportion/envelope/width-depth/overlap/contact/negative-space and
connected-part relations may not be genericized. Earlier construction remains provisional and is
revalidated before later description inherits it. See `A7_STRUCTURAL_SPECIFICITY_INHERITANCE.md`.

### A8. Occlusion inference boundary — CLOSED

The graph now distinguishes “not visibly rendered” from “not structurally inferred.” Important
hidden continuity may be reasoned about provisionally from visible anchors, while exact hidden
appearance remains unsupported unless observed. Measurement does not cross the occluder and final
contour does not claim the hidden interval. See `A8_OCCLUSION_INFERENCE_BOUNDARY.md`.

## Post-alignment validation

`VALIDATION_RELEASE.md` owns D01–D06. D01 is now the next bottleneck. It must start from a
newly sealed input and may reopen the responsible implementation/guidance premise when fresh
visual evidence exposes a real defect.

No current document should claim D01–D06 quality, cross-agent reproducibility, or final release
readiness before that evidence exists.

## Authority map

- deployable drawing behavior: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
- current project state: this file
- sequence: `ROADMAP.md`
- A3 ownership evidence: `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md`
- R03 module ownership baseline: `R03_RUNTIME_OWNERSHIP_INVENTORY.md`
- A4 routing evidence: `A4_RESIDUAL_ROUTING_HARDENING.md`
- A5 guidance evidence: `A5_DRAWING_LEAF_GAP_HARDENING.md`
- A6 structural-orientation evidence: `A6_STRUCTURAL_ORIENTATION_HARDENING.md`
- A7 structural-specificity evidence: `A7_STRUCTURAL_SPECIFICITY_INHERITANCE.md`
- A8 occlusion-inference evidence: `A8_OCCLUSION_INFERENCE_BOUNDARY.md`
- D01–D06 / release contracts: `VALIDATION_RELEASE.md`
- current program gates: `/GATES.md`
- frozen vNext release-candidate contract: `dev/release/vnext/`
- historical release/compatibility evidence: `dev/release/r23/`, older records, and Git history
