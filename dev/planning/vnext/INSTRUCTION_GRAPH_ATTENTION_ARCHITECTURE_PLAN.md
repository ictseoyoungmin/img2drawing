# Instruction graph attention-architecture cleanup plan

Updated: 2026-09-15
Status: Slice A CLOSED · Slice B READY
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
- the final CLOSED transition must pass the same CI surface before merge.

---

## Slice B — make `SKILL.md` a real router

Status: **READY**

### Purpose

Reduce root attention load while preserving all high-value invariants and direct routing.

### Target root contents

Keep only:

1. frontmatter + mission;
2. compact runtime boundary;
3. approximately 6–8 non-negotiable invariants;
4. instruction-graph map pointer;
5. conditional start route;
6. canonical observation/correction loop;
7. completion/output routing.

### Required routing change

For observed work targeting a finished or substantially resolved drawing, `SKILL.md` must directly route to `references/review/visual-quality-gates.md` before acceptance of the first descriptive semantic group. Do not rely on transitive discovery through `line-economy.md`.

### Primary removal candidates from root

Move ownership back to leaves for:

- whole-subject structural-hypothesis textbook detail;
- structural-read textbook detail;
- revalidation procedure detail;
- occlusion decision procedure;
- head/face, hand/grip, foreshortening, legs/feet, clothing specialist policies;
- croquis value detail;
- stroke-retirement detail;
- duplicate runtime boundary explanation;
- detailed completion mechanics.

### Definition of closed

- specialist knowledge remains reachable through canonical owners;
- direct quality-gate route exists;
- no required drawing invariant disappears from the graph;
- root prose is materially smaller than the Slice A baseline;
- regression tests assert routing/ownership, not old duplicated root prose.

---

## Slice C — reduce `references/INDEX.md` to a map

Status: **BLOCKED by Slice B**

### Purpose

Make INDEX a low-attention navigation layer instead of a second textbook.

### Target entry format

Each leaf should normally communicate only:

```text
path
open when: <routing condition>
owns: <canonical responsibility>
```

Short branch-level notes are allowed only when needed to distinguish neighboring leaves.

### Remove or relocate

- duplicated runtime-awareness policy;
- detailed gesture-mode behavior;
- construction prerequisites already owned by foundation/construction leaves;
- long residual-routing examples;
- repeated geometry-vs-material teaching;
- prose that defines policies instead of locating owners.

### Definition of closed

- every deployable leaf remains transitively reachable;
- INDEX does not become a lifecycle or preload curriculum;
- worker can choose the smallest relevant leaf from routing metadata alone;
- INDEX size is materially below the Slice A baseline without losing leaf discoverability.

---

## Slice D — canonical leaf ownership + runtime boundary cleanup

Status: **BLOCKED by Slice C**

### Purpose

Remove semantic duplication between leaves while preserving concise boundary reminders.

### Priority ownership cleanup

1. **Anti-normalization**
   - definition: `foundation/reference-authority.md`;
   - evidence conflict/re-observation: `observation/visual-observation.md`;
   - accept/reject test: `review/visual-quality-gates.md`;
   - reopen decision: `review/residual-correction.md`;
   - final blocker: `review/completion.md`.

2. **Residual runtime provenance**
   - move executable `record_residual() → edit → inspect() → resolve_residual()` tutorial from `review/residual-correction.md` to `api/public-surface.md`;
   - review leaf keeps semantic correction logic only.

3. **Gesture completion**
   - detailed pure/constructive gesture finish criteria remain in `modes/gesture-drawing.md`;
   - `review/completion.md` links to that owner rather than repeating the gesture textbook.

4. **`finish()` mechanics**
   - runtime preconditions belong in `api/public-surface.md`;
   - `review/completion.md` owns the artistic judgment and residual/limitation decision.

### Definition of closed

- each central policy has one canonical definition owner;
- reminders elsewhere are short and route back to the owner;
- non-API review/foundation leaves do not contain long executable runtime tutorials;
- no dogfood-derived anti-normalization protection is weakened.

---

## Slice E — attention-architecture QA and structural CI

Status: **BLOCKED by Slice D**

### Purpose

Prevent the graph from regrowing into overlapping textbooks while avoiding brittle prose locks.

### QA to add

Prefer structural assertions over exact-sentence assertions:

- `SKILL.md` remains the sole skill-root Markdown entrypoint;
- direct required routes exist, including the visual-quality gate;
- all leaves remain reachable from INDEX;
- deployable docs contain no `dev/` or release-control-plane leakage;
- non-API drawing/review leaves do not embed long runtime mutation tutorials;
- canonical policy owners are present and routed;
- root and INDEX stay below explicit attention budgets chosen from the cleaned baseline;
- excessive root fan-out / unreachable leaves / broken links fail CI;
- current-state documentation authority remains synchronized.

### Test migration

Existing tests that require specific duplicated sentences to remain in `SKILL.md` or INDEX should be replaced with assertions that the invariant exists in its canonical owner and remains reachable from the router.

Do not replace all semantic tests: dogfood-derived behavior such as anti-normalization must still have regression coverage. The change is from **where exact prose must live** to **which owner must preserve the behavior**.

### Definition of closed

- current instruction graph and active test suite green;
- historical v1.0.3/v1.0.2 evidence green;
- B17/B18 green;
- new attention-architecture checks green;
- no new drawing rule was added merely to satisfy cleanup CI;
- cleaned graph is ready for the isolated S03.1 fresh-worker rerun.

---

## After Slice E

Return immediately to the active product bottleneck: clean S03.1 fresh-worker rerun.

The rerun must use the isolated worker packet and must not receive this cleanup plan, prior evaluator findings, prior model outputs, correction coordinates, or expected answers. The purpose is to test whether the **cleaned current skill graph** preserves the intended behavior with less attention overhead, not to coach the benchmark worker.

If the clean rerun remains blocked, route only the highest-impact residual back through S04. Do not resume instruction accumulation by default.
