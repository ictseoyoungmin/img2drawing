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
- an open neck connection from the jaw into the clavicle, keeping the head attached without
  turning the cue into the measured P2 neck axis;
- the pelvis centreline and its tilt;
- the shoulder line and its tilt;
- shoulder, elbow, wrist, hip, knee and ankle centres;
- the curvature of each limb between those joints;
- any limb hidden behind clothing or a prop;
- where the feet meet the ground and which way each foot points;
- the overall silhouette envelope;
- the major axis of a large attached object.

Leave out: facial features beyond the centreline and eye-line, hair, garment structure,
muscle, closed volume, prop detail, and footwear detail.

## One centre-path curve per limb by default

Start each arm and leg with one flowing curve through its shoulder/elbow/wrist or
hip/knee/ankle centres. This states direction and curvature without inventing thickness.
Do not bracket a limb with two lines merely because two garment edges are visible; that
turns P1 into a sleeve, trouser or tube drawing.

A second light cue is optional only when a single curve cannot explain an observed
curvature reversal or a necessary silhouette-envelope fact. It stays subordinate, must
not simply trace the opposite clothing edge, and its distance from the centre-path curve
has no metric meaning.

The P2 handoff is explicit: preserve the P1 pose hypothesis, centrelines, curvature intent
and joint evidence, but recompute separately from the subject:

- shoulder -> elbow -> wrist and hip -> knee -> ankle measurement axes;
- each segment's length and foreshortening;
- the neck axis;
- turned ribcage and pelvis axis boxes; and
- hand and foot placement blocks, including occluded ones.

P2 must derive every axis and volume measurement fresh from the subject rather than from
the placement of any optional secondary P1 cue.

## An early stage is not a faint stage

P1 construction is not a whisper. In a completed run the principal face, spine and limb
flows sat around **HB/B** at pressure 0.52–0.62, width 2.2–2.65 and opacity 0.64–0.80;
secondary envelope cues sat lighter, and only the ground cue dropped to 2H at
0.36 / 1.7 / 0.42.

Two things follow:

- **The pencil grade decides more than the numbers.** A 2H stroke at high pressure still
  renders pale. Use B sparingly for the clearest directional accents, HB for readable
  construction, and 2H only for cues you want to recede. Do not make the spine a black
  centre pole.
- **Judge on the raw render.** If P1 is only readable with the contrast turned up, it is
  too faint to review — and the stages built on it will inherit that.

`canvas_scale_guidance` reports a floor per stage. It is a floor, not a target.

## Compare on the raw render, and overlay

Two comparisons, both on the unmodified render:

1. the drawing as rendered, beside the subject;
2. the drawing as if it were on translucent paper laid over the subject.

The overlay is what catches registration error. A drawing that looks plausible alone will
show its crown, joint centres and foot landings sitting off the subject the moment it is
laid on top. Never judge P1 without it.

## Never drop a primitive in for an observed shape

The head is not an ellipse and a foot is not an oval. Reaching for a generic shape because
the stage requires *something* there is the same failure as copying an example's
coordinates: it produces a P1 that satisfies the checklist and describes a different person.

A symmetric ellipse cannot say that this head is tilted slightly down and turned slightly
to one side. It will say whatever its rotation angle happens to say — usually the wrong
thing — and the drawing then reads as someone looking off in a direction the subject is not
looking.

Read the actual shape instead:

- **Head**: its width, where the jaw turns, where the chin sits relative to the cranium's
  midline, and how much cranium the tilt exposes. A head tilted down shows more cranium and
  its eye line sits lower and dips in the middle; a head tilted up does the reverse. The
  eye line is where the tilt becomes visible — get it wrong and the whole face turns.
- **Feet**: each shoe has a direction and a foreshortening. A foot pointing across the body
  is a narrow wedge; one pointing toward the viewer is a short blunt shape. Two identical
  ovals say neither.

## Feet belong in P1

A foot is not a late detail. Which way each foot points states body direction, where the
weight sits and where the figure is going — the same information the shoulders and pelvis
carry. A pair of ankles ending in nothing leaves that unsaid, and downstream stages then
invent it.

What belongs here is the foot's **direction and shape**, linked to the ankle and sitting on
the ground mark. Sole detail, laces and panels are P4's.

## The head decides the drawing

Get the head right first. Crown position, the curvature of the facial centreline, where it
passes the nose, and the direction it exits toward the chin — a small error in any of these
makes the whole figure read as a different pose even when the body is close.

### Both head lines are defined by features, not by the outline

This is where a plausible-looking head goes wrong most often. The outline is drawn, and
then the cross is placed on the *outline's* midpoint instead of on the face.

- **The facial centreline must pass through the nose.** Mark crown, the point between the
  eyes, the nose, the mouth and the chin on the subject, then run the line through them.
  A centreline a few pixels beside the nose turns the face the other way, and no amount of
  correct outline rescues it.
- **The eye line must connect both eyes.** Find each pupil on the subject and draw through
  the two of them. Its tilt is then whatever those two positions give you. An eye line
  drawn level because level looks tidy will say the head is upright when it is not.

Both lines run past the eyes and the nose to the head's edges, curving as they wrap the
form — but they are anchored on the features, not fitted to the silhouette.

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

## Measure the landmarks; do not read them off the picture by eye

Eyeballing a landmark produces errors that are individually small, all in the same
direction, and invisible until the drawing is laid over the subject. Anchor each landmark
on something you can actually locate:

- **the crotch** — where the two legs separate. The hip joints sit just above it. The
  **waistband is not the hip joint**; it is the iliac crest, and it is far higher.
- **the visible hand** — bare skin below a sleeve. That is the wrist, not the point where
  the sleeve ends.
- **the jean hem or sock line** — the ankle. The shoe below it is the foot.
- **the two pupils and the nose** — the eye line and the facial centreline.
- **the shoe outline** — foot direction.

Then derive what is hidden: the elbow sits between the located shoulder and the located
wrist; the knee between the located hip and the located ankle.

Clothing hides the body, and its edges are the trap: **a sleeve edge is not the arm axis, a
waistband is not the hip, a hair silhouette is not the cranium.** Each of those substitutes
a garment landmark for an anatomical one, and each puts the drawing systematically wrong.

## Joint centres must be accurate, not approximate

A few pixels of error per joint is not harmless. When several joints drift the *same*
direction, the errors accumulate and the whole figure reads as shifted to one side. Check
joints against the subject individually, then check whether they share a drift.

Sketch curved forms as curves, not corners — a head, a joint, a shoe or a limb should only
show a corner where the subject actually has one.

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

1. Head: crown; mark both pupils and the nose on the subject; run the eye line through the
   pupils and the centreline through the nose; then the outline around them.
2. Spine S-curve from behind the neck.
3. Shoulder and pelvis lines with their rotation.
4. Joint centres, checked individually and then for shared drift.
5. Limb flow lines following observed curvature.
6. Occluded limbs, inferred.
7. Foot ovals, their direction, and ground contact.
8. Silhouette envelope and any major prop axis.
9. Whole overlay sweep against the success criterion.
