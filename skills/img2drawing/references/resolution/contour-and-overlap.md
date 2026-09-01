# Contour, overlap and selective cleanup

Clean does not mean drawing over everything more darkly. It means selecting which
lines communicate the current form best.

## Ownership

Make contour ownership explicit where silhouettes, face openings, hair masses,
garments, and props overlap. Break a line or preserve an occlusion where one mass
passes into another; do not weld independent contours into a single line.

## Every new line must identify what it separates

Before drawing a contour, name what lies on each side. If both names are the same,
the line adds no new information; it merely repeats an existing line. In
particular, a line running parallel to an existing contour within one line width
is duplication, not articulation.

An arm's inner line separates the *arm* from the *torso*, so it belongs at the
armhole rather than beside the silhouette. A line that simply tracks a short
distance inside the silhouette fails to separate the arm and becomes a shadow
line instead.

For detailed judgment, read
[`observation/measuring-boundaries.md`](../observation/measuring-boundaries.md).

## Structure before surface

Resolve hair first as a large mass over the cranium, clothing as a hang over the
shoulder–sleeve–joint chain, footwear as volume growing from the ankle, and props
through axis, width change, and body contact. Select folds, individual hairs, and
surface texture only after those structures read.

## Retire without raster editing

When a new representation inherits the information of an earlier line, use
`soft_lift` to retain a useful cue or `delete_stroke` to remove it from the current
branch. Both preserve history and provenance. Do not raster-edit the file or erase
outside history; confirm the actual improvement with a fresh render and inspection.
For the shared API, see the stage-free section of
[`review/stroke-retirement.md`](../review/stroke-retirement.md).
