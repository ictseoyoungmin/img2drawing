# Instruction graph attention-architecture cleanup plan

Updated: 2026-09-15
Status: Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · Slice D CLOSED · Slice E CLOSED
Scope: instruction-graph organization and documentation authority only

## Goal

Reduce attention cost and semantic duplication without weakening the drawing rules already proven useful by dogfood.

The target architecture is:

```text
SKILL.md
  = mission + invariants + conditional router + canonical loop

references/INDEX.md
  = map only: when to open / what the leaf owns

specialist leaves
  = canonical drawing knowledge owners

api leaves
  = runtime operation only

review gates
  = evidence-based acceptance / correction / completion decisions
```

This cleanup is **not** permission to add new drawing principles, change renderer behavior, change package version, or reinterpret historical releases.

## Authority model

Mutable development authority is split by purpose:

1. `STATUS.md` — canonical point-in-time current state.
2. `ROADMAP.md` — product sequence, dependencies, rationale, closure definitions.
3. this file — execution authority for instruction-graph cleanup slices A–E.
4. `SKILL.md` / `references/INDEX.md` / leaves — deployable worker instruction graph.
5. release tags, freezes, manifests, and release notes — immutable historical release facts.

When mutable planning documents disagree on a current state label, treat that as a documentation defect. Do not choose whichever file is convenient; synchronize the authorities in one bounded slice.

## Canonical node ownership target

The cleanup must preserve these ownership boundaries.

| Concern | Canonical owner | Other nodes may contain |
| --- | --- | --- |
| observed/imaginative/hybrid truth, anti-normalization definition | `foundation/reference-authority.md` | short reminder + link |
| evidence gathering, whole↔part observation, plausibility-conflict re-observation | `observation/visual-observation.md` | routing reminder |
| structural specificity / provisional construction inheritance | `foundation/structural-specificity.md` | invariant summary |
| hidden continuity vs visible appearance | `foundation/occlusion-inference.md` | bounded routing reminder |
| line economy / semantic grouping | `foundation/line-economy.md` | root invariant summary |
| semantic-group acceptance gates | `review/visual-quality-gates.md` | direct route + short reminder |
| residual cause selection / correction decision | `review/residual-correction.md` + `review/residual-routing.md` | no runtime tutorial |
| construction retirement | `review/stroke-retirement.md` | completion reminder |
| mode-specific finish semantics | matching `modes/*.md` leaf | completion links only |
| final artistic completion decision | `review/completion.md` | no duplicated mode textbook/runtime API |
| runtime operation / provenance call sequence | `api/public-surface.md` | non-API leaves link only |
| replay/output contract | `output/render-profile-and-replay.md` | completion/output route only |

The table is an ownership target, not a reason to delete every cross-reference. Boundary reminders are allowed when they are short and point to the canonical owner.

---

## Slice A — authority synchronization

Status: **CLOSED**

### Purpose

Remove current-state ambiguity before restructuring the deployable graph.

### Changes completed

- synchronized `STATUS.md` and `ROADMAP.md` on 2026-09-15;
- defined `STATUS.md` as point-in-time mutable-state authority;
- defined `ROADMAP.md` as sequencing/dependency/closure-definition authority;
- distinguished S02 implementation closure from pending S03.1 behavioral proof;
- recorded S03.1 and S04 state consistently;
- added this A–E execution plan and canonical node-ownership target;
- extended current-documentation verification to fail on authority/date drift.

### Forbidden changes honored

- no `SKILL.md` reduction;
- no `INDEX.md` reduction;
- no leaf semantic rewrite;
- no renderer/runtime behavior change;
- no package/release version change;
- no dogfood verdict change without new evidence.

### Closure evidence

- `STATUS.md` and `ROADMAP.md` use the same update date and compatible current-state labels;
- S02 is implementation CLOSED after the bounded anti-normalization reopen while S03.1 remains BLOCKED pending clean rerun;
- S04 remains ACTIVE / PARTIAL with zero proven renderer-owned blockers from the current S03.1 batch;
- CI run `34963437056` passed current documentation, runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED state transition;
- merged Slice A main CI also passed the same verification surface.

