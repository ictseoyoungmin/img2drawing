import pytest
import numpy as np
from PIL import Image
from img2drawing import DrawingSession, DrawingIntent, RenderProfile
from img2drawing.inspection import TonalPatch, compare_tonal_patches, inspect_tonal_patches


def strips(path, darkness, *, height=8, paper=255):
    vals = [round(paper-255*d) for d in darkness]
    Image.fromarray(np.repeat(np.array(vals, dtype=np.uint8)[None, :], height, axis=0)).save(path)
    return path


def test_equal_mean_is_not_equal_value_organization(tmp_path):
    ref = strips(tmp_path/'ref.png', [.2,.3,.4,.5])
    drawing = strips(tmp_path/'draw.png', [.2,.5,.3,.4])
    paper = strips(tmp_path/'paper.png', [0]*4)
    p = [TonalPatch(str(i), (i,0,i+1,8), (i,0,i+1,8)) for i in range(4)]
    r = compare_tonal_patches(ref,drawing,paper,p,deadband=.02)
    assert r['reference_chain']['mean_darkness'] == pytest.approx(r['drawing_chain']['mean_darkness'])
    assert r['reference_chain']['direction_reversals'] == 0
    assert r['drawing_chain']['direction_reversals'] == 2
    assert r['adjacent_relations'][1]['opposite_order']
    assert r['evidence_binding'] == 'external_images_unverified'
    assert r['artistic_verdict'] == 'NOT_EVALUATED'


def test_independent_boxes_scaled_canvas_and_nonwhite_paper(tmp_path):
    ref = strips(tmp_path/'ref.png', [.5,.2])
    drawing = strips(tmp_path/'draw.png', [.2,.2,.4,.4],height=16,paper=230)
    paper = strips(tmp_path/'paper.png', [0]*4,height=16,paper=230)
    p = [TonalPatch('a',(1,0,2,8),(0,0,1,8)), TonalPatch('b',(0,0,1,8),(1,0,2,8))]
    r = compare_tonal_patches(ref,drawing,paper,p,output_scale=2)
    assert r['patches'][0]['drawing']['pixels'] == 32
    assert r['patches'][0]['drawing']['mean_darkness'] == pytest.approx(.2, abs=1/255)
    assert r['patches'][1]['drawing']['mean_darkness'] == pytest.approx(.4, abs=1/255)
    assert r['adjacent_relations'][0]['reference_relation'] == 'darker'
    assert r['adjacent_relations'][0]['drawing_relation'] == 'darker'


@pytest.mark.parametrize('patches,scale,deadband', [
    ([TonalPatch('one',(0,0,1,1),(0,0,1,1))],1,.03),
    ([TonalPatch('same',(0,0,1,1),(0,0,1,1))]*2,1,.03),
    ([TonalPatch('out',(0,0,1,1),(0,0,9,1)),TonalPatch('b',(1,0,2,1),(1,0,2,1))],1,.03),
    ([TonalPatch('empty',(0,0,.1,.1),(0,0,1,1)),TonalPatch('b',(1,0,2,1),(1,0,2,1))],1,.03),
    ([TonalPatch('a',(0,0,1,1),(0,0,1,1)),TonalPatch('b',(1,0,2,1),(1,0,2,1))],0,.03),
    ([TonalPatch('a',(0,0,1,1),(0,0,1,1)),TonalPatch('b',(1,0,2,1),(1,0,2,1))],1,float('nan')),
])
def test_invalid_patch_inputs_fail_closed(tmp_path,patches,scale,deadband):
    p=strips(tmp_path/'a.png',[0,0,0,0])
    with pytest.raises(ValueError):
        compare_tonal_patches(p,p,p,patches,output_scale=scale,deadband=deadband)


def test_canonical_patches_cached_and_read_only(tmp_path):
    ref=tmp_path/'ref.png'; Image.new('RGB',(32,32),'white').save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',intent=DrawingIntent(drawing_mode='croquis'),
        render_profile=RenderProfile.from_dict({**RenderProfile.canonical(32,32).to_dict(),'supersample':2,'output_scale':2}))
    oid=s.observe({'test':'visible patch comparison'})
    paper=s.render_at(0,tmp_path/'blank.png')
    s.draw([(8,5),(8,28)],part='test',role='contour',tool_overrides={'width':5,'pressure':.8,'opacity':.8},observation_id=oid)
    final=s.render_final(tmp_path/'final.png')
    patches=[TonalPatch('a',(5,5,11,28),(5,5,11,28)),TonalPatch('b',(18,5,24,28),(18,5,24,28))]
    cp=s.checkpoint_path.read_bytes(); before=s.drawing_state_hash()
    a=inspect_tonal_patches(s,patches,cursors=[0,1]); b=inspect_tonal_patches(s,patches,cursors=[0,1],cached_renders={0:paper.path,1:final.path})
    assert a['results']==b['results']; assert b['evidence_binding']=='canonical_session'
    assert b['results'][1]['patches'][0]['drawing']['mean_darkness']>b['results'][1]['patches'][1]['drawing']['mean_darkness']
    assert s.checkpoint_path.read_bytes()==cp and s.drawing_state_hash()==before
    with pytest.raises(ValueError): inspect_tonal_patches(s,patches,cursors=[1,1])
    with pytest.raises(ValueError,match='invalid cached canonical render'): inspect_tonal_patches(s,patches,cached_renders={1:paper.path})
