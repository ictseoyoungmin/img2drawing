# img2drawing architecture contract

Status: **CURRENT MAIN INVARIANTS**
Updated: 2026-11-28

This document describes durable architecture invariants for current `main`. It is not a release
freeze. Immutable released snapshots remain version-specific:

- v1.0.2 / A10: `dev/release/vnext/CONTRACT_FREEZE.json`;
- v1.0.3 / A14: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- v1.1.0 / R1: `dev/release/vnext/CONTRACT_FREEZE_V1_1_0.json`;
- v1.1.1 / M01: `dev/release/vnext/CONTRACT_FREEZE_V1_1_1.json`;
- v1.2.0 / M02: `dev/release/vnext/CONTRACT_FREEZE_V1_2_0.json`;
- v1.2.1 / M03: `dev/release/vnext/CONTRACT_FREEZE_V1_2_1.json`;
- v1.3.0 / constructive drawing: `dev/release/vnext/CONTRACT_FREEZE_V1_3_0.json`;
- v1.3.1 / maintenance: `dev/release/vnext/CONTRACT_FREEZE_V1_3_1.json`;
- v1.4.0 / mixed media: `dev/release/vnext/CONTRACT_FREEZE_V1_4_0.json`.
- v1.5.0 / optional layers and exchange: `dev/release/vnext/CONTRACT_FREEZE_V1_5_0.json`.

Those freezes may intentionally differ from later `main`; neither is rewritten to describe future work.

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

Final PNG, inspection, canonical replay, and eligible fast timelapse derive from one persisted
`RenderProfile` and its explicitly registered renderer identity/digest. The same pencil engine may
host multiple immutable material contracts; every session selects exactly one. Replay remains
end-to-end from action 0 through the latest action with a declared sampling policy.

The inspection/final seed-parity defect identified during the v1.0.3 RC cycle is closed: v10
normalizes the private compatibility `Stroke.stage` field out of render seed identity, and the
active suite verifies inspect/final parity plus canonical-final ↔ fast-final exactness where that
contract applies. Historical v9 seed semantics remain frozen for explicit v9 replay.

Default sessions select `img2drawing-pencil / 11` and persist the same renderer contract digest as v1.1.0. The v1.0.3 v11 profile is accepted as pixel-equivalent; v9/1, v10/1, foreign digests, and retired region-fill histories fail closed in current source. Use `img2drawing==1.0.3` for their exact historical replay.

v1.3.0 adds `RenderProfile.opacity_normalized(width, height)` for new
sessions. `11-opacity-normalized-v1`, `11-opacity-normalized-v2`, and `11-opacity-normalized-v3` each have a required contract digest and cache identity;
`RenderProfile.canonical()` and historical v11 behavior are unchanged. The same contract follows
inspection, preview, PNG, Fast/Canonical and GIF output. Unknown identities, cross-digest profiles
and a missing normalized digest fail closed. Never silently migrate existing sessions to the new
material model or infer artistic quality from a material regression.

v1.4.0 adds explicit opt-in `RenderProfile.mixed_media(width, height)` contracts.
The default mixed selection is `mixed-media-v3`; `screentones=False` selects v2,
and `styled_paths=False` selects v1. Their distinct digests bind explicit ink paths,
closed contours, white paint and supported analytic screentone to the same ordered
history. The Agent owns path and boundary geometry, holes, shadow selection and
pattern settings; no reference-derived masks, automatic fills or geometry extraction.
Graphite lifts remain graphite-selective, while white ink is covering paint.

Eligible opaque ink-only histories share exact canonical kernels with incremental
Fast replay and bounded packed patch caching. Mixed-media histories containing
graphite/eraser actions, transparent backgrounds and unsupported combinations use
canonical replay. Pure legacy graphite Fast remains supported.
Profile identity does not certify pixel equality across untested NumPy/Pillow versions;
release evidence names its measured environment without rewriting historical fixtures.

Optional v1.5.0 layers retain the same session and action history. Document membership and
stacking do not rewrite native material-layer integers or geometry. Explicit conversion to one
neutral layer preserves the legacy image; later organization uses the separately versioned
Normal isolated-group contract. Inherited locks, opacity, ordered membership, mixed-edit guards
and evidence-preserving undo/redo apply centrally. Layered histories use canonical replay.

PNG/OpenRaster exchange contains raw transparent raster layers, the exact canonical merged
image and measured runtime reflattening differences. Native checkpoints and retained inspection
evidence remain the authority for continued stroke editing. External raster changes are not
silently imported as native marks. PSD, masks, extra blend modes and a visual editor remain
outside the initial layer contract.

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

After successful main CI and observed manifest-driven publication, v1.5.0 is the latest published stable. Its tag targets the tested main commit and all four release assets are uploaded. The manifest and additive freeze define the release contract; the actual GitHub Release, tag, target commit and assets establish publication. Earlier release and development records remain immutable. New sessions default to legacy v11; optional mixed-media and layer contracts extend the existing history. Release notes and `STATUS.md` record bounded mechanical and practical evidence; those observations do not certify general artistic improvement.

The deprecated pre-0.6.0rc2 root aliases, `img2drawing.vnext` and `img2drawing.provenance` import paths, and v9/v10 runtime renderer implementations are removed in v1.1.0. Exact historical replay of those renderer identities belongs to `img2drawing==1.0.3`.

Current source-module filenames are semantic implementation names rather than renderer-generation
tags. Serialized renderer identities may retain v9/v10/v11 generation labels because they are
persistence/replay protocol identifiers, not Python module names.

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
generation-tagged Python module basenames returning to current src
```