---

## Slice B — make `SKILL.md` a real router

Status: **CLOSED**

### Purpose

Reduce root attention load while preserving all high-value invariants and direct routing.

### Changes completed

- reduced the root to frontmatter/mission, a compact runtime boundary, seven non-negotiable invariants, graph routing, a conditional start route, the canonical correction loop, and completion/output routing;
- removed root specialist textbook sections for whole-subject hypothesis detail, structural-read procedure, inheritance procedure, occlusion procedure, head/face, hands/grip, foreshortening, legs/feet, clothing folds, croquis value, and stroke-retirement detail;
- directly routed observed finished/substantially-resolved work to `references/review/visual-quality-gates.md` before the first descriptive semantic-group acceptance;
- kept authored-element navigation directly discoverable from the root;
- changed root regression tests from duplicated-prose location locks to routing/canonical-owner checks;
- kept detailed runtime-awareness semantics owned by API leaves while preserving a compact root boundary.

### Forbidden changes honored

- no `references/INDEX.md` reduction;
- no specialist leaf semantic rewrite;
- no renderer/runtime behavior change;
- no package/release version change;
- no dogfood verdict change.

### Closure evidence

- specialist knowledge remains reachable from `references/INDEX.md` and existing owner leaves;
- instruction-graph verifier now enforces the direct visual-quality route as an img2drawing-specific product route without contaminating the generic graph invariant;
- `SKILL.md` is materially smaller than the Slice A baseline (the rewrite removed 357 old lines while adding 124 focused router lines in the initial diff, a net reduction of 233 lines);
- active-suite regression after the generic/product verifier split is green;
- PR CI run `34968493328` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED transition.

---

## Slice C — reduce `references/INDEX.md` to a map

Status: **CLOSED**

### Purpose

Make INDEX a low-attention navigation layer instead of a second textbook.

### Changes completed

- replaced policy-teaching sections with one compact direct row per deployable leaf;
- each map row now states only `open when:` routing context and `owns:` canonical responsibility;
- removed duplicated runtime-awareness prose, gesture behavior teaching, construction prerequisite prose, residual-routing examples, and repeated geometry-vs-material instruction from INDEX;
- kept only short branch-level distinction where needed, such as opening markmaking after geometry is justified;
- moved tests/verifiers away from requiring duplicated INDEX policy prose;
- added a structural invariant requiring every deployable reference leaf to appear exactly once as a direct INDEX row with both routing and ownership metadata.

### Forbidden changes honored

- no `SKILL.md` rewrite;
- no specialist leaf semantic rewrite;
- no renderer/runtime behavior change;
- no package/release version change;
- no dogfood verdict change.

### Closure evidence

- every deployable leaf remains reachable and is now directly discoverable from INDEX;
- INDEX is explicitly a map, not a lifecycle/preload curriculum;
- the final INDEX rewrite is 87 lines smaller than the Slice B baseline diff (`+78 / -165` for INDEX itself);
- v1.0.3 runtime/markmaking semantics remain verified in `SKILL.md`, API leaves, runtime source, and markmaking owner leaves rather than duplicated in INDEX;
- PR CI run `34972282707` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED state transition.

---

## Slice D — canonical leaf ownership + runtime boundary cleanup

Status: **CLOSED**

### Purpose

Remove semantic duplication between leaves while preserving concise boundary reminders.

### Changes completed

1. **Anti-normalization ownership**
   - canonical definition remains in `foundation/reference-authority.md`;
   - `observation/visual-observation.md` now owns only plausibility-conflict evidence gathering;
   - `review/visual-quality-gates.md` owns accept/reject behavior;
   - `review/residual-correction.md` owns reopen/correction decisions;
   - `review/completion.md` treats unresolved authority drift only as a final blocker;
   - hand, foreshortening, and head/identity leaves retain concise domain reminders and route back to the canonical authority/observation owners.

2. **Residual runtime provenance**
   - moved the executable `record_residual() → corrective edit → inspect() → resolve_residual()` pattern and `observation_id`/freshness compatibility notes to `api/public-surface.md`;
   - `review/residual-correction.md` now keeps semantic correction logic plus a short runtime-boundary route only.

