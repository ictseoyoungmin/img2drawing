# img2drawing vNext roadmap

Updated: 2026-09-05
Workflow: Bottleneck · Production WIP Limit = 1

This roadmap describes the current sequence. Detailed historical closure remains in slice records and capsules; this file should not become an append-only development log.

## Phase A — foundation and product completion

B00–B18 are CLOSED.

Durable result:

```text
one DrawingSession/history core
→ observed / imaginative / hybrid authority
→ stage-free construction and residual correction
→ bounded inspection/evidence
→ compact value authoring
→ intent / mode / style / finish contracts
→ canonical RenderProfile and replay
→ explicit legacy compatibility boundary
→ package / API / schema freeze
```

B18 closed the implementation/release-candidate contract. It did **not** prove fresh visual quality, unseen-subject robustness, or cross-agent reproducibility.

## Phase B — post-freeze alignment before D01 — CLOSED

The instruction-graph audit and exploratory visual evidence exposed a bounded product-surface alignment pass. A1–A6 are now closed; none introduced a second runtime architecture.

| Order | State | Goal |
|---|---|---|
| A1 | CLOSED | repository truth reconciliation across handoff/gates/status/package/changelog |
| A2 | CLOSED | narrow normal public root discovery around `DrawingSession` while preserving compatibility shims |
| A3 | CLOSED | prove current runtime ownership/isolation and classify stage-era modules without cosmetic moves |
| A4 | CLOSED | make residual → leaf → upstream escalation edges explicit in the instruction graph |
| A5 | CLOSED | add only justified high-value guidance leaves for hands/grip and foreshortening/depth |
| A6 | CLOSED | harden major-mass orientation/twist and prevent premature local description/value from masking flat poses |

### A2 — public API surface — CLOSED

Normal users and workers discover `DrawingSession` plus a small declarative facade. Specialized
capability remains in explicit namespaces; pre-rc2 root names are deprecated compatibility
shims. The candidate remains `0.6.0rc2` and no `DrawingSession` method/schema contract changed.

### A3 — physical runtime isolation — CLOSED

The canonical route is mechanically isolated from the historical R23 orchestration cluster:

```text
current
DrawingSession → core + inspection + render + vnext

R23 compatibility
legacy.r23 → run → stages + exemplar + review + registration + historical helpers
```

`img2drawing.inspection` owns current registration/measurement. Physical R23 retirement remains
R03 because moving compatibility implementation before dogfood would add migration risk without
improving the current drawing path.

### A4 — instruction routing edges — CLOSED

`references/review/residual-routing.md` routes visible symptoms by responsible cause rather than
by part name. Repeated local failure, coherent neighboring failures, endpoint conflict,
impossible contact, invented connecting geometry, or concealment by tone/texture trigger
upstream premise inspection rather than more local strokes.

### A5 — high-value drawing leaves — CLOSED

The audit justified focused ownership for local hands/grip and foreshortening/depth while keeping
parent chains, prop topology/contact, contour ownership, observation, and feet in their existing
owners.

Evidence: `A5_DRAWING_LEAF_GAP_HARDENING.md` and
`dev/tests/test_skill_surface_boundary.py`.

### A6 — structural orientation hardening — CLOSED

Exploratory current-version dogfood repeatedly produced locally plausible contours with weaker
whole-pose turn, counter-rotation, asymmetry, and prop/body depth. A6 closes that guidance gap by:

```text
visual observation
  → distinguish tilt from turn / near from far
construction/orientation-and-twist.md
  → own head/ribcage/pelvis turn + counter-rotation
SKILL router
  → require a reversible structural read before local description
croquis
  → broad value / dense hatch off by default
residual routing
  → whole-pose flattening routes upstream
```

A6 changes deployable drawing guidance only. It does not change the frozen runtime/API/schema
contract and does not claim formal D01 success.

Evidence: `A6_STRUCTURAL_ORIENTATION_HARDENING.md` and
`dev/tests/test_skill_surface_boundary.py`.

## Phase C — integrated fresh validation — NEXT

Starts now that A1–A6 are accepted. `VALIDATION_RELEASE.md` owns detailed contracts.

```text
D01 difficult observed croquis    NEXT
D02 observed figure / subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative + hybrid
D06 cross-agent reproducibility
```

Fresh workers receive only the installed/current skill/package, fresh input when applicable,
the user task, declared/inferred intent, and ordinary runtime/output paths. No answer image,
authored coordinates, prior sessions, prior residual priorities, or subject-specific solution
scripts.

A D-case may reopen the responsible B/A premise. Dogfood is validation, not a second architecture layer.

## Phase D — consolidate and release

Starts only after D01–D06 pass.

```text
R01 consolidation      absorb repeated evidence-backed fixes
R02 final regression   modes + resume + correction + PNG/replay/GIF + package
R03 physical R23 retirement / bounded adapter decision
R04 release
```

## Global release exit

Release must directly prove:

- a fresh worker completes `observe/declare → draw → inspect → correct → finish` without Pn;
- observed, imaginative, and hybrid work share one session/history core;
- mode/style differences affect authored behavior rather than metadata or post-filters alone;
- major form, orientation/twist, overlap, grounding, identity, hand/foot/contact, and foreshortened depth survive line/value simplification;
- session cost does not explode through brute-force microstroke accumulation;
- PNG/replay/GIF share canonical renderer provenance and final-state parity;
- public API, package, deployable docs, CI, and support policy tell the same canonical truth;
- no deployable `examples/` directory is required unless representative examples earn that role;
- R23 is absent from the normal route and any retained compatibility window is explicit and tested.

## Authority

- current state: `STATUS.md`
- current program gates: `/GATES.md`
- architecture/release-candidate invariants: B-slice capsules and `dev/release/vnext/`
- A3 runtime ownership audit: `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md`
- A4 routing-edge evidence: `A4_RESIDUAL_ROUTING_HARDENING.md`
- A5 drawing-leaf evidence: `A5_DRAWING_LEAF_GAP_HARDENING.md`
- A6 structural-orientation evidence: `A6_STRUCTURAL_ORIENTATION_HARDENING.md`
- post-alignment dogfood/release: `VALIDATION_RELEASE.md`
- deployable drawing guidance: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
