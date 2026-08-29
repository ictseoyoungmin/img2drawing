# R23 architecture boundary for the vNext reset

Status: **B00 boundary record; vNext contract remains unfrozen**

This record freezes what must be preserved or rejected at the workflow boundary. It
does not implement or freeze the future vNext public API. B01 owns that contract cut.

## R23 shape observed at the baseline

At `25ec454`, the deployable skill combines:

```text
DrawingRun
  → P1–P5 stage registry and optional P6 finish
  → stage contracts + observation lock
  → stage/local review packets and findings
  → P3 region closure + visual-fidelity records
  → P4/P5 resolved-form records
  → P6 manifest/calibration/retirement evidence
  → checkpoint, replay, and timelapse
```

The relevant source areas are present under
`skills/img2drawing/src/img2drawing/{core,canvas,observation,provenance,render,review,stages}`.
The baseline release identity is recorded in `skills/img2drawing/src/img2drawing/_version.py`.

This architecture has genuine engineering value, but the dogfood evidence shows
that its verification machinery can dominate production and can still accept a weak
whole drawing. Gemini exposes the false-positive side; Claude exposes the cost side.

## Disposition

| R23 capability or concept | vNext boundary decision | Reason/evidence |
|---|---|---|
| `StrokeIR`; explicit draw/replace/delete/soft-lift; history/provenance | **KEEP as capability** | R23 assessment lines 3 and 32, 77; both logs value history-preserving edits |
| Pencil-contact renderer; pressure/grade/opacity/taper | **KEEP as capability** | R23 assessment lines 3 and 77; Gemini log lines 163–170 recognizes material output even while rejecting the overall result |
| Atomic checkpoint/resume; deterministic replay; end-to-end timelapse | **KEEP as capability** | R23 assessment lines 3, 5, 32, 77; Claude log lines 1981–1985 |
| Subject/current-drawing/state hash binding and provenance | **KEEP as invariant** | Roadmap §2.1; baseline hardening and existing R23 checks |
| `prepare_stage_review()` | **TRANSFORM into stage-agnostic `inspect()`** | Roadmap §2.2; the current ceremony contributed to Gemini false acceptance and Claude cost |
| Local review artifacts | **TRANSFORM into one unified inspection sheet with focused crops** | Claude dossier: lines 1991–2013 and 2036–2038 |
| Observation lock | **TRANSFORM into a lightweight observation snapshot** | Roadmap §2.2; preserve semantic observation without making stage ceremony the product core |
| Pass memory | **TRANSFORM into correction memory** | Roadmap §2.2; retain prior findings/actions without stage handoff bookkeeping |
| P6 calibration | **TRANSFORM into optional finish/material calibration** | Roadmap §2.2; R23 assessment lines 5 and 36 |
| Stage references/contracts | **TRANSFORM into skill-side drawing guidance** | Roadmap §§2.2 and 2.5; ordered construction grammar remains useful but is not runtime state |
| `StageProgress`, mandatory stage registry, stage-owned state machine | **DEPRECATE from vNext main path** | Roadmap §2.3; R23 assessment lines 29–35 |
| `RegionClosureManifest`, `ResolvedFormManifest`, exact-region completeness | **DEPRECATE from vNext main path** | Gemini log lines 115–128 show these can pass beside a weak result; roadmap §§1.2, 2.3 |
| Mandatory blind/process/visual double ceremony | **DEPRECATE from vNext main path** | R23 assessment lines 25–30, 79; it makes verification larger than drawing |
| P6 as a mandatory runtime stage | **DEPRECATE from vNext main path** | Roadmap §§2.3 and 2.5; finish remains optional capability |
| Administrative downstream invalidation/reopen bookkeeping | **DEPRECATE from vNext main path** | Roadmap §§2.3 and 2.5.9; corrections remain history-preserving and non-linear |

## Responsibility boundary

Runtime must execute authored strokes, preserve edit history, render the current
state, generate inspection artifacts, provide read-only measurements, bind evidence to
state, and support checkpoint/replay. Runtime must not decide anatomy, pose,
likeness, artistic finish, or which mismatch matters most.

The Agent owns observation, mismatch prioritization, correction choice, and visual
acceptance. Ordered construction grammar (read pose → line of action → mass →
balance → joints/limbs → contour → selective detail → optional value) remains a
skill-side drawing aid, not a runtime stage machine.

## Frozen B00 constraints

1. R23 at `25ec4544e86fe37fc28d64575df145a1b711d63a` is read-only legacy/reference
   material.
2. No R23 artifact, manifest, coordinate table, review verdict, or scripted
   fresh-worker result is vNext PASS evidence.
3. B00 creates no new review schema, inspection implementation, DrawingSession, or
   runtime machinery.
4. A future vNext path must optimize for **better drawing with less review overhead**,
   not for a larger gate inventory.
5. Any future implementation must keep one authoritative shared capability path;
   R23 and vNext may not become two co-equal production implementations.

## Reopen triggers

Reopen B00 if the pinned SHA changes, a legacy artifact is promoted into vNext PASS
evidence, or later work claims a reset rationale that contradicts the Gemini/Claude
dogfood evidence. B01 may refine the boundary only after explicitly recording the
affected contract surface.

## Source evidence

- Roadmap: `dev/planning/img2drawing-vnext-bottleneck-roadmap.md`, §§1–3 and B00–B01.
- Gemini dossier: `failure-dossier/gemini.md`.
- Claude dossier: `failure-dossier/claude.md`.
- R23 assessment: external evidence ID `r23-assessment`, SHA-256
  `614645060e6718f51dae22e4ac146aa61f1a9942dda0be8eaa227b906b7ab91b`, lines 1–100.
- Frozen source: `git show 25ec454 -- skills/img2drawing/src/img2drawing`
