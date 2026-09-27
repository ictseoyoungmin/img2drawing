# v11 quality-control bottleneck slice plan

Status: **ACTIVE EXECUTION PLAN**  
Date: 2026-09-13  
Baseline: published `v1.0.3 / A14`  
Current renderer family: `pillow-pencil-contact-v11 / 1`

This plan converts `V11_QUALITY_CONTROL_REDESIGN.md` into narrow, reviewable bottleneck slices.

## Current S03 scope amendment (2026-09-27)

Per user decision, the exact Gojo rerun and the 2026-09-25 figure-based pilot are superseded by
the four simple still-life references and isolated-worker procedure in
`../../dogfood/s03-quality-gates/SIMPLE_SUBJECT_CAMPAIGN.md`. Earlier runs remain historical/pilot
evidence and do not count toward current closure. Image generation may create target references only;
all drawing output must still come from the current public runtime. The current SVG references were
rendered to PNG after the image_gen service reached its usage limit. On 2026-09-27 the user accepted the S03 dogfood release gate with the four still-life classes unfinished. See `../../dogfood/s03-quality-gates/USER_ACCEPTANCE_2026-09-27.md`. This is a release decision, not class-level visual proof.

## Global invariants

The following rules apply to every slice:

1. **No additive renderer v12.** The current family remains `pillow-pencil-contact-v11 / 1`.
2. **No package-version bump during design/dogfood.** Version selection belongs only after full validation.
3. **No image generation, pixel pasting, edge-trace pasting, or raster repair for drawing output.** Original raster or vector target references are allowed only when listed in `SIMPLE_SUBJECT_CAMPAIGN.md`.
4. **Canonical session provenance is preserved.** Dogfood keeps the complete `session.json`; final replay is action 0 → latest, normally `every_n=4`, using the same pencil renderer family as the PNG.
5. **Macro correctness precedes material polish.** A renderer change is forbidden while wrong authored geometry, ownership, overlap, contact, or perspective can explain the visible defect.
6. **One material defect per renderer slice.** Do not combine terminal, grain, pressure, broad-contact, and unrelated rendering changes into one correction.
7. **Fresh visual evidence is required after every accepted correction.** Mechanical tests alone never close a visual slice.
8. **Published v1.0.3 evidence is immutable.** Tag, release artifacts, freeze records, and historical dogfood are read-only authority.

---

# Execution sequence

```text
S01 design closure
  ↓
S02 instruction execution gates
  ↓
S03 fresh-worker visual dogfood
  ↓
S04 residual ownership/classification
  ↓
S05 replay-contract boundary
  ↓
S06 current-v11 material correction, only if S04 proves one
  ↓
S07 second-pass visual + mechanical validation
  ↓
S08 package/version/release decision
```

`S06` may be skipped when S04 finds no renderer-owned blocking defect. `S05` is not skipped: the
replay contract must be made honest before a mutable current-v11 implementation can diverge from
published v1.0.3.

---

# S01 — design closure

## S01.1 Failure taxonomy freeze

**Input**
- the four supplied figure outputs;
- current skill instructions;
- published v1.0.3 behavior.

**Scope**
Classify only recurring failure families, not every local drawing mistake.

Required classes:
- generic/symbolic construction;
- premature hair-strand accumulation;
- rail/tube limbs;
- symbolic feet/props;
- construction/search-line survival;
- weak line hierarchy;
- incomplete perspective propagation;
- ownerless context marks;
- local detail hiding whole-drawing weakness.

**Artifact**
- `V11_QUALITY_CONTROL_REDESIGN.md` failure taxonomy.

**Gate**
Every planned instruction/runtime change must map back to at least one observed failure class.

**Reopen when**
A later dogfood failure cannot be explained by the current taxonomy without forcing an unrelated
rule into it.

## S01.2 Decision-closure contract

Define one compact semantic-group acceptance packet:

```text
visible authority
→ 2–5 neighboring anchors
→ primary physical/semantic owner
→ geometry claim
→ mark-language choice
→ fresh render
→ disproof test
```

Then require:

