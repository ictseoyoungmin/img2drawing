# img2drawing architecture contract

Status: **CURRENT MAIN INVARIANTS**
Updated: 2026-09-11

This document describes durable architecture invariants for current `main`. It is not a release
freeze. The immutable released v1.0.2/A10 snapshot remains in
`dev/release/vnext/CONTRACT_FREEZE.json` and may intentionally differ from current main.

## 1. One canonical orchestration core

`DrawingSession` is the canonical orchestration authority for new work:

```text
observe / declare intent
→ author explicit marks
→ render + inspect
→ choose residual
→ correct responsible authored representation
→ inspect again
→ finish
→ replay/export
```

One authoritative action history feeds current-state reconstruction, rendering, inspection,
provenance, replay, and timelapse. Do not create a second session/history/renderer/inspection tree
for a mode, style, subject, worker, or validation case.

## 2. Stage-free product model

Pn stages, stage cursors, advance/close/reopen runtime state, and stage review objects are not part
of the canonical runtime. Ordered drawing guidance lives in the instruction graph and remains
reversible when evidence disproves an earlier premise.

Current installable source has no R23 orchestration/runtime/legacy namespace. Historical R23 source
and closure evidence live in Git history plus `dev/legacy/` and `dev/release/r23/`; they are not a
supported current orchestration path.

## 3. Agent visual authority

The Agent owns visual interpretation and artistic acceptance. Observation tools, crops, grids,
measurements, overlays, palette samples, renderers, and tests provide evidence; they do not decide
pose, identity, anatomy, topology, correspondence, or final artistic quality.

For observed work, the subject/reference is geometry authority. For imaginative work, declared
intent is authority. Hybrid work explicitly separates preserved reference constraints from authored
transformations.

## 4. Structural truth before polish

- construction marks are provisional reasoning aids, not geometry authority;
- macro pose/form/orientation/balance/overlap/contact outrank local polish;
- inherited construction must be revalidated before downstream description;
- hidden continuity may be inferred only as far as needed to keep visible anchors coherent;
- unsupported hidden appearance must not be rendered as observed;
- line economy reduces redundant marks, not observed structural specificity;
- broad tone may reinforce credible form but may not manufacture missing structure.

## 5. Correction provenance

Residuals and corrections are provenance records, not scores or lifecycle state.

A correction must mutate the actual drawing and then be evaluated from fresh evidence. For a
residual bound to an observation, repairing mutation actions must carry the residual's
`observation_id` when resolving that residual. A later unrelated observation must not silently
replace that provenance link.

Repeated failure of one local correction is a routing signal: re-check the parent premise instead
of accumulating more local strokes.

## 6. Completion

`finish()` records an Agent completion decision; it does not certify artistic quality.

Current main requires:

- a non-blank current drawing state;
- a final inspection bound to the current state;
- an explicit evidence-read record showing that the Agent actually inspected that final evidence;
- no open residual records;
- honest `accepted_limitations` only for non-blocking weaknesses.

`accepted_limitations` cannot bypass an open material residual.

## 7. Render / replay contract

Final PNG, canonical replay, and timelapse use one persisted `RenderProfile` family. Replay remains
end-to-end from action 0 through the latest action with a declared sampling policy.

Known current defect: inspection and final/replay can differ by a few luminance levels because
compatibility-stage metadata participates in hand-dynamics seeding on history reconstruction. The
fix must normalize render input coherently across inspection, canonical replay, and fast replay;
do not patch only one output path.

## 8. Instruction graph contract

`skills/img2drawing/SKILL.md` is the root router. It loads
`skills/img2drawing/references/INDEX.md` and then only the smallest relevant leaves.

Path convention:

- in `SKILL.md`, routed Markdown paths are skill-root-relative and start with `references/`;
- in `references/INDEX.md`, leaf paths are references-root-relative;
- `dev/tools/verify_instruction_graph.py` derives the leaf set from the actual
  `references/**/*.md` tree, rejects broken/bare routed paths, and rejects orphan leaves.

Gesture drawing has two explicit finish modes: pure gesture and constructive gesture. An
unqualified gesture request defaults to constructive gesture. A gesture construction pass inside a
larger requested drawing is not permission to end that larger task.

## 9. Compatibility and release boundary

The latest released stable package is v1.0.2. Current main contains unreleased
compatibility-breaking changes and still reports package version 1.0.2 until a new release version is
chosen. Do not publish a new artifact as v1.0.2 and do not rewrite the immutable v1.0.2 freeze.

Deprecated pre-0.6.0rc2 root aliases remain a separate compatibility surface. Their future removal
requires an explicit versioned compatibility decision.

## 10. Review triggers

Stop and re-check this contract if a change introduces any of the following:

```text
second session/history/renderer/inspection implementation
runtime drawing stages or automatic artistic PASS/FAIL
raster-only geometry mutation outside authoritative history
subject- or model-specific answer geometry in the skill
style/output logic that silently overrides reference geometry
legacy orchestration returning to the normal route
release documents that describe mutable main as an immutable past release
```
