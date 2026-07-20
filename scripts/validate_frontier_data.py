#!/usr/bin/env python3
"""Validate staged or enabled compact-radar records in data/editions.yml."""

from __future__ import annotations

import importlib.util
import re
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
FORBIDDEN_CONTENT_MARKERS = (
    "## ",
    "本轮值得关注的方向信号",
    "下一步",
    "reviewable PR",
    "自动合并",
)
PUBLIC_TEXT_FIELDS = ("summary", "main_result", "integrable_structure", "innovation")
PLACEHOLDER_AUTHORS = {"Author metadata unavailable", "Unknown author", "Unknown authors"}


def normalized_public_text(value: object) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(value).lower())


def controlled_structure_tags() -> set[str]:
    data = yaml.safe_load((ROOT / "data" / "tags.yml").read_text(encoding="utf-8"))
    tags = data.get("frontier_structure_tags") if isinstance(data, dict) else None
    if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag for tag in tags):
        raise ValueError("data/tags.yml requires a non-empty frontier_structure_tags list")
    if len(tags) != len(set(tags)):
        raise ValueError("data/tags.yml contains duplicate frontier structure tags")
    return set(tags)


def main() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    frontier = data.get("frontier") or data.get("frontier_staging")
    if frontier is None:
        print("no compact radar records staged")
        return

    papers = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, papers)
    allowed_tags = controlled_structure_tags()
    for entry in entries:
        paper = papers[entry["paper_id"]]
        authors = paper.get("authors") or []
        if not authors or any(str(author).strip() in PLACEHOLDER_AUTHORS for author in authors):
            raise ValueError(f"{entry['paper_id']} requires verified author metadata")

        for field in PUBLIC_TEXT_FIELDS:
            text = str(entry[field])
            if "?" in text:
                raise ValueError(f"{entry['paper_id']}.{field} contains possible encoding damage")
            for term in FORBIDDEN_PUBLIC_TERMS:
                if term in text:
                    raise ValueError(
                        f"{entry['paper_id']}.{field} contains deprecated public wording: {term}"
                    )
            for marker in FORBIDDEN_CONTENT_MARKERS:
                if marker in text:
                    raise ValueError(
                        f"{entry['paper_id']}.{field} contains report or workflow residue: {marker}"
                    )

        summary = normalized_public_text(entry["summary"])
        main_result = normalized_public_text(entry["main_result"])
        if summary == main_result or (
            min(len(summary), len(main_result)) >= 30
            and (summary in main_result or main_result in summary)
        ):
            raise ValueError(
                f"{entry['paper_id']} repeats the overview in the detailed main result"
            )

        for tag in entry.get("structure_tags", []):
            if tag not in allowed_tags:
                raise ValueError(f"{entry['paper_id']} has uncontrolled structure tag: {tag}")

    dates = [entry["signal_date"] for entry in entries]
    print(
        f"validated {len(entries)} compact radar records "
        f"from {min(dates)} through {max(dates)}"
    )


if __name__ == "__main__":
    main()
