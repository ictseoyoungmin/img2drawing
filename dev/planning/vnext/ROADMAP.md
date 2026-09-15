# img2drawing roadmap

Updated: 2026-09-15
Workflow: Bottleneck · one highest-impact open problem at a time

The v1.0.3 release cycle is closed. New work begins from the published v1.0.3 baseline and must not mutate its tag, wheel, freeze, or historical evidence.

## Authority and precedence

`STATUS.md` is the canonical **point-in-time current-state authority** for mutable development. This roadmap owns sequencing, dependencies, rationale, and closure criteria; it does not create a second current-state truth.

If a state label in this file and `STATUS.md` diverge, treat the divergence as a documentation defect and update both in the same bounded authority slice. Historical release tags/freezes/manifests remain authoritative for their immutable release facts regardless of mutable planning state.

Instruction-graph attention cleanup is sequenced separately in `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`. That plan may change graph organization only within its declared slices; it does not replace S03 as the active product-quality bottleneck.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 added general authoring ergonomics.
- v1.0.2 promoted the exact local-first timelapse backend.
- post-v1.0.2 cleanup physically retired the R23 runtime/legacy cluster.
- renderer v10 closed seed/parity and broad authored-value issues.
- G01 closed gesture/runtime/instruction integration gaps.
- G02 closed the broad-pencil square-terminal / weak-graphite failure class with the renderer family now published as `pillow-pencil-contact-v11 / 1`.
- G03–G06 integrated, froze, verified, and published `v1.0.3 / A14`.
- S01 closed the v11 quality-control taxonomy, reversible evidence-gate design, and no-v12 renderer-family policy.
- S02 integrated the instruction execution gates. S03.1 later caused one bounded reference-authority reopen; that implementation patch is merged, while behavioral proof remains in the clean S03.1 rerun.
- instruction-graph cleanup Slice A synchronized planning authority and added CI enforcement so `STATUS.md` is the one point-in-time mutable-state source.
- instruction-graph cleanup Slice B reduced `SKILL.md` to a true router and made the central visual-quality gate a direct conditional route from the root.
- instruction-graph cleanup Slice C reduced `references/INDEX.md` to a direct map with one `open when` / `owns` row per deployable leaf.
- instruction-graph cleanup Slice D restored canonical leaf ownership: reference authority owns anti-normalization, observation/gates/residual/completion own their distinct decisions, gesture completion stays in its mode leaf, and runtime provenance/finish mechanics live in the public API leaf.
- instruction-graph cleanup Slice E added structural CI for root/INDEX attention budgets, root fan-out, internal route integrity, canonical-owner reachability, and deployable/control-plane separation without changing drawing semantics.

## Current sequence

```text
G01 gesture behavior validation                         CLOSED
G02 broad-pencil material/terminal hardening            CLOSED
G03 integrate validated rc3 into main                   CLOSED
G04 stable-promotion decision                           CLOSED → v1.0.3
G05 stable freeze + wheel verification                  CLOSED
G06 explicit publish manifest + publish                 CLOSED
S01 v11 quality-control failure taxonomy + design       CLOSED
S02 instruction graph execution-gate patch              CLOSED
S03 fresh-worker visual dogfood                         ACTIVE · S03.1 initial batch BLOCKED; clean rerun READY/NOT_RUN; S03.2–S03.4 pending
S04 classify remaining geometry vs material residuals   ACTIVE / PARTIAL · S03.1 classified
S05 contract-digest / replay-boundary migration         BLOCKED by global S04 evidence; REQUIRED before pixel change
S06 current-v11 renderer correction if proven           BLOCKED by S04/S05; MAY SKIP
S07 full visual + mechanical validation                 BLOCKED by S03–S06
S08 choose next package version / release candidate     BLOCKED by S07
```

**No renderer v12 is authorized by this roadmap.** The abandoned PR #48 demonstrated why treating renderer generations as a patch counter would accumulate v12/v13/... without closing the actual drawing-quality bottleneck.

## Instruction-graph attention cleanup — maintenance sequence

This cleanup was bounded maintenance around the S03 bottleneck. It is now closed and does not add a new product-quality target.

```text
Slice A authority synchronization                         CLOSED
Slice B SKILL.md router reduction + direct quality gate   CLOSED
Slice C INDEX.md map-only reduction                       CLOSED
Slice D leaf ownership / runtime-boundary cleanup         CLOSED
Slice E attention-architecture QA + structural CI         CLOSED
clean S03.1 rerun                                         NEXT within active S03
```

The exact scope, forbidden changes, and closure evidence for A–E live in `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`. The cleaned graph must now be validated by the isolated S03.1 fresh-worker rerun rather than expanded with more instructions by default.

## S01 — v11 quality-control redesign — CLOSED

Authority: `V11_QUALITY_CONTROL_REDESIGN.md`.

The observed failure classes were frozen around one higher-level cause: the skill contained many correct principles but did not require enough evidence before a worker accepted symbolic, generic, cluttered, or weakly retired drawing decisions.

The accepted decision-closure model is:

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

Renderer-family identity is also separated conceptually from exact historical pixel identity so quality corrections do not require a new renderer number.

## S02 — instruction execution gates — CLOSED AFTER BOUNDED REOPEN

The skill contains one central `review/visual-quality-gates.md` leaf and concentrated edits to existing owners rather than a new rigid stage pipeline.

Originally closed behavior included:

