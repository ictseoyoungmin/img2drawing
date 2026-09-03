# 0.6.0rc2 release-candidate notes

This candidate keeps the B17/B18 `DrawingSession/0.6.0-vnext` runtime and persisted schema
contracts while aligning package-root discoverability with the stage-free framework model.

- `DrawingSession` is the canonical orchestration surface for normal users and Agents.
- the root exposes only session/declarative inputs plus the small observed-construction facade;
- specialized inspection, observation, record, schema, and low-level history capability lives
  in explicit owning namespaces rather than competing at the root;
- pre-rc2 direct root imports remain available through deprecated lazy compatibility shims;
- observed, imaginative, and hybrid authority still share one correction/output core;
- R23 remains explicit compatibility only.

The RC proves packaging and deterministic mechanical integration. It does not certify
unseen-subject, cross-agent, or artistic quality.

The A2-aligned B18 snapshot in `CONTRACT_FREEZE.json` pins the narrowed root exports,
supported session methods, persisted schemas, intent axes, canonical render profile, and
compatibility boundary before D01-D06.
