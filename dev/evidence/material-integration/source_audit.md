# Material source audit (R23 visual-quality integration)

This audit classifies the two temporary repositories before any promotion into
canonical evidence. The original subject image remains the only geometry
authority; masks, critic scores, and authored coordinate scripts are diagnostic
or instructional material.

| Source | SHA-256 | Classification | Decision |
|---|---|---|---|
| `img2drawing-material-1/.../critic_report.json` | `1af43003215daf92b7ea2df9abacf0e1d27e64b3dd90ed035a9ba5300dd65b4a` | critic measured an agent-authored matte | negative fixture; never likeness authority |
| `img2drawing-material-1/.../subject_matte.png` | `3d3f9832bdd84db1c9389e39759043601cbff907928f9f9cb17282254d13a427` | observation aid promoted to reference | negative fixture; not copied into runtime |
| `img2drawing-material-2/.../final_croquis.png` | `5699ece18a975a1feabd11ebf5d921c2814c13cf4f4af64e086951523d809a05` | subject-specific R23 workflow output | negative visual reference; no coordinates imported |
| `croquis-sniper-girl/01_output/croquis_final.png` | `3381d9da6e120a2d8625b82e3a375a764cb45ffa6519557012499bbbafeef950` | prior R22 post-finish output | regression fixture for blanket identity/restatement |
| `s10-quality-run/final/drawing.png` | `9fb40326de73d3d70f682a4424e786b1b606f3f685cd6608b69317afb479f3e5` | current API migration run | canonical positive process/evidence fixture, still manually inspectable |

The positive fixture was produced by the current `DrawingRun` API with a fresh
observation lock, P4/P5 resolved-form reviews, a history-preserving retirement
record, calibration, and bounded optional P6. It does not inherit any prior
visual verdict. Direct inspection remains mandatory and is recorded separately
from mechanical verification.
