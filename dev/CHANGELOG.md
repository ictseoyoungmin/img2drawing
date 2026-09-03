# img2drawing changelog

Release history for the `img2drawing` skill. This is the external home for
version/release narrative that used to be woven directly into `SKILL.md` and
`references/`, which made the operating instructions read as an append-only
development log rather than a timeless spec (headings and inline prose stamped
with `R02`..`R22` never got cleaned up, and some had already gone stale — e.g.
a stage-contracts doc still labeled `R02` and a local-review doc still labeled
`R05` long after the current release had moved to `R22`).

`SKILL.md` and `references/` now describe only the current, standing behavior.
This file keeps the *why* and the *history* — what each release changed and
what dogfood testing found along the way — without pinning the operational
docs to a specific revision.

The current release is tracked in `src/img2drawing/_version.py`
(`__version__`, `RELEASE_REVISION`, `RELEASE_SLICE`), which `pyproject.toml`
reads from dynamically. That module is the single source of truth for "what
version is this" at build/runtime; release notes may record the version they describe.

## 0.6.0rc2 — Public-root API alignment

Narrowed `img2drawing.__all__` to the normal framework route centered on `DrawingSession`,
its declarative intent/reference/render inputs, and the small observed-construction facade.
Low-level history/action types, schemas, inspection primitives, evidence helpers, and
advanced vNext records remain public through explicit owning namespaces instead of competing
at the package root.

Pre-rc2 direct root imports remain available through deprecated lazy compatibility shims,
so this cleanup improves discoverability without abruptly breaking existing callers. Normal
`dir(img2drawing)` now exposes only the canonical root surface. The B18 contract snapshot was
realigned in the same change and the package candidate was bumped to `0.6.0rc2`; session
methods, persisted schemas, renderer contract, intent axes, and R23 checkpoint support are
unchanged.

## 2026-09-03 — Instruction graph + repository truth reconciliation

Replaced the deployable skill's accumulated guidance surface with a stage-free instruction
graph rooted at `SKILL.md`. The new graph separates foundation, drawing mode, observation,
construction, descriptive geometry, figure/prop/environment leaves, residual review,
output, and the documented public runtime surface. The core drawing rule is now explicit:
**croquis economizes marks, not observed geometry**. Head/face/hair, legs/feet, and clothing
fold guidance rejects symbolic simplification and redundant line accumulation.

Removed `skills/img2drawing/examples/` because the repository does not yet contain examples
strong enough to serve as canonical teaching material. The package manifest and CI now
validate an example-free deployable skill. Runtime implementation and version remain
`0.6.0rc1`; this change does not claim a new visual-quality release.

Reconciled the root handoff/gates, vNext status/roadmap/validation plan, and package notes so
they no longer disagree about R21/R23/B18 state, the location of the vNext freeze, or whether
examples are part of the normal package route. D01 remains the first fresh visual validation
after the small post-freeze alignment pass.

## B18 — Dogfood-ready vNext contract freeze

Pinned the `0.6.0rc1` public exports, `DrawingSession` members, persisted schemas, intent
axes, canonical RenderProfile, ownership, and explicit R23 checkpoint boundary in one
machine-readable snapshot. Audited B09–B17 for incomplete and duplicate paths and added
schema-validated sealed worker input, post-run evaluator, and evidence templates for
D01–D06. No fresh dogfood or visual-quality certification occurred in B18.

## 0.6.0rc1 — vNext package and public API candidate

Aligned the stage-free source, wheel/sdist inventory, installed API, support/migration
contracts, and CI. The wheel ships runtime/data/license material; the sdist adds selected
current Agent guidance. The deployable package intentionally contains no `examples/` tree
until representative examples exist. R23 remains an explicit, frozen compatibility
boundary rather than the current package identity. This candidate proves integration
mechanics, not visual quality.

## R23 — Material-integrated visual quality

