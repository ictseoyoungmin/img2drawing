# P1 Gesture — the whole-body pose hypothesis

**The question this stage answers: how is this person standing?**

P1 is not "a few simple lines". It is a pose hypothesis for the entire figure, and its
quality is decided almost entirely by whether the first few construction lines read the
subject's real 3D pose. Adding more lines does not rescue a wrong reading.

`p1-construction.png` beside this file annotates a subject with exactly these lines,
colour-coded and labelled. Open it before drawing a P1.

## The success criterion

Lay the subject underneath at low opacity and put only P1 on top. Head direction, spine
curvature, shoulder and pelvis rotation, both arms, both legs' joint centres and the
landing direction of the feet must all register against the subject, and **no part may feel
like "roughly around here."**

Then hide the subject. The test is not *"that looks like a person."* It is:

> **"That is this specific person in this specific pose."**

## What P1 states

- crown position, and a **curved** facial centreline running crown → nose → chin;
- head tilt, via an eye-line cross;
- the **spine centreline** as an S-curve: behind the neck → mid-back → waist → sacrum;
- the pelvis centreline and its tilt;
- the shoulder line and its tilt;
- the **line of action**, which is a different line from the spine;
- shoulder, elbow, wrist, hip, knee and ankle centres;
- the curvature of each limb between those joints;
- any limb hidden behind clothing or a prop;
- where the feet meet the ground and which way each foot points;
- the overall silhouette envelope;
- the major axis of a large attached object.

Leave out: facial features beyond the centreline and eye-line, hair, garment structure,
muscle, closed volume, prop detail, and footwear detail.

## Feet belong in P1

Draw each foot as **one simple oval linked to its ankle**, sitting on the ground mark.

A foot is not a late detail. Which way each foot points states body direction, where the
weight sits and where the figure is going — the same information the shoulders and pelvis
carry. A pair of ankles ending in nothing leaves that unsaid, and downstream stages then
invent it.

What belongs here is the **direction**, not the shoe: one oval per foot, angled the way the
subject's foot is angled, with a short link from the ankle circle. Sole shape, laces and
panels are P4's.

## The head decides the drawing

Get the head right first. Crown position, the curvature of the facial centreline, where it
passes the nose, and the direction it exits toward the chin — a small error in any of these
makes the whole figure read as a different pose even when the body is close.

Two failures degrade it immediately:

- **reading the hair silhouette as the cranial outline.** Hair volume is P4's. The cranium
  is underneath it and is usually smaller and differently placed than the hair suggests.
- **drawing the facial centreline as a plain vertical centre line.** A straight centre line
  carries no face rotation. The line must curve across the head's surface.

## Face centreline and spine centreline are two strokes

Trying to solve both with one line breaks the drawing.

- **crown → nose → chin** explains where the *face* is turned.
- **behind the neck → spine → pelvis** explains the *body's* gesture. It starts at the back
  of the neck, following the cervical C-curve — never straight down from the chin.

Draw them as separate strokes. Their visual rhythm should still flow into each other.

## The line of action is not the spine

The spine is an anatomical S-curve inside the torso. The line of action is the whole
figure's energy: it typically enters above the head, cuts diagonally across the body, and
lands ahead of the weight-bearing foot. Both belong in P1, and they are different lines.

## Joint centres must be accurate, not approximate

A few pixels of error per joint is not harmless. When several joints drift the *same*
direction, the errors accumulate and the whole figure reads as shifted to one side. Check
joints against the subject individually, then check whether they share a drift.

## Never join joints with straight lines

Correct joint positions connected by straight `shoulder → elbow → wrist` and
`hip → knee → ankle` segments produce a flat wire dummy. What is actually needed is to
observe each span's **tangent and its convex/concave changes** — the curvature itself is
information about the pose.

Measured straight segments are P2's job. P1's limb lines flow.

## Occluded limbs stay in

Dropping a limb because it is hidden — an arm behind a rifle, a hand in a pocket — breaks
the pose. Shoulder rhythm and torso twist are then read wrong.

State a minimum gesture for the hidden limb, inferred from the visible shoulder/elbow/wrist
evidence and from how the body connects. End the flow line where the hidden hand or foot
must be.

## The example is grammar, never coordinates

`pipeline-overview.png` shows how a P1 is drawn. It does not show where *this* subject's
joints are. Following an example too closely produces a P1 that resembles the example and
does not match the subject.

## Filters assist; they never decide

Orientation fields, gradients and LoG help observe crown and hair flow and large
boundaries. Moving a line to fit a filter can invert a correct decision. **Raw subject plus
overlay is always the final authority.**

## Revise on failure, not on a count

The most common wasted loop is "I revised three times, so it must be better." It is not a
count. If the overlay shows the crown, the nose pass, a joint centre, or the spine position
wrong, the stage is FAIL — however many passes have happened.

## Preserve what is right; discard what is wrong

Two opposite failures:

- redrawing everything because of a small error, and losing a correct structure;
- nudging conservatively when the structure is actually wrong, and preserving the error.

Decide which one you are in before editing. A micro error is a local correction; a wrong
structural reading needs the structure replaced.

## Hardening order

1. Head: crown, facial centreline curvature, nose pass, chin exit, eye-line tilt.
2. Spine S-curve from behind the neck.
3. Shoulder and pelvis lines with their rotation.
4. Line of action across the whole figure.
5. Joint centres, checked individually and then for shared drift.
6. Limb flow lines following observed curvature.
7. Occluded limbs, inferred.
8. Foot ovals, their direction, and ground contact.
9. Silhouette envelope and any major prop axis.
10. Whole overlay sweep against the success criterion.
