## S05 quick commands

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s05_replay_overheads.py \
  --session /path/to/session.json --every-n 4 --out /tmp/s05-replay.json

PYTHONPATH=src python dev/benchmarks/timelapse_perf/measure_frame_io.py \
  --frames /path/to/frame_dir --out /tmp/s05-frame-io

PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s05_forward_history.py
```

See `S05_REPLAY_TRAVERSAL_AND_IO.md` for the exact Lucy measurements and next-bottleneck decision.
