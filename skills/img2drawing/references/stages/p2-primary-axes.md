# P2 Primary Axes — measured segments

**The question this stage answers: how long is each bone, and how is it turned?**

P1 already placed the joints and read each limb's curvature. P2 does not re-place them. It
turns that flow into **measured structure**: segment length, foreshortening, and the
ribcage and pelvis volumes a mannequin needs.

### P1 handoff: flow is not thickness

P1's limb curves are gesture-flow evidence, not measurement axes or width. Preserve the P1
joint evidence and pose direction, then measure fresh against the subject.
P2 authors its own shoulder -> elbow -> wrist and hip -> knee -> ankle axes, segment
lengths and foreshortening, neck axis, turned ribcage/pelvis boxes, and hand/foot blocks.
If a P1 joint is proven wrong, correct that joint explicitly and reopen P1 rather than
silently making a compensating P2 volume.

### P1 line handoff

P1 lines can be correct gesture evidence without remaining visible forever. When a P2
axis or placement block takes over the same visible job, keep the P1 line faint with
`soft_lift` only if it still explains pose rhythm or weight. If it creates a duplicate
read or the P2 representation must stand alone, retire the complete P1 stroke with the
public `delete_stroke` action. This preserves the P1 artifact and history; it does not
rewrite what P1 established. In particular, a P2 foot block may replace a P1 foot
direction mark when the visible result must show one shoe placement, not two outlines.

## What P2 states
- the length of each limb segment, measured against the subject;
- foreshortening of each segment;
- the neck axis;
- the ribcage centre axis and how the ribcage box is turned;
- the pelvis axis and how the pelvis box is turned;
- hand and foot placement blocks;
- any P1 joint the measured chain proves was misplaced;
- the attached object's length and tilt against the body.

## How much to draw
Limb segments as measured straight or lightly cylindrical axes. Ribcage and pelvis as axis
volumes. Simple placement blocks for hands and feet.

Here — unlike P1 — a straight segment is correct. P1 observed curvature; P2 measures the
span it covers.

A large prop is a **measuring axis**: its length and tilt against the body, not a described
object.

## Common failures
- **Comfortable proportion.** Drawing a segment the length it "should" be instead of the
  length the subject shows.
- **Ignoring foreshortening.** A forearm coming toward the viewer is short. Draw it short.
- **Untwisted boxes.** A ribcage box facing front when the subject's torso is turned.
- **Moving a joint for convenience.** Correcting a P1 joint is allowed when the subject
  says so; it is not a way to make the drawing easier.
- **Forgetting an occluded hand.** If P1 inferred a hand in a pocket, P2 gives it a block.
- **Treating P1 flow as a measured axis.** Derive P2 axes and boxes independently from the
  subject rather than treating the P1 centre path as measured width or segment geometry.
- **Losing P1.** If the axes measure well but the pose hypothesis drifted, reopen P1
  instead of compensating here.

## Hardening order
1. Preserve the P1 centrelines, pose rhythm and joint centres.
2. Neck axis.
3. Ribcage box and its turn.
4. Pelvis box and its turn.
5. Arm segment lengths and foreshortening.
6. Leg segment lengths and foreshortening.
7. Hand and foot blocks, occluded ones included.
8. Prop axis measured against the body.

## Useful local review intents
`neck+ribcage`, `ribcage+pelvis boxes`, `shoulder→elbow→wrist`, `hip→knee→ankle`,
`hand blocks`, `object against the torso`.
