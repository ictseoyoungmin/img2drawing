# Context capsule — S02 Region Envelope Evidence

Status: `CLOSED`

Implementation commit: `54daaf6` (`feat: add region envelope evidence`)

## Responsibility

Measure occupied region width independently on subject and drawing so a
plausible axis cannot conceal a thin or missing limb envelope. S02 provides
geometry evidence; it does not close regions, score art, or gate P3.

## Public surface

- `EnvelopeStation(t, contour_a, contour_b, visibility, occlusion,
  uncertainty_radius)` stores one normalized cross-section.
- `RegionEnvelopeObservation` stores region id, side role, normalized axis,
  stations, visible fraction, occlusion, artifact provenance, drawing state,
  and the S01 frozen observation digest.
- `compare_region_envelopes(reference, drawing,
  current_drawing_state_sha256=...)` returns `RegionGeometryComparison`.
- `RegionEnvelopeIntegrityError` rejects provenance drift, mismatched stations,
  and stale drawing evidence when independent comparison is required.

## Inputs and outputs

Inputs are two independently observed profiles: one `source_surface="reference"`
and one `source_surface="drawing"`. A drawing profile must carry its drawing
state digest. Outputs contain axis endpoint deltas, local-axis and optional
subject-height width measurements per station, visible-fraction drift,
occlusion-order change, and integrity evidence with authority
`evidence_not_pass_fail`.

## Invariants

- Axes and contour points use normalized `[0,1]` coordinates.
- Station `t` values are strictly increasing and limited to 2–16 entries.
- Reference and drawing ids and artifact hashes are distinct, while the S01 lock
  digest matches across both profiles.
- A supplied current drawing-state digest must match the drawing profile.
- The comparison is linear in station count and never emits an artistic
  `PASS`/`FAIL` decision.

## Budgets and dependencies

- The 16-station fixture runs 100 comparisons under the 100 ms slice budget.
- Manual paired contour sampling is the production contract; no CV inference,
  network access, or new dependency is used.
- Canonical implementation is `src/img2drawing/registration/envelope.py` with
  one `region_envelope.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S02-region-envelope/closure_report.md`
- `dev/evidence/p3-fidelity/S02-region-envelope/near-arm_fixture.json`
- `dev/evidence/p3-fidelity/S02-region-envelope/near-arm-envelope-board.svg`
- `skills/img2drawing/tests/test_region_envelope.py` (`18 passed`)

## Limitations and next integration

Contours are agent-selected; the utility does not infer anatomy or segment
pixels. S03 should bind these measurements into independent visual-fidelity
region closure and combine them with process review. Later slices may add
dedicated head/torso/leg/prop profiles without changing the station contract.

## Reopen conditions

Reopen S02 if any consumer bypasses independent provenance, treats geometry
evidence as an artistic decision, accepts stale drawing state, or exceeds the
16-station/100 ms budget. Otherwise activate S03 using this capsule and the S01
lock digest as inputs.
