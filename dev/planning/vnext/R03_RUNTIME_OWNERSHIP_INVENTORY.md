# R03 runtime ownership inventory

Updated: 2026-09-04
Baseline: `ddbad8a778803b1674ea66cd2b47acc031bf727b` (`0.6.0rc2`)
Status: **PRE-D01 BASELINE — no runtime change**

## Purpose

This is the detailed physical-code inventory that A3 intentionally did not turn into a
pre-dogfood refactor. It records which shipped Python modules are canonical, shared,
mixed with compatibility residue, or R23-only so R03 can retire code from evidence rather
than rediscovering ownership after D01–D06.

This document is **not** permission to delete compatibility code before the support window
is decided. D01 remains the next product bottleneck. No source, schema, import, or persisted
runtime behavior changes as part of this inventory.

## Classification vocabulary

- **CANONICAL** — part of the current `DrawingSession` product implementation or its declared
  public/declarative surface.
- **SHARED** — current capability used by vNext and safe to retain independently of R23.
- **MIXED** — current capability and compatibility residue share one module/namespace; R03
  must split responsibility before deleting anything.
- **LEGACY-ONLY** — no current vNext orchestration ownership; retained for R23 compatibility,
  old replay/support, or historical callers.
- **ADAPTER** — explicit compatibility boundary whose future depends on the R03 support
  decision.

A classification is about product ownership, not whether the code is technically reusable.
R03 should not preserve an obsolete workflow merely because some of its helpers are generic.
Conversely, a shared primitive must not be deleted because R23 also imports it.

## Reachability baseline

The current `img2drawing.vnext.session.DrawingSession` reaches `core`, `inspection`, `render`,
and vNext modules directly. Canonical output also uses bounded primitives from
`provenance.timelapse`. It does not import the historical `run`, `stages`, `exemplar`,
`review`, `registration`, or `reference` orchestration cluster.

The package build currently discovers every `img2drawing*` package under `src`, so lazy
legacy code is still physically shipped even when normal imports never activate it.
The explicit compatibility cluster (`run`, `stages`, `exemplar`, `review`, `registration`,
`canvas`, `reference`, and the R23 adapter) is roughly **400 KiB of Python source** before
counting mixed observation/root/core residues or schemas. This number is a footprint baseline,
not a removal target by itself.

## Module-by-module inventory

### Package root

| Module | Class | Current ownership | R03 candidate action |
|---|---|---|---|
| `img2drawing.__init__` | MIXED | canonical narrow root plus pre-rc2 and R23 lazy shims | keep canonical exports; decide and prune compatibility shims separately |
| `img2drawing._version` | MIXED | current version/API IDs plus explicit R23 IDs | keep current IDs; move/remove R23 constants with the final adapter decision |

The root's pre-rc2 compatibility window is separate from R23 support. R03 must not silently
retire one because it is retiring the other.

### `img2drawing.vnext` — canonical implementation

All of these are **CANONICAL** and are not physical-retirement candidates merely because the
package is still named `vnext`:

| Module | Ownership |
|---|---|
| `vnext.__init__` | current advanced vNext namespace |
| `vnext.session` | canonical `DrawingSession`, checkpoint/resume, current mutation/inspection lifecycle |
| `vnext.construction` | stage-free observed construction facade |
| `vnext.correction` | residual/correction records |
| `vnext.editing` | authored-element lookup and edit navigation |
| `vnext.evidence` | bounded evidence policy/telemetry |
| `vnext.intent` | intent/mode/style guide data |
| `vnext.completion` | finish record/currentness contract |
| `vnext.output` | canonical PNG/cursor replay/GIF orchestration |
| `vnext.reference_authority` | observed/imaginative/hybrid authority contract |
| `vnext.render_profile` | persisted canonical render contract |
| `vnext.value` | current value-region authoring helpers |

R03 may later flatten the package name only if there is a product reason. A rename is not a
retirement requirement.

### `img2drawing.core` — shared drawing authority with two compatibility seams

