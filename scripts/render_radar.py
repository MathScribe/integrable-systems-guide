#!/usr/bin/env python3
"""Render the research-radar homepage and archives from YAML data."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "data" / "papers.yml"
EDITIONS_PATH = ROOT / "data" / "editions.yml"
HOME_PATH = ROOT / "docs" / "index.md"
ARCHIVE_INDEX_PATH = ROOT / "docs" / "radar" / "index.md"
LATEST_PATH = ROOT / "docs" / "radar" / "latest.md"

ROLE_LABELS = {
    "recent": "近期进展",
    "missed-recent": "近期漏读",
    "journal-version": "正式版本",
    "group-adjacent": "课题组相关",
    "method-background": "方法基础",
    "review-map": "综述地图",
    "backlog-core": "核心旧文",
    "adjacent": "相邻方向",
}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def paper_map() -> dict[str, dict[str, Any]]:
    papers = load_yaml(PAPERS_PATH)
    return {paper["id"]: paper for paper in papers}


def source_links(paper: dict[str, Any]) -> str:
    links: list[str] = []
    arxiv_id = paper.get("arxiv_id")
    if arxiv_id:
        version = paper.get("version") or ""
        label = f"arXiv:{arxiv_id}{version}"
        url = paper.get("url", "")
        if "arxiv.org" not in url:
            url = f"https://arxiv.org/abs/{arxiv_id}"
        links.append(f"[{label}]({url})")

    doi = paper.get("doi")
    if doi and not str(doi).lower().startswith("10.48550/arxiv"):
        journal = paper.get("journal")
        label = f"{journal}, doi:{doi}" if journal else f"doi:{doi}"
        links.append(f"[{label}](https://doi.org/{doi})")

    if not links:
        links.append(f"[source]({paper['url']})")
    return " · ".join(links)


def date_label(paper: dict[str, Any]) -> str:
    submitted = paper.get("submitted")
    updated = paper.get("updated")
    if submitted and updated and submitted != updated:
        return f"提交 {submitted}，修订 {updated}"
    if submitted:
        return f"提交 {submitted}"
    if paper.get("year"):
        return str(paper["year"])
    return ""


def compact(text: str) -> str:
    return " ".join(str(text).split())


def tag_line(paper: dict[str, Any], role: str, limit: int = 5) -> str:
    tags = [ROLE_LABELS[role], *paper.get("tags", [])[:limit]]
    return " ".join(f"`{tag}`" for tag in tags)


def render_entry(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    authors = ", ".join(paper["authors"])
    metadata = f"{authors} · {source_links(paper)}"
    dates = date_label(paper)
    if dates:
        metadata += f" · {dates}"
    return "\n".join(
        [
            f"### {paper['title']}",
            "",
            metadata + "  ",
            tag_line(paper, entry["role"]),
            "",
            f"**做了什么。** {compact(entry['what_it_does'])}",
            "",
            f"**为什么值得读。** {compact(entry['why_read'])}",
        ]
    )


def render_week(week: dict[str, Any], editions: list[dict[str, Any]], papers: dict[str, dict[str, Any]]) -> str:
    sections = [
        f"# 研究雷达归档 · {week['id']}",
        "",
        "[全部归档](index.md) · [返回首页](../index.md)",
        "",
        f"{week['date_range']} · {compact(week['summary'])}",
        "",
    ]
    for edition in sorted(editions, key=lambda item: item["date"], reverse=True):
        roles = [ROLE_LABELS[entry["role"]] for entry in edition["entries"]]
        role_summary = " ".join(f"`{role}`" for role in dict.fromkeys(roles))
        sections.extend(
            [
                f"## {edition['date']}",
                "",
                f"{len(edition['entries'])} 篇 · {role_summary}",
                "",
                compact(edition["summary"]),
                "",
            ]
        )
        for entry in edition["entries"]:
            sections.extend([render_entry(papers[entry["paper_id"]], entry), ""])
        sections.extend(["---", ""])
    if sections[-2:] == ["---", ""]:
        sections = sections[:-2]
    return "\n".join(sections).rstrip() + "\n"


def homepage_items(editions: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen: set[str] = set()
    for edition in sorted(editions, key=lambda item: item["date"], reverse=True)[:3]:
        ranked = sorted(
            (entry for entry in edition["entries"] if entry.get("homepage_rank") is not None),
            key=lambda entry: entry["homepage_rank"],
        )[:3]
        for entry in ranked:
            if entry["paper_id"] in seen:
                continue
            selected.append((edition, entry))
            seen.add(entry["paper_id"])
            if len(selected) == 8:
                return selected
    return selected


def render_home(editions: list[dict[str, Any]], papers: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# 可积系统研究雷达",
        "",
        "面向 DNLS、耦合与多分量 NLS、IST、Riemann--Hilbert 方法、长时渐近、有限带解和非线性波的持续阅读入口。",
        "",
        "[研究雷达归档](radar/index.md) · [资源](resources.md) · [核心主题](topics.md) · [课题组相关](group-work.md)",
        "",
        "## 近期推荐",
        "",
        "这里汇总最近三期中优先级较高的论文，而不是重复展示当天简报。详细注释和完整推荐历史保存在周归档中。",
        "",
    ]
    for edition, entry in homepage_items(editions):
        paper = papers[entry["paper_id"]]
        authors = ", ".join(paper["authors"])
        lines.extend(
            [
                f"### {paper['title']}",
                "",
                f"{authors} · {source_links(paper)}  ",
                tag_line(paper, entry["role"], limit=3),
                "",
                compact(entry["what_it_does"]),
                "",
                f"推荐于 {edition['date']} · [查看详细说明](radar/{edition['week']}.md#{edition['date']})",
                "",
            ]
        )
    lines.extend(
        [
            "## 其他入口",
            "",
            "- [Resources / 资源](resources.md)：课程、讲义、研究者主页和检索入口。",
            "- [Group work / 课题组相关](group-work.md)：本地研究背景、公开笔记和相关链接。",
            "- [Core topics / 核心主题](topics.md)：本站目前关注的方程、方法和非线性波主题。",
            "- [About / 关于](about.md)：策展原则、元数据政策、AI 使用和许可证说明。",
            "",
            "推荐日期表示本站收录时间，不等同于论文发表日期。元数据核对和 AI 使用说明见 [About / 关于](about.md)。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_archive_index(weeks: list[dict[str, Any]], editions: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = defaultdict(int)
    paper_ids: dict[str, set[str]] = defaultdict(set)
    for edition in editions:
        counts[edition["week"]] += 1
        paper_ids[edition["week"]].update(entry["paper_id"] for entry in edition["entries"])

    lines = [
        "# 研究雷达归档",
        "",
        "归档按周组织；每日推荐日期保留在周页面中，用于追溯当时的编辑选择。",
        "",
        "[返回首页](../index.md)",
        "",
    ]
    by_year: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for week in weeks:
        by_year[week["id"].split("-W", 1)[0]].append(week)
    for year in sorted(by_year, reverse=True):
        lines.extend([f"## {year}", ""])
        for week in sorted(by_year[year], key=lambda item: item["id"], reverse=True):
            tags = " ".join(f"`{tag}`" for tag in week.get("tags", []))
            lines.extend(
                [
                    f"### {week['id']} · {week['date_range']}",
                    "",
                    f"{counts[week['id']]} 期 · {len(paper_ids[week['id']])} 篇",
                    "",
                    tags,
                    "",
                    compact(week["summary"]),
                    "",
                    f"[查看本周完整归档]({week['id']}.md)",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def render_latest(editions: list[dict[str, Any]]) -> str:
    latest = max(editions, key=lambda item: item["date"])
    return (
        "# 最新研究雷达条目\n\n"
        "本站不再维护一份与周归档重复的完整“最新简报”。\n\n"
        f"最新一期：[{latest['date']}]({latest['week']}.md#{latest['date']})。\n\n"
        "也可以直接查看 [研究雷达归档](index.md) 或返回 [首页](../index.md)。\n"
    )


def expected_outputs() -> dict[Path, str]:
    data = load_yaml(EDITIONS_PATH)
    papers = paper_map()
    weeks = data["weeks"]
    editions = data["editions"]
    outputs = {
        HOME_PATH: render_home(editions, papers),
        ARCHIVE_INDEX_PATH: render_archive_index(weeks, editions),
        LATEST_PATH: render_latest(editions),
    }
    editions_by_week: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edition in editions:
        editions_by_week[edition["week"]].append(edition)
    for week in weeks:
        path = ROOT / "docs" / "radar" / f"{week['id']}.md"
        outputs[path] = render_week(week, editions_by_week[week["id"]], papers)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()

    stale: list[str] = []
    for path, content in expected_outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("generated radar pages are stale: " + ", ".join(stale))


if __name__ == "__main__":
    main()