- line ownership continuity;
- evidence/anchor packets before descriptive acceptance;
- near/mid/far propagation for strong perspective;
- hair mass → clump → accent ordering;
- rejection of rail/tube limb completion;
- prop/body contact solved as one relation;
- ownerless context/perspective decoration rejected;
- explicit KEEP/SOFTEN/RETIRE construction audit;
- “busier but not more specific” escalation;
- top remaining residual ranking before finish;
- terminal/markmaking semantics kept downstream of justified geometry.

S03.1 exposed one missing execution rule: workers could still let anatomical plausibility or a remembered canonical identity silently overrule readable reference evidence. That caused a bounded reopen adding reference-fidelity / anti-normalization enforcement without introducing a stage pipeline or renderer change.

That implementation patch is now merged, so **S02 implementation is CLOSED again**. Its effectiveness is not considered behaviorally proven until the clean S03.1 rerun executes without evaluator leakage. That pending proof belongs to S03, not to S02's implementation state.

CI run `34761722278` remains the original S02 closure record; the bounded reopen has its own later CI evidence.

## S03 — fresh-worker visual dogfood — ACTIVE

Fresh workers must receive the updated skill, reference, and normal public runtime surface without privileged access to prior solution strokes or evaluator hints.

Required visual classes:

1. strong-perspective close figure — **initial batch BLOCKED; clean rerun READY / NOT_RUN**;
2. full-body 3/4 figure with attached/held prop — NOT_RUN;
3. frontal or near-frontal full body — NOT_RUN;
4. head/hair close-up — NOT_RUN.

Each run must produce reviewable provenance:

- complete canonical `session.json`;
- final PNG;
- action-0→latest GIF, normally `every_n=4`;
- reference/final comparison evidence;
- top remaining residual ledger;
- KEEP/SOFTEN/RETIRE summary.

The supplied failure images define the failure classes, not answer templates. One blocking class prevents S03 closure; results are not averaged.

## S04 — residual ownership decision — ACTIVE / PARTIAL

S03.1 is classified in `../../dogfood/s04-residual-ownership/README.md`.

Current S03.1 decision:

```text
reference/identity substitution        → instruction / subject-specific geometry
visible hand anatomy normalization     → observation / projection / authored geometry
symbolic geometry + scaffold survival  → anti-symbol / completion / retirement
renderer-owned blocking defect         → none proven
```

For every later S03 blocking or repeated residual, continue to classify before renderer work:

```text
wrong path / proportion / ownership / overlap / contact
→ geometry / instruction owner

correct geometry but wrong weight / taper / terminal / grain / deposition
→ material / runtime candidate
```

A renderer candidate must have both real-drawing evidence and a minimal controlled reproduction with authored geometry frozen.

Global S04 cannot close until S03.2–S03.4 evidence is also classified. The current batch does not authorize S06.

## S05 — contract-digest replay boundary — BLOCKED

Before intentional current-v11 pixel divergence, persisted render identity must be able to bind:

```text
renderer_id              stable family
renderer_version         protocol/schema compatibility
renderer_contract_digest exact pixel-behavior identity
```

Replay policy:

- matching family/version/digest → exact replay eligible;
- same family/version with digest mismatch → no silent exact replay claim;
- legacy no-digest history remains loadable under an explicitly non-exact current-source policy;
- published v1.0.3 wheel/tag/freeze remains exact authority for its original v11 contract;
- migration to the current contract is recorded as migration, not historical exact replay.

This slice is required before S06 changes current-v11 pixels.

## S06 — current v11 correction — CONDITIONAL

Only defects proven renderer-owned in S04 receive a renderer slice. Each distinct material defect becomes one independent S06.n bottleneck.

Rules:

- keep renderer family `pillow-pencil-contact-v11 / 1`;
- do not move authored points for material-only fixes;
- do not reseed unrelated stroke body for a local terminal change;
- change only the demonstrated material cause;
- prove locality with controlled reproduction and real dogfood;
- change the contract digest whenever exact pixel behavior changes.

If S04 finds no renderer-owned blocking defect, S06 is skipped.

## S07 — full validation — BLOCKED

Repeat the S03 visual classes and combine:

- fresh-worker visual evidence;
- anti-symbol/ownership audit;
- construction-retirement audit;
- final-scale line hierarchy review;
- canonical/fast exactness for the current contract;
- historical v1.0.3 freeze integrity;
- package/install/runtime CI;
- end-to-end timelapse provenance.

A green CI run alone does not close S07.

## S08 — version/release decision — BLOCKED

Do not predeclare `1.0.4rc1`. Choose release semantics only after S07 proves a coherent product state. Any new freeze must be additive and must not mutate v1.0.3 evidence.

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

- **current point-in-time mutable state: `STATUS.md`**;
- product sequencing, dependencies, and closure criteria: this file, `ROADMAP.md`;
- instruction-graph attention cleanup slices A–E: `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`;
- v11 execution plan: `V11_QUALITY_CONTROL_SLICE_PLAN.md`;
- redesign rationale: `V11_QUALITY_CONTROL_REDESIGN.md`;
- S03 harness + ledgers: `../../dogfood/s03-quality-gates/README.md`;
- S04 residual classification: `../../dogfood/s04-residual-ownership/README.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `../../../docs/releases/v1.0.3.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- G02 visual/material evidence: `../../dogfood/g02-broad-pencil-v11/README.md`;
- v1.0.3 stable freeze: `../../release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- exact v1.0.3 stable candidate: `../../release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.2 snapshot: `../../release/vnext/CONTRACT_FREEZE.json`.
