# vNext sealed dogfood case template

Copy this directory once per D01-D06 case only after B18 closes. The worker receives the
installed/current skill and package, `input/sealed_input.json`, the named subject file
when required, and nothing else from the case directory.

Before dispatch:

1. Rename `input/sealed_input.template.json` to `input/sealed_input.json`.
2. Replace the request, intent, authority, subject basename, and SHA-256 with fresh case
   facts; imaginative work must keep `subject` null.
3. Keep only `sealed_input.json` and its declared subject in `input/`, then run
   `python dev/tools/seal_vnext_dogfood_input.py <case>/input/sealed_input.json`.
4. Record the reported digest outside the worker input and do not modify the input after
   dispatch begins.

Never give the worker an answer image, target drawing, authored coordinates or landmarks,
prior session/action IDs, prior residuals, evaluator rationale/verdict, historical worker
packet, or subject-specific solution script. The evaluator brief is opened by an
independent reviewer only after the worker has returned final evidence.

## Case matrix

| Case | Required authority and intent focus |
|---|---|
| D01 | observed croquis / pose |
| D02 | observed figure drawing / subject |
| D03 | observed tonal study / form-light |
| D04 | observed free-draw / expressive |
| D05-A | imaginative, subjectless |
| D05-B | hybrid with distinct preserved and transformed constraints |
| D06 | the same sealed input dispatched independently to at least two workers |

Mechanical validation is not artistic acceptance. Review the whole image and cost record,
route a defect to the earliest responsible B-slice, reopen it explicitly, and rerun the
affected case from the unchanged sealed input.
