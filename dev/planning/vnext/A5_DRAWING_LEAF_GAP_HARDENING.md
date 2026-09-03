# A5 — high-value drawing-leaf gap hardening

Status: **CLOSED**

## Goal

Close only the remaining instruction gaps that are both high-impact and too cross-cutting to
be expressed cleanly by the existing leaves before D01. A5 is guidance hardening, not a new
runtime feature, drawing stage, or anatomy curriculum.

## Audit result

Two candidates earn dedicated ownership:

1. **hands / grip** → `references/figure/hands-and-grip.md`;
2. **foreshortening / depth compression** → `references/construction/foreshortening-and-depth.md`.

No additional leaf was justified in this pass.

## Why hands / grip needs a leaf

The previous `figure/torso-arms-hands.md` correctly stated that a hand is the terminal of an
arm chain, but local hand fidelity was compressed into a few sentences. That left no focused
contract for palm envelope, thumb opposition, visible finger grouping, fingertip/gap
termination, pocket/prop contact, or the recurring failure mode where a terminal becomes a
mitten-like shape and extra finger ticks are added afterward.

Historical croquis dogfood records also contain this exact class of repair: the hand/forearm
terminal was refined from a sparse/incomplete form into a faceted mitten-like solution plus
local inner marks. That record is evidence that the failure recurs; it is **not** promoted as
an example or current workflow authority.

The new leaf therefore owns only local hand/grip geometry after the shoulder → elbow → wrist
chain is credible. Parent reach remains in `construction/balance-and-limbs.md`; prop topology
and anchors remain in `props/attached-objects.md`; contact ownership remains in
`description/contour-and-overlap.md`.

## Why foreshortening / depth needs a leaf

Current guides referenced foreshortening but did not own the decision. The visual problem spans
projected joint spacing, near/far anchors, overlap order, hidden length, apparent width, and
terminal orientation. Treating it as an ordinary limb-contour problem encourages workers to
restore expected anatomical length or taper even when the reference is strongly compressed in
image-space.

The new construction leaf owns the **projected relation**, not anatomy. It explicitly forbids
“unfolding” a foreshortened limb to expected length, drawing hidden length through an occluder,
or applying a mechanical “near means wider” formula. Local contour remains in description;
hand/foot terminals remain in their figure leaves once the parent projection is credible.

## Routing changes

A4's cause-based router is extended rather than replaced:

```text
hand/grip residual
├─ arm chain/reach wrong             → construction/balance-and-limbs
├─ projected depth wrong             → construction/foreshortening-and-depth
├─ local hand/grip geometry wrong    → figure/hands-and-grip
├─ prop anchor/topology wrong        → props/attached-objects
└─ contact ownership wrong           → description/contour-and-overlap

foreshortening/depth residual
├─ anchors/projected spacing wrong   → construction/foreshortening-and-depth
├─ evidence still uncertain          → observation/visual-observation
├─ local overlap wrong               → description/contour-and-overlap
├─ credible-chain hand/foot terminal → corresponding figure leaf
└─ prop relation contradicts depth   → props/attached-objects
```

This preserves progressive disclosure: workers do not need either leaf unless the current
residual routes there.

## Non-goals

A5 does not:

- add runtime types, schemas, inspection verdicts, or automatic anatomy reasoning;
- introduce a hand-construction stage or a foreshortening stage;
- prescribe canonical finger counts/poses, proportional templates, or hidden anatomy;
- add deployable examples;
- claim D01–D06 visual-quality success.

## Mechanical closure

`dev/tests/test_skill_surface_boundary.py` now checks that:

- both leaves exist in the intended graph owners;
- `SKILL.md`, `INDEX.md`, and residual routing expose the leaves without flattening the graph;
- hands reject mitten/finger-count completion and hidden-digit invention;
- foreshortening preserves projected spacing, near/far anchors, and forbids anatomical
  unfolding.

The runtime/package contract remains `0.6.0rc2` and `DrawingSession/0.6.0-vnext`; A5 changes
only deployable drawing guidance and project-control documentation.

## Next

The pre-D01 alignment pass A1–A5 is complete. D01 difficult observed croquis is the next
validation bottleneck and must begin with fresh sealed input under `VALIDATION_RELEASE.md`.
D01 may reopen an A/B premise if the fresh drawing exposes a real defect.
