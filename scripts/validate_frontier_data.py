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

FORBIDDEN_PUBLIC_TERMS = (
    "新意",
    "创新后果",
    "核心前沿",
    "相邻前沿",
    "结构推进",
    "结构驱动创新",
    "自动整理",
    "谱控制",
)
PUBLIC_TEXT_FIELDS = ("summary", "main_result", "integrable_structure", "innovation")


def main() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    frontier = data.get("frontier") or data.get("frontier_staging")
    if frontier is None:
        print("no compact radar records staged")
        return

    papers = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, papers)
    for entry in entries:
        for field in PUBLIC_TEXT_FIELDS:
            text = str(entry[field])
            for term in FORBIDDEN_PUBLIC_TERMS:
                if term in text:
                    raise ValueError(
                        f"{entry['paper_id']}.{field} contains deprecated public wording: {term}"
                    )

    dates = [entry["signal_date"] for entry in entries]
    print(
        f"validated {len(entries)} compact radar records "
        f"from {min(dates)} through {max(dates)}"
    )


if __name__ == "__main__":
    main()
