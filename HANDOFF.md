# img2drawing project handoff

Current direction: **post-B18 alignment before fresh visual dogfood**

Runtime/package version: `0.6.0rc1` (`DrawingSession/0.6.0-vnext`).

Current truth:

- B00–B18 are CLOSED.
- PR #5 replaced the deployable documentation surface with the new stage-free instruction graph and removed `skills/img2drawing/examples/`.
- The deployable skill starts at `skills/img2drawing/SKILL.md`; `references/INDEX.md` is the routing table.
- `dev/release/vnext/CONTRACT_FREEZE.json` is the frozen vNext machine-readable contract. It is not part of the deployable skill root.
- R23 remains explicit compatibility/history material; physical retirement is still deferred until the post-dogfood retirement step unless a later audit narrows that boundary safely.
- No new D01–D06 fresh visual validation claim has been made yet.

Read first:

1. `skills/img2drawing/SKILL.md`
2. `skills/img2drawing/references/INDEX.md`
3. `dev/planning/vnext/STATUS.md`
4. `dev/planning/vnext/ROADMAP.md`
5. `dev/planning/vnext/VALIDATION_RELEASE.md`

## Next work

Before D01, finish the small post-freeze alignment pass exposed by the instruction-graph audit:

1. repository-truth reconciliation — current task;
2. public root API surface audit/narrowing around `DrawingSession`;
3. physical runtime-isolation audit for stage-era/current-path modules;
4. explicit residual → leaf → upstream escalation routing edges;
5. remaining high-value drawing leaves such as hands/grip and foreshortening.

These are cleanup/hardening tasks, not a second runtime workflow. Do not reactivate Pn/R23 development and do not create a parallel session architecture.

D01 remains the next fresh validation case after this alignment pass is accepted. Do not start it automatically while the user is stepping through these cleanup bottlenecks.

## Authority

- `dev/planning/vnext/STATUS.md` — current project state.
- `dev/planning/vnext/ROADMAP.md` — current sequence and durable phase boundaries.
- `dev/planning/vnext/VALIDATION_RELEASE.md` — D01–D06 and release validation contracts.
- `dev/release/vnext/` — frozen release-candidate control-plane records.
- `dev/release/r23/` and Git history — historical compatibility/release evidence.
- `skills/img2drawing/SKILL.md` + `references/` — deployable Agent guidance only; never use development control-plane material as drawing instructions.
