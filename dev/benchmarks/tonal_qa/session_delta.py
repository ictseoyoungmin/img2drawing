"""Developer CLI for the shared runtime tonal inspection implementation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from img2drawing import DrawingSession
from img2drawing.inspection.tonal import (
    gray, measure_plan, plans_from_current_strokes, polygon_mask,
    inspect_tonal_interval as audit,
)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--subject", type=Path, required=True)
    parser.add_argument("--before", type=int, required=True)
    parser.add_argument("--after", type=int, required=True)
    parser.add_argument("--area", action="append")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    session = DrawingSession.resume(args.session, subject=args.subject)
    report = audit(session, args.before, args.after, args.area)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n",
                        encoding="utf-8")
    print(f'measured {len(report["areas"])} explicitly planned tonal areas; no artistic verdict')


if __name__ == "__main__":
    main()
