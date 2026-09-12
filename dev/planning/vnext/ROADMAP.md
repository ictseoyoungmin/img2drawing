# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap describes the **current unreleased main state after v1.0.2**. Older A/B/D/R plans remain historical evidence; they do not override this sequence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 absorbed general authoring ergonomics from successful explicit-stroke dogfood.
- v1.0.2 promoted the exact local-first timelapse backend.
- Post-v1.0.2 source cleanup physically retired the R23 runtime/legacy cluster from current `src`.
- Post-v1.0.2 instruction hardening added cause-based residual routing, dynamic instruction-graph reachability, explicit observation-id correction provenance, and pure/constructive gesture modes.
- Renderer parity work closed inspect/current-state ↔ final/replay divergence for v10 while preserving frozen v9 replay behavior.
- Renderer v10, markmaking runtime discovery, broad-graphite value authority, and renderer-aware fast timelapse were promoted into the `1.0.3rc1 / A11` candidate.
- RC promotion evidence passed same-environment width×3 v9/v10 comparison plus canonical/fast pixel exactness.
- PR #40 integrated `1.0.3rc1` into `main`; merge commit `dc36a86b45aaeed453505330a8bb423fc78405a2` and post-merge main CI run `34705776246` are green.
- No `1.0.3rc1` publish manifest exists, so v1.0.2 remains the latest published stable release.

## Current sequence

```text
G01 fresh-worker gesture dogfood
  ↓
G02 stable-promotion decision: v1.0.3 vs another RC
  ↓
G03 explicit stable freeze + publish manifest
  ↓
G04 publish only if all current contracts and release notes agree
```

### G01 — gesture behavior validation

Run two fresh-worker cases against the current installed `1.0.3rc1` skill:

1. explicit quick/pure gesture;
2. unqualified `gesture drawing`, which must default to constructive gesture.

Reject a result that stops at isolated head/ribcage/pelvis construction, omits major visible limb chains/support, or treats a construction scaffold as the requested finished gesture drawing. Review the result as artistic-behavior evidence; do not reopen renderer/package identity unless the observed defect is actually reusable runtime or instruction-graph friction.

### G02 — stable-promotion decision

Use the fresh dogfood plus the already closed mechanical RC evidence to decide whether the next artifact is stable `1.0.3` or another release candidate.

Do not repeat already-closed renderer parity, compatibility review, or RC integration work unless new evidence invalidates one of those premises. If dogfood exposes an artistic-quality weakness that belongs only to worker visual reasoning, record it as such rather than changing runtime contracts.

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
- add representative teaching examples only when they are good enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- integrated RC notes: `../../../docs/releases/v1.0.3rc1.md`;
- RC promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- unreleased changes and known issues: `../../../CHANGELOG.md`;
- deployable behavior: `../../../skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `../../../docs/releases/v1.0.2.md`;
- immutable released contract: `../../release/vnext/CONTRACT_FREEZE.json`.
