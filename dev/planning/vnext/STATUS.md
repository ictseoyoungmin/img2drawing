# img2drawing vNext status

Updated: 2026-09-02

```text
SYSTEM:   stage-free product surface and RC integration closed through B17
ACTIVE:   B18 Dogfood-ready system freeze
NEXT:     D01 after B18 closes
SKELETON: none in the B implementation phase
DOGFOOD:  deferred until B18 dogfood-ready freeze
CLOSED:   B00, B01, B01-R1, B02+B03, B04, B05, B06, B07, B07-R1, B08, B09, B10, B11, B12, B13, B14, B15, B16, B17
```

## Current planning decision — implementation first, dogfood after freeze

The previous status said "third dogfood on an unseen subject, then activate B09". That is
superseded.

The project has already used multiple dogfood runs to expose foundation defects:

- B07-R1: a 313,391-line session revealed that value was being authored as 1,398 machine
  hatch strokes; `fill_region()`, calibrated deposition, compact history, and
  `form before value` closed the root cause.
- B01-R1: a line-only re-draw exposed repeated boundary/termination mistakes;
  `SubjectPalette`, boundary-method guidance, "a line separates two named things",
  "do not draw a termination you did not observe", and "the chain before its end"
  closed the recurring method failures.

Those dogfoods remain valid historical evidence, but **no new fresh/unseen-subject or
cross-agent dogfood is scheduled between B09 and B18**. Repeated subject-specific feedback
should no longer continuously reshape the architecture while product capabilities are
still incomplete.

The new sequence is:

```text
B09 → B10 → B11 → B12 → B13 → B14 → B15 → B16 → B17 → B18
                         no new fresh visual dogfood
                                      ↓
                         D01 → D02 → D03 → D04 → D05 → D06
                                      ↓
                         R01 → R02 → R03 → R04
```

See [`ROADMAP.md`](ROADMAP.md) and
[`VALIDATION_RELEASE.md`](VALIDATION_RELEASE.md).

## Active slice — B18

B18 is the sole production WIP.

Goal: freeze the completed implementation contract, audit cross-slice consistency and
known TODOs, and prepare sealed dogfood inputs without running fresh dogfood.

B18 inherits these closed constraints:

- normal docs/imports/examples lead to canonical vNext `DrawingSession`, never R23/Pn;
- B17 wheel/sdist contain only justified runtime modules/data/docs/examples;
- clean-install smoke covers observed and subjectless mechanical workflows through
  create/resume/inspect/correct/finish/replay/output;
- public API, package version, built metadata, support/migration docs, and CI agree; and
- B12 legacy compatibility remains explicit and isolated rather than physically removed.

B18 may rerun deterministic/synthetic fixtures and preserved regression. It must not
claim general visual quality, unseen-subject robustness, or cross-agent proof; those
claims belong to D01–D06 after B18.

## Closed foundation truth

| Slice | State | Durable result |
|---|---|---|
| B00 | CLOSED | frozen R23 baseline and failure dossier |
| B01 | CLOSED | vNext architecture cut; preserve capabilities, remove ceremony |
| B01-R1 | CLOSED | subject material/boundary observation method hardening |
| B02+B03 | CLOSED | immutable `InspectionSheet` + read-only measurement tools |
| B04 | CLOSED | stage-free `DrawingSession`, atomic checkpoint/resume |
| B05 | CLOSED | ordered construction grammar without runtime phase gate; Pn reading de-anchored |
| B06 | CLOSED | Agent-owned residual/correction loop with provenance |
| B07 | CLOSED | quick/focused/deep evidence read budget + telemetry |
| B07-R1 | CLOSED | value-region authoring, session compaction, fill revision, form-before-value |
| B08 | CLOSED | orthogonal `DrawingIntent`, `ModeGuide`, `StyleGuide`, intent provenance |
| B09 | CLOSED | stage-free `FinishGuide`, relational recognition, form-before-value and preserved-constraint policy |
| B10 | CLOSED | intent/state/inspection-bound `FinishRecord` with stale-state and tamper validation |
| B11 | CLOSED | canonical `RenderProfile`, cursor replay, exact PNG parity, bounded GIF export |
| B12 | CLOSED | explicit lazy `legacy.r23` boundary, R23 v1–v3 resume/migration, canonical root exports |
| B13 | CLOSED | immutable observed/imaginative/hybrid authority, subjectless drawing-only inspection, shared correction/output |
| B14 | CLOSED | five distinct portable mode guides, authored tonal value, free-draw across all authorities, one shared core |
| B15 | CLOSED | three style presets, one-base overrides, structured custom guidance, explicit conflict/provenance semantics |
| B16 | CLOSED | derived authored-element lookup, replacement resolution, bounded summaries, orphan-safe unified edit surface |
| B17 | CLOSED | lean wheel/sdist policy, `0.6.0rc1` API/support truth, clean-installed observed/subjectless examples, package/link/license/security CI audit |

