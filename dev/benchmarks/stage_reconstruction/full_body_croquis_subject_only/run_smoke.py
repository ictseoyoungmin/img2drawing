from pathlib import Path
import json
from img2drawing import DrawingRun, ObservationContract, ViewObservation

HERE=Path(__file__).resolve().parent
cfg=json.loads((HERE/'benchmark.json').read_text(encoding='utf-8'))
out=HERE/'_smoke_output'
run=DrawingRun.create(HERE/cfg['subject'],out,working_supersample=2)
run.lock_observation(ObservationContract(
    subject_summary="Subject-only packaging benchmark observation smoke.",
    view=ViewObservation(
        arm_visibility={"subject_left":"unknown","subject_right":"unknown"},
        arm_occlusion={"subject_left":(),"subject_right":()},
        uncertainties=("This benchmark checks lifecycle binding, not pose semantics.",),
    ),
))

if run.references.task_stage_targets:
    raise SystemExit('subject-only benchmark unexpectedly contains task stage targets')

stage_rows=[]
for sid in cfg['required_stages']:
    refs=run.stage_references(sid)
    if refs.task_stage_target is not None:
        raise SystemExit(f'{sid}: unexpected task-stage target')
    if refs.authority_order != ('subject_reference','grammar_exemplar'):
        raise SystemExit(f'{sid}: subject-only authority order drift: {refs.authority_order}')
    stage_rows.append({
        'stage':sid,
        'contract':run.stage_contract(sid).contract_id,
        'authority_order':list(refs.authority_order),
        'grammar_audit':refs.grammar_exemplar.audit_status,
    })

print(json.dumps({
    'benchmark':cfg['id'],
    'reference_mode':cfg['reference_mode'],
    'current_stage':run.current_stage,
    'subject':str(run.references.subject.path),
    'task_stage_target_count':len(run.references.task_stage_targets),
    'stages':stage_rows,
},indent=2))
print('SUBJECT_ONLY_BENCHMARK_PASS')
