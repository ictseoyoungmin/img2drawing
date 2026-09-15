# Visual observation

Observe in the order `whole → relation → part → relation again`.

## Whole

Identify the dominant action, occupied area, support, balance, major silhouette, large
negative spaces, head/ribcage/pelvis relation, and important object axes.

For an observed figure, also ask whether the pose is turned, twisted, compressed, or asymmetric
in ways that a simple silhouette could flatten. Do not treat a plausible outer contour as proof
that the spatial pose has been understood.

When an important form is partly hidden, include the occlusion in the whole read. Ask what owns
the foreground edge, what disappears, whether it reappears, and whether the visible arrangement
requires continuity through the hidden interval. Do not decide that a chain, mass, or connected
part simply terminates because its contour is no longer visible.

## Strong perspective: propagate depth through the whole

When the camera/view is strongly foreshortened, identify coarse depth groups before local finish:

```text
near
mid
far
```

Do not infer exact 3D distance when the reference does not support it. The groups exist to make
relative projection explicit.

For each important connected chain, compare where visible:

- projected anchor spacing;
- apparent width changes;
- overlap order;
- near/far exposure;
- terminal orientation;
- continuity through occlusion.

A large near head or hand is not, by itself, evidence that perspective is solved. If torso,
pelvis, limbs, feet, or props remain flat/diagrammatic, classify that as an upstream depth residual.

## Relations

Compare rather than naming isolated parts:
- shoulder tilt against pelvis tilt;
- head turn against ribcage turn and ribcage turn against pelvis turn;
- near/far shoulder and near/far hip prominence;
- projected centerline or cross-axis direction across each major mass;
- exposed front/side/top plane changes where they are actually visible;
- head width against ribcage width;
- elbow/wrist positions against torso landmarks;
- stance width against pelvis width;
- foot direction against leg direction and ground;
- prop axis against hands, body planes, and overlap order;
- entry direction before an occluder against reappearance direction after it when both are visible;
- visible width/taper before disappearance against visible width/taper after reappearance;
- hidden-continuity plausibility against nearby anchors, contact, and occlusion order.

A useful orientation observation distinguishes **tilt** from **turn**. Two masses may share a
similar screen-space tilt while facing different directions in depth. Likewise, a shoulder line
can look plausible while the ribcage beneath it has been flattened toward frontal symmetry.

## Parts

Only then inspect the part that owns a residual. Read its curvature, width changes, overlap,
contact, internal landmarks, and uncertainty. A part is not observed merely because its
category is known.

Before accepting a local semantic group, identify a small set of neighboring anchors — usually
2–5 are enough — that constrain its placement, scale, direction, overlap, or contact. A local line
that cannot be checked against neighboring evidence is still a hypothesis, not a resolved part.

For an occluded part, separate what is visible from what must only be inferred. Record the last
visible anchor before disappearance, the first visible reappearance when present, local direction
or tangent, nearby width/taper, foreground ownership, and any visible contact/attachment cue.
Those observations may constrain a hidden structural hypothesis; they do not reveal the exact
hidden contour or terminal.

## Plausibility conflict check

When a readable part appears anatomically unusual, stylized, distorted, mirrored, compressed, or
otherwise contrary to expectation, treat the disagreement as a reason to **inspect more carefully**,
not as permission to normalize the drawing.

Use a local crop plus neighboring anchors to ask:

- does the visible silhouette support the surprising relation?
- do overlap and negative space support it?
- does the terminal orientation agree with the connected chain?
- is the apparent oddity explained by perspective, stylization, occlusion, or pose?

If the visible evidence remains coherent, preserve it even when category knowledge suggests a more
conventional anatomy or design. Anatomy and object knowledge may disprove an impossible hidden
hypothesis, but they may not overwrite a readable visible projection. When evidence is genuinely
ambiguous, preserve uncertainty or gather better evidence rather than silently replacing the part
with a familiar template.

For familiar or named subjects, do the same with identity: the supplied reference instance outranks
memory of a canonical hairstyle, face, costume, accessory, or pose.

## Relation again

Return to the whole after every local correction. A locally attractive head, hand, fold, or
shoe is still wrong if it breaks scale, rhythm, balance, orientation, twist, or the subject's
silhouette.

Ask whether the whole became **more specific or merely busier**. If new lines improve local
recognition but make the subject more generic, flatter, more parallel, or more symmetric, the
correction failed at the parent relation.

If several local parts become simultaneously cleaner but the whole pose becomes more frontal,
parallel, or symmetric than the subject, classify that as an upstream orientation residual rather
than local progress. Route to `../construction/orientation-and-twist.md`.

Likewise, if a visible part downstream of an occluder drifts because the hidden interval was
ignored, do not patch only the visible endpoint. Route to `../foundation/occlusion-inference.md`,
re-read both sides of the overlap, and revise the parent continuity hypothesis.

Use `../review/visual-quality-gates.md` when a local group is about to be accepted or when the
whole/local relationship remains ambiguous.

Evidence tools can enlarge or measure what is visible. The Agent remains responsible for
interpreting the result. Do not invent exact 3D angles when the reference only supports a
relative near/far or turn judgment. Do not claim an exact hidden path when the reference only
supports continuity, topology, or a coarse direction/depth relation.
