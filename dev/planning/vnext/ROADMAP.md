# img2drawing vNext roadmap

Updated: 2026-09-03
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

## Phase B — post-freeze alignment before D01

The instruction-graph audit exposed a small set of product-surface mismatches that should be closed before fresh dogfood. These are maintenance/hardening tasks, not new runtime architecture slices.

| Order | State | Goal |
|---|---|---|
| A1 | CLOSED | repository truth reconciliation across handoff/gates/status/package/changelog |
| A2 | CLOSED | narrow the normal public root API around `DrawingSession` while preserving compatibility shims |
| A3 | CLOSED | prove current runtime ownership/isolation and classify stage-era modules without cosmetic moves |
| A4 | CLOSED | make residual → leaf → upstream escalation edges explicit in the instruction graph |
| A5 | NEXT | harden only high-value missing drawing leaves such as hands/grip and foreshortening |

A1–A5 follow the same bottleneck rule: solve the highest-impact mismatch without creating a parallel workflow. If an audit proves a closed B-slice premise wrong, reopen that premise narrowly instead of inventing an A-specific runtime feature.

### A2 — public API surface — CLOSED

The accepted mental model is:

```text
normal worker/user
    ↓
DrawingSession + declarative root contracts
    ↓
explicit specialized namespaces only when needed
    ↓
legacy compatibility only through explicit legacy boundary
```

`img2drawing.__all__` now contains only the canonical root route plus the small observed-construction facade. Inspection/observation/vNext/core capability remains available from its owning namespace, and pre-rc2 root names resolve through deprecated lazy shims rather than disappearing. The aligned candidate is `0.6.0rc2`; the `DrawingSession` method/schema contracts remain unchanged.

### A3 — physical runtime isolation — CLOSED

A3 separates instruction vocabulary from runtime package ownership. The source tree does not
need a one-to-one folder match with the instruction graph.

The canonical route is mechanically isolated from the historical R23 orchestration cluster:

```text
current
DrawingSession → core + inspection + render + vnext

R23 compatibility
legacy.r23 → run → stages + exemplar + review + registration + other historical helpers
```

`img2drawing.inspection` owns current registration/measurement capability. The generic
`img2drawing.registration` package is historical R23 comparison machinery. Likewise, the
instruction-graph `review` concept is current, while the Python `img2drawing.review` package is
historical stage-review/pass-memory/resolved-form implementation.

`run.py`, `stages/`, `exemplar/`, `review/`, and `registration/` remain physically present only
because they back explicit compatibility. Moving them before dogfood would create migration-only
risk without changing the current path, so final deletion/consolidation stays in R03.

Evidence: `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md` and
`dev/tests/test_runtime_physical_isolation.py`.

### A4 — instruction routing edges — CLOSED

The instruction graph now routes visible residuals by responsible cause rather than by the noun
that appears wrong. `references/review/residual-routing.md` provides compact conditional routes
for foot/shoe, head/face, hand/grip, props, silhouette/overlap, clothing/folds, grounding, and
value/tonal residuals.

Representative route:

```text
foot looks wrong
├─ parent leg axis/stance wrong → construction/balance-and-limbs
├─ ground relation wrong       → environment/ground-and-context
├─ local shoe geometry wrong   → figure/legs-feet
└─ contact ownership wrong     → description/contour-and-overlap
```

Repeated local failure, coherent neighboring failures, endpoint conflict, impossible contact,
invented connecting geometry, or concealment by tone/texture are explicit upstream-escalation
signals. These are conditional routing edges inside the existing loop, not sequential drawing
stages. `INDEX.md` remains compact and sends workers to the dedicated routing leaf only when the
cause is uncertain.

Evidence: `A4_RESIDUAL_ROUTING_HARDENING.md` and
`dev/tests/test_skill_surface_boundary.py`.

### A5 — remaining drawing leaves — NEXT

Add guidance only when a recurring visual failure cannot be expressed cleanly by an existing leaf. Hands/grip and foreshortening are current candidates because they combine structure, contact, overlap, and identity. Avoid encyclopedic anatomy content.

A5 should first determine whether each candidate truly needs a separate leaf or whether a focused
hardening of the existing `torso-arms-hands`, `balance-and-limbs`, `contour-and-overlap`, and
`attached-objects` guides is sufficient. Prefer the smaller change that improves worker behavior.

## Phase C — integrated fresh validation

Starts after A1–A5 are accepted. `VALIDATION_RELEASE.md` owns detailed contracts.

```text
D01 difficult observed croquis
D02 observed figure / subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative + hybrid
D06 cross-agent reproducibility
```

Fresh workers receive only the installed/current skill/package, fresh input when applicable, the user task, declared/inferred intent, and ordinary runtime/output paths. No answer image, authored coordinates, prior sessions, prior residual priorities, or subject-specific solution scripts.

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
- major form, overlap, grounding, identity, and contact survive line/value simplification;
- session cost does not explode through brute-force microstroke accumulation;
- PNG/replay/GIF share canonical renderer provenance and final-state parity;
- public API, package, deployable docs, CI, and support policy tell the same canonical truth;
- no deployable `examples/` directory is required for release unless representative examples have actually earned that role;
- R23 is absent from the normal route and any retained compatibility window is explicit and tested.

## Authority

- current state: `STATUS.md`
- current program gates: `/GATES.md`
- architecture/release-candidate invariants: existing B-slice capsules and `dev/release/vnext/`
- A3 runtime ownership audit: `A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md`
- A4 routing-edge evidence: `A4_RESIDUAL_ROUTING_HARDENING.md`
- post-alignment dogfood/release: `VALIDATION_RELEASE.md`
- deployable drawing guidance: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