| Module | Class | Current ownership | R03 candidate action |
|---|---|---|---|
| `core.__init__` | SHARED | low-level supported stroke/history namespace | keep |
| `core.action` | SHARED + residue | current `AgentDrawingSession`/`DrawingAction`; action schema still carries inert `stage` | keep; consider stage-field retirement only with explicit schema/migration proof |
| `core.fill` | SHARED | `FillRegion`/`ReservedLight` deterministic value primitive | keep |
| `core.history` | SHARED + residue | authoritative `CanvasHistory`; `CanvasAction.stage` persists for compatibility | keep; same schema caution as `core.action` |
| `core.ir` | SHARED + residue | current `Stroke`/`StrokeIR`; `Stroke.stage` remains inert compatibility provenance | keep; do not churn persisted history just for naming cleanliness |
| `core.stroke` | SHARED | current stroke/tool materialization | keep |
| `core.tools` | SHARED | current tool states/presets | keep |
| `core.session` | MIXED | current hash/toolset helpers plus an older persisted `core.session.DrawingSession` facade | split helpers from the old duplicate session facade; retire the duplicate only after callers are inventoried |

The `stage` fields in shared IR/history are the most important **schema residue**. They do not
create a stage machine in vNext, but removing them is a persisted-format change and should not
be bundled into R23 deletion unless there is measurable benefit.

### `img2drawing.inspection` — current specialized public capability

All four modules are **SHARED/current** and remain:

- `inspection.__init__`
- `inspection.model`
- `inspection.measure`
- `inspection.sheet`

This package owns current ROI, guide, measurement, drawing-state hashing, and stage-free
registration. It is not the historical `img2drawing.registration` package.

### `img2drawing.render` — current material/render stack

The canonical `pillow_pencil_contact` renderer depends on the graphite/material submodules,
so old-looking P-number comments inside those files are not evidence that the modules are
legacy-only.

All of the following are **SHARED/current** unless D/R evidence later proves a utility dead:

- `render.__init__`
- `render.pillow_pencil_contact`
- `render.contact_profile`
- `render.pillow_graphite`
- `render.pillow_graphite_grain`
- `render.pillow_hand_dynamics`
- `render.pillow_paper_interaction`
- `render.pillow_pencil_grades`
- `render.pillow_eraser_material`
- `render.presets`
- `render.tone_scale`
- `render.scale_guidance`
- `render.line_weight`

R03 must follow import/use evidence rather than deleting renderer layers by historical naming.

### `img2drawing.provenance` — mixed replay namespace

| Module | Class | Current ownership | R03 candidate action |
|---|---|---|---|
| `provenance.timelapse` | MIXED | vNext uses cursor/GIF primitives, while the module also retains old `stage`/`critic` selection and types against `core.session.DrawingSession` | extract/retain neutral cursor/GIF primitives; retire historical selection modes after caller audit |
| `provenance.replay` | LEGACY-ONLY candidate | loads the older `core.session.DrawingSession`, not canonical vNext checkpoints | remove or move behind compatibility once no supported caller depends on it |
| `provenance.__init__` | MIXED | exports both current timelapse and old replay helper | narrow after the two modules are separated |

This is the clearest small mixed seam that R03 can simplify without touching drawing semantics.

### `img2drawing.observation` — mixed specialized namespace

| Module | Class | Current ownership | R03 candidate action |
|---|---|---|---|
| `observation.palette` | SHARED/current | documented `SubjectPalette`/`MaterialSample` evidence helper | keep |
| `observation.uncertainty` | SHARED/optional candidate | small generic evidence record exposed by the namespace, but not owned by `DrawingSession` | keep through dogfood; retain only if current namespace/support evidence uses it |
| `observation.evidence` | MIXED/optional candidate | generic grayscale/edge evidence helpers, not canonical orchestration | keep through dogfood; decide from current capability use, not R23 history |
| `observation.contract` | LEGACY-ONLY candidate | R23 `ObservationContract`/`ViewObservation` pre-draw lock model | move/remove with R23 observation support if no current caller exists |
| `observation.lock` | LEGACY-ONLY candidate | R23 frozen observation/reopen records | retire with R23 lifecycle runtime |
| `observation.views` | LEGACY-ONLY candidate | historical view helpers | retire if caller audit confirms R23-only ownership |
| `observation.__init__` | MIXED | exposes both current palette helpers and historical records | narrow to current evidence surface after split |

Do not delete the whole namespace: `SubjectPalette` is explicitly documented as a current
specialized public capability.

### `img2drawing.canvas` — historical orchestration convenience

