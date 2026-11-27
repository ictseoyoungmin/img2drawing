# v1.5.0 — optional layered editing and exchange

Design selected: 2026-11-28 (Asia/Seoul). Baseline: published v1.4.0,
main `a3921fbf48e9725da99caf48481b2dde5202a7f4`.

[Work OS](https://app.notion.com/p/425c6a3b5bf181c5a45dd7d037572ebb) ·
[development branch](https://github.com/ictseoyoungmin/img2drawing/tree/dev/v1.5.0-layered-editing)

`STATUS.md` owns current progress. This document owns the bounded design and acceptance
criteria; it does not establish publication or artistic quality.

## Product intent

The same runtime serves casual line art, deliberate hand-drawn studies, mixed-media
illustration, and repeatable professional editing. Ordinary drawing remains immediately
available. Enabling layers, running specialist inspections, and exporting exchange files
are choices made for the task, not prerequisites imposed on every drawing.

One `DrawingSession`, one authoritative action history, and the existing authored marks
remain the foundation. Document organization must not require a second drawing runtime,
a mandatory visual editor, a fixed style, or a separate professional session type.

## Scope and sequence

| Slice | Priority | Deliverable | Acceptance |
| --- | --- | --- | --- |
| S01 | P0 | Contract, compatibility boundary, regression criteria | Decisions below match implementation and public guidance. |
| S02 | P0 | Native layer tree, ordered membership, persistence | Central inherited locks; atomic failure; undo/redo/resume; old serialization unchanged. |
| S03 | P0 | Isolated compositor and explicit legacy conversion | Immediate conversion is pixel-exact; group opacity, visibility, eraser scope, budgets and canonical replay verified. |
| S04 | P0 | Mixed graphite/ink/area/tone group transforms | Explicit width/pattern policy; guarded preview/apply; full-batch rollback; no changes to existing helper defaults. |
| S05 | P1 | Transparent PNG and OpenRaster exchange | Correct hierarchy/order/visibility/opacity; canonical merge; measured reflattening difference; native checkpoint retained. |
| S06 | P0 | Integration and practical workflow verification | Automated regression plus independent ordinary/professional workflow evidence, with untested limits stated. |
| S07 | P1 | Public guidance, package and release preparation | Installed package and CI verified; separate actual release observation before publication closure. |

Regression tests start in S02–S04. S06 integrates the evidence rather than postponing
appearance checks to the end. First implementation supports Normal composition only.
Additional blend modes are a P1 follow-up requiring an explicit compositing contract and
export parity tests. PSD and a visual layer editor are P2; neither blocks the native layer
foundation or ORA exchange. Masks, pass-through groups, cross-layer erasing, raster import,
and automatic reconstruction of stroke data from an edited ORA are outside this contract.

## Native document model

`StrokeIR.layer_document` is optional and absent from legacy serialized output. A versioned
document contains immutable paint/group nodes, an ordered list of members per paint node,
and an active paint-layer ID. Parent links and sibling indices define bottom-to-top order;
groups are isolated. Every live mark belongs to exactly one paint node. Cycles, orphan
parents, duplicate ownership, unsupported modes, malformed values, and resource excess
are rejected before committing.

Node properties are ID, name, kind, parent, sibling order, visibility, lock, opacity, and
blend mode. Paint membership is independent of `Stroke.layer` and `InkElement.layer`.
Those original integers remain authored material data: graphite hand/grain seeds include
them. Rearranging document layers must never rewrite them, mark IDs, or geometry.

Typed `layer.*` actions live in the existing `CanvasHistory`. Checkpoints persist those
events, not a second competing document snapshot. Same-ID replacement retains its slot;
replacement IDs and explicit split fragments inherit the source layer. Added marks route
to the active layer or an explicit `layer_id` recorded on the add event. Erasers share the
same membership model. Empty nodes persist until explicitly removed.

Inherited lock protects mark mutations, assignment, and structural edits. Name, visibility,
and opacity remain deliberate display/property controls. A child cannot unlock itself
through a locked ancestor. Deletion initially accepts only empty, inactive nodes; content
removal or reassignment is explicit and reversible. The UI/API must not silently unlock,
flatten, move, or discard content to make an operation succeed.

All layer state participates in state hashing. Prepared edits therefore become stale after
document edits. Semantic-group reviews also bind relevant member order and visible ancestor
properties. Existing unlayered hashes and fingerprints are unchanged.

## Conversion and compositing

No migration occurs during resume. `enable_layers()` explicitly wraps all current marks
in one paint node in their existing stable native-layer order, including erasers and
interleaved materials. Automatically splitting legacy numeric layers or media buckets could
change eraser scope or drawing order, so the initial conversion does not do that.

The document contract includes an identity compatibility route: one effective nonempty
paint node holding every mark in its legacy order, with visible unit-opacity ancestors,
renders through the unchanged native renderer. Names, locks and empty organization nodes
do not defeat this route. Immediate conversion preserves exact pixels.

Nontrivial document composition renders each paint layer at working resolution using the
existing material kernels and explicit document order. Groups composite children bottom to
top into transparent surfaces. Opacity is applied once to the completed node alpha, with
specified rounding, then the root is placed over the profile background. Downsample once.
An eraser lifts earlier graphite only in its own paint layer; ink, including white paint,
remains paint. Groups do not broaden eraser scope.

The mixed legacy renderer composites directly onto paper. Transparent intermediate
composition can change integer rounding, even before resampling. Therefore splitting an
existing drawing is an explicit compositing edit and is not promised to preserve bytes.
Old render-profile IDs, contract digests and goldens stay immutable. The document contract
owns the new semantics; it does not rename or silently replace the graphite renderer.

Document render limits bound dimensions, node count/depth, work across all leaves, and
simultaneously live surfaces. Work budgets are shared, not reset for each layer. Existing
timelapse fast paths reject document histories until separately proved; canonical replay
uses the same layer-aware snapshots and renderer as final/inspection/preview.

## Unified explicit transforms

The shared authoring API prepares a detached typed batch bound to cursor, state hash,
profile digest, and action digest. Preview and apply recheck the guards under the session
lock. Apply commits once. A bad final member, stale proposal, changed nested metadata,
locked member, invalid geometry, or failed checkpoint write rolls back the entire batch.

| Choice | Meaning |
| --- | --- |
| `width_policy="preserve"` | Preserve graphite width and ink min/max diameter; pressure and relative contact-width factors stay unchanged. |
| `width_policy="scale"` | Uniformly scale graphite and ink widths with the geometry. |
| `tone_policy="page"` | Move the tone boundary/holes; retain page-space pitch, phase, angle and gradient. |
| `tone_policy="object"` | Move boundaries, phase origin and gradient endpoints; scale pitch and rotate/reflect the lattice. |

Selections with graphite or ink paths require nonsingular similarity transforms. Area and
page-fixed tone selections can accept nonsingular affine transforms. Object-following
tones require similarities because the stored round-dot lattice cannot represent shear.
Existing helper defaults remain unchanged. Authored path erasers are not transformed as
ordinary strokes; the entire unsupported selection is rejected.

## Exchange contract

The PNG bundle and ORA contain raw transparent paint-layer images; layer opacity is recorded
once in metadata/XML, not baked and applied again. Hidden content is retained. Groups use
isolated stacks. Internal bottom-to-top order is reversed for ORA topmost-first XML. A
nontransparent profile background becomes an explicit bottom layer.

`mergedimage.png` is the exact canonical render. Independent layer images are downsampled
separately, and filtering does not commute with source-over composition. Reflattening them
can therefore differ from the canonical merged image. Export receipts report both hashes,
differing-pixel count and maximum channel difference; they never assert universal editor
pixel identity. Generated archive paths and an XML writer protect arbitrary visible names.

The original checkpoint is retained alongside exchange output by default. It remains the
authority for editable points, pressure, tools, procedural tones, corrections and replay.
The user can edit raster layers in another application; those raster edits are not silently
presented as changes to native strokes. A reference-bound checkpoint still requires the
original reference (identified by its digest) when resumed.

## Evidence required before release

- Existing default/normalized/mixed contracts, release fixtures and legacy checkpoints pass
  unchanged in the pinned test environment; dependency-specific limits remain explicit.
- Conversion fixtures cover graphite, mixed, white ink, tone, erasers, and opaque/transparent
  backgrounds. Real retained v1.4 sessions are replayed on copies, never overwritten.
- Mixed selections verify both policies, reflection, invalid last-member rollback, lock
  inheritance, stale/tampered proposal rejection, preview parity, resume and undo/redo.
- Document tests cover group opacity at overlaps, parent visibility, ordering without seed
  changes, split/replacement membership and leaf-local erasers.
- ORA tests inspect archive ordering, exact mimetype, escaped XML, hidden data, group opacity,
  canonical merged pixels and truthful recomposition measurements. External application
  opening remains a separately recorded practical check.
- Installed worker workflows demonstrate simple drawing without layers and optional layered
  revision/export. Mechanical success does not establish general artistic improvement.

## Dated development evidence — 2026-11-28

This records the bounded implementation check, not a stable release or general artwork verdict.
Current open/closed state remains in `STATUS.md`.

- Full active local suite: **844 passed**, Python 3.12 / Pillow 12.3.0 / NumPy 2.2.6.
  Package boundary (wheel, sdist, skill ZIP and installed API), current documentation,
  instruction graph, path/JSON/Python checks passed. Hosted integration CI is a separate gate.
- Neutral conversion regression covers all seven existing material profiles with opaque and
  nonopaque backgrounds. Cross-material fixtures cover erasers, white ink, tone and groups.
- Real retained 1024×1536 SS2 sessions were rendered with the released 1.4.0 interpreter and
  candidate source under Pillow 13.0.0 / NumPy 2.3.5. Released, candidate unlayered and candidate
  layered RGBA bytes match for each drawing. The original source checkpoints remain unchanged.

| Retained drawing | Content | Identical RGBA SHA-256 |
| --- | --- | --- |
| Graphite | 859 actions; 720 current strokes | `85c0bc4ec9d06ed2d39950403207e3db9f3789f65580330220b99a6085f07aa5` |
| Mixed profile | 654 actions; 627 current ink elements, no graphite | `3c3132d84eab9d29de3026c7d18c9c7ef4c68058a1a2251355ee25c2a9c86ac8` |

An independent worker used an installed development wheel and only public guidance/API:

- Ordinary route: three explicit pencil strokes, layers disabled, viewed inspection, finish
  decision, save and exact resume.
- Optional route: graphite path, ink path, solid ink area and screentone, one group and four
  paint layers; naming, visibility, opacity, inherited lock and ordering; shared scale/translation
  with width scaling and object-following tone; genuinely viewed preview before atomic apply.
- Both ORA sidecar and PNG-bundle native checkpoints retained all four elements, layer tree,
  viewed inspection evidence and finish decision, and resumed to exact final pixels while the
  original output folder was absent.
- Canonical merged PNGs matched final PNG bytes. The independently downsampled layer images
  differed at 267 of 16,384 pixels, maximum channel difference 2, exactly as the manifest reported.
  This is one measured example, not an error bound for other drawings or applications.
- The worker exposed and prompted correction of matrix notation and root exporter routing.
  Native resume guidance now explains that `output_dir` selects an existing evidence root;
  it does not relocate evidence into an empty folder.

Independent review also produced regressions for reused retired IDs in imported layered
graphite histories, observation/intent provenance after undo, redo-tail layer replay, portable
inspection evidence, and empty-group surface accounting. Small synthetic worker use does not
certify professional editor completeness. External Krita opening/reflattening remains NOT_RUN.


## Stable-candidate preparation — 2026-11-28

[PR #124](https://github.com/ictseoyoungmin/img2drawing/pull/124) was integrated at `b1ca145`;
[development integration CI](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46051134484)
passed the initial implementation and package gates. A separate stable freeze and publish
manifest are now prepared for 1.5.0; the development records remain unchanged.

Current-reference manga authoring, layered revision, portable native resumption and full replay
are PENDING assessment. Actual Krita open/edit/save/reopen and flatten comparison are PENDING.
No new artwork acceptance, external interoperability PASS, final candidate CI or publication is
claimed by this preparation. Record observed outcomes before selecting the promotion commit.
The actual GitHub Release/tag/assets remain the final publication authority.

## Practical workflow and release selection — 2026-11-28

S06 is complete with the limitations below; S07 final CI and actual publication remain
separate gates recorded in `STATUS.md`.

- [PR #125](https://github.com/ictseoyoungmin/img2drawing/pull/125) merged at `3bdce30` after
  [exact-head CI](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46058543138) passed
  851 active, 49 runtime and 45 Pillow 13 replay checks and package/repository gates. These runs
  overlap. The original 27-node page exposed full-canvas composition cost; occupied-alpha
  composition keeps its pixels exact while reducing work from 348,340,985 to 230,710,832 under
  the unchanged 268,435,456 limit. No native layer consolidation is required for the final page.
- The new installed public-API page finishes at cursor 1178 with 921 ink/area/tone elements,
  27 nodes, seven retained inspections and three actual material corrections. Preview/apply,
  fresh evidence and finish cover value hierarchy, hair/eye overlap and boot-ground contact.
  Independent visual review accepts that bounded correction scope; simplified hair, hands,
  cloth, ruins and coarse dot tone remain. Review feedback was supplied during the workflow.
- Copied PNG and ORA native handoffs resume with original-path reads blocked and reproduce
  exact final RGBA while preserving finish and inspection evidence; 116 delivery files remain
  unchanged. Full-span 0→1178 canonical replay samples every 16 actions: all 75 staged PNG and
  decoded GIF frames match, and eight independent cursor renders match pixel/state hashes.
- Actual Krita 5.2.9 document-engine checks verify 23 raw paint rasters, non-opacity hierarchy,
  real name/visibility/opacity/position edits and exact baseline/edited KRA reopen. GUI use was
  not tested. Fractional input opacity is converted to 8 bits; Krita ORA re-save further changes
  three final-page values by one level. Native→Krita has 351,807 differing pixels, maximum 79,
  mean RGBA8 error 0.98724270. Exported-layer recomposition→Krita has maximum 2 and mean
  0.06452322. Repeated tone differences cause mild broad brightening, not only boundary changes.
- The [release notes](../../../docs/releases/v1.5.0.md) retain full comparison values and
  scope. Exact native appearance belongs to the canonical PNG and checkpoint; KRA preserves
  the tested imported editing state. This is bounded practical evidence, not a promise of
  pixel-exact external exchange or universal professional artwork/print fidelity.

Stable source/plugin versions, additive freeze and publish manifest select 1.5.0. Prior
development and release records remain unchanged. Successful final/main CI and observation
of the tag plus four release assets are required to close S07.