Translated the temporary material repositories into current-source contracts:
independent P4/P5 resolved-form visual closure, optional bounded P6 identity
finish with real-canvas pressure calibration, selective R23 evidence helpers,
and a packaged fresh-worker generalization run. The material-1 matte critic and
material-2 subject-specific PASS remain negative fixtures rather than geometry
or likeness authorities. Release evidence is digest-bound and checkout-portable;
mechanical verification stays separate from artistic inspection.

## Documentation restructuring (2026-08-22)
`SKILL.md` and eight `references/` files were rewritten to drop release-codename
framing (`## R09 P2 Hardening` → `## P2 Hardening`, etc.) and state rules
directly instead of as "RXX does X" narrative. Purely historical dogfood
anecdotes were moved here. While doing this, an internal inconsistency was
found and fixed: `SKILL.md`'s grammar-exemplar audit table still listed
`P2_primary_axes` as `FAIL`, even though the R04 entry below it (and
`exemplars/full_body_croquis/audit_manifest.json`) already recorded it as
corrected and passing. The table now reflects the manifest's actual status.

Two dead tool references were also found and removed: `SKILL.md` pointed to
`tools/validate_canonical_example.py` and `dev/dogfood/r08_fresh_p1_regression.py`,
neither of which exists in this tree.

## R22 — Large attached-object topology
A large prop or attached object must not survive P5 as a generic pair of
rails when the subject visibly contains major subpart topology.

Dogfood case: a rifle's verified global axis/extent was kept and only P5 was
reopened. The previous two-rail read was replaced by separate
suppressor/barrel, handguard, scope, receiver, grip and stock relationships,
while intentionally omitting screws, knobs and rail teeth.

## R21 — Subject-only default + fresh-worker defect closure
Made one subject image the normal operating mode
(`subject_reference > grammar_exemplar`, with `task_stage_targets` as an
optional extra). Closed defects found by the R20 fresh-worker dogfood:
runtime/review/session provenance unified into one version module, atomic
resumable persistence on `stage_start`/`draw`/`draw_many`/`prepare_stage_review`,
scalar finding-string normalization, and the fresh-worker audit tooling moved
inside the canonical skill folder.

## R20 — Fresh-worker E2E closure rule
Established that a clean filesystem/subprocess in the *same* Agent
conversation is not sufficient evidence of fresh-worker autonomy — the
semantic worker still remembers prior development context. Defined the
strict E2E test protocol (new worker/session gets only the packaged release
and the task, no prior dogfood reports/action IDs/coordinates/fixes, no
importing `dev/dogfood/*`) and introduced `tools/audit_fresh_worker.py` as a
mechanical evidence auditor for the returned run.

## R19 — P5 silhouette separation / contour ownership
Established contour-ownership handoff rules for P5 cleanup. Dogfood found a
left hair/sleeve defect that was *not* renderer semantic merging: two
distinct strokes from the R18 history had sampled paths only `0.51px` apart
with local tangents differing by just `3.33°`, so normal rendering read them
as one line. Fix: moved the long lower hair boundary inside the cardigan
silhouette, keeping the sleeve as the background-silhouette owner.

## R18 — P5 clean block-in / construction retirement
Added the P5 cleanup-preflight rule (reopen upstream rather than hide a
structural defect under a clean silhouette) and replayable construction
retirement (`soft_lift` instead of destructive raster erase). Dogfood found
exactly the preflight case: a central jeans negative space was too wide at
P3; P5 refused to hide it, reopened P3, rebuilt P4, and only then produced P5.

## R17 — P4 structural connections
Dogfood found three P4 failure modes that must trigger revision: full-width
elbow/knee lines reading as clothing stripes, faceted mitten/diamond
hand-or-foot polygons, and ankle/hand blocks detached from the upstream limb
mass.