```text
anti-symbol audit
+ hierarchy audit
+ KEEP / SOFTEN / RETIRE audit
+ whole-subject recheck
```

**Gate**
The contract must remain reversible: any later evidence can reopen the parent premise. It must not
become a fixed runtime stage pipeline.

## S01.3 Renderer/replay architecture decision

Freeze the architectural rule:

```text
renderer_id              = stable renderer family
renderer_version         = protocol/schema compatibility
renderer_contract_digest = exact pixel-behavior identity
```

Historical exactness belongs to immutable package/tag/freeze evidence, not to an endless sequence
of v11/v12/v13 implementations in current `src`.

**Gate**
No renderer code changes are authorized before this rule is reflected in the implementation plan.

## S01 close condition

S01 closes when taxonomy, instruction decision closure, and replay/version policy agree with one
another and no slice requires a renderer v12.

---

# S02 — instruction execution gates

S02 changes the worker's decision path, not renderer pixels.

## S02.1 Central quality gate

Add and route `references/review/visual-quality-gates.md`.

It owns:
- semantic-group evidence packet;
- line ownership;
- anti-symbol audit;
- hierarchy audit;
- construction retirement;
- whole-read return;
- final largest-residual ranking.

**Mechanical gate**
- instruction graph reachability passes;
- skill surface boundary explicitly includes the new leaf;
- no release/internal control-plane text leaks into deployable skill docs.

## S02.2 Ownership + anti-symbol enforcement

Strengthen only the leaves that own observed failures:

- `foundation/line-economy.md` — one continuous physical owner per final stroke;
- `observation/visual-observation.md` — anchor evidence and near/mid/far grouping for strong perspective;
- `figure/head-face-hair.md` — mass → clump → accent hard sequence;
- `construction/balance-and-limbs.md` + `figure/legs-feet.md` — reject rail completion;
- `props/attached-objects.md` — solve prop/body contact as one relation;
- `environment/ground-and-context.md` — reject ownerless context/perspective decoration;
- `figure/clothing-folds.md` — require force/contact cause for fold/hatch marks.

**Visual reasoning gate**
For each rule, state what visible evidence proves it passed and what failure should reopen the
parent premise. Merely adding another warning sentence does not close the slice.

## S02.3 Retirement + completion enforcement

Update:
- `review/stroke-retirement.md` with explicit `KEEP / SOFTEN / RETIRE` decisions;
- `review/residual-correction.md` with "busier but not more specific" escalation;
- `review/completion.md` with top-residual ranking and explicit hierarchy/retirement accounting;
- `markmaking/pressure-and-terminals.md` so terminal semantics remain downstream of justified geometry and do not imply a renderer-generation bump.

**Gate**
A worker cannot reasonably call a drawing finished while:
- generic symbols remain in visible-enough regions;
- construction/search marks dominate the final read;
- major line classes are visually indistinguishable;
- a larger unresolved residual is merely omitted from the finish rationale.

## S02.4 Instruction integration regression

Run the full current instruction/skill test surface.

**Close condition**
- current docs consistency PASS;
- runtime surface PASS;
- instruction graph reachability PASS;
- active tests PASS;
- immutable v1.0.3 freeze verification PASS.

If a test fails because it encodes an obsolete assumption that post-release source must equal the
v1.0.3 release tree, correct the verifier to test immutable historical authority instead of mutable
HEAD equality. Do not weaken actual release evidence.

---

# S03 — fresh-worker visual dogfood

S03 is the first quality proof. Workers receive the updated skill, reference, and normal public
runtime. They do **not** receive prior solution strokes as an answer template.

Each task produces:
- reference identifier/source;
- complete canonical `session.json`;
- final PNG;
- end-to-end GIF from action 0 to latest, normally `every_n=4`;
- reference/final comparison board or equivalent inspection evidence;
- residual ledger with top three remaining visible mismatches;
- explicit KEEP/SOFTEN/RETIRE summary for surviving construction.

## S03.1 Apple still life

Review the apple silhouette, stem/leaf attachment, volume, light/shadow separation, and retirement of exploratory marks.

