"""Release-acceptance check for a specific img2drawing release (R22).

This validates that the checked-out skill tree still carries the R22
doctrine and that the R22 dogfood trace still demonstrates a closed run.
It is release-specific by design (each release gets its own snapshot of
this check, the way `dev/release/*-r21-*` files are pinned to R21) and is
not meant to keep working unmodified once the tree moves past R22 — the
RELEASE_REVISION gate below exists to fail loudly rather than silently
pass against the wrong release.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEV_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = DEV_ROOT.parent
SKILL_ROOT = REPO_ROOT / 'skills' / 'img2drawing'

sys.path.insert(0, str(SKILL_ROOT / 'src'))

import img2drawing
from img2drawing._version import RELEASE_REVISION
from img2drawing.stages import get_stage_registry

TARGET_REVISION = 'R22'
if RELEASE_REVISION != TARGET_REVISION:
    raise SystemExit(
        f'this validator targets {TARGET_REVISION}; current tree is {RELEASE_REVISION}'
    )

skill = (SKILL_ROOT / 'SKILL.md').read_text(encoding='utf-8')
p5 = (SKILL_ROOT / 'references/stages/p5-clean-blockin.md').read_text(encoding='utf-8')
for phrase in ['Large Attached-object Topology', 'major subpart topology']:
    if phrase.lower() not in skill.lower():
        raise SystemExit(f'missing {TARGET_REVISION} doctrine: {phrase}')
for phrase in ['large attached-object topology', 'major topology']:
    if phrase.lower() not in p5.lower():
        raise SystemExit(f'missing {TARGET_REVISION} P5 guidance: {phrase}')

spec = get_stage_registry('full_body_croquis')[-1]
if not any('attached-object subpart topology' in x.lower() for x in spec.draw):
    raise SystemExit('P5 StageSpec missing attached-object topology')
if not any('large attached object' in x.lower() for x in spec.review_questions):
    raise SystemExit('P5 review questions missing attached-object topology review')

trace = json.loads((DEV_ROOT / 'docs/audits/r22_attached_object_topology.json').read_text(encoding='utf-8'))
if trace['schema'] != 'img2drawing.r22_attached_object_topology.v1':
    raise SystemExit(f'{TARGET_REVISION} trace schema drift')
if trace['reopen']['target_stage'] != 'P5_clean_blockin':
    raise SystemExit(f'{TARGET_REVISION} did not reopen P5')
if trace['p5']['decision'] != 'advance' or trace['p5']['remaining_concerns']:
    raise SystemExit(f'{TARGET_REVISION} P5 did not close')
if trace['current_stage'] is not None:
    raise SystemExit(f'{TARGET_REVISION} run should be complete')
if trace['after_rifle_jacket_contact']['near_sample_count_a'] != 0:
    raise SystemExit(f'{TARGET_REVISION} prop/jacket contour ownership still risks welding')

print(f'{TARGET_REVISION}_RELEASE_VALIDATION_PASS {img2drawing.__version__}')