## R16 — P1 craniofacial gesture / head envelope
Introduced segmented open cranial construction to stop P1 heads reading as a
polygon, badge, or closed egg. Dogfood deliberately reopened P1 from P4,
rejected two head passes, and closed a third only once the isolated head no
longer read as a closed badge — rebuilding P2/P3 from the corrected branch
rather than resurrecting the old ones.

## R15 — P3 occupied-volume fidelity
Added the rule to reopen P3 when fresh whole-view evidence shows the mass
abstraction is still too narrow or too anatomical for a clothed subject.
Dogfood sequence: P3 reopen → broad clothed torso/sleeves/legs → REVISE
counter-leg overshoot → local correction → ADVANCE.

## R14 — Stroke weight / line hierarchy calibration
Defined the P1→P3 visual hierarchy (average weight vs. expressive
modulation) and added `render.line_weight.calibrate_line_weight()` as a
deterministic A/B review utility.

## R13 — Fresh-worker E2E defect closure
R12's clean-extract dogfood proved autonomous P1→P3 closure but exposed six
practical defects, closed here: consistent version authority across
`SKILL.md`/package/packets, runnable benchmark packaging, reliable
`finish()` ordering, checkpoint/resume, local-review registration evidence,
and canvas-scale material guidance. Also added the fresh residual-mismatch
sweep requirement, after R12 showed a worker could clear its remembered
concern list while a real subject-vs-drawing mismatch remained.

## R12 — Clean-extract dogfood
Proved a worker can autonomously close P1→P3 end to end, but exposed the
operational friction and premature-closure risks that R13 then closed.

## R11 — Reopen recovery
Added `DrawingRun.reopen_stage()` for branch-safe recovery when a later
stage reveals an earlier stage was wrong, under the "earliest responsible
stage" rule.

## R10 — P3 hardening
Dogfooded P3 as a complete autonomous hardening slice. Visual QA kept passes
3–5 at `REVISE` after exposing egg/rail/connection failures that a cleared
concern list alone would have missed. Established the clothed-mass /
hidden-body-bias policy.

## R09 — P2 hardening
Dogfooded P2 as a complete autonomous hardening slice. Found that a
structurally complete first P2 pass can still be wrong in axis direction;
established the recommended head→pelvis→arms→legs review order.

## R08 — Fresh P1 regression
Required an independently re-authored P1 regression on a working canvas
different from the canonical example's, to prove the hardening behavior
generalizes rather than being memorized from the canonical coordinates.

## R07 — Canonical example
Established `examples/full_body_croquis/run.py` as the canonical executable
demonstration of the hardening loop (crown-origin P1 → review → REVISE →
correction → ADVANCE), deliberately stopping at `P2_primary_axes` rather than
claiming a full P1→P5 drawing.

## R06 — Worker pass memory
Added `pass_memory.json` / `carried_concerns` so a worker doesn't mentally
restart the current stage after every review pass.

## R05 — Agent-selected local review
Added `DrawingRun.prepare_local_review()` for Agent-chosen ROI review,
distinct from whole-view review.

## R04 — Corrected P2 grammar exemplar
Replaced the over-developed P2 exemplar image with a deterministic,
axes-only exemplar generated from `sources/p2_axes_v2.json`. Flipped the P2
grammar-exemplar audit from FAIL to PASS.

## R03 — Grammar exemplar audit
Audited the bundled P1–P5 grammar exemplars against their frozen
StageContracts. Initial results: P1 FAIL, P2 FAIL, P3 PASS, P4 FAIL, P5 FAIL
(P2 was corrected to PASS in R04; P1/P4/P5 remain FAIL).

## R02 — Frozen stage contract
Introduced the machine-readable `StageContract` (owns / must_preserve /
allowed / forbidden / detail_ceiling / next_stage_unlocks) written by
`prepare_stage_review()`.

## R01 — Reference authority
Established the three reference roles (`subject_reference`,
`task_stage_target`, `grammar_exemplar`) and their priority order.