Authoritative closed detail remains in `capsules/`, slice closure records, and committed
evidence. This status file is a current control plane, not a replacement for those records.

## B01-R1 durable observation contract

The latest local hardening is accepted as foundation, not a new workflow.

- `SubjectPalette` only classifies among material patches already identified by the Agent;
  it does not infer semantic correspondence by itself.
- `ambiguous_pairs()` tells the Agent which subject materials are too close for a simple
  measurement assumption.
- `boundary_kind()` names both sides and whether a luminance-only method can see the
  distinction.
- a correction is a new premise and must re-ask the same observation questions.
- repeated marks inherit structural variation; regular sawtooth/ruler repetition is not
  a substitute for observed termination.

This improves observation method without reviving review ceremony or computer-vision
geometry authority.

## B07-R1 durable representation/cost contract

- broad tone/value is one authored `fill_region()` decision, not hundreds of hand/machine
  actions persisted as artistic decisions;
- a disproved value premise is revised through append-only
  `DrawingSession.replace_fill_region()` and can
  bind directly to B06 correction provenance;
- renderer deposition calibration happens outside the drawing session;
- `ReservedLight` may preserve observed light inside a correct form but may not invent
  missing arm/body separation or volume;
- session size is an operational quality signal, but shrinking the file cannot justify a
  visually weak representation.

## Implementation phase guard — B09 through B18

Until B18 closes:

- Production WIP Limit = 1.
- Do not start a new fresh/unseen-subject dogfood run.
- Do not run cross-agent quality campaigns.
- Do not use subject-specific coordinates/answer images to "prove" a new slice.
- Do not create `CroquisSession`, `TonalSession`, `FreeDrawSession`, `ModeStage`,
  `StyleStage`, `FinishStage`, lifecycle cursors, or automatic artistic PASS.
- Use synthetic/deterministic fixtures, compatibility fixtures, existing preserved
  evidence, and direct contract review to close implementation mechanics.
- If a closed foundation premise is disproved by implementation evidence, REOPEN the
  responsible slice narrowly rather than adding a workaround to the active slice.
- Do not physically remove R23 during B09–B18. B12 isolates it; physical retirement is
  post-dogfood R03.

## Remaining implementation queue

```text
B09  Finish / recognition authoring                     CLOSED
B10  Intent-aware completion                            CLOSED
B11  Canonical RenderProfile + replay/GIF parity         CLOSED
B12  Legacy runtime / persistence isolation              CLOSED
B13  Reference authority + subjectless runtime           CLOSED
B14  Drawing-mode capability completion                  CLOSED
B15  Style authoring completion                          CLOSED
B16  Agent authoring / editing ergonomics                CLOSED
B17  Package / public API / release-candidate truth      CLOSED
B18  Dogfood-ready system freeze                         ACTIVE
```

Each slice has its execution contract in `slices/B09.md` … `slices/B18.md`.

## Post-freeze validation and release

After B18 only:

```text
D01 difficult observed croquis
D02 observed figure / subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative + hybrid
D06 cross-agent reproducibility

R01 consolidate repeated dogfood fixes
R02 final regression
R03 physical R23 retirement
R04 release
```

Dogfood defects always route back to the responsible implementation slice. Examples:

- face/hair recognition relation failure → B09 REOPEN
- premature finish semantics → B10 REOPEN
- replay/GIF mismatch → B11 REOPEN
- subjectless/hybrid authority failure → B13 REOPEN
- mode contract failure → B14 REOPEN
- style conflict → B15 REOPEN
- edit ergonomics/provenance failure → B16 REOPEN

## Current repository truth

- Frozen R23 baseline: `25ec4544e86fe37fc28d64575df145a1b711d63a`
- Planning pivot base includes latest observation hardening commit
  `731a04db37ecda14d8f5de28d946a97adaa8dde6`.
- Canonical vNext remains one `DrawingSession` / history / renderer / inspection /
  correction core.
- Legacy stage runtime is isolated under `img2drawing.legacy.r23` and remains
  compatibility/history material until post-dogfood R03 retirement.
- Observed, imaginative, and hybrid work share one immutable `ReferenceAuthority`
  contract; subjectless evidence is drawing-only and never fabricates a reference.
- Croquis, figure drawing, tonal study, line study, and free-draw resolve to distinct
  immutable guidance while sharing one session/history/inspection/correction/output core.
- Three retained style presets, single-base overrides, and complete structured custom
  guidance affect authored policy only; style selection never mutates geometry or the
  canonical RenderProfile.
- Current/superseded/deleted stroke and fill responsibility is derived from authoritative
  history on demand; bounded summaries are cursor/state-bound and never checkpointed.
