# v11 quality-control redesign

Status: **DESIGN ACTIVE — implementation intentionally blocked**  
Date: 2026-09-13  
Baseline: published `v1.0.3 / A14`  
Current renderer family: `pillow-pencil-contact-v11 / 1`

## Decision

Do **not** create renderer v12 for the current failure class.

The prior additive-v12 experiment is abandoned. Renderer generation numbers are not a feature counter and must not advance every time line quality, terminal behavior, or drawing guidance is corrected.

The next bottleneck is broader than terminal shape: current outputs show that the skill can contain correct principles while still allowing a worker to produce symbolic, generic, cluttered, weakly retired drawings. The redesign therefore starts with the drawing decision contract, then modifies the current v11 renderer only where fresh visual evidence proves a material/runtime defect.

No package RC/version bump is authorized by this document. Design and dogfood come first.

## Evidence: failure pattern in the supplied outputs

Four recent figure outputs expose a common family of failures across close-perspective and full-body views.

### 1. Genericization survives despite subject-specific instructions

Observed symptoms:

- legs collapse into near-parallel rails instead of preserving taper, joint transition, foreshortening, and shoe orientation;
- arms/sleeves become tubes or rounded capsules;
- feet simplify into block/wedge symbols;
- rifles/attached objects read as long rails plus circles/rectangles rather than one coherent constructed object with body contact;
- face components can read as placed symbols rather than consequences of a cranial/jaw volume and face turn.

The current skill already says these forms should not be generic. The failure is therefore not missing prose; it is missing execution gates.

### 2. Hair is described as strands before the mass is convincingly solved

Repeated light parallel hair strokes appear even where the important problem is the outer hair mass, parting, clump overlap, jaw/neck handoff, or foreground ownership.

This violates the existing `head-face-hair` intent in practice even though that leaf explicitly warns against parallel strand filling.

### 3. Construction/search marks survive too long

The outputs retain many faint exploratory or explanatory marks after stronger descriptive lines already exist. Because the lines are low-contrast, they can appear harmless individually, but together they flatten hierarchy and make the final drawing look unfinished.

The present retirement rule is advisory. It does not force the worker to prove that each surviving construction mark still contributes unique information.

### 4. Line hierarchy is weak

Important silhouette/occlusion boundaries, minor internal seams, hair accents, construction lines, and incidental hatch marks often occupy too narrow a visual hierarchy. The result is not simply a renderer-pressure problem; it is also a semantic-authoring problem because the worker has not committed to which relation owns visual priority.

### 5. Close-perspective drawings do not fully propagate depth through the body

Large head scale is not itself an error in a close camera view. The problem is that head enlargement can coexist with a torso/pelvis/leg chain that reads flat, weakly connected, or diagrammatic. Perspective must propagate through projected spacing, overlap, width change, near/far exposure, and terminal orientation — not merely through one enlarged local mass.

### 6. Context lines can become unowned decoration

In the close-perspective environment sketch, several long light lines read as generic perspective/context marks rather than visible edges or clearly declared ground/plane evidence. Environment marks need the same ownership rule as figure marks.

### 7. Local readability can hide whole-drawing weakness

A face, pocket, seam, or rifle detail may be individually recognizable while the global figure remains too symmetric, too rail-like, too flat, or insufficiently grounded. The current loop recommends returning to the whole, but does not require a concrete whole-read verdict before continuing.

## Root cause

The current skill has strong declarative principles but a weak **decision closure contract**.

Today the routing graph can tell a worker:

- observe whole → relation → part → relation again;
- do not use generic symbols;
- retire obsolete construction;
- hair is a mass, not parallel strands;
- fix macro residuals before micro polish.

However, it does not require the worker to produce a minimal evidence packet proving that these rules were actually applied before a semantic group is accepted.

This permits the following failure loop:

```text
read correct guidance
→ author plausible shorthand
→ render looks recognizable
→ add more local marks
→ construction remains
→ no explicit anti-symbol / ownership / hierarchy audit
→ finish with a drawing that is recognizable but generic and unfinished
```

The redesign must change the loop itself rather than add more descriptive prose around the same behavior.

---

# Part A — renderer/replay architecture

## A1. Keep v11 as the current renderer family

For the next quality cycle:

```text
current renderer family = pillow-pencil-contact-v11 / 1
```

