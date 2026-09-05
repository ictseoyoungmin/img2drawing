# Line economy

**Croquis economizes marks, not observed geometry.**

Line economy removes redundant decisions. It does not remove the subject's real bends,
width changes, overlaps, contact points, asymmetry, folds, component relations, or
identity-bearing structure.

## What to economize

Economize:
- repeated search marks around one boundary;
- parallel lines that communicate the same edge;
- decorative texture that does not explain form;
- construction cues already replaced by a stronger descriptive line;
- low-impact accents while a larger relationship is still wrong.

Do not economize away:
- a silhouette turn that changes pose, orientation, topology, or identity;
- a joint, anchor, or width transition that distinguishes the connected form;
- a mass break or component envelope that changes the subject silhouette;
- a fold, seam, or boundary whose location explains tension, force, or contact;
- a support/contact relationship that makes the subject sit, stand, hang, grip, or connect credibly;
- a critical overlap or negative space.

## Sparse does not mean generic

A complex curve can be described with one deliberate stroke. A face can be recognized from
a few accurately placed feature and contour lines. A shoe can use only several lines while
still preserving its actual orientation and construction. An articulated or mechanical form can
use few marks while still preserving its real axes, widths, joints, and overlaps.

Prefer one confident line that carries multiple correct relationships over many simple
lines that average the form into a symbol.

## Author related geometry as a semantic group

Do not organize a pass by an arbitrary number of strokes. Group together marks that answer the
same structural question: one contour interval, one connected component relation, one hair mass,
one grip/contact, one clothing tension family, one prop subassembly, or another coherent visible
problem.

Within that group, keep enough neighboring context to preserve continuity and ownership. Then
render and inspect the group in the whole drawing before moving on. This reduces two opposite
failures: isolated micro-edits that never repair the parent relation, and giant passes whose
residual cause becomes impossible to locate.

A semantic group is an authoring convenience, not a runtime stage. Its size follows the observed
relationship and can be revised whenever fresh evidence shows that the chosen scope was wrong.

## Detail is not classified by size

A small feature is not automatically secondary. If it determines orientation, contact, scale,
identity, topology, or another high-impact relation, preserving it may be structurally necessary.
Conversely, a visually large texture or value area can remain secondary if it does not decide the
structural read.

Defer secondary detail, not structural specificity. See `structural-specificity.md`.

## Failure signal

If adding lines makes a region busier but not more specific, stop. Re-observe the boundary or
parent relation, retire redundant marks, and replace the pile with the smallest line set that
states the correct geometry.

If a semantic group is already geometrically correct but still reads broken because of endpoint
weight, taper, opacity, or another material setting, do not redraw its points merely to change the
rendering behavior. Retune the stroke material and preserve the authored geometry.