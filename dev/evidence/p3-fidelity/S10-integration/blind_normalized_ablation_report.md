# S10 normalized A/B/C blind visual comparison (pre-binding run)

## Method and scope

This comparison used only the subject raster and three final drawing rasters.
The evaluator did not consult run metadata, reports, scripts, stage rationales,
exemplar verdicts, or prior findings. The candidates were treated as A, Bn, and
Cn only from their supplied paths.

Important implementation qualification: the original Cn runner serialized its
modular cards to metadata but did not bind them to the `DrawingRun` action path.
This remains a valid image-only description of those rasters, but it is **not**
a valid estimate of modular-card visual effect.

## Overall verdict

**A is strongest, but still `REVISE`. Bn and Cn remain generic figure studies
rather than recognizable drawings of this subject.**

A retains the largest portion of the identity bundle: an angular bob-like head
silhouette, eyes/nose/mouth marks, an angled side/back torso, a visible sleeve,
tactical jacket/strap/patch/pocket cues, shorts and thigh-mounted object, heavy
boots, and a diagonal long-weapon silhouette. It is still not a close likeness:
the head is oversized and helmet-like, the facial construction is minimal, the
arm is simplified, and the rifle is not resolved into recognizable components.

Bn adds face/bang-like marks, a collar indication, and sparse garment marks, but
the head remains circular and generic while the torso reads as a frontal
capsule. Cn is nearly the same generic construction; its additional lines do
not create a recognizable bob, tactical outfit, near-arm volume, or rifle
topology.

## Region comparison

| Region | A | Bn | Cn | Earliest residual |
|---|---|---|---|---|
| Head / hair / face | Angular bob-like outline, bangs, eyes, nose, mouth; proportions and turn remain wrong. | Circular/hood-like head with a few face marks; no convincing bob. | Circular generic head; hair and face are less readable than A. | P1/P2 head direction; P3 head/hair mass; P5 features only after mass closure. |
| Torso orientation | Angled side/back envelope, but shoulder asymmetry is weak. | Large rounded frontal capsule. | Same capsule; no stronger turn. | P1/P2 torso/shoulder axes; P3 torso mass. |
| Near arm | Visible broad-ish sleeve, but flat and without clear hand volume. | Thin hanging contour, unlike the subject's exposed arm. | Same thin arm. | P2 near-arm exposure; P3 envelope/station widths. |
| Pelvis / legs | Shorts, pockets, thigh cues and stance survive, but remain schematic. | Generic shorts and straight legs; no clear holster/stocking transition. | Same generic lower body. | P3 pelvis/leg asymmetry; P4 segmentation. |
| Tactical clothing | Jacket, straps, patch/pockets and thigh object are suggested. | Sparse marks without coherent tactical identity. | Sparse lines without coherent identity. | P3 clothing separation; P4/P5 garment details. |
| Boots | Heavy silhouettes with soles/toes, still simplified. | Polygonal wedges with limited construction. | Similar wedges; no gain. | P3 boot mass; P4/P5 construction. |
| Rifle topology / overlap | Diagonal axis and several masses, but scope/receiver/sling/stock order is incomplete. | Thin bent rod without component sequence. | Darker continuous rod, still without rifle topology. | P2 prop axis; P3 topology; P4 occlusion/connection. |
| Overall likeness | Simplified tactical/sniper figure with several subject cues. | Generic person with an object, not this subject. | Generic person with an object, not this subject. | P1/P2 observation/orientation, then P3 mass closure. |

## Bn versus Cn under equal detail budget

Both normalized conditions contain exactly 82 identity-role actions. The rasters
show no visible Cn improvement over Bn, but this is not attributable to cards:
the Cn cards were not runtime-bound, and the two runs share most of the same
hard-coded subject-derived scaffold. Bn may have slightly clearer sparse
face/bang/collar marks; Cn's more prominent long-object lines do not improve
identification.

This equal-budget result is a useful single-sample outcome check, not proof of
statistical causality. Replicated runs or a matched-stroke controlled study are
still needed to claim that the condition itself caused the observed gap. Because
Cn did not receive its intended runtime treatment, the cautious conclusion is
only: **A is visibly better; the modular-card effect is unresolved.**

## Post-run binding verification

The corrected C runner was executed separately at
`drawings/s10-ablation/C_modular_grammar_cards_bound_v2/`. All 166 authored
draw/replace actions carry the stage card ID (P1 10, P2 10, P3 27, P4 16, P5
103), all nine worker packets carry the current card, and checkpoint/session/
review-manifest persistence is enabled. Its final SHA256 is identical to Cn's
because this slice adds provenance enforcement; it does not rewrite the
hard-coded geometry plan. A new card-driven stroke-plan run is required before
making a visual causal claim.

That card-driven run is now recorded at
`drawings/s10-ablation/C_modular_grammar_cards_card_driven/`. It consumed all
166 stage-bound cards in the stroke plan, kept all 166 point arrays equal to the
bound-v2 control, and changed only line material; its final SHA is
`80534c5043c3257dbd00f5183c563f545a22b1a98b280b177c40631e4c5b2788`. This is a
runtime-consumption proof and a raster-effect measurement, not yet a likeness
claim: the matched B replay and independent blind comparison are still pending.

## Earliest blockers and decision

- Earliest blocker: P1/P2 failed to preserve the back-three-quarter torso,
  over-shoulder head direction, exposed near-arm side, and rifle axis.
- Next blocker: P3 did not close head/hair shape, torso/near-arm/pelvis masses,
  or rifle topology.
- Later blocker: P4/P5 must preserve eyes/nose/mouth, bob/bangs, tactical
  garment grammar, thigh/holster details, rifle component/occlusion, and boots.

The visual gate remains `REVISE`. Mechanical `ADVANCE` and equal action budgets
must not be treated as subject-fidelity proof unless the complete identity
bundle is visibly retained in the final raster.