Do not add v12 merely because v11 behavior is corrected in unreleased development.

`renderer_id` should identify a renderer family/protocol, not every implementation iteration.

## A2. Move exact reproducibility to a contract digest + package release boundary

The registry already exposes a renderer contract digest, but `RenderProfile` persists only renderer id/version. That encourages old implementations to stay installable forever just to keep numbered identities alive.

Redesign target:

```text
RenderProfile
├─ renderer_id              family identity, stable
├─ renderer_version         protocol/schema compatibility, rarely changes
└─ renderer_contract_digest exact pixel-behavior contract
```

Exact replay rule:

1. Same renderer family + same contract digest → replay is eligible for exact rendering.
2. Same family + different digest → do not silently claim exact replay.
3. A historical published package/tag remains the canonical way to reproduce its frozen digest.
4. Explicit migration may re-render under the current contract, but that is a migration, not historical replay.

The published `v1.0.3` tag and wheel remain immutable truth for the original v11 contract. Current-source v11 may evolve only after this digest boundary exists or an equivalent fail-closed mechanism is proven.

## A3. Stop accumulating historical renderer implementations in active src

Long-term target:

```text
active src
└─ one current pencil-contact implementation

historical exactness
├─ published wheel/tag
├─ frozen contract/evidence
└─ explicit migration tooling
```

Do not keep growing `_BACKENDS` as v9, v10, v11, v12, ... solely to preserve every past source implementation in the current install.

A bounded compatibility window may remain temporarily while migration is introduced, but permanent generation accumulation is not the architecture.

## A4. Renderer fixes must preserve geometry authority

Material corrections may change width, pressure response, terminal deposition, grain, or paper interaction, but must not silently re-author already-correct points.

For terminal behavior specifically:

- operate on renderer sampling/patch behavior, not by replacing authored geometry;
- terminal effect must remain local to the justified visible suffix;
- a terminal mode change must not reseed the entire stroke body unless the contract explicitly says material identity changed;
- `contact` should remain the neutral/default authority against which release behavior is compared.

## A5. Version policy

Do not bump package version merely to open a development slice.

Preferred sequence:

```text
main stable identity
→ design branch
→ implementation branch on current family
→ visual dogfood
→ mechanical regression
→ only then choose next package version / RC
```

Release numbering follows a validated package boundary, not internal experimentation count.

---

# Part B — instruction redesign

## B1. Replace advisory guidance with reversible visual evidence gates

Do not reintroduce a rigid stage pipeline. Use **reversible gates** that can be reopened at any time.

Each semantic group must carry a compact decision packet before it is accepted:

```text
1. visible authority
   - what exact reference evidence supports this group?
2. anchors
   - 2–5 neighboring anchors that constrain placement/scale/direction
3. ownership
   - what physical boundary/form/relation owns each final line?
4. geometry claim
   - what curvature/overlap/width/depth/contact relation is being asserted?
5. mark language
   - why this role/weight/terminal/material expresses that geometry?
6. disproof test
   - what fresh visual evidence would cause this group to be replaced?
```

This packet is small. It is not paperwork for its own sake; it exists to stop symbolic shorthand from becoming accepted geometry without comparison.

## B2. Add a mandatory line-ownership rule

Every surviving final stroke must have one primary owner, such as:

- silhouette boundary;
- overlap/occlusion boundary;
- form turn / plane break;
- seam / component boundary;
- hair-mass or clump boundary;
- feature/identity line;
- structural contact;
- value hatch family;
- environment plane/edge.

A stroke may communicate multiple facts only when they belong to the **same continuous physical relation**.

Do not allow one convenience stroke to continue across ownership changes — for example hair → arm, jaw → collar, garment edge → background line, or object rail → body contour.

Unowned final marks are either construction/search marks that must be retired or decorative noise that should not be authored.

## B3. Add an anti-symbol audit before local detail is accepted

For visible-enough parts, reject these shorthand failures unless the reference truly supports them:

- head = circle + feature icons;
- hair = parallel strand field;
- arm/leg = parallel rail pair;
- hand = mitten + ticks;
- foot/shoe = box/wedge without observed orientation/construction;
- rifle/prop = rails + generic circles/rectangles;
- clothing = outline plus decorative zigzag/hatch noise;
- environment = arbitrary perspective rays with no visible plane/edge owner.

