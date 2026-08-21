from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence

from .model import RegistrationGraph


def column_label(index: int) -> str:
    value = int(index) + 1
    out = ""
    while value:
        value, rem = divmod(value - 1, 26)
        out = chr(65 + rem) + out
    return out


@dataclass(frozen=True)
class GridSpec:
    columns: int = 10
    rows: int = 10
    bounds: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)

    def validated(self) -> "GridSpec":
        if not (1 <= int(self.columns) <= 64 and 1 <= int(self.rows) <= 64):
            raise ValueError("grid dimensions must be in [1,64]")
        u0, v0, u1, v1 = map(float, self.bounds)
        if not (0 <= u0 < u1 <= 1 and 0 <= v0 < v1 <= 1):
            raise ValueError("grid bounds must be ordered inside [0,1]")
        return self

    def label(self, col: int, row: int) -> str:
        return f"{column_label(col)}{row+1}"

    def cell_of(self, u: float, v: float) -> tuple[int, int] | None:
        self.validated(); u0,v0,u1,v1 = self.bounds
        if not (u0 <= u <= u1 and v0 <= v <= v1):
            return None
        fu = (u-u0)/(u1-u0); fv = (v-v0)/(v1-v0)
        col = min(self.columns-1, max(0, int(fu*self.columns)))
        row = min(self.rows-1, max(0, int(fv*self.rows)))
        return col,row

    def cell_bounds(self, col: int, row: int) -> tuple[float,float,float,float]:
        self.validated()
        if not (0 <= col < self.columns and 0 <= row < self.rows):
            raise IndexError("grid cell out of range")
        u0,v0,u1,v1=self.bounds
        du=(u1-u0)/self.columns; dv=(v1-v0)/self.rows
        return u0+col*du, v0+row*dv, u0+(col+1)*du, v0+(row+1)*dv

    def to_dict(self) -> dict:
        return {"columns": self.columns, "rows": self.rows, "bounds": list(self.bounds)}


@dataclass(frozen=True)
class CellOccupancy:
    cell: str
    col: int
    row: int
    node_names: tuple[str,...] = ()
    segment_ids: tuple[str,...] = ()
    uncertain_landmarks: tuple[str,...] = ()
    roi_ids: tuple[str,...] = ()

    @property
    def classes(self) -> tuple[str,...]:
        out=[]
        if len(self.node_names) > 1: out.append("M")
        elif len(self.node_names) == 1: out.append("N")
        elif self.segment_ids: out.append("E")
        if self.uncertain_landmarks: out.append("U")
        if self.roi_ids: out.append("R")
        return tuple(out) or (".",)

    def to_dict(self) -> dict:
        return {"cell":self.cell,"col":self.col,"row":self.row,"classes":list(self.classes),
                "node_names":list(self.node_names),"segment_ids":list(self.segment_ids),
                "uncertain_landmarks":list(self.uncertain_landmarks),"roi_ids":list(self.roi_ids)}


def segment_cells(a: tuple[float,float], b: tuple[float,float], grid: GridSpec) -> tuple[str,...]:
    """Exact-ish normalized line/grid traversal via parametric grid-boundary intersections."""
    grid.validated(); u0,v0,u1,v1=grid.bounds
    ax,ay=a; bx,by=b
    ts={0.0,1.0}
    dx=bx-ax; dy=by-ay
    if abs(dx)>1e-12:
        for i in range(1,grid.columns):
            x=u0+(u1-u0)*i/grid.columns
            t=(x-ax)/dx
            if 0 < t < 1: ts.add(float(t))
    if abs(dy)>1e-12:
        for i in range(1,grid.rows):
            y=v0+(v1-v0)*i/grid.rows
            t=(y-ay)/dy
            if 0 < t < 1: ts.add(float(t))
    ordered=sorted(ts)
    probes=[ordered[0],ordered[-1]]
    probes += [(a+b)/2 for a,b in zip(ordered,ordered[1:])]
    cells=[]
    for t in sorted(probes):
        x=ax+dx*t; y=ay+dy*t
        cr=grid.cell_of(x,y)
        if cr is None: continue
        label=grid.label(*cr)
        if label not in cells: cells.append(label)
    return tuple(cells)


def _circle_intersects_rect(u:float,v:float,r:float,bounds:tuple[float,float,float,float])->bool:
    x0,y0,x1,y1=bounds
    cx=min(max(u,x0),x1); cy=min(max(v,y0),y1)
    return (u-cx)**2+(v-cy)**2 <= r*r + 1e-15


def build_cell_occupancy(
    graph: RegistrationGraph, grid: GridSpec, *, rois: Mapping[str, Sequence[float]] | None = None,
) -> dict[str, CellOccupancy]:
    graph.validated(); grid.validated(); rois=dict(rois or {})
    nodes: dict[str,list[str]]={}; segments:dict[str,list[str]]={}; uncertain:dict[str,list[str]]={}; roi_cells:dict[str,list[str]]={}
    for name,lm in graph.landmarks.items():
        cr=grid.cell_of(lm.u,lm.v)
        if cr is not None: nodes.setdefault(grid.label(*cr),[]).append(name)
        if lm.uncertainty_radius>0:
            for c in range(grid.columns):
                for r in range(grid.rows):
                    if _circle_intersects_rect(lm.u,lm.v,lm.uncertainty_radius,grid.cell_bounds(c,r)):
                        uncertain.setdefault(grid.label(c,r),[]).append(name)
    for edge in graph.connections:
        a=graph.landmark(edge.a); b=graph.landmark(edge.b)
        for cell in segment_cells((a.u,a.v),(b.u,b.v),grid):
            segments.setdefault(cell,[]).append(edge.id)
    for roi_id, raw in rois.items():
        x0,y0,x1,y1=map(float,raw)
        for c in range(grid.columns):
            for r in range(grid.rows):
                a0,b0,a1,b1=grid.cell_bounds(c,r)
                if max(x0,a0) < min(x1,a1) and max(y0,b0) < min(y1,b1):
                    roi_cells.setdefault(grid.label(c,r),[]).append(str(roi_id))
    out={}
    labels=set(nodes)|set(segments)|set(uncertain)|set(roi_cells)
    for c in range(grid.columns):
        for r in range(grid.rows):
            label=grid.label(c,r)
            if label not in labels: continue
            out[label]=CellOccupancy(label,c,r,tuple(sorted(nodes.get(label,()))),tuple(sorted(segments.get(label,()))),tuple(sorted(uncertain.get(label,()))),tuple(sorted(roi_cells.get(label,()))))
    return out
