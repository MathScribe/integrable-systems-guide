#!/usr/bin/env python3
"""Regression tests for the cumulative compact radar and confirmed sample."""

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
VALIDATE_SPEC = importlib.util.spec_from_file_location(
    "validate_radar", ROOT / "scripts" / "validate_radar.py"
)
if VALIDATE_SPEC is None or VALIDATE_SPEC.loader is None:
    raise RuntimeError("cannot load scripts/validate_radar.py")
validate_radar = importlib.util.module_from_spec(VALIDATE_SPEC)
VALIDATE_SPEC.loader.exec_module(validate_radar)


def sample_entry(paper_id: str = "arxiv:2607.13773") -> dict[str, object]:
    return {
        "paper_id": paper_id,
        "signal_date": "2026-07-15",
        "signal_type": "new-preprint",
        "directions": ["waves", "structures"],
        "reading_note": {
            "lead": "构造平面波背景上的任意多峰多谷孤子族。",
            "detail": "分类基本解形态并构造任意 K-hump 与 M-valley 混合结构。",
            "method_scope": "两分量 Fokas–Lenells 系统的 N-fold Darboux 变换。",
        },
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
            "keywords": ["Darboux transformation", "topological vector potential"],
            "arxiv_categories": ["nlin.PS", "nlin.SI"],
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
        'class="radar-reading-detail"',
        'class="radar-reading-method"',
        "方法与范围",
        'class="radar-row-summary"',
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
        {**entry, "reading_note": {**entry["reading_note"], "lead": r"在有限 \(n\) 层面得到结果。"}},
    )
    assert '<span class="arithmatex">\\(n\\)</span>' in math_card

    old_entry = {
        **sample_entry("arxiv:old"),
        "signal_date": "2026-05-01",
    }
    frontier = {
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
    assert "2026-W29" not in home
    assert "Multihump-Multivalley Soliton Families" in home
    assert "Old paper" in home
    assert "## 站内导航" in home
    assert 'class="radar-browse-controls"' in home
    assert 'data-radar-action="previous"' in home
    assert 'data-radar-action="next"' in home
    assert 'data-radar-action="reset"' in home
    assert 'id="radar-paper-search"' in home
    assert "搜索论文、作者、方程或方法" in home
    assert "radar-week-overview" not in home
    assert "本周概览" not in home
    assert "data-radar-week-option" not in home
    assert 'data-earliest-date="2026-05-01"' in home
    assert "当前收录：2026.05—2026.07" in home
    assert "全部已收录" in home
    assert 'value="spectral">散射与谱方法' in home
    assert 'value="asymptotics">渐近与统计' in home
    assert 'data-default-period="all"' in home
    assert 'data-radar-directions=' in home
    assert '.radar-search-heading}' in home
    assert 'data-radar-anchor="paper-' in home
    assert 'data-radar-date="2026-07-15"' in home
    assert "论文来自 arXiv 与期刊记录" in home
    assert 'id="radar-time-filter"' in home
    assert 'id="radar-topic-filter"' in home
    assert 'target="_blank" rel="noopener noreferrer"' in home
    assert card.index('</summary>') < card.index('class="radar-paper-overview"')
    assert '<details class="radar-paper-details" open' not in card
    assert '<h4>创新</h4>' not in card
    assert 'data-radar-search=' in card
    note_entry = {**entry, "reading_note": {
        "lead": "主结论 < 带条件的结论", "detail": "结果细节", "method_scope": "仅在小数据下成立",
    }}
    render_radar.validate_frontier_entry(note_entry, papers)
    note_card = render_radar.render_frontier_entry(papers[entry["paper_id"]], note_entry)
    assert "主结论 &lt; 带条件的结论" in note_card
    assert "仅在小数据下成立" in note_card
    assert 'class="radar-paper-meta"' not in note_card
    try:
        render_radar.validate_frontier_entry({**entry, "reading_note": {"lead": "不完整"}}, papers)
    except ValueError as exc:
        assert "reading_note" in str(exc)
    else:
        raise AssertionError("an incomplete reading note should be rejected")
    assert "## 数据来源与筛选" in home
    assert "Crossref" in home
    assert "[数据来源](sources.md)" in home
    assert "[数据与筛选方法](editorial-policy.md)" in home
    assert home.index("## 数据来源与筛选") > home.index("## 站内导航")
    assert "Exactly Solvable and Integrable Systems" not in home
    assert "推荐于" not in home

    javascript = (ROOT / "docs" / "javascripts" / "radar.js").read_text(encoding="utf-8")
    assert 'window.addEventListener("hashchange", onHashChange)' in javascript
    assert 'window.addEventListener("popstate", onPopState)' in javascript
    assert "card.dataset.radarDirections" in javascript
    assert 'target.card.scrollIntoView({ block: "start" })' in javascript

    invalid = {**entry, "directions": ["spectral", "waves", "structures"]}
    try:
        render_radar.validate_frontier_entry(invalid, papers)
    except ValueError as exc:
        assert "one or two" in str(exc)
    else:
        raise AssertionError("three directions should be rejected")

    withdrawn_papers = {**papers, entry["paper_id"]: {**papers[entry["paper_id"]], "status": "withdrawn"}}
    try:
        render_radar.validate_frontier_entry(entry, withdrawn_papers)
    except ValueError as exc:
        assert "withdrawn" in str(exc)
    else:
        raise AssertionError("a withdrawn paper must not remain publicly selected")


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

    assert "checked_through" not in frontier
    assert data["schema_version"] == 2
    assert "frontier_weeks" not in data
    assert len(cumulative) == len(entries)
    assert all(entry.get("reading_note") or registry[entry["paper_id"]].get("doi") for entry in entries)
    assert {entry["signal_type"] for entry in entries} <= {
        "new-preprint",
        "major-revision",
        "journal-publication",
    }


def test_bibliography_without_event_date() -> None:
    paper = {"id": "doi:10.1000/test", "title": "Journal example", "authors": ["Ada Example"],
             "url": "https://doi.org/10.1000/test", "doi": "10.1000/test", "journal": "Journal", "year": 2027}
    entry = {"paper_id": paper["id"], "signal_date": None, "signal_type": "journal-publication",
             "added_on": "2026-09-27", "event_source": paper["url"], "directions": ["waves"]}
    papers = {paper["id"]: paper}
    render_radar.validate_frontier_entry(entry, papers)
    card = render_radar.render_frontier_entry(paper, entry)
    assert '<details' not in card and 'radar-expand-icon' not in card
    assert '<time' not in card and 'None' not in card
    assert 'data-radar-date=""' in card and 'data-radar-added-on="2026-09-27"' in card
    assert 'Journal (2027)' in card and 'Ada Example' in card
    dated = {**entry, "paper_id": "dated", "signal_date": "2026-09-26", "added_on": "2026-09-28"}
    ordered = render_radar.all_frontier_entries({"entries": [dated, entry]}, {**papers, "dated": {**paper, "id": "dated"}})
    assert ordered[0] == entry  # A known event keeps its date, regardless of intake.
    assert '<time datetime="2026-09-26"' in render_radar.render_frontier_entry(paper, dated)
    for invalid in ({**entry, "added_on": None}, {**entry, "signal_type": "new-preprint"},
                    {**entry, "signal_date": ""}, {**entry, "reading_note": {}},
                    {k: v for k, v in entry.items() if k != "event_source"}):
        try:
            render_radar.validate_frontier_entry(invalid, papers)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted incomplete bibliography fallback: {invalid}")
    try:
        render_radar.validate_frontier_entry(entry, {paper["id"]: {**paper, "doi": None}})
    except ValueError:
        pass
    else:
        raise AssertionError("bibliography-only selection requires a journal DOI")


def test_bibliographic_date_and_version_validation() -> None:
    paper = {
        "id": "arxiv:2608.12345",
        "title": "A validation fixture",
        "authors": ["Ada Example"],
        "url": "https://arxiv.org/abs/2608.12345",
        "arxiv_id": "2608.12345",
        "submitted": "2026-08-20",
        "updated": "2026-08-22",
        "version": "v2",
        "metadata_checked_at": "2026-08-23",
    }
    assert validate_radar.validate_papers([paper]) == 1

    invalid_cases = (
        ({**paper, "updated": "2026-08-19"}, "precedes"),
        ({**paper, "version": "2"}, "invalid arXiv version"),
        ({**paper, "submitted": "2026/08/20"}, "ISO date"),
    )
    for invalid, expected_message in invalid_cases:
        try:
            validate_radar.validate_papers([invalid])
        except ValueError as exc:
            assert expected_message in str(exc)
        else:
            raise AssertionError(f"invalid bibliographic metadata accepted: {invalid}")


def main() -> None:
    test_component_contract()
    test_enabled_frontier()
    test_bibliographic_date_and_version_validation()
    test_bibliography_without_event_date()
    group_page = render_radar.render_group_work(render_radar.load_yaml(ROOT / "data" / "group-work.yml"))
    for retained in ("data-group-papers", "MathSciNet", "Google Scholar", "Semantic Scholar", "arxiv.org/search", "Public notes", "courseNotes", "Reading projects"):
        assert retained in group_page, f"group page lost existing content: {retained}"
    print("compact radar schema and enabled frontier tests passed")


if __name__ == "__main__":
    main()
