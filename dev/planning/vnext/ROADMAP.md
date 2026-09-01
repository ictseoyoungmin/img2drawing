# img2drawing vNext full roadmap

Updated: 2026-09-01
Workflow: Bottleneck · Production WIP Limit = 1

This roadmap reflects current HEAD and user direction. The governing change is that no
new fresh visual dogfood is inserted between B09 and B18. Complete and freeze the product
surface first, then validate it through the integrated D01–D06 campaign.

## Phase A — foundation

| ID | State | Goal | Authority |
|---|---|---|---|
| B00 | CLOSED | R23 baseline and failure dossier | `capsules/B00.md` |
| B01 | CLOSED | vNext architecture cut | `capsules/B01.md` |
| B01-R1 | CLOSED | subject observation/boundary hardening | `STATUS.md` + preserved evidence |
| B02+B03 | CLOSED | inspection and measurement foundation | `capsules/B02-B03.md` |
| B04 | CLOSED | stage-free `DrawingSession` | `capsules/B04.md` |
| B05 | CLOSED | construction grammar and canonical Pn de-anchoring | `capsules/B05.md` |
| B06 | CLOSED | residual-driven correction and provenance | `capsules/B06.md` |
| B07 | CLOSED | bounded evidence and telemetry | `capsules/B07.md` |
| B07-R1 | CLOSED | value-region authoring, compaction, form-before-value | `STATUS.md` |
| B08 | CLOSED | orthogonal intent/mode/style scaffold | `capsules/B08.md` |

The foundation provides one loop:

```text
observe/read subject or declare intent
→ draw through one authoritative history
→ inspect bounded evidence
→ record the highest-impact residual
→ edit the responsible representation
→ inspect fresh evidence
```

## Phase B — complete the product surface

| ID | State now | Goal | Depends |
|---|---|---|---|
| B09 | CLOSED | finish and relational recognition authoring | B08 + hardening |
| B10 | CLOSED | intent-aware completion | B09 |
| B11 | CLOSED | canonical `RenderProfile` and replay/GIF parity | B10 |
| B12 | CLOSED | legacy runtime and persistence isolation | B11 |
| B13 | CLOSED | reference authority and subjectless runtime | B12 |
| B14 | ACTIVE | drawing-mode capability completion | B13 |
| B15 | SKELETON | style authoring completion | B14 |
| B16 | SKELETON | Agent authoring/editing ergonomics | B15 |
| B17 | SKELETON | package/public API/release-candidate truth | B16 |
| B18 | SKELETON | dogfood-ready system freeze | B17 |

```text
B00…B08 CLOSED
      ↓
B09 → B10 → B11 → B12 → B13 → B14 → B15 → B16 → B17 → B18
      [NO NEW FRESH DOGFOOD BETWEEN THESE SLICES]
```

Each slice closes its technical contract with deterministic fixtures,
unit/integration regression, preserved evidence, and direct review. It makes no
fresh-unseen-subject or cross-agent quality claim.

### B09 — finish and relational recognition

Connect `pose | subject | form_light | expressive` to distinct authoring policy.
Recognition is a relationship-quality target—not P7 or a lifecycle gate. Face, hair,
hands, feet, clothing, and props are judged through subject-specific spacing, overlap,
contact, termination, and topology. Form remains legible before value or detail.

### B10 — intent-aware completion

Define done as absence of material residuals against declared intent, not stage/checklist
completion. `FinishRecord` binds the Agent decision to current state, intent, final
inspection, history cursor, rationale, and accepted limitations. It is not an automatic
artistic certificate, and later material mutation makes it stale.

### B11 — canonical rendering and replay

Separate `StyleGuide` from rendering. Bind renderer/version, material, paper,
supersampling, seed, compositing, and encoding in one versioned `RenderProfile`. One
history/profile provides action-0-to-latest replay, bounded GIF, and canonical PNG parity.

### B12 — legacy isolation

