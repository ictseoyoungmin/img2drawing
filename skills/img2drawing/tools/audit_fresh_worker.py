from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'skills/img2drawing/src'
sys.path.insert(0,str(SRC))

import img2drawing

STAGES=[
    'P1_gesture',
    'P2_primary_axes',
    'P3_primary_masses',
    'P4_structural_connections',
    'P5_clean_blockin',
]
OLD_DOGFOOD_PREFIXES=tuple(f'R{i:02d}-' for i in range(8,20))

def fail(msg: str):
    raise SystemExit(msg)

def audit(run_dir: Path) -> dict:
    run_dir=run_dir.resolve()
    cp_path=run_dir/'session/checkpoint.json'
    if not cp_path.is_file():
        fail(f'missing checkpoint: {cp_path}')
    cp=json.loads(cp_path.read_text(encoding='utf-8'))
    checkpoint_schema=cp.get('schema')
    if checkpoint_schema not in {
        'img2drawing.run_checkpoint.v1',
        'img2drawing.run_checkpoint.v2',
        'img2drawing.run_checkpoint.v3',
    }:
        fail(f'unsupported checkpoint schema: {checkpoint_schema!r}')

    progress=cp.get('progress') or {}
    if int(progress.get('current_index',-1)) != len(STAGES):
        fail(f'run is not complete: current_index={progress.get("current_index")}')
    advanced=progress.get('advanced_reviews') or {}
    missing=[s for s in STAGES if not advanced.get(s)]
    if missing:
        fail(f'missing advanced reviews: {missing}')

    reviews=cp.get('reviews') or {}
    stage_summary={}
    revision_count=0
    for stage in STAGES:
        rows=reviews.get(stage) or []
        if not rows:
            fail(f'no artifact-bound reviews for {stage}')
        latest=rows[-1]
        if latest.get('decision')!='advance':
            fail(f'latest {stage} review is not ADVANCE')
        if latest.get('remaining_concerns'):
            fail(f'latest {stage} review still has concerns')
        if not latest.get('advance_rationale'):
            fail(f'latest {stage} ADVANCE lacks rationale')
        if not latest.get('drawing_artifact_sha256') or not latest.get('drawing_state_sha256'):
            fail(f'{stage} review is not artifact/state bound')
        revision_count += sum(1 for r in rows if r.get('decision')=='revise')
        stage_summary[stage]={
            'review_count':len(rows),
            'decisions':[r.get('decision') for r in rows],
            'latest_digest':advanced.get(stage),
        }

        # On-disk review packets: every pass should have review evidence + memory packet.
        stage_dir=run_dir/'reviews'/stage
        pass_dirs=sorted(p for p in stage_dir.glob('pass_*') if p.is_dir())
        if len(pass_dirs) < len(rows):
            fail(f'{stage}: fewer pass directories than checkpoint reviews')
        required={
            'current_drawing.png','subject_vs_drawing.png','worker_packet.json',
            'worker_packet.md','pass_memory.json','review.json','stage_contract.json',
        }
        for pd in pass_dirs[:len(rows)]:
            missing_files=sorted(name for name in required if not (pd/name).is_file())
            if missing_files:
                fail(f'{pd}: missing review evidence {missing_files}')

        # Current P3 closure is deliberately dual: process review alone is not
        # sufficient.  Legacy v1 runs remain auditable, but a v2/v3 run must
        # carry the region manifest and independent visual record in its latest
        # pass and checkpoint.
        if stage == 'P3_primary_masses' and checkpoint_schema in {
            'img2drawing.run_checkpoint.v2',
            'img2drawing.run_checkpoint.v3',
        }:
            if not (latest.get('decision') == 'advance'):
                fail('P3 latest process review is not ADVANCE')
            visual=cp.get('visual_fidelity_reviews', {}).get(stage)
            manifest=cp.get('region_closure_manifests', {}).get(stage)
            if not visual or visual.get('decision') != 'advance':
                fail('P3 v2/v3 run is missing independent visual ADVANCE')
            if not manifest or manifest.get('blockers'):
                fail('P3 v2/v3 run is missing blocker-free region closure')
            latest_pass=pass_dirs[len(rows)-1]
            for name in ('blind_visual_packet.json', 'region_closure_manifest.json', 'visual_fidelity_review.json'):
                if not (latest_pass/name).is_file():
                    fail(f'{latest_pass}: missing P3 dual-gate evidence {name}')

    history=((cp.get('agent_session') or {}).get('history') or {})
    actions=history.get('actions') or []
    if not actions:
        fail('drawing history is empty')

    action_ids=[]
    direct_stroke_actions=0
    correction_actions=0
    for item in actions:
        prov=item.get('provenance') or {}
        aid=str(prov.get('action_id') or '')
        if aid:
            action_ids.append(aid)
        action=str(item.get('action') or '')
        if action in {'stroke.add','stroke.replace'}:
            direct_stroke_actions += 1
        if action in {'stroke.replace','stroke.soft_lift','stroke.segment_replace',
                      'stroke.segment_soft_lift','stroke.delete'}:
            correction_actions += 1

    copied=[aid for aid in action_ids if aid.startswith(OLD_DOGFOOD_PREFIXES)]
    if copied:
        fail(
            'run appears to reuse historical dogfood action IDs instead of fresh work: '
            + ', '.join(copied[:10])
        )
    if direct_stroke_actions < 10:
        fail(f'too few direct stroke actions: {direct_stroke_actions}')

    # Final artifacts are mandatory.
    for rel in [
        'final/drawing.png',
        'compare/subject_vs_final.png',
        'session/session.json',
        'session/checkpoint.json',
    ]:
        if not (run_dir/rel).is_file():
            fail(f'missing final artifact: {rel}')

    # The semantic report is evidence for later human/Agent audit, not trusted as proof.
    report=run_dir/'DOGFOOD_REPORT.md'
    if not report.is_file():
        fail('missing DOGFOOD_REPORT.md')

    # Reopen is not mandatory: a good fresh run may never discover an upstream defect.
    reopens=cp.get('reopens') or []
    reopen_summary=[
        {
            'target_stage':r.get('target_stage'),
            'discovered_in_stage':r.get('discovered_in_stage'),
            'invalidated_stages':r.get('invalidated_stages'),
        }
        for r in reopens
    ]

    warnings=[]
    if revision_count == 0:
        warnings.append(
            'No REVISE decisions occurred. This is mechanically valid but deserves '
            'extra visual scrutiny for premature closure.'
        )
    if correction_actions == 0:
        warnings.append(
            'No correction/retirement actions occurred. Inspect whether the worker '
            'actually hardened stages or simply advanced.'
        )
    if not reopens:
        warnings.append(
            'No upstream reopen occurred. This is not a failure; later visual audit '
            'must verify that no downstream compensation hid an earlier defect.'
        )

    result={
        'schema':'img2drawing.fresh_worker_mechanical_audit.v1',
        'img2drawing_version':img2drawing.__version__,
        'run_dir':str(run_dir),
        'complete':True,
        'stage_summary':stage_summary,
        'revision_count':revision_count,
        'direct_stroke_actions':direct_stroke_actions,
        'correction_actions':correction_actions,
        'reopens':reopen_summary,
        'historical_dogfood_action_ids_found':False,
        'final_artifacts_present':True,
        'report_present':True,
        'warnings':warnings,
        'semantic_visual_audit_required':True,
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-dir',required=True,type=Path)
    ap.add_argument('--write-json',type=Path)
    args=ap.parse_args()
    result=audit(args.run_dir)
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if args.write_json:
        args.write_json.parent.mkdir(parents=True,exist_ok=True)
        # Keep the persisted artifact strict JSON.  The CLI already emits a
        # newline separately; writing the two-character ``\\n`` literal here
        # made ``json.loads`` reject the audit artifact even though stdout was
        # valid JSON.
        args.write_json.write_text(text+'\n',encoding='utf-8')
    print(text)
    print('FRESH_WORKER_MECHANICAL_AUDIT_PASS')

if __name__=='__main__':
    main()
