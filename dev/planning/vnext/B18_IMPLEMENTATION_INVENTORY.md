# B18 implementation-completeness inventory

Reviewed: 2026-09-02

This is the freeze audit across B09-B17. It records where each contract lives and what
would reopen it; it does not create another product roadmap or runtime owner.

| Slice | Frozen responsibility | Authoritative implementation/evidence | Reopen trigger |
|---|---|---|---|
| B09 | relational finish authoring | `vnext/intent.py`, finish references, `test_vnext_finish.py` | finish guidance cannot express a material relation |
| B10 | current-state completion provenance | `vnext/completion.py`, `DrawingSession.finish`, `test_vnext_completion.py` | stale/tampered evidence can remain current |
| B11 | deterministic profile and output/replay parity | `vnext/render_profile.py`, `vnext/output.py`, `test_vnext_rendering.py` | final PNG/replay/GIF or renderer provenance diverges |
| B12 | explicit lazy R23 boundary and migration | `legacy/r23.py`, `test_vnext_legacy_boundary.py` | canonical imports load/advertise Pn or migration loses shared truth |
| B13 | observed/imaginative/hybrid authority | `vnext/reference_authority.py`, subjectless session path, `test_vnext_reference_authority.py` | authority mutates or subjectless inspection fabricates reference evidence |
| B14 | five drawing-mode guides on one core | `vnext/intent.py`, `references/modes/`, `test_vnext_modes.py` | a mode requires a separate lifecycle or lacks distinct authoring policy |
| B15 | three presets, one-base overrides, structured custom style | `vnext/intent.py`, `references/styles/`, `test_vnext_styles.py` | style overrides geometry or becomes renderer state |
| B16 | derived author navigation and unified edits | `vnext/editing.py`, session edit methods, `test_vnext_editing.py` | ownership forks, orphan edits, or persisted parallel index appears |
| B17 | package/API/support/migration/installed examples | `verify_vnext_b17.py`, package docs, `test_vnext_package_contract.py` | source/build/install/API or artifact boundary diverges |

## Open-work audit

The canonical vNext source contains no TODO/FIXME/TBD marker, `NotImplementedError`,
ellipsis placeholder, or empty function body. Public root exports resolve, and the B18
snapshot pins them together with public session members and persisted schema IDs. No
known product feature is deferred with “dogfood will define the API”; D01-D06 test the
frozen interface and reopen the responsible row above when evidence disproves it.

## Duplicate and legacy classification

- `img2drawing.vnext.session.DrawingSession` is the only canonical orchestration class
  and the object exported at the package root.
- `img2drawing.core.session.DrawingSession` is a preserved low-level legacy replay record
  used by historical provenance utilities. It is not root-exported and is retired or
  renamed only in post-dogfood R03, not duplicated for vNext.
- `vnext.value.replace_fill_region()` is a compatibility function that delegates to
  `DrawingSession.replace_fill_region()`; it owns no history access or edit algorithm.
- `VNextDrawingSession` is an identity alias, not a subclass or second implementation.
- R23 stage/review/reference modules remain physically present only for the B12 rollback
  and migration boundary. A canonical root import does not load them.

## Freeze boundary

`skills/img2drawing/CONTRACT_FREEZE.json` is the machine-readable D01-D06 baseline.
Private helper names and reversible implementation choices are not frozen. Public export,
session member, schema, intent-axis, renderer/profile, ownership, or compatibility changes
require an explicit responsible-slice reopen and a corresponding version/schema update.
