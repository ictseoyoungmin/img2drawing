# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap describes the **current unreleased main/RC state after v1.0.2**. Older A/B/D/R plans remain historical evidence and do not override this sequence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 added general authoring ergonomics.
- v1.0.2 promoted the exact local-first timelapse backend.
- Post-v1.0.2 cleanup physically retired the R23 runtime/legacy cluster.
- Renderer v10 closed seed/parity and broad authored-value issues while preserving explicit v9 replay.
- `1.0.3rc1 / A11` integrated renderer v10 and its promotion evidence into main.
- G01 fresh gesture dogfood reopened and then closed runtime/instruction integration gaps in `1.0.3rc2 / A12`.
- PR #42 integrated rc2 into main and post-merge main CI passed.
- G01 remains **PASS/CLOSED**: gesture is a public runtime mode, and final gesture marks must carry facing/asymmetry/attachment information instead of geometric or rounded stock primitives.
- No v1.0.3 RC publish manifest exists; v1.0.2 remains the latest published stable release.

## Current sequence

```text
G02 broad-pencil material/terminal hardening — ACTIVE
  ↓
G03 integrate validated rc3 into main
  ↓
G04 stable-promotion decision: v1.0.3 vs another RC
  ↓
G05 explicit stable freeze + publish manifest
  ↓
G06 publish only after all current contracts agree
```

### G01 — gesture behavior validation — CLOSED

Same-reference pure + constructive dogfood found and closed three reusable defects: missing public `gesture` runtime intent, anti-faceted guidance overcorrecting into generic rounded blobs, and semantic markmaking preset IDs being confused with low-level runtime tool names. Bounded evidence is `../../dogfood/g01-gesture-rc2/README.md`.

### G02 — broad-pencil material and terminal quality — ACTIVE

Thick-line dogfood exposed a renderer/material failure hidden by earlier thin-line work. Transitional broad marks can show a rectangular high-alpha continuity core at their ends, and broad interiors can read too much like a flat digital ribbon instead of graphite on paper.

Root-cause inspection localized the failure to the v10 broad authored-value core, not to gesture instructions or authored geometry. v10's radial shoulder is physical, but the continuity core uses Pillow line segments whose visible terminal is a butt/square cut. Its intentionally subtle core texture can also dominate the shoulder and weaken the apparent paper tooth.

Because renderer semantics are immutable per identity, G02 does **not** patch `pillow-pencil-contact-v10 / 1` in place. The corrective candidate is:

```text
1.0.3rc3 / A13
new sessions → pillow-pencil-contact-v11 / 1
explicit v10/1 → preserved rc1/rc2 replay
explicit v9/1  → preserved v1.0.2 replay
```

v11 is deliberately narrow:

- ordinary thin strokes delegate byte-for-byte to v10;
- the existing v10 broad radial shoulder and authored-value policy remain the base material model;
- broad continuity cores gain pressure/taper-resolved round contact terminals;
- broad core/shoulder composition gains stronger deterministic page-fixed graphite/tooth variation, mean-normalized to preserve authored value;
- canonical final and fast timelapse use the same registered v11 patch builder.

Required G02 gates:

```text
deterministic broad-stroke reproduction
→ v10 failure reproduced
→ v11 terminal morphology regression test
→ v11 broad graphite/tooth regression test
→ v10↔v11 thin pixel exactness
→ v11 canonical↔fast exactness
→ full current + historical + package CI
→ visual comparison board
```

The rc1 width×3 v9/v10 benchmark remains valid historical evidence for v10, but it cannot by itself authorize stable promotion of changed v11 bytes. If G02 closes, record fresh v11 evidence before the stable decision.

### G03 — rc3 integration

After G02 mechanical and visual gates close, integrate `1.0.3rc3` to `main` through a PR. Do not create a stable or RC publish manifest merely because the candidate is on main.

### G04 — stable-promotion decision

Use renderer replay preservation, v11 canonical/fast exactness, thin non-regression, G01 gesture dogfood, G02 broad-pencil quality evidence, and final package verification to choose stable `1.0.3` or another RC.

Deprecated pre-0.6.0rc2 root shims remain a separate compatibility decision and must not be silently bundled into stable promotion.

### G05 — stable freeze and publish preparation

Only after choosing stable promotion:

- create a new immutable v1.0.3 contract freeze rather than editing `v1.0.2-A10`;
- create an explicit stable publish manifest;
- update stable release notes/support metadata;
- rerun active tests, current-runtime isolation, instruction-graph reachability, package/sdist/wheel audit, clean install, replay/timelapse parity, fresh renderer evidence, and frozen-history verification;
- verify built wheel metadata and hashes.

### G06 — publish

Publish only from the explicit stable manifest after every current-facing document, package identity, release note, and mechanical gate agrees. The immutable v1.0.2 release history remains unchanged.

## Later / optional

- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- add representative teaching examples only when they are strong enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- rc3 candidate notes: `../../../docs/releases/v1.0.3rc3.md`;
- rc2 historical notes: `../../../docs/releases/v1.0.3rc2.md`;
- rc1 renderer promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- unreleased changes: `../../../CHANGELOG.md`;
- deployable behavior: `../../../skills/img2drawing/SKILL.md` + references;
- latest published stable: `../../../docs/releases/v1.0.2.md`;
- immutable released contract: `../../release/vnext/CONTRACT_FREEZE.json`.
