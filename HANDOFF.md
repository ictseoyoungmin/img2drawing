# img2drawing project handoff

Current direction: **post-B18 alignment before fresh visual dogfood**

Runtime/package version: `0.6.0rc2` (`DrawingSession/0.6.0-vnext`).

Current truth:

- B00–B18 are CLOSED.
- A1 repository-truth reconciliation, A2 public-root API alignment, A3 runtime physical-isolation audit, and A4 residual-routing hardening are CLOSED.
- PR #5 replaced the deployable documentation surface with the stage-free instruction graph and removed `skills/img2drawing/examples/`.
- The deployable skill starts at `skills/img2drawing/SKILL.md`; `references/INDEX.md` is the routing table.
- The instruction graph now includes `references/review/residual-routing.md`: workers route visible symptoms by responsible relationship and escalate to upstream construction/observation/contact/environment premises when the local part is only a symptom.
- The package root is intentionally narrow around `DrawingSession`; specialized capability lives in explicit owning namespaces and pre-rc2 root names are compatibility shims only.
- Canonical `DrawingSession` imports do not depend on `img2drawing.run`, `stages`, `exemplar`, the historical `review` runtime, or the historical `registration` runtime.
- `img2drawing.inspection` owns current stage-free inspection/measurement/registration capability.
- `img2drawing.run`, `stages`, `exemplar`, `review`, and `registration` are classified as R23 compatibility implementation. Their names do **not** define the current instruction graph or a second normal workflow.
- Physical deletion/renaming of that R23 cluster is deferred to R03, where the compatibility window can be decided after D01–D06 evidence.
- `dev/release/vnext/CONTRACT_FREEZE.json` is the current machine-readable contract. It is not part of the deployable skill root.
- No new D01–D06 fresh visual validation claim has been made yet.

Read first:

1. `skills/img2drawing/SKILL.md`
2. `skills/img2drawing/references/INDEX.md`
3. `dev/planning/vnext/STATUS.md`
4. `dev/planning/vnext/ROADMAP.md`
5. `dev/planning/vnext/VALIDATION_RELEASE.md`

## Next work

Before D01, continue the small post-freeze alignment pass exposed by the instruction-graph audit:

1. repository-truth reconciliation — CLOSED;
2. public root API alignment around `DrawingSession` — CLOSED;
3. runtime physical-isolation audit — CLOSED;
4. explicit residual → leaf → upstream escalation routing edges — CLOSED;
5. **remaining high-value drawing leaves such as hands/grip and foreshortening — NEXT**.

A5 must be evidence-backed and compact. Add a separate drawing leaf only when a recurring visual
failure cannot be expressed cleanly by the existing graph. Hands/grip and foreshortening are the
leading candidates because they combine chain structure, contact, overlap, perspective, and
identity-bearing geometry; do not expand the skill into a general anatomy textbook.

These are cleanup/hardening tasks, not a second runtime workflow. Do not reactivate Pn/R23
development and do not create a parallel session architecture.

D01 remains the next fresh validation case after this alignment pass is accepted. Do not start it
automatically while the user is stepping through these cleanup bottlenecks.

## Authority

- `dev/planning/vnext/STATUS.md` — current project state.
- `dev/planning/vnext/ROADMAP.md` — current sequence and durable phase boundaries.
- `dev/planning/vnext/A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md` — source/package ownership classification.
- `dev/planning/vnext/A4_RESIDUAL_ROUTING_HARDENING.md` — operational residual-routing closure.
- `dev/planning/vnext/VALIDATION_RELEASE.md` — D01–D06 and release validation contracts.
- `dev/release/vnext/` — current release-candidate control-plane records.
- `dev/release/r23/` and Git history — historical compatibility/release evidence.
- `skills/img2drawing/SKILL.md` + `references/` — deployable Agent guidance only; never use development control-plane material as drawing instructions.
