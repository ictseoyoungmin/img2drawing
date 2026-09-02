"""Run the canonical observed-authority mechanical example."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mechanical_workflows import run_observed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("observed-example-output"))
    args = parser.parse_args()
    print(json.dumps(run_observed(args.output), indent=2))