The audit question is not "is the category recognizable?" It is:

> Does the smallest surviving line set preserve the subject-specific curvature, taper, overlap, orientation, contact, and asymmetry that distinguishes this instance from a generic symbol?

If no, route upstream before adding detail.

## B4. Make perspective propagation explicit

When camera foreshortening is strong, record depth groups before local rendering:

```text
near group
mid group
far group
```

For each connected chain, verify:

- projected spacing;
- apparent width change;
- overlap order;
- near/far exposure;
- terminal orientation;
- connection through occlusion.

A large near head with a diagrammatic flat body is a failed perspective solution even when the head itself is attractive.

## B5. Hair: mass → clumps → accents, with a hard stop between levels

New hair rule:

1. Solve head + hair outer mass and jaw/neck/shoulder ownership.
2. Solve major parting and a small number of clump boundaries.
3. Inspect at whole-head scale.
4. Only then add selected strand accents.

If parallel strand accents are carrying the silhouette or compensating for an unresolved hair mass, delete them and reopen the mass.

## B6. Limbs: prohibit rail completion

A limb interval may not be considered resolved merely because two side lines connect joint A to joint B.

At least one subject-specific relation must be visible where evidence allows it:

- taper/width change;
- near/far edge asymmetry;
- joint insertion/overlap;
- bend/rotation cue;
- foreshortened projected spacing;
- garment compression/tension that explains the form;
- terminal orientation/contact.

This applies equally to sleeves and trouser legs.

## B7. Props and body contact must be solved as one relation

For attached/held objects, do not finish the object independently and then place it beside the body.

Verify together:

- object principal axis and thickness;
- attachment/contact points;
- hand or strap ownership;
- overlap order against torso/limbs;
- visible negative spaces;
- continuation through occlusion;
- scale relative to neighboring body landmarks.

## B8. Construction retirement becomes a required audit

Before a drawing can be treated as clean/final, classify each surviving provisional mark:

```text
KEEP    contributes unique structural/form information intentionally visible
SOFTEN  still useful but must remain subordinate
RETIRE  duplicated, contradicted, or replaced by stronger description
```

Default is **RETIRE once its information has been replaced**.

A large population of faint lines is not automatically acceptable because opacity is low.

## B9. Enforce visual hierarchy

Use at least three semantic dominance levels conceptually, independent of exact numeric pressure:

```text
primary   silhouette / decisive overlap / focal identity
secondary internal form / seam / clump / prop structure
tertiary  construction remnant / hatch / context accent
```

The worker must inspect whether these levels actually read differently at final scale. If not, retune or retire; do not rely on nominal tool names alone.

## B10. Hatching and context need causal ownership

Hatching is allowed only when it serves at least one of:

- value family;
- plane turn;
- material direction;
- fold compression/tension;
- cast/contact shadow;
- explicit stylistic treatment requested by the user.

Random light scratches are not "detail".

Environment lines must similarly correspond to visible or intentionally constructed planes/edges. Do not add generic perspective rays merely to make the scene look more complete.

## B11. Whole-read gate after every accepted local group

After a local group changes, fresh inspection must answer:

- Did the whole become more specific or merely busier?
- Did silhouette, pose, depth, balance, or identity drift?
- Did a local correction introduce a new tangent/merge/ownership conflict?
- Is the next highest-impact residual still local?

If the whole became more generic, flatter, more parallel, or more symmetric, reopen the parent premise immediately.

## B12. Completion must require explicit residual ranking

Before final finish, the Agent must name the three largest remaining visible mismatches, or explicitly state that fewer than three remain.

For each remaining mismatch:

```text
blocking? yes/no
owner
why it remains
why it is acceptable if non-blocking
```

This prevents "recognizable" from silently becoming equivalent to "finished".

For `finish_intent="subject"`, face/hair, hands/feet, clothing, prop, grounding/context, line hierarchy, and construction retirement must all be explicitly accounted for.

---

# Part C — instruction graph changes

Implementation should prefer a small number of stronger edits over more leaf proliferation.

## C1. New central leaf

Add:

`references/review/visual-quality-gates.md`

Owns:

- semantic-group evidence packet;
- line ownership;
- anti-symbol audit;
- hierarchy audit;
- retirement audit;
- whole-read return;
- final top-residual ranking.

