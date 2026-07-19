#!/usr/bin/env python3
"""Validate staged or enabled compact-radar records in data/editions.yml."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_radar", ROOT / "scripts" / "render_radar.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load scripts/render_radar.py")
render_radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_radar)


def main() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    frontier = data.get("frontier") or data.get("frontier_staging")
    if frontier is None:
        print("no compact radar records staged")
        return

    papers = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, papers)
    dates = [entry["signal_date"] for entry in entries]
    print(
        f"validated {len(entries)} compact radar records "
        f"from {min(dates)} through {max(dates)}"
    )


if __name__ == "__main__":
    main()
