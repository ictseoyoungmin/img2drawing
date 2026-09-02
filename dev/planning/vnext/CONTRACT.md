# img2drawing vNext architecture contract

Status: **CURRENT**
Updated: 2026-09-01

This document owns architecture invariants shared by the closed B00–B11 foundation
(including B01-R1/B07-R1) and B12–B18 implementation. `ROADMAP.md` owns sequencing;
slice cards own deliverables. Fresh visual dogfood starts only after the B18 freeze.

## 1. One canonical core

One `DrawingSession` is the canonical orchestration authority:

```text
DrawingSession
  ├─ observe
  ├─ draw / draw_many
  ├─ replace / replace_segment / soft_lift / delete
  ├─ fill_region / replace_fill_region
  ├─ inspect
  ├─ record_residual / record_correction
  ├─ intent / intent_history / set_intent
  ├─ checkpoint / resume
  ├─ render / replay / export
  └─ finish

PoseObservation + ConstructionMark* → InitialConstruct
InitialConstruct → author_initial_construct → inspect_initial_construct
```

```text
Agent observation / authored intent
              ↓
DrawingSession → one authoritative action history → StrokeIR snapshot
                                                     ├─ renderer
                                                     ├─ inspection
                                                     └─ replay/output
```

- `DrawingSession` and shared history are the only session/action truth.
- Renderer and inspection consume the same read-only authored snapshot.
- B02+B03 `InspectionSheet` is the only vNext inspection implementation.
- Geometry and value changes are explicit authored history actions.
- The Agent owns visual acceptance and highest-impact residual selection.

## 2. Stage-free lifecycle

```text
create → observe/declare → draw → inspect → choose residual
       → correct → inspect → repeat → finish
```

The canonical lifecycle has no P1–P6, `stage_start`, `advance`, `close_stage`,
`reopen_stage`, or downstream invalidation. Ordered drawing grammar is authoring guidance,
not a runtime cursor or gate.

## 3. Durable invariants

- Every reference/mode/finish/style intent shares one session, history, renderer,
  inspection, and correction core.
- Public vNext code does not branch on Pn or a stage registry.
- Inspection binds exact evidence and state digests; stale evidence cannot represent
  current truth.
- Checkpoints are portable and atomic and preserve history/evidence/intent/correction
  continuity after resume.
- A correction action is not proof of improvement; it requires fresh render/inspection.
- `ResidualRecord` binds an Agent-selected mismatch to evidence and responsible context.
  `CorrectionRecord` binds explicit actions to fresh after-evidence. Neither is a score or
  lifecycle state.
- Macro pose, form, and composition residuals outrank detail/style polish.
- **Form before value:** major limb, torso, clothing volume, overlap, and prop contact
  remain legible without tone. A value primitive cannot replace missing structure.
- Broad value is one authored region decision such as `fill_region()`, not hundreds of
  persisted generated microstrokes.
- A disproved value premise is revised append-only through
  `DrawingSession.replace_fill_region()` and
  correction provenance.

## 4. Observation and measurement authority

Observation tools assist Agent judgment; they do not decide correspondence or geometry.

- Crop, grid, plumb, angle, distance, and profile answer bounded read-only questions.
- A luminance profile sees luminance difference, not an invisible material boundary.
- `SubjectPalette` compares Agent-identified material patches and ambiguous pairs; it is
  not a semantic detector.
- Name the two forms or materials a proposed boundary separates before drawing it.
- Never invent an unseen termination from an anatomy default.
- A correction is a new premise and repeats the relevant observation question.

The first subject read must explicitly record body view, torso turn, near/far side,
visibility, occlusion, overlap order, and uncertainty. In a turned figure, exposed
shoulder/upper-arm/forearm/elbow volume and a partly pocket-occluded hand are macro
relationships; do not collapse a visibly thick arm into a narrow contour because the hand
is hidden.

## 5. Evidence budget

`EvidencePolicy` quick/focused/deep values are presentation/read budgets, not stages:

```text
quick   → whole sheet only; no extra ROI/guide/grid/measurement
focused → exactly 1–3 prioritized ROI; no extra guide/grid/measurement
deep    → up to 3 ROI + guide/grid/measurement; escalation_reason required
```

`EvidenceTelemetry` records inspection/read/artifact/review-turn/elapsed work. It never
chooses geometry, residual priority, or artistic PASS.

## 6. Intent and reference authority

`DrawingIntent`, `ModeGuide`, `FinishGuide`, and `StyleGuide` are portable plain data:

```text
DrawingIntent
  ├─ reference_mode: observed | imaginative | hybrid
  ├─ drawing_mode: croquis | figure_drawing | tonal_study | line_study | free_draw
  ├─ finish_intent: pose | subject | form_light | expressive
  ├─ style_profile: preset/custom identifier
  └─ provenance
```

The axes are independent; none is lifecycle state. `IntentChangeRecord` preserves each
intent snapshot, reason, and history cursor append-only. Changing intent never rewrites
geometry automatically.

B13 completes these authority meanings through one correction core:

- **observed:** material mismatch between readable subject and drawing;
- **imaginative:** mismatch between declared intent/composition/shape goal and drawing;
- **hybrid:** mismatch against a preserved reference constraint or explicit transformation.

Imaginative/hybrid work cannot invent subject overlays or fake measurement authority.

## 7. Mode, finish, and style

`ModeGuide` may declare primary observations, recommended grammar, omissions, finish
emphasis, and completion questions. It cannot own phase count, cursor, `advance`,
`close`, or PASS. The deliberately small B14 target is:

```text
croquis
figure_drawing
tonal_study
line_study
free_draw
```

B09 connects `pose | subject | form_light | expressive` to distinct authoring guidance
without a `FinishStage` or P7. Recognition is relational.

```text
StyleGuide    = how the Agent authors marks
RenderProfile = how the renderer materializes authored marks
```

Style is not a post-filter and cannot override subject geometry. B15 retains one base
plus explicit overrides; it does not create an inheritance graph or general DSL.

## 8. Completion

B10 `FinishRecord` contains:

```text
intent_digest
drawing_state_hash
final_inspection_id
history_cursor
accepted_limitations
rationale
```

It is Agent decision provenance, not an automatic artistic certificate. Later material
mutation, intent change, stale inspection, or a new material residual invalidates its
current status.

## 9. Replay and output parity

One canonical history and versioned `RenderProfile` must reproduce final PNG, latest
replay state, and the final GIF frame as the same output family. The profile binds at
least renderer ID/version, canvas, material/pencil, paper/grain, supersampling, seed
domain, compositing, and encoding. Timelapse uses action 0 through latest with a declared
sampling policy such as `every_n`.

## 10. Persistence and legacy boundary

- R23 baseline `25ec4544e86fe37fc28d64575df145a1b711d63a` is read-only history.
- `img2drawing` is canonical; R23 is explicit at `img2drawing.legacy.r23`.
- Canonical imports and wildcard exports do not load or advertise stage/review/reopen/Pn
  persistence.
- R23 checkpoint v1–v3 resume/migration reuses the existing R23 validator and shared
  action/history implementation.
- Unsupported schemas fail with versioned, actionable guidance.
- Migration preserves subject/action/source-state lineage. It records absent historical
  renderer identity honestly and binds an explicit target `RenderProfile`.
- Stage progress, stage reviews, reopens, and legacy finish claims remain historical and
  never become vNext authority.
- No `core_v2`, alternate history, or copied renderer/tool tree is allowed.
- B12 performs no physical deletion.
- Physical R23 retirement occurs only at R03 after D01–D06 and R02 regression—not B18.

## 11. Implementation/dogfood boundary

B09–B18 may close with deterministic or synthetic fixtures, migration/compatibility
fixtures, unit/integration/checkpoint/replay/packaging regression, preserved historical
evidence, and direct contract/code review.

They may not use new unseen-subject dogfood as a closure gate, run a cross-agent quality
campaign, present an answer image or subject-specific coordinate table as generic proof,
or add a parallel workflow to fit one dogfood result. Full fresh validation starts at
D01 after B18; defects reopen the responsible slice.

## 12. Architecture review triggers

Stop and re-check this contract if any of the following appears:

```text
ModeStage / StyleStage / FinishStage
advance_mode / close_mode / mode_complete / style_complete
automatic likeness/style/artistic PASS
per-mode session/history/renderer/inspection copies
legacy Pn returning to the normal route
raster-only geometry mutation outside history
style renderer/post-filter overriding geometry truth
imaginative mode inventing reference authority
```

## 13. Remaining implementation surface

```text
B12  legacy isolation
B13  subjectless/reference authority
B14  mode capability completion
B15  style authoring completion
B16  edit ergonomics
B17  package/public API/release-candidate truth
B18  system freeze for dogfood
```

Each active slice freezes only the smallest required schema/API. D01–D06 after B18 own
full visual robustness claims.