## S03.2 Ceramic mug still life

Review the rim ellipse, body taper, handle attachment/negative space, volume, and contact shadow.

## S03.3 Closed umbrella still life

Review canopy silhouette/folds, shaft continuity, handle shape, lean, and floor contact.

## S03.4 Potted plant still life

Review leaf masses and stems, pot opening/body, overlap order, volume, and contact shadow.

## S03 close condition

Ordinary evidence closure requires reviewable artifacts and no blocking residual in all four classes. The current release uses the separate 2026-09-27 user acceptance decision; class ledgers remain NOT_RUN and no measured visual PASS is claimed.

---

# S04 — residual ownership and renderer eligibility

S04 decides whether any renderer work is justified.

## S04.1 Residual ledger

For every blocking or repeated residual record:

```text
symptom
visible evidence
responsible owner
parent premise
geometry correct? yes/no/uncertain
material/render behavior correct? yes/no/uncertain
next disproof test
```

Allowed primary owners:
- observation evidence;
- construction/proportion/perspective;
- contour/overlap/ownership;
- subject-specific geometry;
- mark-language selection;
- renderer material/runtime;
- completion/retirement decision.

## S04.2 Geometry-first elimination

A residual is **not renderer-eligible** when changing authored points, overlap, contact, proportion,
line ownership, or semantic role can plausibly fix it.

For a renderer candidate, freeze the authored geometry and reproduce the defect while changing only
material/runtime inputs.

## S04.3 Material-defect proof

A renderer-owned defect requires both:

1. **real-drawing evidence** — visible in one or more S03 outputs with geometry judged correct;
2. **minimal controlled reproduction** — same defect reproduced without relying on the surrounding drawing.

Examples of possible renderer-owned classes:
- premature terminal fade;
- blunt/swollen terminal despite correct path;
- discontinuity under a valid thin flick;
- broad-contact square end;
- unexpected body reseeding after terminal-only change;
- material hierarchy collapsing despite distinct authored dynamics.

Do not predeclare which class exists.

## S04 close condition

Produce one of two decisions:

```text
A. no renderer-owned blocking defect
   → skip S06 and proceed through S05 replay-boundary work to S07

B. N proven renderer-owned defects
   → create exactly N independent S06.x correction slices
```

---

# S05 — renderer contract-digest / replay boundary

This slice must close before current-v11 pixel behavior is intentionally changed.

## S05.1 Persist exact renderer contract identity

Extend persisted render/session identity so new authoritative histories can bind:

```text
renderer_id
renderer_version
renderer_contract_digest
```

Do not rewrite old session history in place.

## S05.2 Exact-match rule

Define and test:

- id/version/digest match → exact replay eligible;
- same id/version but digest mismatch → no silent exact replay claim;
- unknown/missing historical digest → explicitly legacy/ambiguous under current source, with historical package/tag remaining the exact authority.

## S05.3 Explicit migration path

When a user intentionally chooses current rendering for an old history, record that as migration or
re-render-under-current-contract. Do not label migrated pixels as historical exact replay.

## S05.4 Compatibility window

Do **not** remove v9/v10 implementations merely to make this slice look complete. First prove digest
binding and migration behavior. Historical backend retirement, if useful later, is a separate bounded
cleanup after replay semantics are trustworthy.

## S05 close condition

- new sessions persist digest;
- exact replay refuses/flags a mismatched digest;
- legacy no-digest sessions remain loadable under an explicitly non-exact current-source policy;
- immutable v1.0.3 tag/package remains reproducible and unmodified;
- canonical/fast paths agree for the current contract.

---

# S06 — current-v11 material correction

S06 exists only for defects proven in S04. Each defect becomes a separate `S06.n` slice.

Template for every `S06.n`:

## S06.n.1 Freeze geometry + baseline

Store:
- exact authored points/dynamics;
- current v11 contract digest;
- minimal reproduction;
- real dogfood crop/full view;
- expected locality of the material change.

## S06.n.2 Minimal implementation correction

