# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap describes the selected **v1.0.3 stable candidate** after the rc1–rc3 integration cycle. Older A/B/D/R plans remain historical evidence and do not override this sequence.

## Closed foundation

- v1.0.0 established the first stable stage-free Agent Skill/runtime surface.
- v1.0.1 added general authoring ergonomics.
- v1.0.2 promoted the exact local-first timelapse backend.
- Post-v1.0.2 cleanup physically retired the R23 runtime/legacy cluster.
- Renderer v10 closed seed/parity and broad authored-value issues while preserving explicit v9 replay.
- `1.0.3rc1 / A11` integrated renderer v10 and its promotion evidence into main.
- G01 fresh gesture dogfood reopened and closed runtime/instruction integration gaps in `1.0.3rc2 / A12`.
- G02 broad-pencil dogfood reproduced and closed the square-terminal / weak-graphite failure with additive renderer `pillow-pencil-contact-v11 / 1` in `1.0.3rc3 / A13`.
- PR #43 integrated rc3 into main at `bcc931c79a4c4cf799aec3a5265d21145bfb546b`; post-merge main CI passed.
- G01 and G02 are both **PASS/CLOSED** for their target failure classes.

## Current sequence

```text
G01 gesture behavior validation                    CLOSED
G02 broad-pencil material/terminal hardening      CLOSED
G03 integrate validated rc3 into main             CLOSED
G04 stable-promotion decision                     CLOSED → choose v1.0.3
G05 stable freeze + wheel verification             ACTIVE
  ↓
G06 explicit publish manifest + publish            NEXT
```

### G01 — gesture behavior validation — CLOSED

Same-reference pure + constructive dogfood found and closed three reusable defects: missing public `gesture` runtime intent, anti-faceted guidance overcorrecting into generic rounded blobs, and semantic markmaking preset IDs being confused with low-level runtime tool names. Bounded evidence is `../../dogfood/g01-gesture-rc2/README.md`.

### G02 — broad-pencil material and terminal quality — CLOSED

Thick-line dogfood exposed a renderer/material failure hidden by earlier thin-line work. Transitional broad marks could show a rectangular high-alpha continuity core at their ends, and broad interiors could read too much like a flat digital ribbon instead of graphite on paper.

The corrective renderer is additive rather than an in-place rewrite:

```text
v1.0.3 stable / A14
new sessions → pillow-pencil-contact-v11 / 1
explicit v10/1 → preserved rc1/rc2 replay
explicit v9/1  → preserved v1.0.2 replay
```

Closed gates:

- deterministic broad-stroke reproduction;
- v10 square/butt terminal reproduced;
- v11 pressure-resolved round broad terminal regression;
- v11 stronger page-fixed graphite/tooth regression with mean-value tolerance;
- v10↔v11 2 px thin pixel exactness;
- v11 canonical-final ↔ fast-final exactness;
- full current + historical + package CI;
- drawing-scale and 9–14 px heavy-graphite visual dogfood.

Evidence: `../../dogfood/g02-broad-pencil-v11/README.md`.

### G03 — rc3 integration — CLOSED

PR #43 integrated rc3 to main and post-merge CI passed all mechanical gates. No publish manifest was created as part of rc3 integration.

### G04 — stable-promotion decision — CLOSED

Decision: **promote v1.0.3 stable rather than create another RC**.

The decision is grounded in replay preservation, v11 canonical/fast exactness, thin non-regression, G01 gesture dogfood, G02 broad-pencil visual quality evidence, and full package/history verification.

Deprecated pre-0.6.0rc2 root shims remain a separate compatibility decision and are not bundled into this stable promotion.

### G05 — stable freeze and wheel verification — ACTIVE

The stable candidate is `1.0.3 / A14 / v1.0.3_gesture_renderer_quality` on `release/1.0.3-stable`.

Required order:

1. keep the v1.0.2 `CONTRACT_FREEZE.json` immutable;
2. add the independent v1.0.3 freeze `CONTRACT_FREEZE_V1_0_3.json`;
3. update version/release docs and current package-contract tests to stable identity;
4. run active tests, current-runtime isolation, instruction graph, package/install audit, replay/timelapse parity, fresh renderer evidence, and frozen-history verification;
5. build a wheel from the exact stable branch HEAD;
6. verify wheel filename, `METADATA` version, and SHA-256 before any publish manifest exists.

### G06 — publish — NEXT

Only after G05 passes:

- add `dev/release/publish/v1.0.3.json`;
- rerun branch and PR CI;
- merge the stable PR with the expected head SHA pinned;
- verify post-merge main CI;
- allow the existing `img2drawing-publish-release` workflow to create GitHub Release `v1.0.3` from that exact main SHA;
- verify the release target and wheel/sdist assets.

## Later / optional

- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- add representative teaching examples only when they are strong enough not to become accidental answer templates;
- expand fresh cross-agent/cross-subject validation when needed for broader product claims.

## Authority

- current state: `STATUS.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- G02 visual/material evidence: `../../dogfood/g02-broad-pencil-v11/README.md`;
- v1.0.3 stable notes: `../../../docs/releases/v1.0.3.md`;
- v1.0.3 stable freeze: `../../release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- rc1 renderer promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- currently published stable until G06: `../../../docs/releases/v1.0.2.md`;
- immutable v1.0.2 snapshot: `../../release/vnext/CONTRACT_FREEZE.json`.
