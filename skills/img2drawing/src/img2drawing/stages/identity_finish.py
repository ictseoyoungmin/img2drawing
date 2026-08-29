from .model import StageSpec
from .contract import StageContract


IDENTITY_FINISH_STAGE = StageSpec(
    "P6_identity_finish", 6, "Optional Identity Finish / Line Expression",
    "Only after P1–P5 are visually closed, add a bounded set of identity-defining feature, hair, garment and line-expression marks.",
    (
        "the frozen head turn, eye line, jaw and feature intervals",
        "hair parting, grouped locks and face occlusion",
        "identity-defining garment breaks, sparse folds and prop contacts",
        "the selected pressure/taper calibration on the actual canvas",
    ),
    (
        "proportional eye/nose/mouth relationship bound to the observed head turn",
        "outer hair mass plus a small number of grouped internal locks",
        "sparse form-following folds at anchors, tension and compression events",
        "selective contour accent and restatement with explicit pressure samples",
    ),
    (
        "upstream pose, volume, view or contour-ownership correction",
        "pixel-by-pixel edge tracing",
        "blanket confirmation or whole-contour darkening",
        "broad charcoal/value bands and unlimited micro-detail",
    ),
    review_questions=(
        "Does the eye line and facial centreline still state the locked head turn?",
        "Are the eyes, nose, mouth and chin in a proportional relationship rather than arbitrary marks?",
        "Does hair remain grouped into a seated mass with only representative locks?",
        "Do sparse folds explain anchor, tension or compression rather than texture?",
        "Is accent limited to the selected high-information 15–25% of marks?",
        "Did no P1–P5 blocker get hidden under identity detail?",
    ),
    advance_when=(
        "P1–P5 preflight is clear of structural blockers.",
        "Feature, hair, garment and line-expression marks stay inside their declared budgets.",
        "A fresh whole-view and applicable close-crop review finds no unresolved identity mismatch owned by P6.",
    ),
    suggested_crops=("face relation", "hair grouping", "garment anchor/fold", "hands/footwear/prop contact"),
)


IDENTITY_FINISH_CONTRACT = StageContract(
    contract_id="full_body_croquis.P6.v1",
    stage_id="P6_identity_finish",
    tier=6,
    representation_name="optional_identity_finish",
    owns=(
        "head-turn-preserving eye, nose, mouth and chin relationship",
        "grouped hair locks and face occlusion",
        "identity-defining garment and prop marks",
        "selective pressure, taper and accent expression",
    ),
    inherits_from="P5_clean_blockin",
    must_preserve=(
        "P5 contour ownership and clean block-in",
        "P3 volume and proportion",
        "P1/P2 head turn, balance and ground contact",
    ),
    allowed_representation=(
        "proportional facial features bound to the observed head turn",
        "grouped hair locks and representative tips",
        "sparse structural garment folds",
        "selective restatement with per-point pressure and taper",
    ),
    forbidden_representation=(
        "pixel tracing",
        "upstream structural correction",
        "blanket confirmation",
        "broad value bands",
        "unlimited micro texture",
    ),
    detail_ceiling=(
        "identity-defining relationships only",
        "no rendering claim",
        "bounded line-expression budget",
    ),
    next_stage_unlocks=(),
)


__all__ = ["IDENTITY_FINISH_STAGE", "IDENTITY_FINISH_CONTRACT"]
