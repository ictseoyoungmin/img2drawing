# img2drawing roadmap

Updated: 2026-09-11
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap describes the **current unreleased main state after v1.0.2**. Older A/B/D/R plans remain historical evidence; they do not override this sequence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 absorbed general authoring ergonomics from successful explicit-stroke dogfood.
- v1.0.2 promoted the exact local-first timelapse backend.
- Post-v1.0.2 source cleanup physically retired the R23 runtime/legacy cluster from current `src`.
- Post-v1.0.2 instruction hardening added cause-based residual routing, dynamic instruction-graph reachability, explicit observation-id correction provenance, and pure/constructive gesture modes.
- CI now separates current runtime checks from frozen historical evidence and no longer runs publish preparation for ordinary main commits.

## Current sequence

```text
G01 fresh-worker gesture dogfood
  ↓
G02 inspect/final/replay render-input parity
  ↓
G03 post-v1.0.2 compatibility and version review
  ↓
G04 new freeze / release candidate / clean-install regression
  ↓
G05 publish only if all current contracts and release notes agree
```

### G01 — gesture behavior validation

Run two fresh-worker cases against the current installed skill:

1. explicit quick/pure gesture;
2. unqualified `gesture drawing`, which must default to constructive gesture.

Reject a result that stops at isolated head/ribcage/pelvis construction, omits major visible limb chains/support, or treats a construction scaffold as the requested finished gesture drawing.

### G02 — renderer parity

Close the strict xfail for `inspect()` versus final/replay rendering. The fix must normalize the render input across inspection, canonical replay, and fast replay rather than changing only one path or silently changing the frozen v1.0.2 renderer contract.

### G03 — compatibility/version review

Current main contains compatibility-breaking post-v1.0.2 changes, including stricter `finish()` preconditions and physical retirement of R23 implementation namespaces. Determine the next release version from documented support policy and actual public compatibility; do not reuse `1.0.2` for new artifacts.

Deprecated pre-0.6.0rc2 root shims are intentionally separate from the R23 retirement and should be removed only if that release explicitly chooses to break them.

### G04 — release hardening

For the selected next version:

- create a new contract freeze rather than editing `v1.0.2-A10`;
- run full active tests, current-runtime isolation, dynamic instruction-graph reachability, package/sdist/wheel audit, clean install, replay/timelapse parity, and frozen-history verification;
- ensure docs, package metadata, release notes, support policy, and CI all describe the same state.

### G05 — publish

Publish only from an explicit new release manifest. The immutable v1.0.2 tag, release notes, and historical freeze remain unchanged.

## Later / optional

- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- add representative teaching examples only when they are good enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- unreleased changes and known issues: `../../../CHANGELOG.md`;
- deployable behavior: `../../../skills/img2drawing/SKILL.md` + references;
- latest released notes: `../../../docs/releases/v1.0.2.md`;
- immutable released contract: `../../release/vnext/CONTRACT_FREEZE.json`.
