# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

The v1.0.3 release cycle is closed. New work begins from the published v1.0.3 baseline and must not mutate its tag, wheel, freeze, or historical evidence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 added general authoring ergonomics.
- v1.0.2 promoted the exact local-first timelapse backend.
- post-v1.0.2 cleanup physically retired the R23 runtime/legacy cluster.
- renderer v10 closed seed/parity and broad authored-value issues.
- G01 closed gesture/runtime/instruction integration gaps.
- G02 closed the broad-pencil square-terminal / weak-graphite failure class with the renderer family now published as `pillow-pencil-contact-v11 / 1`.
- G03–G06 integrated, froze, verified, and published `v1.0.3 / A14`.

## Current sequence

```text
G01 gesture behavior validation                         CLOSED
G02 broad-pencil material/terminal hardening            CLOSED
G03 integrate validated rc3 into main                   CLOSED
G04 stable-promotion decision                           CLOSED → v1.0.3
G05 stable freeze + wheel verification                  CLOSED
G06 explicit publish manifest + publish                 CLOSED
Q01 v11 quality-control failure taxonomy + design       ACTIVE
Q02 instruction graph execution-gate patch              BLOCKED by Q01
Q03 fresh-worker visual dogfood                         BLOCKED by Q02
Q04 classify remaining geometry vs material residuals   BLOCKED by Q03
Q05 current-v11 renderer correction if still required   BLOCKED by Q04
Q06 contract-digest / replay-boundary migration         REQUIRED before release
Q07 full visual + mechanical validation                 BLOCKED by Q05/Q06
Q08 choose next package version / release candidate     BLOCKED by Q07
```

**No renderer v12 is authorized by this roadmap.** The abandoned PR #48 demonstrated why treating renderer generations as a patch counter would accumulate v12/v13/... without closing the actual drawing-quality bottleneck.

## Q01 — v11 quality-control redesign — ACTIVE

Authority: `V11_QUALITY_CONTROL_REDESIGN.md`.

Recent outputs show a repeated gap between what the skill says and what a worker actually accepts:

- parallel hair strands appear before hair mass/clump structure is convincingly solved;
- arms, legs, trousers, and attached objects can collapse into rails/tubes;
- feet and props become recognizable symbols instead of observed construction;
- construction/search lines remain because retirement is advisory rather than audited;
- line hierarchy remains weak despite semantic roles;
- strong camera perspective can enlarge the head without coherently propagating depth through torso/pelvis/limbs;
- generic context lines appear without a clear visible owner;
- local detail can accumulate while the whole remains generic or flat.

The skill already contains many correct principles. Q01 therefore does not solve the problem by adding more warnings. It redesigns **decision closure** around reversible visual evidence gates.

### Q01 target

Each semantic group must be accepted only after evidence establishes:

```text
visible authority
→ neighboring anchors
→ physical/semantic owner
→ geometry claim
→ mark-language choice
→ fresh render
→ anti-symbol / hierarchy / retirement audit
→ whole-subject recheck
→ accept, revise, or reopen
```

The design also separates renderer-family identity from exact historical pixel identity so quality corrections do not require a new renderer number.

## Q02 — instruction graph patch — BLOCKED

Planned concentrated edits rather than leaf proliferation:

- add one central `review/visual-quality-gates.md` leaf;
- strengthen `SKILL.md` canonical loop;
- add ownership continuity to line economy;
- add depth-group/anchor evidence to observation;
- harden hair mass → clump → accent sequencing;
- reject rail completion for limbs;
- bind prop construction to body contact;
- reject ownerless environment/context rays;
- convert stroke retirement into KEEP/SOFTEN/RETIRE audit;
- require largest-remaining-residual ranking before finish.

## Q03 — fresh-worker dogfood — BLOCKED

Dogfood must use workers that receive the updated skill, reference, and normal runtime surface without privileged access to prior solution strokes.

Minimum visual classes:

1. strong-perspective/close figure;
2. full-body 3/4 figure with attached/held prop;
3. frontal or near-frontal full body;
4. head/hair close-up.

The supplied recent outputs define the failure classes, not answer templates.

## Q04 — residual ownership decision — BLOCKED

After the instruction patch, re-run the visual tasks. Remaining problems must be classified before renderer work:

```text
wrong path / proportion / ownership / overlap / contact → geometry/instruction
correct geometry but wrong weight/taper/terminal/grain   → material/runtime
```

Renderer changes are forbidden while the visible problem can still be explained by incorrect authored geometry or line ownership.

## Q05 — current v11 correction — BLOCKED

If Q03/Q04 prove a material/runtime defect, modify the **current v11 family**. Do not create v12 solely for the fix.

Renderer correction rules:

- do not move already-correct authored points for a material-only fix;
- do not let terminal changes reseed or materially change an unrelated stroke body;
- keep terminal behavior bounded to the intended physical suffix;
- preserve canonical/fast exactness for the current contract;
- use fresh visual dogfood, not only synthetic pixel tests.

## Q06 — contract-digest replay boundary — REQUIRED before release

Current registry exposes a renderer contract digest, while `RenderProfile` persists only id/version. This must be reconciled before a mutable current-v11 implementation can coexist honestly with published v1.0.3 replay claims.

Target:

```text
renderer_id              stable family
renderer_version         protocol/schema compatibility
renderer_contract_digest exact pixel-behavior identity
```

Replay policy:

- matching digest → exact replay eligible;
- mismatched digest → fail closed or explicit migration;
- published v1.0.3 wheel/tag/freeze remains exact authority for its original v11 contract;
- historical implementations do not need to accumulate forever in active `src`.

## Q07 — full validation — BLOCKED

Must combine:

- fresh-worker visual evidence;
- anti-symbol and ownership review;
- construction-retirement review;
- final-scale hierarchy review;
- renderer canonical/fast exactness;
- historical v1.0.3 freeze integrity;
- package/install/runtime CI.

## Q08 — version/release decision — BLOCKED

Do not predeclare `1.0.4rc1`. Choose the next package version only after Q07 proves a coherent product state.

## Historical v1.0.3 authority

The released renderer boundary remains historically true for the published package:

```text
v1.0.3 stable / A14
new sessions in that package → pillow-pencil-contact-v11 / 1
explicit v10/1 → rc1/rc2 replay
explicit v9/1  → v1.0.2 replay
```

This historical statement does not require future current source to keep incrementing renderer generations.

## Authority

- current state: `STATUS.md`;
- active design: `V11_QUALITY_CONTROL_REDESIGN.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `../../../docs/releases/v1.0.3.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- G02 visual/material evidence: `../../dogfood/g02-broad-pencil-v11/README.md`;
- v1.0.3 stable freeze: `../../release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- exact v1.0.3 stable candidate: `../../release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.2 snapshot: `../../release/vnext/CONTRACT_FREEZE.json`.
