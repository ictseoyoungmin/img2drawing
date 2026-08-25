# S10 mechanical and A/B/C audit

## Result

| Check | Result |
|---|---|
| S01–S08 artifacts and policy records | PASS |
| checkpoint/review/observation/drawing digest bindings | PASS |
| P3 manifest and visual-review artifact shape | PASS mechanically |
| S09 A/B/C on the actual s1s9 subject | **NOT EXECUTED** |
| independent blind evaluator as a separate worker/process | **NOT PROVEN** |
| raster-derived geometry measurement | **NOT EXECUTED** |
| overall S10 | **NOT CLOSED** |

The S09 `ablation_report.json` under `dev/evidence/p3-fidelity/S09-exemplar-ablation/` is a deterministic harness fixture. It is not evidence that the s1s9 drawing was rendered under conditions A, B, and C. `run_s1s9.py` contains no A/B/C trial invocation.

Likewise, the s1s9 P3 artifact labels the evaluator `s1s9-independent-visual-evaluator`, but the finding and `advance` decision are authored inline by `_submit_p3_visual_gate()`. The label does not establish worker/process independence.

The existing region evidence is integrity-bound and useful for provenance, but its reference and drawing geometry are both agent-authored normalized observations. Near-zero deltas therefore cannot establish rendered likeness; the blind review in `blind_visual_report.md` is the controlling semantic result.

## Artifact defect fixed in S10

`skills/img2drawing/tools/audit_fresh_worker.py` wrote the literal two-character string `\\n` after JSON, causing `json.loads()` to reject `mechanical_audit.json`. The writer now emits an actual newline, preserving strict JSON.

## Earliest-stage decision

- P1/P2: craniofacial direction and torso/shoulder axes.
- P3: head/hair mass, torso bridge, near-arm occupied width, pelvis asymmetry, and prop topology.
- P4/P5: only downstream garment, boot, cuff/hand, and identity details after those blockers close.

Do not use P5 polish to compensate for these upstream residuals.
