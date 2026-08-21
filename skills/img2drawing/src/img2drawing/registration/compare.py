from __future__ import annotations

from dataclasses import dataclass
import json, math
from importlib.resources import files
from typing import Mapping

from .grid import GridSpec, segment_cells
from .model import RegistrationGraph


class RegistrationIntegrityError(ValueError):
    pass


@dataclass(frozen=True)
class ComparisonProfile:
    landmark_delta_hint: float = 0.025
    segment_similarity_hint: float = 0.65
    roi_padding_cells: int = 1

    @classmethod
    def packaged(cls) -> "ComparisonProfile":
        raw=json.loads(files("img2drawing.data").joinpath("registration_profile.json").read_text(encoding="utf-8"))
        return cls(**raw["comparison"])


@dataclass(frozen=True)
class ComparisonIntegrity:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    reference_surface: str
    drawing_surface: str
    distinct_observation_ids: bool
    distinct_source_artifacts: bool
    exact_coordinate_clone_fraction: float

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "reference_surface": self.reference_surface,
            "drawing_surface": self.drawing_surface,
            "distinct_observation_ids": self.distinct_observation_ids,
            "distinct_source_artifacts": self.distinct_source_artifacts,
            "exact_coordinate_clone_fraction": self.exact_coordinate_clone_fraction,
        }


@dataclass(frozen=True)
class LandmarkDelta:
    name:str; du:float; dv:float; distance:float; uncertainty_sum:float; outside_uncertainty:bool; hint:bool
    def to_dict(self)->dict:
        return self.__dict__.copy()


@dataclass(frozen=True)
class SegmentDelta:
    connection_id:str; reference_cells:tuple[str,...]; drawing_cells:tuple[str,...]; similarity:float; changed_cells:tuple[str,...]; hint:bool
    def to_dict(self)->dict:
        return {"connection_id":self.connection_id,"reference_cells":list(self.reference_cells),"drawing_cells":list(self.drawing_cells),"similarity":self.similarity,"changed_cells":list(self.changed_cells),"hint":self.hint}


@dataclass(frozen=True)
class ROIProposal:
    id:str; bounds:tuple[float,float,float,float]; cells:tuple[str,...]; reasons:tuple[str,...]
    def to_dict(self)->dict:
        return {"id":self.id,"bounds":list(self.bounds),"cells":list(self.cells),"reasons":list(self.reasons),"authority":"review_hint_only"}


@dataclass(frozen=True)
class StructuralComparison:
    landmark_deltas:tuple[LandmarkDelta,...]
    segment_deltas:tuple[SegmentDelta,...]
    roi_proposals:tuple[ROIProposal,...]
    grid:GridSpec
    integrity: ComparisonIntegrity

    def to_dict(self)->dict:
        return {
            "schema":"img2drawing.structural_comparison.v2",
            "authority":"evidence_not_pass_fail",
            "integrity": self.integrity.to_dict(),
            "grid":self.grid.to_dict(),
            "landmark_deltas":[v.to_dict() for v in self.landmark_deltas],
            "segment_deltas":[v.to_dict() for v in self.segment_deltas],
            "roi_proposals":[v.to_dict() for v in self.roi_proposals],
        }


def _edge_map(graph:RegistrationGraph):
    return {e.id:e for e in graph.connections}


def _connected_components(cells:set[tuple[int,int]])->list[set[tuple[int,int]]]:
    out=[]
    while cells:
        seed=cells.pop(); comp={seed}; stack=[seed]
        while stack:
            c,r=stack.pop()
            for n in ((c-1,r),(c+1,r),(c,r-1),(c,r+1)):
                if n in cells:
                    cells.remove(n); comp.add(n); stack.append(n)
        out.append(comp)
    return out


