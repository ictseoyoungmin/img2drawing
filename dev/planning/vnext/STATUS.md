# img2drawing current status

Updated: 2026-09-05

```text
SYSTEM:           product/API/schema/package contract frozen through B18; drawing guidance aligned through A8
PACKAGE:          1.0.0 · DrawingSession/1.0.0-vnext
STABLE BASELINE:  v1.0.0
DEMO EVIDENCE:    GPT-6 Astra observed croquis · 490 actions · 0 fill actions · exact PNG/replay final parity
ACTIVE ON MAIN:   none
NEXT ENGINEERING: v1.0.1 Astra-derived authoring ergonomics, generalized only
FORMAL DOGFOOD:   D01–D06 not started
```

## Current decision

v1.0.0 publishes the current A8-aligned system as a bounded stable baseline. No new drawing
feature is added for the release: package/release identity, documentation, showcase evidence, and
release automation are the only release-surface changes.

The Astra result is strong positive capability evidence. It demonstrates that a capable worker can
use the current instruction graph and runtime to preserve whole-subject orientation, counter-turn,
asymmetry, occlusion/depth, identity-bearing detail, stroke retirement, and deterministic replay
without broad fill. It does **not** retroactively mark D01-D06 as passed and does not justify
shipping the run's subject-specific coordinates or scripts as examples.

## Stable truths

- New work uses one stage-free `DrawingSession` orchestration route.
- The normal package root stays narrow; specialized capability remains in explicit namespaces.
- The deployable skill is `skills/img2drawing/SKILL.md` plus its progressive-disclosure references.
- A6 owns orientation/twist and anti-flattening guidance.
- A7 owns structural specificity and revalidation of inherited construction.
- A8 separates visible evidence, provisional hidden structure, and rendered visible description.
- Croquis keeps broad value/dense regular hatch off by default until structure reads without tone.
- R23 remains explicit compatibility only; physical retirement is still a later bounded decision.
- Mechanical CI proves package/API/persistence/replay contracts, not artistic quality.
- The curated Astra showcase is human-facing evidence, not a worker answer template.

## v1.0.0 evidence boundary

The stable release records the demonstrated session as:

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

The run executed on the release-equivalent A8 baseline whose package identity was still
`0.6.0rc2`; v1.0.0 changes release identity/documentation but not drawing/runtime behavior after
that demonstration.

## Next: v1.0.1

Absorb Astra-derived lessons only where they generalize across subjects and workers. Current
candidates are geometry-preserving stroke retuning, shared curve sampling, continuous-edge pencil
handling, and reusable semantic authoring/correction ergonomics. Subject-specific coordinates,
control-point tables, or solution scripts are forbidden as product knowledge.

After the bounded v1.0.1 absorption pass, resume fresh sealed validation under
`VALIDATION_RELEASE.md`. A real fresh-run failure may reopen the earliest responsible A/B premise.

## Closed foundation

B00–B18 and A1–A8 remain CLOSED. Their detailed evidence stays in slice records, audits,
`dev/evidence/`, and `dev/release/` rather than being duplicated here.

## Authority map

- deployable drawing behavior: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`
- stable release notes: `docs/releases/v1.0.0.md`
- curated demo: `showcase/entries/croquis-sniper-girl-astra-v1/`
- stable package/API/schema/render snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`
- sequence: `ROADMAP.md`
- formal D01–D06 contracts: `VALIDATION_RELEASE.md`
- current gates: `/GATES.md`
- R03 ownership baseline: `R03_RUNTIME_OWNERSHIP_INVENTORY.md`
