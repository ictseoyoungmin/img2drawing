# img2drawing current status

Updated: 2026-09-06

```text
SYSTEM:           product/API/schema/package foundation frozen through B18; drawing guidance aligned through A9
PACKAGE:          1.0.1 · DrawingSession/1.0.1-vnext
STABLE BASELINE:  v1.0.1
DEMO EVIDENCE:    GPT-6 Astra observed croquis · 490 actions · 0 fill actions · exact PNG/replay final parity
ACTIVE ON MAIN:   none after v1.0.1 release merge
NEXT ENGINEERING: fresh sealed D01 validation
FORMAL DOGFOOD:   D01–D06 not started
```

## Current decision

v1.0.1 is a bounded absorption patch over the v1.0.0 Astra-success baseline. It copies no
subject-specific solution geometry. A9 converts demonstrated authoring friction into reusable
mechanics: geometry-preserving stroke retuning, deterministic shared Catmull-Rom sampling, a
low-taper continuous-boundary pencil preset, semantic authoring scope, and an explicit distinction
between geometry and material residuals.

The Astra result remains positive capability evidence rather than a worker answer template. It
demonstrates that a capable worker can preserve whole-subject orientation, counter-turn,
asymmetry, occlusion/depth, identity-bearing detail, stroke retirement, and deterministic replay
without broad fill. It does **not** retroactively mark D01-D06 as passed.

## Stable truths

- New work uses one stage-free `DrawingSession` orchestration route.
- The normal package root stays narrow; specialized capability remains in explicit namespaces.
- The deployable skill is `skills/img2drawing/SKILL.md` plus its progressive-disclosure references.
- A6 owns orientation/twist and anti-flattening guidance.
- A7 owns structural specificity and revalidation of inherited construction.
- A8 separates visible evidence, provisional hidden structure, and rendered visible description.
- A9 separates geometry correction from material retuning, makes curve smoothness topology-aware,
  and absorbs semantic authoring/correction grouping without adding lifecycle state.
- `retune_stroke()` emits the existing replacement history action; no persistence schema was added.
- `sample_catmull_rom()` is an authoring utility, not reference authority.
- `continuous_pencil` is a general low-taper continuity aid; `form_pencil` defaults are unchanged.
- Croquis keeps broad value/dense regular hatch off by default until structure reads without tone.
- R23 remains explicit compatibility only; physical retirement is still a later bounded decision.
- Mechanical CI proves package/API/persistence/replay contracts, not artistic quality.
- The curated Astra showcase is human-facing evidence, not a worker answer template.

## Astra evidence boundary

The stable demonstration remains:

```text
worker:          GPT-6 Astra
reference mode:  observed
drawing mode:    croquis
finish intent:   subject
actions:         490
stroke adds:     358
replacements:    120
deletions:       12
fill actions:    0
replay frames:   124, every_n=4, cursor 0→490
final parity:    canonical PNG == replay final PNG
gif final error: max channel error 1
```

A9 uses only generalized evidence from that run. The task-local scripts, authored coordinates,
control-point tables, and answer image remain excluded from worker-facing product knowledge.

## Next: D01

Resume the fresh sealed validation campaign under `VALIDATION_RELEASE.md`. D01 receives the
current installed skill/package and a fresh difficult observed subject, without the Astra answer
image, coordinates, scripts, prior session, or evaluator rationale.

A real fresh-run failure may reopen the earliest responsible A/B premise. Do not add more guidance
merely because a weaker worker differs from Astra; first distinguish a product defect from worker
visual-reasoning capability.

## Closed foundation

B00–B18 and A1–A9 remain CLOSED. Their detailed evidence stays in slice records, audits,
`dev/evidence/`, and `dev/release/` rather than being duplicated here.

## Authority map

- deployable drawing behavior: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
- stable release notes: `docs/releases/v1.0.1.md`
- A9 absorption record: `A9_ASTRA_AUTHORING_ABSORPTION.md`
- curated demo: `showcase/entries/croquis-sniper-girl-astra-v1/`
- stable package/API/schema/render snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`
- sequence: `ROADMAP.md`
- formal D01–D06 contracts: `VALIDATION_RELEASE.md`
- current gates: `/GATES.md`
- R03 ownership baseline: `R03_RUNTIME_OWNERSHIP_INVENTORY.md`