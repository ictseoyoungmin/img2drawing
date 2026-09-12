# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap describes the **current unreleased main/RC state after v1.0.2**. Older A/B/D/R plans remain historical evidence; they do not override this sequence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 absorbed general authoring ergonomics from successful explicit-stroke dogfood.
- v1.0.2 promoted the exact local-first timelapse backend.
- Post-v1.0.2 source cleanup physically retired the R23 runtime/legacy cluster from current `src`.
- Post-v1.0.2 instruction hardening added cause-based residual routing, dynamic instruction-graph reachability, explicit observation-id correction provenance, and pure/constructive gesture modes.
- Renderer parity work closed inspect/current-state ↔ final/replay divergence for v10 while preserving frozen v9 replay behavior.
- Renderer v10, markmaking runtime discovery, broad-graphite value authority, and renderer-aware fast timelapse were promoted into the `1.0.3rc1 / A11` candidate.
- RC1 promotion evidence passed same-environment width×3 v9/v10 comparison plus canonical/fast pixel exactness.
- PR #40 integrated `1.0.3rc1` into `main`; post-merge main CI was green.
- G01 rc1 fresh dogfood reopened gesture integration after exposing a public runtime-mode mismatch and a generic rounded-mass failure. These findings did not invalidate the closed renderer/timelapse evidence.
- `1.0.3rc2 / A12` repairs the gesture runtime vocabulary, anti-primitive/anti-blob instruction contract, and semantic markmaking preset adapter.
- G01 same-reference pure + constructive fresh-session dogfood is **PASS/CLOSED for the target failure class**. Reference-supported roundness is preserved; orientationless/attachment-free stock primitives are rejected.
- No `1.0.3rc1` or `1.0.3rc2` publish manifest exists, so v1.0.2 remains the latest published stable release.

## Current sequence

```text
G02 broad-pencil material/terminal hardening
  ↓
G03 integrate validated rc2/corrective candidate into main
  ↓
G04 stable-promotion decision: v1.0.3 vs another RC
  ↓
G05 explicit stable freeze + publish manifest
  ↓
G06 publish only if all current contracts and release notes agree
```

### G01 — gesture behavior validation — CLOSED

G01 covered two user-facing cases against the same reference:

1. explicit quick/pure gesture;
2. unqualified `gesture drawing`, which defaults to constructive gesture.

The rc1 run found:

- `DrawingIntent(drawing_mode="gesture")` was not accepted by the runtime;
- anti-faceted guidance could overcorrect into generic smooth beans/ovals/capsules;
- semantic markmaking preset IDs such as `gesture-flow` could be mistaken for literal low-level
  `session.draw(tool=...)` values.

The rc2 corrective slice:

- adds `gesture` to the public drawing-intent vocabulary and a public `ModeGuide` without creating a workflow stage;
- requires subject-specific facing/asymmetry/attachment evidence instead of geometric or rounded stock icons;
- explicitly allows reference-supported roundness, so the worker does not invent corners merely to prove a form is non-primitive;
- documents and tests `resolve_mark_for_intent()` / `ResolvedMark.draw_kwargs()` as the semantic-preset → runtime-tool adapter;
- leaves the rc1 renderer/timelapse implementation unchanged.

Intermediate dogfood passes that still read as coarse polyline construction, circle-head shorthand,
or closed pelvis blobs were rejected. The final reviewed pass preserves head facing, arm/leg chains,
support, rifle overlap, hip-to-leg attachment, and a stronger constructive near/far read without
invented faceting. The bounded evidence record is
`../../dogfood/g01-gesture-rc2/README.md`.

This closure does not claim production croquis quality or cross-agent/cross-subject generalization.

### G02 — broad-pencil material and terminal quality — NEXT

The next highest-impact open problem was already visible in thick-line dogfood: broad pencil strokes
can read too much like a digital ribbon. At larger widths:

- graphite/tooth variation is too weak;
- stroke interiors can become too uniformly opaque;
- start/end terminals can appear blunt or square;
- simply increasing width does not produce a convincing broad-pencil contact/release.

Open a focused deterministic renderer slice before stable promotion. The intended loop is:

```text
broad-stroke reproduction fixture
→ inspect terminal geometry + graphite/tooth distribution
→ locate smallest v10 owner
→ repair terminal taper/contact material
→ canonical/fast exactness
→ thin-line non-regression
→ width×3/broad visual QA
```

Do not modify frozen v9 replay behavior. If the v10 renderer/timelapse implementation changes, the
existing rc1 promotion evidence no longer mechanically covers those changed bytes and the affected
parity/performance evidence must be renewed.

### G03 — candidate integration

After the broad-pencil gate is closed, integrate the validated corrective candidate into `main`
through a PR with full CI. Do not create an RC/stable publish manifest merely because the candidate
is present on main.

### G04 — stable-promotion decision

Use the closed renderer parity/performance evidence, G01 gesture dogfood, broad-pencil quality gate,
and final mechanical verification to decide whether the next artifact is stable `1.0.3` or another
release candidate.

Deprecated pre-0.6.0rc2 root shims remain intentionally separate from the R23 retirement. Their
removal requires an explicit compatibility decision and must not be bundled silently into stable
promotion.

### G05 — stable freeze and publish preparation

Only after choosing stable promotion:

- create a new immutable v1.0.3 contract freeze rather than editing `v1.0.2-A10`;
- create an explicit stable publish manifest;
- update stable release notes/support metadata to the chosen stable identity;
- rerun full active tests, current-runtime isolation, dynamic instruction-graph reachability, package/sdist/wheel audit, clean install, replay/timelapse parity, promotion-evidence verification, and frozen-history verification;
- verify built wheel metadata and hashes before publication.

### G06 — publish

Publish only from the explicit stable manifest after every current-facing document, package identity,
release note, and mechanical gate agrees. The immutable v1.0.2 tag, release notes, publish manifest,
and historical freeze remain unchanged.

## Later / optional

- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- add representative teaching examples only when they are good enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- rc2 candidate notes: `../../../docs/releases/v1.0.3rc2.md`;
- rc1 integrated notes: `../../../docs/releases/v1.0.3rc1.md`;
- rc1 renderer promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- unreleased changes and known issues: `../../../CHANGELOG.md`;
- deployable behavior: `../../../skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `../../../docs/releases/v1.0.2.md`;
- immutable released contract: `../../release/vnext/CONTRACT_FREEZE.json`.
