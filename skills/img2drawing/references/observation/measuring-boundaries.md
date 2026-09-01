# Measuring boundaries

Most drawing errors that survive a correction loop are not misread coordinates. They
are edges found with a method that could not see the thing being measured, or lines
drawn where the subject has none. Both pass every check that only compares the drawing
to itself.

## A line separates two named things

Before authoring any contour, name what is on each side of it. If both sides cannot be
named, it is not a contour and it should not be drawn yet.

This is checkable and it catches three separate mistakes:

- **Duplication.** If the two names are the same on both sides of an existing line, the
  new stroke is restating a contour rather than articulating anything. A hand outline
  drawn along a jacket silhouette that already traced the same bulge adds no
  information and doubles the edge.
- **Displacement.** An inner limb edge that separates "sleeve" from "sleeve" is running
  in the wrong place. The inner edge of an arm separates *arm* from *torso*, so it
  belongs at the armhole, not a line-width inside the silhouette.
- **Mislabelling.** The same arc can be a hand's underside or a sleeve's cuff. Which one
  it is decides where every other mark in that region goes.

Record the answer in `part`: `far_arm_inner_edge` names a relation, `hand_shape` does not.

## A luminance threshold only answers a luminance question

Profiling a subject by "darker than N" segments the image into dark and not-dark. It
cannot find a boundary whose two sides sit on the same side of N.

On a subject in dark clothing this fails in a specific, repeatable way: bare skin and a
mid-grey background are close in lightness and far from the garment, so a darkness
profile reports skin as absent body and cuts a notch into the silhouette exactly where a
hand or a thigh emerges. A drawing built on that profile puts the cuff — and therefore
the wrist, and therefore the whole forearm chain — tens of pixels away from the joint.

Sample the materials first and ask which one a region actually is:

```python
from img2drawing import SubjectPalette

palette = SubjectPalette("subject.png")
palette.sample("background", (700, 660, 740, 700))
palette.sample("garment",    (560, 640, 580, 660))
palette.sample("skin",       (340, 830, 370, 860))
palette.sample("hair",       (430, 110, 470, 150))

palette.classify(595, 688)              # -> ('skin', 10.9)   not background, not absent body
palette.classify_row(686, (520, 650))   # runs of each material along one scanline
palette.boundary_kind((575, 686), (595, 686))
```

`ambiguous_pairs()` reports the materials this particular subject cannot separate by
colour. Read it before trusting any profile: if `skin` and `background` come back close,
every silhouette edge next to bare skin needs a second look, and
`boundary_kind()["visible_to_luminance_threshold"]` says whether a darkness scan could
have seen that edge at all.

The palette classifies nothing on its own. The Agent supplies the reference patches from
regions it has already identified by eye; the palette only answers which of those a pixel
is nearest.

## Do not draw a termination you did not observe

Hands, feet, facial features and hair tips are where invention is cheapest and most
damaging: an invented ending fixes a wrong silhouette and contradicts the overlap order
around it.

Before drawing any terminal, say explicitly whether it is **visible**, **partly
visible**, or **occluded**, and record occluded ones in the observation's
`occluded_limb_evidence`. Then:

- visible: draw what is there, at the size it is there;
- partly visible: draw only the visible part and let the contour end;
- occluded: draw no ending at all. The limb's own contour runs into whatever hides it.

Two arms do not imply two visible hands. Knuckles are not visible on a gloved hand in a
pocket. A jaw does not continue to the ear when hair covers it. In each of those cases
the correct mark count is zero.

## Verify a correction the same way you verified the premise

A correction is a new premise and inherits nothing. After replacing a contour, re-ask
what it separates and re-measure with a method that can see both sides — otherwise a
second wrong reading simply overwrites the first, which is more expensive than the
original error because it also consumes the correction budget.
