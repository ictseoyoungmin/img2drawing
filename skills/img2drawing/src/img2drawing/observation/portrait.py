"""Explicit face-local comparison; no detection, alignment solver or artistic score."""
from __future__ import annotations

from collections.abc import Mapping
import math

from ..inspection import Measurement, Registration
from .landmarks import LandmarkSet, compare_landmarks, compare_ratios
from .spatial import compare_axes


def compare_portrait_landmarks(reference: LandmarkSet, drawing: LandmarkSet, *,
                               registration: Registration, labels,
                               width_axis, height_axis=None) -> Measurement:
    """Reuse registered point distances, normalized by a declared local face span.

    Width is the primary normalizer. Height and diagonal are optional additional
    context, never inferred from the width. No alignment or correspondence is fitted.
    """
    labels = tuple(labels) if not isinstance(labels, str) else labels
    width = compare_landmarks(reference, drawing, registration=registration,
                              labels=labels, normalizer=width_axis)
    span = width.value['normalizer_length_canvas']
    height = (None if height_axis is None else compare_landmarks(
        reference, drawing, registration=registration, labels=labels,
        normalizer=height_axis).value['normalizer_length_canvas'])
    diag = None if height is None else math.hypot(span, height)
    rows = []
    for item in width.value['landmarks']:
        row = dict(item)
        row['normalized_by_width'] = row['normalized_distance']
        row['normalized_by_height'] = None if height is None else row['distance']/height
        row['normalized_by_diagonal'] = None if diag is None else row['distance']/diag
        rows.append(row)
    return Measurement('portrait_landmark_comparison', {
        'landmarks': rows, 'normalized_rms_width': width.value['normalized_rms'],
        'normalized_rms_height': None if height is None else width.value['normalized_rms']*span/height,
        'normalized_rms_diagonal': None if diag is None else width.value['normalized_rms']*span/diag,
        'largest_mismatch': max(rows, key=lambda x:x['distance']),
        'portrait_scale_canvas': {'width':span,'height':height,'diagonal':diag},
    }, 'canvas', {'labels':list(labels),'width_axis':list(width_axis),
                  'height_axis':None if height_axis is None else list(height_axis),
                  'registration':registration.to_dict()},
        {'operation':'explicit portrait-local landmark comparison','inference':False,
         'artistic_verdict':'NOT_EVALUATED'})


def portrait_likeness_packet(reference: LandmarkSet, drawing: LandmarkSet, *,
                             registration: Registration, feature_labels,
                             width_axis, height_axis=None, feature_groups=None,
                             ratio_checks=(), axis_checks=()) -> Measurement:
    """Group explicitly visible local points; preserve ratio/axis inputs and values.

    Groups may share anchors, but no aggregate weighting or quality threshold is
    applied. The caller chooses which evidence is actually observed and readable.
    """
    feature_labels = tuple(feature_labels) if not isinstance(feature_labels,str) else feature_labels
    width_axis = tuple(width_axis) if not isinstance(width_axis,str) else width_axis
    height_axis = (None if height_axis is None else tuple(height_axis) if not isinstance(height_axis,str) else height_axis)
    landmarks = compare_portrait_landmarks(reference,drawing,registration=registration,
                   labels=feature_labels,width_axis=width_axis,height_axis=height_axis)
    groups = {} if feature_groups is None else feature_groups
    if not isinstance(groups,Mapping) or len(groups)>32:
        raise ValueError('feature_groups requires at most 32 named groups')
    by_name = {row['name']:row for row in landmarks.value['landmarks']}
    results={}
    for name, selected in groups.items():
        if not isinstance(name,str) or not name.strip() or isinstance(selected,str):
            raise ValueError('named group requires explicit landmark labels')
        selected=tuple(selected)
        if not selected or len(set(selected))!=len(selected) or any(x not in by_name for x in selected):
            raise ValueError('group must select unique measured landmarks')
        rows=[by_name[x] for x in selected]
        results[name]={'labels':list(selected),'normalized_rms_width':math.sqrt(
            math.fsum(row['normalized_by_width']**2 for row in rows)/len(rows)),
            'largest_mismatch':max(rows,key=lambda row:row['distance'])}
    ratios=[compare_ratios(reference,drawing,registration=registration,numerator=a,denominator=b).to_dict()
            for a,b in ratio_checks]
    axes=[compare_axes(reference,drawing,registration=registration,axis=a).to_dict() for a in axis_checks]
    return Measurement('portrait_likeness_packet', {'landmarks':landmarks.value,'groups':results,
            'ratios':ratios,'axes':axes},'canvas',landmarks.inputs,
            {'operation':'explicit face-local evidence packet','inference':False,'artistic_verdict':'NOT_EVALUATED'})