All current vNext mutation/render/inspection paths operate directly through `DrawingSession`,
`CanvasHistory`, `inspection`, and canonical output. The following wrappers are therefore
**LEGACY-ONLY candidates** today:

- `canvas.__init__`
- `canvas.runtime`
- `canvas.inspection`
- `canvas.editing`
- `canvas.transactions`

`img2drawing.run.DrawingRun` is the known owner. R03 should remove these with `DrawingRun`
unless an independent supported caller appears.

### `img2drawing.reference` — R23 reference-bundle model

All three modules are **LEGACY-ONLY candidates**:

- `reference.__init__`
- `reference.model`
- `reference.loader`

Current observed/imaginative/hybrid authority lives in `vnext.reference_authority`; current
inspection/registration lives in `inspection`. Do not keep this package merely because the
word "reference" is still central to the product.

### `img2drawing.registration` — historical registration contracts

All ten modules are **LEGACY-ONLY candidates** under the current product model:

- `registration.__init__`
- `registration.model`
- `registration.grid`
- `registration.compare`
- `registration.envelope`
- `registration.human`
- `registration.orientation`
- `registration.lower_body`
- `registration.head_hair`
- `registration.prop_topology`

Current stage-free registration is already in `img2drawing.inspection`. R23 exports these
historical comparison contracts lazily when explicitly requested.

### `img2drawing.review` — R23 lifecycle/review runtime

A3 already established that this Python package is not the current instruction-graph
`references/review/` concept. All fifteen modules are **LEGACY-ONLY candidates**:

- `review.__init__`
- `review.adaptive_evidence`
- `review.artifact`
- `review.comparison`
- `review.contour_contact`
- `review.correction`
- `review.fidelity`
- `review.local_review`
- `review.pass_memory`
- `review.preview`
- `review.record`
- `review.reference_review`
- `review.reopen`
- `review.resolved_form`
- `review.worker_protocol`

Their ownership is stage review/pass memory/reopen/resolved-form/identity-finish compatibility,
not the stage-free residual loop.

### `img2drawing.stages` — R23 stage machine

All seven modules are **LEGACY-ONLY candidates**:

- `stages.__init__`
- `stages.model`
- `stages.contract`
- `stages.registry`
- `stages.full_body_contracts`
- `stages.full_body_croquis`
- `stages.identity_finish`

This is the most unambiguous physical-retirement group once R23 full-run resume is no longer
supported.

### `img2drawing.exemplar` — R23 grammar/ablation runtime

Both modules are **LEGACY-ONLY candidates**:

- `exemplar.__init__`
- `exemplar.ablation`

Current instruction knowledge lives in the skill instruction graph, not runtime grammar cards.

### `img2drawing.run`

`run.py` is **LEGACY-ONLY** and is the main physical R23 orchestration body. It owns
`DrawingRun`, stage progression, stage review/reopen state, grammar-card bindings, old
reference bundles, and related compatibility behavior.

It should not be rewritten into another canonical runner. R03 must either retain it as a
bounded old-runtime dependency or make the compatibility adapter independent enough to remove
it.

### `img2drawing.legacy`

| Module | Class | Current ownership | R03 candidate action |
|---|---|---|---|
| `legacy.__init__` | ADAPTER | explicit compatibility namespace | keep while any R23 support remains |
| `legacy.r23` | ADAPTER | lazy historical export map plus checkpoint inspect/resume/migrate | shrink to the smallest supported checkpoint adapter; remove full-runtime exports when policy permits |

## Non-Python runtime data

| Asset | Ownership | R03 candidate action |
|---|---|---|
| `data/pencil_contact_profile.json` | current render | keep |
| `data/pencil_presets.json` | current tools/render | keep |
| `data/tone_scale.json` | current value/render | keep |
| `data/registration_profile.json` | historical-registration candidate | remove with old registration if caller audit confirms no current use |

## The main R03 blocker: migration currently depends on the full old runtime

The current compatibility surface supports **R23 inspection, v1-v3 resume, and one-way
migration**. Those are not equivalent costs:

1. `legacy.r23.resume_checkpoint()` imports and calls `img2drawing.run.DrawingRun.resume()`;
2. `legacy.r23.migrate_checkpoint()` first calls that resume path, then converts the resulting
   old runtime state into a vNext checkpoint;
