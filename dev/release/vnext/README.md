# v1.0.2 release/control-plane records

This directory contains the immutable **v1.0.2 / A10** release freeze plus maintainer-facing
support/migration notes around that release. `CONTRACT_FREEZE.json` is the machine-readable
released snapshot and must not be rewritten to describe later `main` changes.

Current `main` is post-v1.0.2 and intentionally differs from this freeze: the R23 runtime/legacy
namespace has since been physically retired, finish/evidence contracts have hardened, and the
instruction graph has continued to evolve. Current repository truth lives in
`dev/planning/vnext/STATUS.md` and `CHANGELOG.md` until a new version/freeze is created.

Files here are control-plane/history records, not deployable drawing guidance and not part of the
Agent Skill attention surface.
