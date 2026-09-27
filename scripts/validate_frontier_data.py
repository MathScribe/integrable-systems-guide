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
PUBLIC_TEXT_FIELDS = ("lead", "detail", "method_scope")
PLACEHOLDER_AUTHORS = {"Author metadata unavailable", "Unknown author", "Unknown authors"}


def normalized_public_text(value: object) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", str(value).lower())


def validate_direction_vocabulary() -> None:
    data = yaml.safe_load((ROOT / "data" / "tags.yml").read_text(encoding="utf-8"))
    directions = data.get("frontier_directions") if isinstance(data, dict) else None
    if data.get("schema_version") != 2 or not isinstance(directions, dict):
        raise ValueError("data/tags.yml requires schema2 and frontier_directions")
    if set(directions) != {"spectral", "waves", "asymptotics", "structures"}:
        raise ValueError("Only the four approved research directions are allowed")
    if not all(isinstance(label,str) and label.strip() for label in directions.values()):
        raise ValueError("Research direction labels must be non-empty")


def main() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    if data.get("schema_version") != 2 or set(data) != {"schema_version", "frontier"}:
        raise ValueError("editions must use schema2 without retired weekly aggregates")
    frontier = data["frontier"]

    papers = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, papers)
    validate_direction_vocabulary()
    for entry in entries:
        paper = papers[entry["paper_id"]]
        authors = paper.get("authors") or []
        if not authors or any(str(author).strip() in PLACEHOLDER_AUTHORS for author in authors):
            raise ValueError(f"{entry['paper_id']} requires verified author metadata")

        public_text = entry.get("reading_note")
        if public_text is None:
            continue
        for field, value in public_text.items():
            text = str(value)
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

        summary = normalized_public_text(public_text["lead"])
        main_result = normalized_public_text(public_text["detail"])
        if summary == main_result or (
            min(len(summary), len(main_result)) >= 30
            and (summary in main_result or main_result in summary)
        ):
            raise ValueError(
                f"{entry['paper_id']} repeats the overview in the detailed main result"
            )

    dates = [render_radar.frontier_sort_date(entry) for entry in entries]
    print(
        f"validated {len(entries)} compact radar records "
        f"from {min(dates)} through {max(dates)}"
    )


if __name__ == "__main__":
    main()
