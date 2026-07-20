#!/usr/bin/env python3
"""Regression tests for the cumulative compact radar and confirmed sample."""

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
            "submitted": "2026-07-14",
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
        "<h4>研究问题与主要结果</h4>",
        "<h4>可积结构与方法</h4>",
        "<h4>创新</h4>",
        "展开研究内容与创新",
        "2026-07-15",
        "nlin.PS",
        "Darboux transformation",
        "arXiv</a>",
        "PDF</a>",
        "arXiv 提交日期",
        "2026-07-14",
        "（UTC）",
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

    math_card = render_radar.render_frontier_entry(
        papers["arxiv:2607.13773"],
        {**entry, "summary": r"在有限 \(n\) 层面得到结果。"},
    )
    assert '<span class="arithmatex">\\(n\\)</span>' in math_card

    old_entry = {
        **sample_entry("arxiv:old"),
        "signal_date": "2026-05-01",
        "arxiv_categories": [],
        "structure_tags": ["inverse scattering"],
    }
    frontier = {
        "checked_through": "2026-07-19",
        "entries": [entry, old_entry],
    }
    cumulative = render_radar.all_frontier_entries(frontier, papers)
    assert [item["paper_id"] for item in cumulative] == ["arxiv:2607.13773", "arxiv:old"]

    home = render_radar.render_frontier_home(
        {
            "weeks": [
                {
                    "id": "2026-W29",
                    "date_range": "2026-07-13 至 2026-07-19",
                    "summary": "测试周。",
                    "screening": {"selected": 2},
                }
            ],
            "frontier": frontier,
        },
        papers,
    )
    assert "这里精选近期" in home
    assert "2026-W29" in home
    assert "Multihump-Multivalley Soliton Families" in home
    assert "Old paper" in home
    assert "## 站内导航" in home
    assert 'class="radar-week-navigation"' in home
    assert 'data-radar-action="older"' in home
    assert 'data-radar-action="newer"' in home
    assert 'data-radar-action="all"' in home
    assert 'id="radar-paper-search"' in home
    assert "搜索标题、作者、标签或内容" in home
    assert 'class="radar-week-overview" data-radar-screening-week="2026-W29" hidden' in home
    assert "<strong>本周概览：</strong>测试周。" in home
    assert home.index("radar-week-overview") < home.index("radar-paper-card")
    assert 'data-default-week="2026-W29"' in home
    assert 'data-radar-week="2026-W29"' in home
    assert '.radar-search-heading}' in home
    assert 'data-radar-anchor="paper-' in home
    assert 'data-radar-month-group="2026-07"' in home
    assert "候选来源：" in home
    assert "## 数据来源与筛选" in home
    assert "Crossref" in home
    assert "普通网页搜索只用于查漏" in home
    assert "[数据与筛选方法](editorial-policy.md)" in home
    assert home.index("## 数据来源与筛选") > home.index("## 站内导航")
    assert "Exactly Solvable and Integrable Systems" not in home
    assert "推荐于" not in home

    javascript = (ROOT / "docs" / "javascripts" / "radar.js").read_text(encoding="utf-8")
    assert 'window.addEventListener("hashchange", activeHashHandler)' in javascript
    assert 'document.addEventListener("click", activePaperLinkHandler)' in javascript
    assert "card.dataset.radarWeek" in javascript
    assert 'card.scrollIntoView({ block: "start" })' in javascript

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
    assert "frontier_staging" not in data

    registry = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, registry)
    cumulative = render_radar.all_frontier_entries(frontier, registry)
    assert entries
    assert cumulative
    assert len({entry["paper_id"] for entry in entries}) == len(entries)

    # Freeze the confirmed migration baseline without blocking future daily updates.
    if frontier.get("checked_through") == "2026-07-20":
        expected_counts = {
            "2026-W25": 13,
            "2026-W26": 22,
            "2026-W27": 10,
            "2026-W28": 17,
            "2026-W29": 17,
            "2026-W30": 1,
        }
        assert len(entries) == 80
        assert len(cumulative) == 80
        assert Counter(render_radar.frontier_week_id(entry) for entry in entries) == expected_counts
        assert {week["id"] for week in data["frontier_weeks"]} == set(expected_counts)
        assert Counter(entry["signal_type"] for entry in entries) == {
            "new-preprint": 58,
            "journal-publication": 22,
        }


def main() -> None:
    test_component_contract()
    test_enabled_frontier()
    print("compact radar schema and enabled frontier tests passed")


if __name__ == "__main__":
    main()
