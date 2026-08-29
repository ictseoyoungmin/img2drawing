import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from img2drawing import DrawingRun
run=DrawingRun.resume(PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run")
r=run.submit_stage_review(
 contract_findings=[
  "The artifact stays inside gesture_and_weight_path: no ribcage/pelvis mass contour, no limb thickness, no clothing contour, no facial features.",
  "The slung rifle is present only as a single major axis, which the contract allows because the prop changes the global envelope.",
 ],
 subject_findings=[
  "The subject is a back-three-quarter standing figure: the torso faces away and toward image-right, and the head is turned further right so the right ear sits image-left of the facial mass.",
  "The subject's facial centre bows clearly toward image-right between the crown and the chin; that bow is the only carrier of face direction at this abstraction.",
  "The subject's weight sits on the far image-left leg, which runs almost vertically under the pelvis, while the near image-right leg is braced outward and lands lower and wider in frame.",
  "The subject's rifle axis runs from an upper-left suppressor tip down to a buttstock at the image-left hip, roughly 74 degrees from horizontal.",
 ],
 exemplar_findings=[
  "The bundled P1 grammar exemplar carries a KNOWN GRAMMAR EXEMPLAR DEFECT (neck-origin gesture, near-closed oval head, no distinct counterbalance) and was used only as a reminder of stroke economy.",
  "No exemplar pose, coordinate, or proportion was imported; all geometry came from the subject photograph.",
 ],
 drawing_findings=[
  "Whole-view evidence shows the entire drawing is far too faint: the dominant gesture is not materially stronger than the subordinate construction, so no line hierarchy exists at all.",
  "In the head_face local crop the crown arc and the two temporal-jaw arcs visually close into a single continuous egg/badge; the required gaps between crown and side arcs are not readable.",
  "In the head_face local crop the facial centre segment reads as an almost straight vertical bisection, so the drawing communicates no face-direction information.",
  "In the pelvis_legs local crop the pelvis-to-support transfer reads as a hard angular kink rather than a curved handoff of weight.",
  "In the pelvis_legs local crop the counterbalance leg is so faint it barely registers, so support versus counterbalance is not yet unambiguous.",
  "Overall proportions (head height, shoulder span, pelvis breadth, leg length, landing points) agree with the subject and do not need reworking.",
 ],
 local_review_ids=["P1_gesture:pass_01:head_face","P1_gesture:pass_01:pelvis_legs"],
 corrections=[],
 remaining_concerns=[
  "whole drawing is too faint and has no dominant-gesture hierarchy",
  "head envelope closes into a badge instead of segmented open arcs",
  "facial centre is too straight to carry face direction",
  "pelvis-to-support transfer is an angular kink rather than a weight-bearing curve",
  "counterbalance leg is too weak to read as a distinct role",
 ],
 decision="revise")
print(r.decision, r.digest()[:12])
