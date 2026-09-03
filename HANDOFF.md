# img2drawing project handoff

Current direction: **fresh visual validation after the completed pre-D01 alignment pass**

Runtime/package version: `0.6.0rc2` (`DrawingSession/0.6.0-vnext`).

Current truth:

- B00–B18 are CLOSED.
- A1 repository truth, A2 public-root alignment, A3 runtime isolation, A4 residual routing, and A5 high-value drawing-leaf hardening are CLOSED.
- The deployable skill starts at `skills/img2drawing/SKILL.md`; `references/INDEX.md` is the progressive-disclosure routing table.
- `references/review/residual-routing.md` routes visible symptoms by responsible relationship and escalates upstream when the local part is only a symptom.
- `references/figure/hands-and-grip.md` owns local visible hand/grip geometry only after the parent arm chain is credible. It rejects mitten-style completion and invented hidden digits.
- `references/construction/foreshortening-and-depth.md` owns projected length, near/far order, overlap, hidden length, and terminal orientation. It rejects unfolding compressed forms to expected anatomical length.
- The package root remains intentionally narrow around `DrawingSession`; specialized capability lives in explicit owning namespaces and pre-rc2 root names are compatibility shims only.
- Canonical `DrawingSession` imports do not depend on historical `run/stages/exemplar/review/registration` orchestration.
- `img2drawing.inspection` owns current stage-free inspection/measurement/registration capability.
- Historical `run`, `stages`, `exemplar`, Python `review`, and Python `registration` remain R23 compatibility implementation until R03.
- `dev/release/vnext/CONTRACT_FREEZE.json` is the current machine-readable release-candidate contract, outside the deployable skill.
- No D01–D06 fresh visual validation claim has been made yet.

Read first:

1. `skills/img2drawing/SKILL.md`
2. `skills/img2drawing/references/INDEX.md`
3. `dev/planning/vnext/STATUS.md`
4. `dev/planning/vnext/ROADMAP.md`
5. `dev/planning/vnext/VALIDATION_RELEASE.md`

## Next work

The pre-D01 alignment pass is complete:

1. repository-truth reconciliation — CLOSED;
2. public root API alignment around `DrawingSession` — CLOSED;
3. runtime physical-isolation audit — CLOSED;
4. explicit residual → leaf → upstream escalation routing edges — CLOSED;
5. bounded hands/grip and foreshortening/depth drawing leaves — CLOSED.

**D01 difficult observed croquis is NEXT.** It is the first fresh visual validation case and
must follow `VALIDATION_RELEASE.md`: fresh sealed input, current installed skill/package, no
answer image or prior subject-specific solution coordinates, and actual render/inspection/
correction evidence. A real failure may reopen the responsible A/B premise.

Do not reactivate Pn/R23 development, create a parallel session architecture, or treat
mechanical CI as artistic-quality proof.

## Authority

- `dev/planning/vnext/STATUS.md` — current project state.
- `dev/planning/vnext/ROADMAP.md` — current sequence and durable phase boundaries.
- `dev/planning/vnext/A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md` — source/package ownership classification.
- `dev/planning/vnext/A4_RESIDUAL_ROUTING_HARDENING.md` — operational residual-routing closure.
- `dev/planning/vnext/A5_DRAWING_LEAF_GAP_HARDENING.md` — hand/grip and foreshortening/depth guidance closure.
- `dev/planning/vnext/VALIDATION_RELEASE.md` — D01–D06 and release validation contracts.
- `dev/release/vnext/` — current release-candidate control-plane records.
- `dev/release/r23/` and Git history — historical compatibility/release evidence.
- `skills/img2drawing/SKILL.md` + `references/` — deployable Agent guidance only; never use development control-plane material as drawing instructions.
