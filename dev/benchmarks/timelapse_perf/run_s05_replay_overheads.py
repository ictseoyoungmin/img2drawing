from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from img2drawing.vnext.session import DrawingSession

from forward_history_replay import ForwardHistoryReplay


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    parser.add_argument("--every-n", type=int, default=4)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    session = DrawingSession.resume(args.session)
    history = session._agent.history
    cursors = list(range(0, history.cursor + 1, args.every_n))
    if not cursors or cursors[-1] != history.cursor:
        cursors.append(history.cursor)

    t0 = time.perf_counter()
    baseline = [history.state_at(cursor) for cursor in cursors]
    baseline_s = time.perf_counter() - t0

    replay = ForwardHistoryReplay(history)
    t0 = time.perf_counter()
    forward = list(replay.snapshots(cursors, copy_strokes=False))
    forward_s = time.perf_counter() - t0

    parity = [a.to_dict() == b.to_dict() for a, b in zip(baseline, forward)]
    metrics = {
        "schema": "img2drawing.timelapse_s05_replay_overheads.v1",
        "session": str(Path(args.session)),
        "actions": history.cursor,
        "frames": len(cursors),
        "every_n": args.every_n,
        "state_at_every_frame_s": baseline_s,
        "forward_zero_copy_s": forward_s,
        "speedup": baseline_s / forward_s if forward_s else None,
        "all_sampled_state_parity": all(parity),
        "parity_frames": sum(parity),
        "forward_stats": replay.stats.__dict__,
    }
    Path(args.out).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
