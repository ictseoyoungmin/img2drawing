"""Face-local evidence cannot be hidden by whole-figure normalization."""
import pytest
from img2drawing.observation import (Landmark, LandmarkSet, compare_landmarks,
    compare_portrait_landmarks, portrait_likeness_packet)
from img2drawing.inspection import Registration
from img2drawing.runtime import runtime_capabilities


def points(space='subject', delta=0., visibility='observed', scale=1.):
    coords={'left':(10,50),'right':(70,50),'crown':(40,10),'chin':(40,90),
            'left-eye':(27+delta,42),'right-eye':(53,44),'nose':(42,58),
            'left-mouth':(29,70),'right-mouth':(51,71),'head':(40,0),'feet':(40,1000)}
    return LandmarkSet(space,(int(100*scale),int(1100*scale)),tuple(
        Landmark(k,tuple(v*scale for v in pos),'explicit fixture',visibility if k=='left-eye' else 'observed') for k,pos in coords.items()))


def packet(r,d,reg=None,**kw):
    args=dict(registration=reg or Registration.identity(r.size),feature_labels=('left-eye','right-eye','nose','left-mouth','right-mouth'),
              width_axis=('left','right'),height_axis=('crown','chin'),
              feature_groups={'eyes':('left-eye','right-eye'),'mouth':('left-mouth','right-mouth')},
              ratio_checks=((('left-eye','right-eye'),('left','right')),),axis_checks=(('left-mouth','right-mouth'),))
    args.update(kw)
    return portrait_likeness_packet(r,d,**args)


def test_local_scale_not_diluted_by_figure():
    r,d=points(),points('canvas',delta=3)
    q=packet(r,d).value
    full=compare_landmarks(r,d,registration=Registration.identity(r.size),labels=['left-eye'],normalizer=['head','feet'])
    assert full.value['normalized_rms']==pytest.approx(.003)
    assert q['landmarks']['largest_mismatch']['normalized_by_width']==pytest.approx(.05)
    assert q['groups']['eyes']['normalized_rms_width']==pytest.approx(.05/2**.5)
    assert q['groups']['mouth']['normalized_rms_width']==0
    assert q['landmarks']['portrait_scale_canvas']=={'width':60.,'height':80.,'diagonal':100.}
    assert q['ratios'][0]['inputs']['numerator']==['left-eye','right-eye']
    assert q['axes'][0]['inputs']['axis']==['left-mouth','right-mouth']


def test_no_invented_height_and_no_verdict():
    r,d=points(),points('canvas',delta=3)
    q=packet(r,d,height_axis=None)
    assert q.value['landmarks']['normalized_rms_diagonal'] is None
    assert q.value['landmarks']['portrait_scale_canvas']['height'] is None
    assert q.provenance['artistic_verdict']=='NOT_EVALUATED'
    assert q.provenance['inference'] is False


def test_registered_scale_invariant():
    r,d=points(),points('canvas',delta=3,scale=2)
    a=packet(r,points('canvas',delta=3)).value
    b=packet(r,d,Registration(r.size,d.size,scale=(2,2))).value
    assert a['landmarks']['normalized_rms_width']==pytest.approx(b['landmarks']['normalized_rms_width'])
    assert b['landmarks']['largest_mismatch']['distance']==6


@pytest.mark.parametrize('kwargs',[{'feature_groups':{'bad':('absent',)}},{'feature_groups':{'bad':('nose','nose')}}, {'feature_groups':{'bad':'nose'}},{'feature_labels':('nose','nose')},{'width_axis':('left','left')},{'height_axis':('chin','chin')}])
def test_bad_evidence_fails_closed(kwargs):
    with pytest.raises(ValueError):packet(points(),points('canvas'),**kwargs)


def test_uncertain_not_measured():
    with pytest.raises(ValueError,match='not an observed landmark'):packet(points(visibility='uncertain'),points('canvas'))


def test_readonly_discovery():
    assert 'img2drawing.observation.portrait_likeness_packet' in runtime_capabilities().observation_helpers
    r,d=points(),points('canvas')
    snap=r.to_dict(),d.to_dict();q=packet(r,d);assert q.value['landmarks']['normalized_rms_width']==0
    assert snap==(r.to_dict(),d.to_dict())
