# Full-body croquis

Harden stages sequentially. Never sweep P1→P5 in one unreviewed pass.

Use `img2drawing.render.pillow_pencil_contact` for ordinary croquis renders, comparisons,
replay, final export and timelapse. No legacy Pillow fallback exists.

## P1
Settle how the subject stands: head position and tilt, spine and torso rhythm, shoulder and
pelvis tilt, the direction each limb travels through its joint centres, where the feet meet
the ground, and which way each foot points. Use exactly one centre path per limb; do not
add torso or garment boundary lines. No single construction line should overpower the
rest. When a large attached object changes balance or silhouette, add its
major axis too.

Nothing else. Clothing, hair, face and muscle belong downstream.

Compare subject ↔ drawing for pose, balance and proportion, and judge stage scope against
the frozen contract and `references/stages/p1-gesture.md`.

Keep P1 open while any major pose, balance or proportion mismatch remains. Once P1 is self-reviewed as closed, begin P2 without waiting for user confirmation.

## P2–P5
Repeat the same autonomous hardening protocol. If a later stage exposes a P1/P2/P3/P4 foundation error, reopen the earliest responsible stage instead of compensating downstream.
