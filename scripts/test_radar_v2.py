#!/usr/bin/env python3
"""Regression tests for the compact 30-day radar schema and confirmed sample."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_radar", ROOT / "scripts" / "render_radar.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load scripts/render_radar.py")
render_radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_radar)


def sample_entry(paper_id: str = "arxiv:2607.13773") -> dict[str, object]:
    return {
        "paper_id": paper_id,
        "signal_date": "2026-07-15",
        "signal_type": "new-preprint",
        "week": "2026-W29",
        "arxiv_categories": ["nlin.PS", "nlin.SI"],
        "structure_tags": ["Darboux transformation", "topological vector potential"],
        "summary": "论文系统构造平面波背景上的任意多峰多谷孤子族，并给出新的拓扑分析。",
        "main_result": "作者分类基本解形态，并构造任意 K-hump 与 M-valley 的混合结构。",
        "integrable_structure": "方法基于两分量 Fokas--Lenells 系统的 N-fold Darboux transformation。",
        "innovation": "结果从有限低阶例子推进到任意结构，并揭示零点与极点对虚拟单极场的共同贡献。",
    }


def test_component_contract() -> None:
    papers = {
        "arxiv:2607.13773": {
            "id": "arxiv:2607.13773",
            "title": "Multihump-Multivalley Soliton Families",
            "authors": ["Jin-Peng Yang", "Yan-Hong Qin"],
            "url": "https://arxiv.org/abs/2607.13773",
            "arxiv_id": "2607.13773",
            "doi": "10.48550/arXiv.2607.13773",
        },
        "arxiv:old": {
            "id": "arxiv:old",
            "title": "Old paper",
            "authors": ["A. Author"],
            "url": "https://example.test/old",
            "arxiv_id": None,
            "doi": None,
        },
    }

    entry = sample_entry()
    render_radar.validate_frontier_entry(entry, papers)
    card = render_radar.render_frontier_entry(papers["arxiv:2607.13773"], entry)

    required_fragments = (
        "研究问题与主要结果",
        "可积结构与方法",
        "<h4>创新</h4>",
        "展开研究内容与创新",
        "2026-07-15",
        "nlin.PS",
        "Darboux transformation",
        "arXiv</a>",
        "PDF</a>",
    )
    for fragment in required_fragments:
        assert fragment in card, fragment

    forbidden_fragments = (
        "创新后果",
        "结构推进",
        "结构驱动创新",
        "核心前沿",
        "相邻前沿",
        "自动整理",
        "BibTeX",
        "谱控制",
    )
    for fragment in forbidden_fragments:
        assert fragment not in card, fragment

    old_entry = {
        **sample_entry("arxiv:old"),
        "signal_date": "2026-05-01",
        "arxiv_categories": [],
        "structure_tags": ["inverse scattering"],
    }
    frontier = {
        "window_days": 30,
        "generated_through": "2026-07-19",
        "entries": [entry, old_entry],
    }
    visible = render_radar.visible_frontier_entries(frontier, papers)
    assert [item["paper_id"] for item in visible] == ["arxiv:2607.13773"]

    home = render_radar.render_frontier_home(
        {
            "weeks": [
                {
                    "id": "2026-W29",
                    "date_range": "2026-07-13 至 2026-07-19",
                    "summary": "测试周。",
                }
            ],
            "frontier": frontier,
        },
        papers,
    )
    assert "最近 30 天" in home
    assert "2026-W29" in home
    assert "Multihump-Multivalley Soliton Families" in home
    assert "推荐于" not in home

    invalid = {**entry, "structure_tags": ["one", "two", "three"]}
    try:
        render_radar.validate_frontier_entry(invalid, papers)
    except ValueError as exc:
        assert "more than two" in str(exc)
    else:
        raise AssertionError("three displayed structure tags should be rejected")


def test_enabled_frontier() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    frontier = data.get("frontier")
    assert frontier is not None, "the frontier dataset must be enabled"
    assert frontier.get("window_days") == 30
    assert "frontier_staging" not in data

    registry = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, registry)
    visible = render_radar.visible_frontier_entries(frontier, registry)
    assert entries
    assert visible
    assert len({entry["paper_id"] for entry in entries}) == len(entries)

    # Freeze the confirmed migration baseline without blocking future daily updates.
    if frontier.get("generated_through") == "2026-07-19":
        expected_counts = {
            "2026-W25": 2,
            "2026-W26": 16,
            "2026-W27": 6,
            "2026-W28": 15,
            "2026-W29": 5,
        }
        assert len(entries) == 44
        assert len(visible) == 44
        assert Counter(render_radar.frontier_week_id(entry) for entry in entries) == expected_counts
        assert {week["id"] for week in data["frontier_weeks"]} == set(expected_counts)
        assert Counter(entry["signal_type"] for entry in entries) == {
            "new-preprint": 36,
            "journal-publication": 8,
        }


def main() -> None:
    test_component_contract()
    test_enabled_frontier()
    print("compact radar schema and enabled frontier tests passed")


if __name__ == "__main__":
    main()