3. **Gesture completion**
   - detailed pure/constructive gesture finish semantics remain owned by `modes/gesture-drawing.md`;
   - `review/completion.md` routes to the mode owner rather than repeating gesture-specific primitive criteria.

4. **`finish()` mechanics**
   - evidence-read, open-residual, stale-inspection, empty-canvas, and public `finish()` mechanics now live in `api/public-surface.md`;
   - `review/completion.md` owns the artistic decision, residual ranking, and accepted-limitation judgment only.

5. **Ownership regression tests**
   - updated reference-fidelity and gesture tests to assert canonical owners instead of duplicated prose locations;
   - added `test_instruction_leaf_ownership.py` to prevent runtime mutation tutorials and mode textbooks from regrowing inside review leaves.

### Forbidden changes honored

- no renderer/runtime implementation behavior change;
- no package/release version change;
- no dogfood verdict change;
- no new drawing principle added;
- no Slice E attention budgets/fan-out policy added early.

### Closure evidence

- each central policy has one canonical definition owner with short routed reminders elsewhere;
- review leaves no longer embed the executable residual provenance tutorial or detailed `finish()` runtime mechanics;
- gesture completion remains fully covered in its mode owner;
- dogfood-derived anti-normalization semantics remain regression-tested;
- implementation CI run `34977641399` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED transition.

---

## Slice E — attention-architecture QA and structural CI

Status: **CLOSED**

### Purpose

Prevent the graph from regrowing into overlapping textbooks while avoiding brittle prose locks.

### Changes completed

- added explicit attention ceilings derived from the cleaned Slice D baseline: `SKILL.md` 12,000 bytes and `references/INDEX.md` 10,000 bytes;
- capped direct root leaf fan-out at 16 routes, leaving bounded headroom over the cleaned 13-route baseline without allowing the root to become a second index;
- extended the graph verifier so slash-qualified deployable Markdown routes must resolve inside the reference graph;
- made canonical policy-owner leaves an explicit structural reachability invariant;
- moved deployable/control-plane separation into the direct graph verifier while preserving the existing skill-surface regression tests;
- added focused Slice E regression tests that execute the attention budget, route-integrity, control-plane, and owner-reachability checks;
- retained existing sole-entrypoint, direct visual-quality route, direct INDEX map-row, generic reachability, and Slice D ownership tests rather than replacing them with new prose locks.

### Attention baseline and budgets

The closed Slice D graph measured:

```text
SKILL.md                              9,066 bytes
references/INDEX.md                   7,692 bytes
root direct leaf routes              13  (INDEX excluded)
```

Slice E ceilings are:

```text
SKILL.md                             12,000 bytes
references/INDEX.md                  10,000 bytes
root direct leaf routes              16
```

These are architecture guardrails, not drawing rules. A future increase requires an explicit attention-architecture decision rather than incidental instruction growth.

### Forbidden changes honored

- no drawing principle or subject policy added;
- no renderer/runtime implementation behavior changed;
- no package/release version changed;
- no S03/S04 dogfood verdict changed;
- no historical release evidence rewritten.

### Closure evidence

- implementation PR CI run `34982967070` passed repository/package invariants, current documentation, runtime surface, the strengthened instruction-graph verifier, S03 harness, active tests including the new Slice E suite, historical evidence, B17/supply-chain verification, and B18;
- the strengthened graph verifier passed on the cleaned deployable graph without requiring any semantic instruction additions;
- `STATUS.md`, `ROADMAP.md`, and this execution plan now agree that A–E are CLOSED;
- the clean S03.1 rerun remains READY / NOT_RUN and is the next product-quality action.

---

## After Slice E

Return immediately to the active product bottleneck: clean S03.1 fresh-worker rerun.

The rerun must use the isolated worker packet and must not receive this cleanup plan, prior evaluator findings, prior model outputs, correction coordinates, or expected answers. The purpose is to test whether the **cleaned current skill graph** preserves the intended behavior with less attention overhead, not to coach the benchmark worker.

If the clean rerun remains blocked, route only the highest-impact residual back through S04. Do not resume instruction accumulation by default.
