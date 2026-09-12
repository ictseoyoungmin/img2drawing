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
- G01 rc1 fresh-worker dogfood then **reopened** gesture integration after exposing a public runtime-mode mismatch and a generic rounded-mass failure. These findings do not invalidate the closed renderer/timelapse evidence.
- No `1.0.3rc1` or `1.0.3rc2` publish manifest exists, so v1.0.2 remains the latest published stable release.

## Current sequence

```text
G01-R2 mechanical rc2 verification
  ↓
G01-R3 same-reference fresh-worker gesture dogfood
  ↓
G02 stable-promotion decision: v1.0.3 vs another RC
  ↓
G03 explicit stable freeze + publish manifest
  ↓
G04 publish only if all current contracts and release notes agree
```

### G01-R2 — 1.0.3rc2 gesture integration repair

The rc1 dogfood found two reusable defects:

1. `DrawingIntent(drawing_mode="gesture")` was rejected although gesture is a user-facing skill mode;
2. anti-faceted guidance could overcorrect into smooth generic bean/oval/capsule masses that remained mannequin-like.

The rc2 corrective slice therefore:

- adds `gesture` to the public drawing-intent vocabulary and a public `ModeGuide` without creating a workflow stage;
- strengthens head, ribcage, and pelvis guidance around observed asymmetry and attachment relations;
- treats both hard geometric icons **and** stock rounded blobs as unfinished shorthand;
- leaves the rc1 renderer/timelapse implementation byte-identical so its promotion evidence remains authoritative for that subsystem.

Mechanical closure requires current-doc, runtime, instruction-graph, full active suite, package/install, and frozen-history gates to pass under package identity `1.0.3rc2 / A12`.

### G01-R3 — gesture behavior validation

After mechanical rc2 verification, rerun the same two fresh-worker cases against the same reference:

1. explicit quick/pure gesture;
2. unqualified `gesture drawing`, which must default to constructive gesture.

Reject a result that:

- stops at isolated construction or omits major limb/support relations;
- leaves an orientationless or nearly generic circle-head despite readable profile/jaw/nape information;
- replaces faceted torso/pelvis masses with smooth stock beans, ovals, eggs, or capsules;
- loses observed shoulder/back/hip asymmetry, taper, near/far relation, or leg-attachment direction;
- reads as a generic mannequin rather than this subject's specific pose.

Only actual visual evidence can close G01.

### G02 — stable-promotion decision

Use the rc2 fresh dogfood plus the already closed rc1 renderer evidence and rc2 mechanical verification to decide whether the next artifact is stable `1.0.3` or another release candidate.

Do not repeat already-closed renderer parity or performance work unless the measured renderer/timelapse paths change. If new dogfood exposes another reusable runtime or instruction-graph defect, reopen only the responsible owner.

Deprecated pre-0.6.0rc2 root shims remain intentionally separate from the R23 retirement. Their removal requires an explicit compatibility decision and must not be bundled silently into stable promotion.

### G03 — stable freeze and publish preparation

Only after choosing stable promotion:

- create a new immutable v1.0.3 contract freeze rather than editing `v1.0.2-A10`;
- create an explicit stable publish manifest;
- update stable release notes/support metadata to the chosen stable identity;
- rerun full active tests, current-runtime isolation, dynamic instruction-graph reachability, package/sdist/wheel audit, clean install, replay/timelapse parity, promotion-evidence verification, and frozen-history verification;
- verify built wheel metadata and hashes before publication.

### G04 — publish

Publish only from the explicit stable manifest after every current-facing document, package identity, release note, and mechanical gate agrees. The immutable v1.0.2 tag, release notes, publish manifest, and historical freeze remain unchanged.

## Later / optional

- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- improve semantic markmaking preset/runtime discovery if future dogfood shows workers confusing semantic preset names with low-level `tool=` names;
- add representative teaching examples only when they are good enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- rc2 candidate notes: `../../../docs/releases/v1.0.3rc2.md`;
- rc1 integrated notes: `../../../docs/releases/v1.0.3rc1.md`;
- rc1 renderer promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- unreleased changes and known issues: `../../../CHANGELOG.md`;
- deployable behavior: `../../../skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `../../../docs/releases/v1.0.2.md`;
- immutable released contract: `../../release/vnext/CONTRACT_FREEZE.json`.
