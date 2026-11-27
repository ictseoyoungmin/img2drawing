# Mixed-media markmaking

Open only for explicit ink/manga, opaque ink masses, white ink or screentone requests.
The ordinary pencil default and mode-specific finish criteria are unchanged. Reference
authority and geometry still precede material; see
[reference authority](../foundation/reference-authority.md).
Choose the profile and exact calls through [mixed-media API](../api/mixed-media.md).

## Choose marks by meaning, not by effect count

| Material | Use when the observed or declared relation calls for |
|---|---|
| Light graphite | Provisional construction, volume axes, search or deliberate graphite texture |
| G-pen | A variable-weight contour, overlap/contact accent, or taper whose changing width carries form |
| Fineliner | Delicate internal detail or an intentionally uniform structural edge |
| Wet ink brush | A continuous broad opaque stroke with a deliberate path and contact width |
| Solid ink | An explicitly bounded dark plane, silhouette mass or shadow with intended reserves |
| Dot tone | A controlled intermediate value on a chosen form/lighting region |
| White ink | A deliberately opaque light/edge on a lower mark, not deletion or paper transparency |

G-pen pressure changes diameter, not center opacity. Use the thinnest mark that preserves
important feature geometry; increase contour weight only where overlap, contact, depth,
or the requested style justifies it. Round joins and tapered tips suit flowing organic marks.
Miter/bevel joins and butt/square caps can express corners and mechanical edges; do not
turn every sampled curve into a sharp joint. Broad wet brush is opaque, not textured graphite.

## A flexible authoring loop

Light construction can precede ink, but no stage is mandatory. Establish the silhouette,
form turns, important overlap and negative spaces first. Author a small meaningful group,
then inspect it in relation to the whole. Separate the contour decision from the dark mass
decision: a closed outline is not automatically a shadow or a fill.

Ink masses follow observed/declaratively justified boundaries, plane changes, contact
and light families. Keep intentional light reserves as explicit holes where lower media
should show through. White ink instead covers lower marks, even on transparent or colored
paper. Do not conceal faulty geometry with white paint. Retire an incorrect element by ID
or replace its boundary; the previous state remains in history.

Choose a common page phase for adjacent tones that should read continuously. Choose pitch
relative to final resolution and viewing size, not to a copied reference's dot grid.
Coverage is an ideal area fraction, not opacity. Dense dots merge and leave smaller
uncovered spaces; use solid ink at true black and no tone at zero. Avoid tiny poorly
sampled dots, unnecessarily many tone regions, abrupt pattern clashes, and accidental
moiré. A linear gradient expresses an explicitly chosen gradual value change, not an
automatic lighting field. Inspect at final scale and in useful crops. For ambiguous
planes, reopen the geometry/value decision before adjusting pitch or coverage.

Once stronger descriptive ink carries a construction mark's meaning, choose KEEP,
SOFTEN or RETIRE through [retirement](../review/stroke-retirement.md). Graphite lift affects
graphite only; it cannot erase an ink correction. Remove the actual ink owner instead
of stacking new opaque marks to hide it. A reused semantic group still needs fresh review
after a member changes.

A coverage measurement, successful API call, valid contour, or correct replay is
mechanical evidence, not an artistic verdict. Use [visual gates](../review/visual-quality-gates.md)
and the existing residual/whole-drawing loop. Do not finish a generic face, pose,
overlap or costume just because the line art and tone look clean.
