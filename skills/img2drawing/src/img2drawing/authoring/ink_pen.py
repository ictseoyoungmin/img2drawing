"""Public pen authoring: explicit geometry to existing typed ink actions."""
from __future__ import annotations

from ..core.pen import PenDefinition


def g_pen(controls, *, pressure_knots, max_width, min_width=0., gamma=1.3,
          geometry="polyline", start_cap="round", end_cap="round", join="round",
          paint="black", curve_tolerance=.05, width_tolerance=.05, miter_limit=4.):
    """Author pressure-driven opaque ink; width is in logical canvas pixels."""
    return PenDefinition("g-pen",geometry,controls,pressure_knots,min_width,max_width,gamma,
                         start_cap,end_cap,join,paint,curve_tolerance,width_tolerance,miter_limit)


def fineliner(controls, *, width, geometry="polyline", paint="black",
              curve_tolerance=.05, cap="round", join="round", miter_limit=4.):
    """Author a constant-width fineliner with explicit join and cap."""
    return PenDefinition("fineliner",geometry,controls,((0.,1.),(1.,1.)),width,width,
                         1.,cap,cap,join,paint,curve_tolerance,.05,miter_limit)


def ink_brush(controls, *, pressure_knots, max_width, min_width=0., gamma=1.,
              geometry="polyline", start_cap="round", end_cap="round", paint="black",
              curve_tolerance=.05, width_tolerance=.05):
    """Continuous opaque wet-ink brush with authored contact diameter and tip.

    Uses the same swept-disk kernel as round pens, not a dry-brush texture or
    a simulated fluid. Pressure controls contact width only. Point tips require
    explicit zero endpoint pressure and a sufficiently long taper.
    """
    return PenDefinition("ink-brush",geometry,controls,pressure_knots,min_width,max_width,
                         gamma,start_cap,end_cap,"round",paint,curve_tolerance,width_tolerance)


def read_pen_definition(session, element_id):
    """Recover the current authored recipe, never stale or inferred controls."""
    with session._lock:
        records=session.authored_elements(element_type="ink",status="current")
        record=next((r for r in records if r.element_id==element_id),None)
        if record is None:
            raise ValueError("pen definition requires a current ink element")
        action=session._agent.history.actions[record.latest_seq-1]
        raw=(action.provenance or {}).get("pen_definition")
        if raw is None:
            raise ValueError("no current pen definition")
        recipe=PenDefinition.from_dict(raw)
        element=next(e for e in session.current_ir().ink_elements if e.element_id==element_id)
        if recipe.resolve()!=element.mark:
            raise ValueError("pen definition does not reproduce current resolved geometry")
        return recipe


__all__=["PenDefinition","g_pen","fineliner","ink_brush","read_pen_definition"]