Make `img2drawing` canonical and place R23 under `img2drawing.legacy.r23`. Canonical
imports cannot load stage registry, stage review, reopen, or Pn persistence. Resume and
migration reuse the shared stroke/history/renderer core; no copied `core_v2` exists.
Physical R23 deletion remains deferred.

### B13 — reference authority and subjectless runtime

Complete runtime support for declarations scaffolded in B08:

```text
observed    → readable subject is evidence authority
imaginative → subjectless canvas + declared intent is authority
hybrid      → preserved reference constraints + explicit transformations are authority
```

Support subjectless `DrawingSession` and reference-free inspection/correction semantics
without fake overlays, measurements, or reference authority.

### B14 — drawing-mode capability

Complete `croquis`, `figure_drawing`, `tonal_study`, `line_study`, and `free_draw` on one
core. `ModeGuide` may describe observations, grammar, omissions, finish emphasis, and
completion questions, but never stage count, cursor, `advance`, or automatic PASS.

### B15 — style authoring

Complete a small evidence-backed surface starting with `pencil_loose`,
`graphite_academic`, and `graphite_tonal`, using one base plus explicit overrides and
optional structured custom prose. Style cannot change geometry truth or become a raster
post-filter.

### B16 — authoring/editing ergonomics

Make existing draw/replace/segment/lift/delete/fill operations easy to locate and use in
long correction loops. Reuse `part`, `role`, provenance, and supersession instead of
creating a new ownership lifecycle.

### B17 — package and release-candidate truth

Align wheel/sdist, clean install, examples, public/support matrix, documentation links,
package content, versioning, migration, and CI with canonical vNext truth. This proves
integration readiness, not final visual quality.

### B18 — dogfood-ready freeze

Freeze the canonical API, session schema, intent, `RenderProfile`, mode/style surface,
and legacy-adapter boundary. Close known implementation TODOs. Subsequent dogfood defects
reopen responsible B-slices instead of adding new feature slices.

## Phase C — integrated dogfood

Starts only after B18. [`VALIDATION_RELEASE.md`](VALIDATION_RELEASE.md) owns the detailed
contracts.

```text
D01 difficult observed croquis
D02 observed figure and subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative and hybrid
D06 cross-agent reproducibility
```

All runs use unseen/fresh inputs, omit answer images, authored coordinate tables, prior
sessions/traces, and Pn packets, and evaluate cost together with visual quality. A defect
reopens its responsible B-slice—for example, facial relation failure reopens B09,
subjectless persistence reopens B13, replay parity reopens B11, and edit-surface failure
reopens B16.

## Phase D — harden and release

Starts only after D01–D06 pass.

```text
R01 consolidation      absorb repeated fixes into canonical docs/API
R02 final regression   modes + checkpoint/resume + PNG/replay/GIF
R03 physical R23 retirement
R04 release
```

Only R03 may delete remaining stage runtime, review manifests, Pn references, stale
exports, or legacy package data—or retain a deliberately time-bounded adapter. Frozen Git
baseline and historical evidence remain intact.

## Global release exit

Release must directly prove all of the following:

- A new-task worker completes `observe/declare → draw → inspect → correct → finish`
  without Pn.
- Observed, imaginative, and hybrid authority use one session/history core.
- Mode differences appear in authored behavior rather than metadata alone.
- Style differences appear in line/value/edge/detail decisions rather than post-filters.
- Major form and overlap remain legible without tone.
- Canonical session cost does not explode through brute-force authored microstrokes.
- PNG/replay/GIF share renderer provenance and final-state parity.
- Package, docs, examples, and CI point to the same canonical route.
- R23 is not exposed as a normal route outside its explicit compatibility/history boundary.

## Planning authority

- Current state: `STATUS.md`.
- Architecture invariants: `CONTRACT.md`.
- Executable work: `slices/B09.md` through `slices/B18.md`.
- Post-freeze validation/release: `VALIDATION_RELEASE.md`.
- Historical HTML and temporary plans are inputs, never current status authority.
