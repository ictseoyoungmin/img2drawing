# Opacity response investigation (experimental, not release authority)

Scope: S07 renderer-owned residual; production Pencil v11 and all published
profiles remain unchanged. The optional patch is developer-only research data,
not installed runtime code. Do not apply it to the integration or stable tree.

## Observed cause

A local private portrait refinement showed invented dark neck ribbons. Seven
manually selected corresponding patches gave reference chain variation 0.176
with zero direction reversals versus refined PNG variation 1.434 with four
reversals, despite similar patch-average darkness. The interrupted portrait
checkpoint was not recovered; this is external PNG diagnostic only.

A separate explicit 292×266 crop study produced 13-action banded and 32-action
rebuilt value stages. Fourteen 76%-strength soft-lifts (46 actions) changed mean
neck darkness only 0.7883 to 0.7804. Fixed-path opacity measurements reproduce
the renderer-owned part independently of the private photo. In v11, the broad
shoulder accumulates a nonzero baseline local flow even at low authored alpha;
the continuity floor may leave visible graphite at zero opacity. Geometry and
explicit pressure stay fixed.

| Opacity | v11 broad center | experimental broad center |
|---:|---:|---:|
| .8 | .809608 | .573333 |
| .4 | .809706 | .315770 |
| .2 | .809363 | .156510 |
| .096 | .808417 | .076142 |
| .025 | .807064 | .017730 |
| .005 | .074985 | .002118 |
| 0 | .075201 | 0 |

Width 38, pressure .65, identical authored path, 200×100, supersample 3.
Thin width-3 control also leaves a continuity floor at zero opacity.
Experimental model uses sample-length/radius-normalized optical depth,
with radial-kernel integral and authored alpha, caps core/floor and skips
zero-opacity marks. It has its own explicitly experimental renderer identity.
It is not compatible with v11 profile digests and is not a version selection.
Same explicit neck study in separate candidate session: mean darkness .2795,
variation .6068, one reversal (still not faithful likeness or visual PASS).
Separate 46-action v11 and 32-action experimental local study GIFs passed
their respective final-frame/tolerance checks.

## Reproduce without changing the active checkout

Renderer source blobs at the tested integrated base acfe452e4013cdb939ee14e8ce7fd84cd6150bbc:
- deposit.py: 8db01ab1b781d40f16a10f1d7e758b2729cedca7
- contract.py: 48dd7df6466321ff3e2405bae1dac3f12d0df007

Run from this research checkout with dependencies installed and use an ignored
qa-results directory (outputs must not be committed). Make a **disposable**
detached worktree, or copy the pinned tree to a scratch directory, before
applying the experiment.

```sh
ROOT="$(pwd)"
EXPERIMENT="$(mktemp -d)/checkout"
python dev/benchmarks/tonal_qa/opacity_response.py --out qa-results/opacity-v11
git worktree add --detach "$EXPERIMENT" acfe452e4013cdb939ee14e8ce7fd84cd6150bbc
git -C "$EXPERIMENT" apply --check "$ROOT/dev/benchmarks/tonal_qa/experimental-opacity.patch"
git -C "$EXPERIMENT" apply "$ROOT/dev/benchmarks/tonal_qa/experimental-opacity.patch"
PYTHONPATH="$EXPERIMENT/skills/img2drawing/src" \
  python "$ROOT/dev/benchmarks/tonal_qa/opacity_response.py" --experimental --out "$ROOT/qa-results/opacity-experimental"
```

The experimental check asserts ordered decreasing darkness for the tested
straight strokes and exact zero deposit at zero opacity. It does not assert
universal monotonicity for arbitrary geometry, seed variation or pressure.

## Required before a supported renderer decision

- preserve exact v11 golden pixels and legacy profile replay; explicit new
  contract authority for changed pixels, with no silent profile migration;
- test widths across thin/broad transition, pressure gradients, tight turns,
  crossings and self-overlap, repeated intentional passes, terminal behavior,
  grain and supersampling/scale;
- test local segment lifting, material-only edits, checkpoint resume, incremental
  and canonical full sampled replay under each supported contract;
- evaluate actual independent drawings, not just the diagnostic or crop study.

Do not promote this patch, change a release tag, or claim independent S00/S07
closure based on this experiment. No private references, answer paths, sessions,
generated rasters or GIFs are included.