This becomes the bridge between existing observation/subject leaves and completion.

## C2. Modify existing leaves rather than duplicate them

Targeted changes:

- `SKILL.md`
  - canonical loop explicitly includes evidence gate + retirement;
  - start route opens `visual-quality-gates.md` for observed finished drawings;
  - renderer-generation policy is not drawing guidance and stays out of worker instructions.

- `foundation/line-economy.md`
  - add ownership continuity rule;
  - distinguish "one informative line" from a convenience line that crosses physical owners.

- `observation/visual-observation.md`
  - add near/mid/far depth grouping for strong perspective;
  - require anchor evidence for the next semantic group.

- `figure/head-face-hair.md`
  - hard sequence: mass → clump → accent;
  - reject strand accumulation before mass closure.

- `construction/balance-and-limbs.md` and `figure/legs-feet.md`
  - add rail-completion rejection.

- `props/attached-objects.md`
  - require object/body relation to be solved jointly.

- `environment/ground-and-context.md`
  - require owner for context lines; reject generic perspective decoration.

- `review/stroke-retirement.md`
  - convert retirement from suggestion to explicit KEEP/SOFTEN/RETIRE audit.

- `review/residual-correction.md`
  - add "busier but not more specific" escalation and ownership conflict checks.

- `review/completion.md`
  - require largest-remaining-residual ranking and hierarchy/retirement accounting.

- `markmaking/pressure-and-terminals.md`
  - keep terminal semantics narrow;
  - state that terminal choice occurs only after geometry + owner are justified;
  - do not elevate terminal semantics into a renderer-generation boundary.

---

# Part D — implementation order

Do not change renderer pixels before the instruction redesign has a measurable visual contract.

```text
Q01  failure taxonomy + visual-quality-gate design        ACTIVE
Q02  instruction graph patch                              BLOCKED by Q01
Q03  fresh-worker dogfood on supplied failure classes     BLOCKED by Q02
Q04  classify remaining failures: geometry vs material    BLOCKED by Q03
Q05  modify current v11 only for proven material defects  BLOCKED by Q04
Q06  renderer contract-digest/replay boundary              may run with Q05, must close before release
Q07  full dogfood + exact mechanical regression           BLOCKED by Q05/Q06
Q08  choose package version/release                        BLOCKED by Q07
```

No `v12` is authorized in this sequence.

---

# Part E — acceptance evidence

## Instruction acceptance

A fresh worker, given only reference + updated skill, must demonstrate across at least:

- one close/strong-perspective figure;
- one full-body 3/4 figure with attached/held prop;
- one frontal or near-frontal full body;
- one head/hair close-up.

Required visual checks:

- no parallel-strand hair field carrying unresolved mass;
- no limb rails accepted as finished structure;
- no block feet when reference supports orientation/construction detail;
- no prop-as-rails shorthand where thickness/contact are visible;
- no arbitrary context rays;
- construction retirement visibly improves clarity;
- hierarchy reads at final output scale;
- top residuals are explicitly ranked before finish;
- whole-subject specificity improves, not merely line count.

## Renderer acceptance

Only after a residual is proven material/runtime-owned:

- same authored geometry remains unchanged through material retuning;
- terminal/material change is spatially bounded to the intended region;
- stable seed/material behavior outside the edited material region is preserved where the contract requires it;
- canonical final and fast final remain pixel-exact for the current contract;
- current v11 family identity remains stable;
- historical v1.0.3 exactness remains reproducible through its frozen package/tag/contract authority.

## Release acceptance

Do not create an RC because implementation exists. Create a release candidate only after fresh-worker dogfood and renderer/runtime gates close.

---

# Non-goals

This redesign does not:

- introduce a rigid P1→P2→P3 lifecycle;
- make measurements or heuristics decide artistic correctness;
- permit raster paint-over or image generation;
- replace observation with anatomy/category priors;
- require every drawing to be fully shaded;
- force one fixed visual style;
- preserve every historical renderer implementation forever in active `src`;
- create renderer v12.

## Working principle

The new contract is:

> **A drawing group is not accepted because it exists, looks plausible, or uses the right tool name. It is accepted only when fresh visual evidence shows that its owned relation became more specific without damaging the whole.**