def validate_comparison_integrity(reference: RegistrationGraph, drawing: RegistrationGraph) -> ComparisonIntegrity:
    reference.validated(); drawing.validated()
    errors: list[str] = []
    warnings: list[str] = []

    if reference.source_surface != "reference":
        errors.append("reference graph must be bound to source_surface='reference'")
    if drawing.source_surface != "drawing":
        errors.append("drawing graph must be bound to source_surface='drawing'")

    distinct_obs = bool(reference.observation_id and drawing.observation_id and reference.observation_id != drawing.observation_id)
    if not reference.observation_id or not drawing.observation_id:
        errors.append("both graphs require explicit observation_id provenance")
    elif not distinct_obs:
        errors.append("reference and drawing registrations must use distinct observation_id values")

    distinct_artifacts = bool(
        reference.source_artifact_sha256 and drawing.source_artifact_sha256
        and reference.source_artifact_sha256 != drawing.source_artifact_sha256
    )
    if not reference.source_artifact_sha256 or not drawing.source_artifact_sha256:
        errors.append("both graphs require source_artifact_sha256 provenance")
    elif not distinct_artifacts:
        errors.append("reference and drawing registrations must be bound to distinct rendered artifacts")

    common = sorted(set(reference.landmarks) & set(drawing.landmarks))
    exact = 0
    for name in common:
        a=reference.landmark(name); b=drawing.landmark(name)
        if abs(a.u-b.u) <= 1e-12 and abs(a.v-b.v) <= 1e-12:
            exact += 1
    clone_fraction = 0.0 if not common else exact / len(common)
    if common and clone_fraction >= 0.80:
        warnings.append(
            "most common landmark coordinates are exactly identical; independently re-observe the drawing instead of copying reference coordinates"
        )

    return ComparisonIntegrity(
        valid=not errors,
        errors=tuple(errors), warnings=tuple(warnings),
        reference_surface=reference.source_surface, drawing_surface=drawing.source_surface,
        distinct_observation_ids=distinct_obs, distinct_source_artifacts=distinct_artifacts,
        exact_coordinate_clone_fraction=float(clone_fraction),
    )


def compare_registrations(
    reference:RegistrationGraph,
    drawing:RegistrationGraph,
    *,
    grid:GridSpec|None=None,
    profile:ComparisonProfile|None=None,
    require_independent: bool = False,
)->StructuralComparison:
    reference.validated(); drawing.validated(); grid=(grid or GridSpec()).validated(); profile=profile or ComparisonProfile.packaged()
    integrity = validate_comparison_integrity(reference, drawing)
    if require_independent and not integrity.valid:
        raise RegistrationIntegrityError("; ".join(integrity.errors))

    landmark=[]; flagged_cells:set[tuple[int,int]]=set(); reasons_by_cell:dict[tuple[int,int],set[str]]={}
    for name in sorted(set(reference.landmarks)&set(drawing.landmarks)):
        a=reference.landmark(name); b=drawing.landmark(name)
        du=b.u-a.u; dv=b.v-a.v; dist=math.hypot(du,dv); unc=a.uncertainty_radius+b.uncertainty_radius
        hint=dist>=profile.landmark_delta_hint and dist>unc
        landmark.append(LandmarkDelta(name,du,dv,dist,unc,dist>unc,hint))
        if hint:
            for p in ((a.u,a.v),(b.u,b.v)):
                cr=grid.cell_of(*p)
                if cr is not None: flagged_cells.add(cr); reasons_by_cell.setdefault(cr,set()).add(f"landmark:{name}")
    ref_edges=_edge_map(reference); drw_edges=_edge_map(drawing); segment=[]
    for eid in sorted(set(ref_edges)&set(drw_edges)):
        re=ref_edges[eid]; de=drw_edges[eid]
        ra=reference.landmark(re.a); rb=reference.landmark(re.b); da=drawing.landmark(de.a); db=drawing.landmark(de.b)
        rc=segment_cells((ra.u,ra.v),(rb.u,rb.v),grid); dc=segment_cells((da.u,da.v),(db.u,db.v),grid)
        union=set(rc)|set(dc); inter=set(rc)&set(dc); sim=1.0 if not union else len(inter)/len(union)
        changed=tuple(sorted(union-inter)); hint=sim<profile.segment_similarity_hint
        segment.append(SegmentDelta(eid,rc,dc,sim,changed,hint))
        if hint:
            for label in changed:
                for c in range(grid.columns):
                    for r in range(grid.rows):
                        if grid.label(c,r)==label:
                            flagged_cells.add((c,r)); reasons_by_cell.setdefault((c,r),set()).add(f"segment:{eid}")
    proposals=[]
    for i,comp in enumerate(_connected_components(set(flagged_cells)),1):
        pad=max(0,int(profile.roi_padding_cells)); minc=max(0,min(c for c,_ in comp)-pad); maxc=min(grid.columns-1,max(c for c,_ in comp)+pad); minr=max(0,min(r for _,r in comp)-pad); maxr=min(grid.rows-1,max(r for _,r in comp)+pad)
        b0=grid.cell_bounds(minc,minr); b1=grid.cell_bounds(maxc,maxr)
        allcells=tuple(grid.label(c,r) for c,r in sorted(comp,key=lambda x:(x[1],x[0])))
        reasons=sorted({reason for cr in comp for reason in reasons_by_cell.get(cr,())})
        proposals.append(ROIProposal(f"roi-{i:02d}",(b0[0],b0[1],b1[2],b1[3]),allcells,tuple(reasons)))
    return StructuralComparison(tuple(landmark),tuple(segment),tuple(proposals),grid,integrity)
