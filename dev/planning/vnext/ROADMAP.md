# img2drawing roadmap

Updated: 2026-09-06
Workflow: Bottleneck · Production WIP Limit = 1

## Phase A — product foundation — CLOSED

B00–B18 established one stage-free `DrawingSession`/history core with observed/imaginative/hybrid
authority, residual correction, bounded evidence, value-region authoring, intent/mode/style/finish
contracts, canonical render/replay, package/API/schema freeze, and explicit R23 compatibility.

## Phase B — post-freeze drawing alignment — CLOSED

A1–A8 aligned repository truth, public-root discoverability, runtime isolation, residual routing,
high-value figure/depth guidance, structural orientation, cross-subject structural specificity,
and occlusion inference. No second runtime architecture was introduced.

```text
A1 repository truth
→ A2 public root alignment
→ A3 runtime ownership/isolation
→ A4 cause-based residual routing
→ A5 hands/grip + foreshortening/depth leaves
→ A6 orientation/twist hardening
→ A7 structural specificity + construction revalidation
→ A8 occlusion inference boundary
```

## Phase C — v1.0.0 stable baseline — CLOSED

v1.0.0 promoted the A8-aligned system without adding drawing/runtime behavior after the successful
GPT-6 Astra demonstration. It established a stable evidence boundary rather than claiming formal
cross-agent/cross-subject validation.

Release evidence includes the real reference-versus-drawing comparison, the canonical 124-frame
end-to-end timelapse, a 490-action explicit-stroke session summary, zero fill actions, and exact
canonical PNG/replay final parity.

The subject-specific authoring scripts, coordinates, and control-point notes from the Astra run
remain evidence only and are not shipped as skill examples.

## Phase D — v1.0.1 Astra-derived absorption — CLOSED

A9 absorbs only reusable product lessons exposed by the successful run:

```text
A9
├─ geometry-preserving stroke material retune
│  └─ img2drawing.vnext.retune_stroke()
├─ deterministic shared smooth-curve sampling
│  └─ img2drawing.vnext.sample_catmull_rom()
├─ continuous-edge pencil handling
│  └─ continuous_pencil preset; form_pencil unchanged
├─ semantic authored/correction grouping
│  └─ guidance only; no stage/lifecycle state
└─ geometry-residual vs material-residual discipline
   └─ preserve correct points for material-only corrections
```

The patch uses the existing `replace_stroke` history action for retuning and adds no persisted
action kind or schema. Curve helpers remain authoring aids rather than geometry authority, and
smoothness must stop at real cusps, corners, tangency breaks, component joins, or equivalent
topology changes.

A9 deliberately does **not** copy subject-specific solution geometry, add model-specific code,
automatic artistic scoring, answer-template examples, or a new lifecycle. See
`A9_ASTRA_AUTHORING_ABSORPTION.md`.

## Phase E — fresh integrated validation — NEXT

Run the formal sealed campaign owned by `VALIDATION_RELEASE.md`:

```text
D01 difficult observed croquis
D02 observed figure / subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative + hybrid
D06 cross-agent reproducibility
```

Fresh workers receive the installed/current skill/package, fresh input when applicable, the user
request, declared/inferred intent, and documented runtime/output paths. They do not receive the
Astra answer image, coordinates, scripts, prior session, or evaluator rationale.

A lower-quality worker result does not automatically imply another instruction patch. First
separate product/runtime friction from worker visual-reasoning capability. Reopen the earliest
responsible A/B premise only when fresh evidence identifies a reusable product defect.

## Phase F — consolidation / compatibility / later releases

After evidence justifies it:

```text
R01 consolidate repeated evidence-backed fixes
R02 representative regression
R03 physical R23 retirement or bounded migration-only adapter decision
future release claims limited to demonstrated evidence
```

## Release principles

- a stable version may publish a bounded, explicitly scoped demonstrated capability;
- broader cross-agent/cross-subject claims require the corresponding fresh evidence;
- drawing quality remains Agent-owned rather than mechanically certified;
- package/API/persistence/replay truth must remain deterministic and testable;
- showcase material is evidence for humans, never hidden worker answer geometry;
- one shared runtime and correction model remains the architectural constraint;
- successful-worker mechanics may be absorbed only when they generalize beyond the demonstrated subject.

## Authority

- current state: `STATUS.md`
- stable v1.0.1 notes: `../../../docs/releases/v1.0.1.md`
- A9 absorption record: `A9_ASTRA_AUTHORING_ABSORPTION.md`
- curated Astra demo: `../../../showcase/entries/croquis-sniper-girl-astra-v1/`
- formal D01–D06 contracts: `VALIDATION_RELEASE.md`
- stable contract snapshot: `../../release/vnext/CONTRACT_FREEZE.json`
- deployable drawing guidance: `../../../skills/img2drawing/SKILL.md` + references