3. resolving `DrawingRun` activates `run/stages/exemplar/review` and related R23 code.

Therefore the full old runtime cannot be physically removed while both old-run **resume** and
the current implementation of **migration** remain supported.

R03 needs an explicit support decision:

```text
Option A — keep time-bounded full R23 resume
  → old runtime remains shipped

Option B — migration-only compatibility
  → implement direct checkpoint-to-vNext migration without constructing DrawingRun
  → retire run/stages/review/exemplar/etc. after parity tests

Option C — end R23 runtime support
  → retain historical Git/dev fixtures only
  → unsupported checkpoints fail with an actionable migration/support message
```

The preferred long-term shape is **B** if real users still need old checkpoints: a small
reader/migrator is cheaper and safer than shipping an entire alternate orchestration system.
D01–D06/R02 evidence should complete before making that compatibility-policy change.

## Secondary mixed seams to revisit at R03

### 1. Shared history still carries `stage`

`DrawingAction.stage`, `CanvasAction.stage`, and `Stroke.stage` remain because R23 and old
persisted histories share the same low-level representation. vNext writes one opaque
compatibility value and does not branch on it.

Do not remove this field merely for aesthetic purity. R03 should ask whether the footprint,
complexity, or schema clarity benefit is large enough to justify a new persisted schema and
migration. If not, leaving an inert field in shared IR is preferable to destabilizing history.

### 2. Two `DrawingSession` concepts still exist

The canonical public class is `img2drawing.vnext.session.DrawingSession`. A separate older
`img2drawing.core.session.DrawingSession` remains as a persisted session/replay facade.
Current vNext mostly uses `core.session` for hash/toolset helpers, while old provenance replay
still loads the duplicate class.

R03 should split the neutral helpers from the old class, then remove/rename the duplicate if
no supported caller remains.

### 3. Timelapse carries historical selection modes

`provenance.timelapse.select_cursors()` is reused by current output but still understands
historical `stage` and `critic` snapshots. Extracting neutral `action/every_n` cursor selection
would let R03 remove stage semantics without replacing the canonical renderer.

### 4. Root compatibility is two different policies

Pre-rc2 root shims and R23 root shims currently share `__getattr__` machinery but are governed
by different support promises. Track them separately during retirement.

## R03 execution order after D01–D06 and R02

```text
R03.0  freeze support decision
       full resume vs migration-only vs end-of-support

R03.1  decouple migration if migration remains supported
       parse/validate old checkpoint without DrawingRun orchestration
       prove action/state/reference identity and failure behavior

R03.2  remove legacy-only orchestration cluster
       run → stages → review/exemplar → registration/reference/canvas
       preserve only shared primitives actually reached by vNext

R03.3  split mixed namespaces
       observation current helpers vs old records
       provenance neutral replay/GIF vs old session/stage modes
       core.session neutral helpers vs old duplicate session

R03.4  prune compatibility roots and legacy constants according to support policy
       keep pre-rc2 and R23 decisions independent

R03.5  re-audit package footprint/import graph
       canonical root must remain stage-free
       wheel/sdist must contain only intended compatibility

R03.6  rerun R02 release regression and checkpoint migration fixtures
```

## Do not do before D01

- do not move/delete the historical runtime merely to make the tree look cleaner;
- do not change `DrawingAction`/`CanvasAction`/`Stroke` persisted fields;
- do not rename `vnext` for cosmetics;
- do not rewrite R23 migration before fresh visual validation;
- do not make dogfood depend on this inventory.

D01 should test the frozen candidate, not a new cleanup branch of the runtime.

## R03 exit evidence

Before physical retirement is accepted, require all of the following:

- one explicit support decision for R23 resume/migration;
- a fresh import graph proving canonical root/session does not activate compatibility code;
- package-content and source-footprint before/after inventory;
- all retained old checkpoint schemas either migrate successfully or fail actionably;
- canonical `DrawingSession` checkpoint/resume and PNG/replay/GIF parity unchanged;
- no stage/review/Pn alternate workflow discoverable from normal root/public docs;
- R02 product regressions still green after the retirement diff.

## Relationship to A3

A3 proved **isolation now**: the current route does not activate the historical cluster.
This document records **retirement ownership later**: what R03 may remove, what it must keep,
and which mixed seams require separation first.
