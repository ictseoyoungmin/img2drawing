# Retired R23 runtime cluster

The post-v1.0.2 source cleanup retired the remaining R23 orchestration cluster and the implementation layers that became orphaned with it from the installable package.

Removed from `skills/img2drawing/src/img2drawing/`:

- `run.py`
- `stages/`
- `exemplar/`
- `review/`
- `registration/`
- `canvas/`
- historical `reference/`
- R23 observation contract/lock/evidence/uncertainty/view modules (the current palette API remains)
- `data/registration_profile.json`, whose only runtime loader belonged to retired registration comparison code

The exact pre-retirement tree remains recoverable from commit
`4074a2080ad739acdf179bb0784869a8831c5ef0`. The released v1.0.2 tree is also immutable under tag
`v1.0.2`; use those Git objects when historical source inspection is required instead of copying
retired runtime code back into current `src`.

The pytest-only `img2drawing.legacy.r23` bridge and the R23 implementation tests that depended on
this cluster were removed from the active test suite in the same cleanup. Historical release and
bottleneck validation now bind to frozen artifacts/Git blobs rather than requiring retired modules
to remain importable from the current package.

This archive is a pointer, not an alternate runtime.
