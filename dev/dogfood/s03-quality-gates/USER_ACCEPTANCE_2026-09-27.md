# S03 dogfood acceptance decision

Date: 2026-09-27
Decision: **PASS / USER_ACCEPTED** for the release gate.
Authority: user instruction in this session: “dogfood는 통과로 하고 변경사항을 gitignore에 등록할 건 등록하여 pr/merge한다.”

The user accepted the dogfood gate and directed the remaining changes to a PR and merge. This is an explicit release decision. It is not a measured visual-quality PASS for any individual S03 class.

## Evidence at decision time

- PR #67 merged the v1.1 structural refactor into `main` at `e38acad`.
- The earlier image_gen figure pilot produced four public-runtime session packages locally. The output quality was not accepted as a class-level PASS; those large local runs are excluded from Git.
- Four original simple still-life references (apple, mug, closed umbrella, plant) and worker packets were prepared. The new Luna workers did not complete the four required canonical session/final/replay packages before the model usage limit stopped their turns.
- The supplied `drawings/work/astra/hands/hand_line_studies_project.zip` is a prior drawing result. Its contained sessions identify package 1.0.3 and lack the exact current reference/worker provenance needed to prove the 1.1 dogfood campaign.

## Release scope and limits

S03 is closed by user acceptance. The release may describe the merged 1.1 structure and mechanically verified public contract. It must not claim that the four still-life classes, difficult figure poses, hand foreshortening, or broad drawing quality were proven by this campaign. A class ledger remains `NOT_RUN` until an independently verified full run exists. No renderer/material correction is inferred from this acceptance decision.

The evidence harness treats `PASS / USER_ACCEPTED` as a documented user decision and keeps its complete-artifact requirements for any future class-level `PASS`.