Allowed changes are limited to the demonstrated material cause.

Forbidden:
- changing authored points to disguise a renderer problem;
- adding renderer v12;
- bundling unrelated pressure/grain/terminal changes;
- changing whole-stroke random identity when only a short terminal suffix should change.

## S06.n.3 Locality proof

Verify the correction changes the intended visual region/behavior and does not introduce unexplained
changes to unrelated stroke body, neighboring strokes, or geometry.

## S06.n.4 Real visual proof

Re-render the real dogfood task and inspect at:
- local crop;
- whole subject;
- final presentation scale.

A synthetic PASS without visible improvement in the real drawing is not closure.

## S06.n close condition

- demonstrated defect removed or materially reduced;
- no new blocking residual;
- renderer identity remains v11 family;
- contract digest changes if and only if exact pixel behavior changed;
- S05 replay rules correctly distinguish the new current contract from v1.0.3's historical contract.

---

# S07 — second-pass visual + mechanical validation

S07 proves the integrated product rather than individual patches.

## S07.1 Fresh-worker rerun

For the current release, the user-accepted S03 gate replaces a second fresh-worker visual rerun. Future visual-proof work must use fresh workers and must not reuse previous solution strokes as hidden scaffolding.

Compare:
- pre-redesign baseline;
- post-instruction result;
- post-renderer result when S06 exists.

## S07.2 Visual acceptance

For the current release, the dated user acceptance record owns this decision and limits the visual claim. The detailed checklist below applies when measured class-level visual proof is resumed.

Require explicit review of:
- whole pose/composition;
- perspective propagation;
- silhouette/overlap/contact;
- subject specificity vs symbols;
- head/face/hair;
- limbs/hands/feet;
- prop/body relation;
- clothing/fold causality;
- environment ownership;
- line hierarchy;
- construction retirement;
- top remaining residuals.

## S07.3 Mechanical regression

Require:
- full active test suite;
- instruction graph reachability;
- clean package/install/runtime checks;
- canonical/fast exactness for current contract;
- historical v1.0.3 freeze integrity;
- end-to-end timelapse provenance on committed current-version fixtures; local dogfood sessions may supplement but are not release artifacts.

## S07 close condition

For the current release, the documented user decision owns visual acceptance. S07 closes only when the active mechanical, package/install, replay, and historical-freeze gates are green. This does not create a new measured visual-quality claim.

---

# S08 — package/version/release decision

Only now choose release semantics.

## S08.1 Change classification

Determine whether the validated result is:
- instruction-only patch behavior;
- additive compatible persisted metadata/runtime behavior;
- compatibility-affecting API/session change;
- another category supported by repository release policy.

Do not assume `1.0.4`, `1.1.0`, or `2.0.0` in advance.

## S08.2 Release candidate freeze

If release is warranted:
- choose package version and release revision;
- create a new contract freeze rather than mutating v1.0.3 evidence;
- record the current v11 contract digest;
- build clean wheel/sdist;
- run full validation from the candidate artifact.

## S08.3 Publish

Publish only after the frozen candidate matches the validated product state.

`v1.0.3` tag, release, wheel, sdist, promotion evidence, and freeze remain untouched.

---

# Reopen rules

Any downstream slice may reopen an upstream slice.

```text
symbolic/generic shape survives dogfood      → reopen S02 owner leaf
whole pose/perspective drifts                → reopen observation/construction in S02
material fix needs point movement            → reject S06 cause; reopen S04
new v11 pixels cannot be replay-classified   → reopen S05
CI green but visual result remains weak       → S07 stays OPEN
new package number needed to hide uncertainty → reject S08; reopen responsible slice
```

A child slice never closes merely because its local implementation is finished when the parent
visual premise is still wrong.

---

# Immediate next slice

The design contract is sufficiently specified to close **S01**. The immediate bottleneck is
**S02 instruction execution-gate integration and its full regression closure**.

Do not start S03 until S02 CI is completely green on the design branch. Do not start renderer pixel
work until S03/S04 produce a renderer-eligible defect and S05 closes the digest replay boundary.