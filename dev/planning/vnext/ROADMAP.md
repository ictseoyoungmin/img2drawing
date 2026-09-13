# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

This roadmap records the completed **v1.0.3 release cycle** and the current handoff boundary. Older A/B/D/R plans remain historical evidence and do not override current `STATUS.md` or the published release record.

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
- PR #44 removed generation-tagged Python module filenames from current `src` while preserving serialized v9/v10/v11 replay identities.
- PR #45 promoted the verified v1.0.3/A14 candidate to `main`; release commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976` passed main CI and published GitHub Release `v1.0.3`.
- PR #46 closed README/STATUS publication state; final documentation-only main commit `e4f3c79361ab588ab2e89bc99326c242bee3740b` passed CI without creating a duplicate release.

## Current sequence

```text
G01 gesture behavior validation                    CLOSED
G02 broad-pencil material/terminal hardening       CLOSED
G03 integrate validated rc3 into main              CLOSED
G04 stable-promotion decision                      CLOSED → choose v1.0.3
G05 stable freeze + wheel verification             CLOSED
G06 explicit publish manifest + publish            CLOSED
NEXT PRODUCT BOTTLENECK                            UNSELECTED
```

There is **no active v1.0.3 release gate**. `v1.0.3` is published and CLOSED. Future work starts from the `Unreleased` section of `CHANGELOG.md` after a new highest-impact bottleneck is explicitly selected; this roadmap does not pre-authorize a particular next feature or validation campaign.

### G01 — gesture behavior validation — CLOSED

Same-reference pure + constructive dogfood found and closed three reusable defects: missing public `gesture` runtime intent, anti-faceted guidance overcorrecting into generic rounded blobs, and semantic markmaking preset IDs being confused with low-level runtime tool names. Bounded evidence is `../../dogfood/g01-gesture-rc2/README.md`.

### G02 — broad-pencil material and terminal quality — CLOSED

Thick-line dogfood exposed a renderer/material failure hidden by earlier thin-line work. Transitional broad marks could show a rectangular high-alpha continuity core at their ends, and broad interiors could read too much like a flat digital ribbon instead of graphite on paper.

The released renderer boundary is:

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

The decision was grounded in replay preservation, v11 canonical/fast exactness, thin non-regression, G01 gesture dogfood, G02 broad-pencil visual quality evidence, and full package/history verification.

Deprecated pre-0.6.0rc2 root shims remain a separate compatibility decision and were not bundled into v1.0.3.

### G05 — stable freeze and wheel verification — CLOSED

The selected stable package was frozen as `1.0.3 / A14 / v1.0.3_gesture_renderer_quality`.

Completed evidence:

- immutable v1.0.2 `CONTRACT_FREEZE.json` preserved;
- independent `CONTRACT_FREEZE_V1_0_3.json` added;
- exact stable package tree pinned by `V1_0_3_STABLE_PROMOTION.json`;
- stable branch CI `34749311565` passed;
- package tree `5758c5efa60d80a0d483bcb3573258e34d609055` verified;
- candidate wheel `img2drawing-1.0.3-py3-none-any.whl` verified before publication intent.

### G06 — publish — CLOSED

Publication completed through the explicit `dev/release/publish/v1.0.3.json` manifest.

Verified publication evidence:

- PR #45 merged the publication intent to `main`;
- main release CI `34749869989` passed;
- publish workflow `34749920471` passed;
- Git tag / GitHub Release `v1.0.3` targets `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`;
- published wheel SHA-256: `89061b74984e1ffbb78b48fa1de81aacd64c9d4bfb2ec6baadc41b703bc240f7`;
- published sdist SHA-256: `08067b1aec8384a94dc323d6ea511be84ffe006069f5180ff3c44c9d9a1dd4c4`;
- PR #46 documentation closure triggered a no-op publish workflow, confirming no duplicate release.

## Later / optional candidates

These are **not active or pre-authorized**; select only when one becomes the highest-impact open problem.

- fresh unseen-reference / cross-subject generalization dogfood;
- remove deprecated root compatibility shims in a separately versioned compatibility cleanup;
- add representative teaching examples only when they are strong enough not to become accidental answer templates;
- expand cross-agent validation when broader product claims require it.

## Authority

- current state: `STATUS.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `../../../docs/releases/v1.0.3.md`;
- G01 behavioral evidence: `../../dogfood/g01-gesture-rc2/README.md`;
- G02 visual/material evidence: `../../dogfood/g02-broad-pencil-v11/README.md`;
- v1.0.3 stable freeze: `../../release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- exact v1.0.3 stable candidate: `../../release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- rc1 renderer promotion evidence: `../../release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- immutable v1.0.2 snapshot: `../../release/vnext/CONTRACT_FREEZE.json`.
