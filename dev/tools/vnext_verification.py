"""Shared mechanics for narrow vNext slice verification entry points."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skills" / "img2drawing" / "src"
ENV = {**os.environ, "PYTHONPATH": str(SRC)}


def run_pytest(*paths: str) -> None:
    subprocess.run(
        (sys.executable, "-m", "pytest", "-q", *paths),
        cwd=ROOT,
        env=ENV,
        check=True,
    )


def run_cli(description: str, handlers: Mapping[str, Callable[[], None]]) -> None:
    """Support both a positional mode and the historical ``--mode`` spelling."""

    modes: Sequence[str] = tuple(handlers)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("mode", nargs="?", choices=modes)
    group = parser.add_mutually_exclusive_group()
    for name in modes:
        group.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args()
    selected = args.mode or next((name for name in modes if getattr(args, name)), None)
    if selected is None:
        parser.error("select a verification mode")
    handlers[selected]()


__all__ = ["ROOT", "SRC", "run_cli", "run_pytest"]
