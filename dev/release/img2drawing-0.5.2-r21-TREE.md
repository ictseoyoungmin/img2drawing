# img2drawing 0.5.2-R21 skill-only tree

```text
img2drawing
├── benchmarks
│   └── stage_reconstruction
│       ├── full_body_croquis_subject_only
│       │   ├── benchmark.json
│       │   ├── run_smoke.py
│       │   └── subject.png
│       └── README.md
├── examples
│   └── full_body_croquis
│       ├── README.md
│       ├── run.py
│       └── subject.png
├── exemplars
│   ├── full_body_croquis
│   │   ├── sources
│   │   │   └── p2_axes_v2.json
│   │   ├── audit_manifest.json
│   │   ├── manifest.json
│   │   ├── p1_gesture.png
│   │   ├── p2_axes.png
│   │   ├── p3_masses.png
│   │   ├── p4_structure.png
│   │   └── p5_clean_blockin.png
│   └── schemas
│       └── exemplar_manifest.schema.json
├── playbooks
│   ├── autonomous-stage-hardening.md
│   ├── full-body-croquis.md
│   └── subject-only-stage-derivation.md
├── references
│   ├── figure
│   │   ├── attached-objects.md
│   │   ├── gesture-line-of-action.md
│   │   └── limbs-joints.md
│   ├── observation
│   │   └── visual-observation.md
│   ├── pencil
│   │   └── graphite.md
│   ├── review
│   │   ├── correction-loop.md
│   │   ├── dual-reference-review.md
│   │   ├── fresh-worker-defect-closure.md
│   │   ├── local-review-api.md
│   │   ├── reference-authority.md
│   │   ├── reopen-recovery.md
│   │   ├── when-to-advance.md
│   │   └── worker-pass-memory.md
│   ├── stages
│   │   ├── p1-gesture.md
│   │   ├── p2-primary-axes.md
│   │   ├── p3-primary-masses.md
│   │   ├── p4-structural-connections.md
│   │   ├── p5-clean-blockin.md
│   │   └── stage-contracts.md
│   ├── worker
│   │   └── autonomous-worker-contract.md
│   └── INDEX.md
├── schemas
│   ├── canonical_example_trace.schema.json
│   ├── drawing_action.schema.json
│   ├── exemplar_audit.schema.json
│   ├── fresh_p1_regression.schema.json
│   ├── local_review.schema.json
│   ├── observation.schema.json
│   ├── p2_hardening_regression.schema.json
│   ├── p3_hardening_regression.schema.json
│   ├── pass_memory.schema.json
│   ├── reference_bundle.schema.json
│   ├── registration.schema.json
│   ├── reopen_record.schema.json
│   ├── reopen_recovery_regression.schema.json
│   ├── review.schema.json
│   ├── session.schema.json
│   ├── stage.schema.json
│   ├── stage_contract.schema.json
│   ├── timelapse.schema.json
│   └── worker_packet.schema.json
├── src
│   └── img2drawing
│       ├── canvas
│       │   ├── __init__.py
│       │   ├── editing.py
│       │   ├── inspection.py
│       │   ├── runtime.py
│       │   └── transactions.py
│       ├── core
│       │   ├── __init__.py
│       │   ├── action.py
│       │   ├── history.py
│       │   ├── ir.py
│       │   ├── session.py
│       │   ├── stroke.py
│       │   └── tools.py
│       ├── data
│       │   ├── exemplars
│       │   │   └── full_body_croquis
│       │   │       ├── audit_manifest.json
│       │   │       ├── manifest.json
│       │   │       ├── p1_gesture.png
│       │   │       ├── p2_axes.png
│       │   │       ├── p3_masses.png
│       │   │       ├── p4_structure.png
│       │   │       └── p5_clean_blockin.png
│       │   ├── __init__.py
│       │   ├── pencil_contact_profile.json
│       │   ├── pencil_presets.json
│       │   └── registration_profile.json
│       ├── exemplar
│       │   ├── __init__.py
│       │   └── audit.py
│       ├── observation
│       │   ├── __init__.py
│       │   ├── contract.py
│       │   ├── evidence.py
│       │   ├── uncertainty.py
│       │   └── views.py
│       ├── provenance
│       │   ├── __init__.py
│       │   ├── replay.py
│       │   └── timelapse.py
│       ├── reference
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   └── model.py
│       ├── registration
│       │   ├── __init__.py
│       │   ├── compare.py
│       │   ├── grid.py
│       │   ├── human.py
│       │   └── model.py
│       ├── render
│       │   ├── __init__.py
│       │   ├── cairo.py
│       │   ├── contact_profile.py
│       │   ├── line_weight.py
│       │   ├── pillow.py
│       │   ├── pillow_eraser_material.py
│       │   ├── pillow_graphite.py
│       │   ├── pillow_graphite_grain.py
│       │   ├── pillow_hand_dynamics.py
│       │   ├── pillow_paper_interaction.py
│       │   ├── pillow_pencil_contact.py
│       │   ├── pillow_pencil_grades.py
│       │   ├── pillow_subpixel.py
│       │   ├── presets.py
│       │   ├── scale_guidance.py
│       │   └── svg.py
│       ├── review
│       │   ├── __init__.py
│       │   ├── artifact.py
│       │   ├── comparison.py
│       │   ├── contour_contact.py
│       │   ├── correction.py
│       │   ├── dual_reference.py
│       │   ├── local_review.py
│       │   ├── pass_memory.py
│       │   ├── record.py
│       │   ├── reference_review.py
│       │   ├── reopen.py
│       │   └── worker_protocol.py
│       ├── stages
│       │   ├── __init__.py
│       │   ├── contract.py
│       │   ├── full_body_contracts.py
│       │   ├── full_body_croquis.py
│       │   ├── model.py
│       │   └── registry.py
│       ├── __init__.py
│       ├── _version.py
│       └── run.py
├── tools
│   ├── audit_fresh_worker.py
│   └── validate_r21_release.py
├── pyproject.toml
├── QUICKSTART.md
├── README.md
└── SKILL.md
```
