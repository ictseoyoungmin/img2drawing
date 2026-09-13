# G02 broad-pencil v11 dogfood

Date: 2026-09-13
Candidate base: `bcc931c79a4c4cf799aec3a5265d21145bfb546b`
Renderer under review: `pillow-pencil-contact-v11 / 1`
Verdict: **PASS / CLOSED for the reported broad-pencil failure class**

## User-observed failure

Thick pencil work exposed two defects that were hard to see in earlier thin-line drawings:

1. transitional broad strokes could end as a blunt rectangular/butt cut;
2. the broad interior could read as a flat digital ribbon with weak graphite/paper tooth.

The defect was reproduced against explicit v10 and localized to the broad authored-value continuity core. v10's radial shoulder was already physical; the high-alpha core could still dominate the terminal and flatten the material read.

## Candidate behavior

v11 is additive and does not mutate v9/v10 replay semantics.

- ordinary thin strokes delegate to v10 byte-for-byte;
- broad continuity cores add pressure-resolved round physical contact at the two terminals;
- broad material modulation uses deterministic page-fixed tooth plus micro-grain;
- local modulation is mean-normalized so stronger texture does not silently re-author average value;
- canonical final and fast timelapse share the registered v11 patch builder.

## Mechanical evidence

`dev/tests/test_v103_broad_pencil_material.py` locks:

- 2 px v10↔v11 thin pixel exactness;
- 8 px terminal graphite extending behind the authored endpoint while body mean value stays within 4%;
- 14 px broad-core local material variation increasing over v10 while mean value stays within 4%.

`dev/tests/test_v103_renderer_policy.py` locks current v11 selection, explicit v9/v10 replay, material-policy pixel differentiation, and v11 canonical-final ↔ fast-final pixel exactness including late lower-layer recomposition.

The final rc3 branch, PR-triggered CI, and post-merge `main` CI all passed active tests, frozen historical checks, package/install verification, and the immutable v1.0.2 history gate.

## Real drawing dogfood

A fresh hand-authored line/gesture study was made from the current character reference using the same `StrokeIR` for v10 and v11. The study deliberately mixed ordinary 1.9 px structure lines with 6–10 px broad marks on hair, jacket, sleeve, shorts, stockings, boots, rifle, and sparse environment strokes. No reference pixels were copied into the drawing.

A second high-pressure stress pass used 9–14 px strokes, opacity 0.80–0.90, `dry-graphite-expressive`, strict value authority, and zero authored taper so terminal morphology could not hide behind a taper.

Observed result:

- **terminal morphology:** v11 removes the visible square/butt core termination. Jacket, waist, leg, hair, and rifle endpoints round into the physical contact footprint rather than ending on a hard perpendicular cut;
- **graphite/tooth:** v11 broad cores show more local dark/light tooth breakup under both ordinary and heavy passes instead of reading as one flat band;
- **thin structure:** ordinary thin contours remain visually unchanged, consistent with the byte-exact regression gate;
- **value authority:** the material becomes more textured without an obvious global darkening or washout in the drawing-scale comparison.

## Local review artifact hashes

These artifacts were generated during the stable-promotion review; the hashes preserve provenance even though the binary review boards are not committed to the repository.

```text
real_dogfood_v10.png              2f4c7cf704d7489d2ce63d00baf50687f4a8ec76be20852187df8f0c3a8634aa
real_dogfood_v11.png              f3aa52476d166ea2cf1c7f3a44dfd976c9a50a952a468d221c1a072205e16ab6
real_dogfood_review_board.png     bb143b9f707b4a9a3bce1820d39123c69a72ceb4c7002b8fcab6c1adb4e7c4f8
endpoint_pixel_zoom.png           69e2509ad4779f8ffb8238166ee68156c9c9f91364722827f3b19ec0739c25a9
heavy_graphite_v10.png            983642c0ed062fa1efc8105e08f27073fe5bd8396a2fe6672f99ea92034ef1b7
heavy_graphite_v11.png            a2826741850f4599b5a4524e6d617930f8724288349696079ce6ee4988cdedc3
heavy_graphite_review_board.png   da036121558bbf2f44cf1c1b76a4c237f6d35114546ba2fcf891f5b445a5de5a
heavy_graphite_endpoint_zoom.png  5bd92f33d4e4b54dce203d79f2e1c57ab93e6415b29593f0746f3145540b79a5
```

## Promotion consequence

G02 no longer blocks stable promotion. Together with G01 gesture dogfood, v11 canonical/fast exactness, explicit v9/v10 replay preservation, full package CI, and the stable-wheel verification gate, this evidence supports choosing **v1.0.3 stable** rather than another RC.
