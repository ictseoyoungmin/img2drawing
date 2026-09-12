# Stroke role vocabulary

A stroke role describes **why a mark exists in the drawing**. It is semantic, not merely a brush
setting. Choose the role from the relationship the mark explains, then choose a tool preset and
authored dynamics that fit that role.

Do not use one tool for every mark simply because it renders successfully.

## Initial vocabulary

### `construction`

Temporary structural reasoning: axes, cross-lines, mass boundaries, joint-volume cues, hidden
continuity, or other provisional relations. Usually light and easy to retire. Construction is not
visible-geometry authority.

### `gesture`

Flow, rhythm, load path, or major directional energy. Gesture often benefits from a pressure swell
and a clean release, but its geometry still comes from observation or declared intent.

### `form`

Ordinary descriptive form line. Use for visible boundaries or internal form turns that need stable,
readable pencil behavior without special emphasis.

### `contour`

A visible ownership boundary, silhouette, contact handoff, or important overlap edge. Contour is a
semantic relation, not permission to make every exterior edge equally dark.

### `accent`

A deliberately stronger local mark used for focal hierarchy, deep overlap, eye corner, contact,
crease origin, or another small high-value relation. Accents should be sparse enough to remain
meaningful.

### `hair`

A mark belonging to hair/fur/whisker-like flow where directional grouping and terminal behavior
matter. Do not turn the role into many parallel strands when the observed structure is a larger
mass.

### `hatch`

A repeated line used to build value or form direction. Hatching is value construction, not a
substitute for missing geometry.

### `broad_mass`

A broad graphite contact used to establish a larger value mass, textured shadow, or materially
broad mark. Use only when the drawing intent actually needs a broad contact.

### `environment`

Contextual linework whose visual priority is normally lower than the main subject unless the
reference or declared intent makes it structurally important.

## Role selection

Ask what relationship the mark must communicate:

```text
provisional reasoning?            -> construction
whole-flow or directional energy? -> gesture
ordinary visible form?            -> form
ownership / silhouette / overlap? -> contour
small deliberate emphasis?        -> accent
hair-like directional terminal?   -> hair
value built from repeated lines?   -> hatch
large graphite contact/value mass? -> broad_mass
contextual environment relation?  -> environment
```

This is a vocabulary, not a lifecycle. Different roles may coexist in one local region. A face can
contain a form contour, a dark accent at the eye corner, a construction cross-line that will later
be retired, and hair-role flicks at the boundary.

## Role does not replace geometry

Changing `semantic_role` does not fix a wrong path. If the contour is misplaced, return to the
visual leaf that owns the geometry. If the path is correct but its pressure, taper, opacity,
terminal, or graphite behavior is wrong, keep the geometry and route to markmaking.
