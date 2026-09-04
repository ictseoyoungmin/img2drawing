# A7 — structural specificity and construction inheritance hardening

Status: **CLOSED**

## Goal

Close a cross-subject guidance failure exposed by exploratory drawing work: wording such as
“detail later” can be interpreted as permission to simplify the first construction into generic
symbols, after which later passes refine around those symbols instead of re-observing the parent
structure.

A7 generalizes the correction across figures, mechanisms, props, objects, and other observed
subjects. It changes guidance only; runtime/API/schema contracts remain frozen.

## Durable invariants

1. **Defer secondary detail, not structural specificity.**
   Early passes may omit texture, decoration, repeated small features, and other low-impact local
   information, but they must already preserve the subject-specific relations that control
   placement, orientation, proportion, envelope, width/depth change, overlap, contact, negative
   space, anchors, and connected parts.
2. **Construction primitives are provisional, not geometry authority.**
   Earlier marks do not earn preservation merely because they were drawn first or because later
   marks depend on them.
3. **A descriptive pass revalidates its parent structure before inheriting it.**
   If the parent relation is wrong, replace the responsible geometry before adding contour,
   detail, value, or accents.

## Detail boundary

A7 deliberately avoids classifying detail by physical size. A small feature may be structurally
important when it decides orientation, contact, scale, identity, topology, or another high-impact
relation. A visually large texture/value area may still be secondary when it does not decide the
structural read.

## Instruction changes

- add `references/foundation/structural-specificity.md` as the cross-subject owner;
- generalize `SKILL.md` from observed-figure structural prerequisites to whole-subject structural
  specificity;
- update `INDEX.md` so a rough silhouette/simple construction does not imply readiness for local
  description;
- update line economy so sparse marks cannot justify generic structure;
- update residual correction and descriptive geometry so downstream passes cannot freeze an
  incorrect parent construction;
- add mechanical regression checks in `dev/tests/test_skill_surface_boundary.py`.

## Non-goals

A7 does not:

- add a runtime stage or lifecycle gate;
- add automatic structure scoring or visual PASS logic;
- prescribe subject-specific primitives, templates, or coordinate rules;
- remove construction abstraction as a reasoning aid;
- claim D01–D06 visual-quality success.

## Next

D01 difficult observed croquis remains the next formal sealed validation case. The same A7
invariants also apply to D02–D05 whenever later description would otherwise inherit an unverified
parent structure.
