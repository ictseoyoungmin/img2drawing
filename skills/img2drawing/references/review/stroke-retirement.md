# Stroke retirement

Retire a mark when a newer representation carries its information more clearly.

Retirement is an explicit visual audit, not a suggestion to apply only when the drawing already
looks dirty.

Before a drawing is treated as clean/final, classify every surviving provisional/search mark:

- **KEEP** — it contributes unique information intentionally visible in the requested finish;
- **SOFTEN** — it still helps rhythm, form direction, weight, or a deliberate hidden handoff but
  must remain perceptually subordinate;
- **RETIRE** — stronger description already carries its information, the mark contradicts corrected
  geometry, duplicates another line, creates false ownership/topology, or adds noise without a new
  relationship.

Default to **RETIRE after replacement**.

Low opacity does not automatically make a mark harmless. A large population of faint cranial
spheres, axes, rail guides, hair search arcs, perspective rays, or fold scratches can flatten line
hierarchy and make a resolved drawing look unfinished.

Use a softened remnant only when it contributes something the final descriptive marks do not.
Construction is not preserved because it was useful earlier.

Do not raster-paint over errors or mutate history outside the supported edit surface. A
correction should remain replayable: replace, soften, or delete the authored element, then
render and inspect the current state again.

After the audit, inspect the whole at final output scale. Retirement succeeded when clarity and
specificity improve without removing a relationship the drawing still needs.

Line economy improves during retirement. A clean drawing often becomes more specific while
containing fewer visible marks.

Use `visual-quality-gates.md` for the hierarchy, ownership, and finish checks that surround this
audit.
