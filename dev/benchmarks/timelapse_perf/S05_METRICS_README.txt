S05 exact local evidence commands:

PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s05_replay_overheads.py \
  --session /path/to/session.json --every-n 4 --out /tmp/s05-replay.json

PYTHONPATH=src python dev/benchmarks/timelapse_perf/measure_frame_io.py \
  --frames /path/to/frame_dir --out /tmp/s05-frame-io

Fast regression:

PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s05_forward_history.py
