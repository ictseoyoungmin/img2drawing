# v1.3 constructive drawing — S00 matched evaluation contract

State: **IN_PROGRESS**. This developer-only first slice seals reference identity, prompt,
observed intent, worker/model configuration, canvas and equal resource budgets before
any independent runs. It checks matched evidence metadata and actual file hashes,
not artistic quality. No runtime or renderer changes.

Baseline arms are pinned to v1.2.0 and the merged v1.2.1 maintenance release commit.
The eventual v1.3.0 candidate commit must be recorded before its run. Use a separate
fresh worker for each arm and do not pass prior outputs, answer strokes, evaluator
notes or the hidden comparison to workers. The run's freshness field is an attestation
requiring reviewer evidence; distinct IDs alone do not establish independence.

## Six-class matrix

| Class | Current case selection |
|---|---|
| portrait | User-provided private photo; seal locally, never commit reference or outputs |
| full_body | Pending source selection |
| hand_object | Pending source selection |
| hair | Pending source selection |
| still_life | Pending source selection (existing S03 references are candidates) |
| environment | Pending source selection |

The previous developer-authored portrait is exploratory evidence, not a fresh-worker
baseline. Set the actual model identifier, configuration and equal budget before
starting a case. Unknown token budget can be explicitly null, but unmetered usage
does not support a token-efficiency claim.

## Commands

```sh
python dev/benchmarks/constructive_qa/protocol.py seal case-spec.json reference.png sealed-case.json
python dev/benchmarks/constructive_qa/protocol.py verify sealed-case.json reference.png
python dev/benchmarks/constructive_qa/protocol.py pair sealed-case.json reference.png baseline-run.json baseline-evidence candidate-run.json candidate-evidence
```

Case spec fields: case_id, subject_class, user_request, intent (reference_mode=observed,
drawing_mode, finish_intent, style_profile), worker (model, configuration), budget
(max_actions, max_wall_seconds, max_tokens), canvas (width, height). The sealed digest
covers all fields and the source bytes. Only the normal request, reference, allowed
skill/runtime and execution conditions belong in the worker input. Keep evaluator
records separate.

Run fields: schema=img2drawing.constructive_qa.run.v1, case_digest, arm, commit (full
SHA), worker_run_id, freshness (status, evidence), usage (actions, wall_seconds,
tokens), artifacts (session, final_png, timelapse_gif, comparison, review; each an
evidence-root-relative file and SHA-256). The checker refuses mismatched input hashes,
baseline versions/commits, reused worker IDs, out-of-budget records and tampered or
escaping artifact paths. It never outputs a visual PASS. Independently verify actual
worker execution conditions, session replay action 0 to latest, PNG/GIF fidelity,
and all applicable visual gates in review. Record geometry/landmark deviation,
tonal coverage, line hierarchy/ownership, time, actions and measured tokens; do not
turn diagnostic values into an automatic artistic verdict.

Do not commit private reference bytes, reference fingerprints, sessions, frame packs,
or answer geometry. Keep them in authorized local evidence storage. S00 remains open
until all six reference cases, prompts, actual model settings, budgets, baseline results
and review evidence are fixed. S07 remains the independent quality gate.
