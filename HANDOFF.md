# img2drawing project handoff

Current direction: **post-B18 alignment before fresh visual dogfood**

Runtime/package version: `0.6.0rc2` (`DrawingSession/0.6.0-vnext`).

Current truth:

- B00–B18 are CLOSED.
- A1 repository-truth reconciliation and A2 public-root API alignment are CLOSED.
- PR #5 replaced the deployable documentation surface with the stage-free instruction graph and removed `skills/img2drawing/examples/`.
- The deployable skill starts at `skills/img2drawing/SKILL.md`; `references/INDEX.md` is the routing table.
- The package root is intentionally narrow around `DrawingSession`; specialized capability lives in explicit owning namespaces and pre-rc2 root names are compatibility shims only.
- `dev/release/vnext/CONTRACT_FREEZE.json` is the current machine-readable contract. It is not part of the deployable skill root.
- R23 remains explicit compatibility/history material; physical retirement is still deferred until the post-dogfood retirement step unless the next audit safely narrows that boundary.
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
3. **physical runtime-isolation audit for stage-era/current-path modules — NEXT**;
4. explicit residual → leaf → upstream escalation routing edges;
5. remaining high-value drawing leaves such as hands/grip and foreshortening.

A3 should classify code before moving or deleting it. The goal is not cosmetic folder cleanup;
it is to determine whether each remaining stage-era/current-path module is shared capability,
current implementation, explicit compatibility, or a real retirement candidate. Preserve working
migration/runtime behavior until evidence supports a move.

These are cleanup/hardening tasks, not a second runtime workflow. Do not reactivate Pn/R23
development and do not create a parallel session architecture.

D01 remains the next fresh validation case after this alignment pass is accepted. Do not start it
automatically while the user is stepping through these cleanup bottlenecks.

## Authority

- `dev/planning/vnext/STATUS.md` — current project state.
- `dev/planning/vnext/ROADMAP.md` — current sequence and durable phase boundaries.
- `dev/planning/vnext/VALIDATION_RELEASE.md` — D01–D06 and release validation contracts.
- `dev/release/vnext/` — current release-candidate control-plane records.
- `dev/release/r23/` and Git history — historical compatibility/release evidence.
- `skills/img2drawing/SKILL.md` + `references/` — deployable Agent guidance only; never use development control-plane material as drawing instructions.
