# A4 — Residual routing-edge hardening

Updated: 2026-09-03
Status: **CLOSED**

## Problem

The instruction graph already contained strong individual leaves, but the routing between
visible symptoms and their responsible premises was too implicit. A worker could correctly
notice “the foot is wrong” yet still spend marks in `figure/legs-feet.md` when the actual
cause was the parent leg chain or ground relation.

A4 makes those conditional edges explicit without introducing a new runtime state machine or
a sequential drawing lifecycle.

## Durable rule

The deployed instruction surface now routes by cause rather than by the noun that appears
wrong:

```text
visible residual
→ name the broken relationship
→ decide whether the parent premise is credible
→ local owning leaf when genuinely bounded
→ upstream construction / observation / contact / environment when symptomatic
→ mutate drawing
→ inspect fresh render
```

The key operational question is:

`what relationship would have to become true for this residual to disappear?`

## Deployable changes

`skills/img2drawing/references/review/residual-routing.md` is the progressive-disclosure
routing leaf. It contains compact conditional routes for:

- foot/shoe;
- head/face;
- hand/grip;
- props;
- silhouette/overlap;
- clothing/folds;
- grounding/environment;
- value/tonal residuals.

Each route distinguishes local geometry from parent structure, contact/overlap, ground
relation, and observation uncertainty where applicable.

`SKILL.md`, `references/INDEX.md`, and `review/residual-correction.md` now point workers to
that leaf when the visible part may only be a symptom. The index remains a compact routing
table rather than becoming a diagnostic encyclopedia.

## Escalation signals

The deployed guide explicitly treats the following as reasons to move upstream:

- the same local residual survives a deliberate local correction;
- neighboring parts fail in one coherent direction;
- fixing one endpoint breaks the other endpoint of the same relation;
- contact cannot become credible without moving the parent chain or mass;
- a local contour requires invented geometry to connect;
- texture, tone, or extra strokes would only conceal the mismatch.

This is scope correction inside the existing drawing loop, not a stage reset.

## Representative routing proof

The foot example now resolves into four distinct owners:

```text
foot looks wrong
├─ leg chain / stance / support → construction/balance-and-limbs
├─ ground plane / contact       → environment/ground-and-context
├─ local foot / shoe geometry  → figure/legs-feet
└─ overlap/contact ownership    → description/contour-and-overlap
```

Equivalent cause-based edges exist for head/face, hand/grip, props, folds, silhouette, and
value residuals.

## Mechanical guard

`dev/tests/test_skill_surface_boundary.py` now verifies that:

- the new routing leaf is part of the deployable review surface;
- the skill and index expose it through progressive disclosure;
- representative local and upstream destinations are present;
- the routing language explicitly rejects noun-only routing and stage-reset semantics;
- no development/release control-plane terminology leaks into the skill-facing documents.

Mechanical verification does not prove drawing quality. It proves the instruction graph now
contains the intended operational edges before fresh visual dogfood.

## Closure

A4 is CLOSED because the instruction surface can now answer both questions:

1. which smallest leaf owns a genuinely local residual?
2. when should that residual escalate to a parent premise instead?

No runtime/API/schema/render contract changed, and no fresh D01–D06 quality claim is made.

## Next

A5 should add only high-value missing drawing guidance that cannot be expressed cleanly by
existing leaves. Hands/grip and foreshortening remain the leading candidates; this work must
stay evidence-backed and compact rather than expanding into an anatomy encyclopedia.
