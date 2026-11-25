# v1.2.1 opt-in tonal and replay QA

This is a **controlled synthetic** regression/measurement harness. It is not a recreation of the original portrait or a blind visual-quality result; WK-96 and WK-97 remain open until those independent gates have evidence.

Run from the checkout after installing the skill:

```sh
python -m pip install -e 'skills/img2drawing'
python dev/benchmarks/tonal_qa/benchmark.py swatch --out qa-results/swatch
python dev/benchmarks/tonal_qa/benchmark.py replay --out qa-results/replay4 --size 2048 --actions 511 --every-n 4
python dev/benchmarks/tonal_qa/benchmark.py replay --out qa-results/retry16 --size 2048 --actions 511 --every-n 16 --force-retry
python dev/benchmarks/tonal_qa/benchmark.py replay --out qa-results/retry4 --size 2048 --actions 511 --every-n 4 --force-retry
```

Replay benchmark requires Linux and FFmpeg. Each replay case constructs the same explicit analytic history (507 strokes, local segment correction, soft lift, reshape, delete). It checks checkpoint/resume state, exact last replay frame, GIF fidelity, cursor coverage and history immutability. The forced retry injects one validation failure after normal encoding, not relaxed thresholds. It does not simulate a real portrait or partial segment eraser. Compare the 33/129-frame retries to assess scaling, not to assert a universal constant-memory bound. RSS is sampled process-tree sum every 50ms (shared pages may be counted more than once; brief peaks can be missed). Child Python and largest FFmpeg subprocess high-water RSS are reported separately; they are not a simultaneous aggregate.

The swatch compares shared centerlines and varying width, opacity, pressure against an empty render with the same profile. It measures brightness loss in reserved highlights, target marks and darkness outside the target; these are diagnostic metrics, not an artistic quality score.

Keep generated sessions, frame packs, PNGs and GIFs outside Git. The opt-in workflow is limited to the QA branch on push, with manual dispatch available. Only small JSON and representative swatch PNGs are uploaded temporarily. No always-on expensive CI on main.
