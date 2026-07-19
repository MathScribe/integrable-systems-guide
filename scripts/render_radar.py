#!/usr/bin/env python3
"""Render the research-radar homepage and archives from YAML data.

The renderer supports two schemas during the migration:

* the legacy daily-edition schema, whose generated output is kept unchanged;
* the compact 30-day ``frontier`` schema, which emits native paper cards and
  expandable research annotations without relying on JavaScript.
"""

from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from datetime import date, timedelta
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

SIGNAL_LABELS = {
    "new-preprint": "新预印本",
    "major-revision": "重大修订",
    "journal-publication": "正式发表",
}

ARXIV_CATEGORY_RE = re.compile(r"^[a-z-]+(?:\.[A-Z]{2})?$")


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
    value = " ".join(str(text).split())
    return re.sub(
        r"(?<=[\u3400-\u9fff，。；：！？、）】》]) (?=[\u3400-\u9fff（【《])",
        "",
        value,
    )


def tag_line(paper: dict[str, Any], role: str, limit: int = 5) -> str:
    tags = [ROLE_LABELS[role], *paper.get("tags", [])[:limit]]
    return " ".join(f"`{tag}`" for tag in tags)


def render_entry(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    """Render one legacy entry without changing the historical output."""
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
        "最新论文：[arXiv · Exactly Solvable and Integrable Systems](https://arxiv.org/list/nlin.SI/recent) · [arXiv · Pattern Formation and Solitons](https://arxiv.org/list/nlin.PS/recent)",
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
            "- [Resources / 资源](resources.md)：最新论文、文献检索、课程讲义和研究资料入口。",
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


# ---------------------------------------------------------------------------
# Compact 30-day schema
# ---------------------------------------------------------------------------


def parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date: {value!r}") from exc


def validate_frontier_entry(entry: dict[str, Any], papers: dict[str, dict[str, Any]]) -> None:
    required = (
        "paper_id",
        "signal_date",
        "signal_type",
        "summary",
        "main_result",
        "integrable_structure",
        "innovation",
    )
    missing = [field for field in required if not compact(entry.get(field, ""))]
    if missing:
        raise ValueError(f"frontier entry {entry.get('paper_id', '<unknown>')} missing: {', '.join(missing)}")

    paper_id = entry["paper_id"]
    if paper_id not in papers:
        raise ValueError(f"frontier entry references unknown paper_id: {paper_id}")

    parse_iso_date(entry["signal_date"], f"{paper_id}.signal_date")
    signal_type = entry["signal_type"]
    if signal_type not in SIGNAL_LABELS:
        raise ValueError(f"{paper_id}.signal_type is invalid: {signal_type}")

    categories = entry.get("arxiv_categories", [])
    if len(categories) > 2:
        raise ValueError(f"{paper_id} has more than two displayed arXiv categories")
    for category in categories:
        if not ARXIV_CATEGORY_RE.fullmatch(str(category)):
            raise ValueError(f"{paper_id} has invalid arXiv category: {category}")

    tags = entry.get("structure_tags", [])
    if len(tags) > 2:
        raise ValueError(f"{paper_id} has more than two displayed structure tags")


def validate_frontier(frontier: dict[str, Any], papers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    entries = frontier.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("frontier.entries must be a non-empty list")

    seen: set[str] = set()
    for entry in entries:
        validate_frontier_entry(entry, papers)
        paper_id = entry["paper_id"]
        if paper_id in seen:
            raise ValueError(f"frontier contains duplicate paper_id: {paper_id}")
        seen.add(paper_id)
    return entries


def source_links_html(paper: dict[str, Any]) -> str:
    links: list[str] = []
    arxiv_id = paper.get("arxiv_id")
    if arxiv_id:
        abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        links.append(f'<a href="{html.escape(abs_url, quote=True)}">arXiv</a>')
        links.append(f'<a href="{html.escape(pdf_url, quote=True)}">PDF</a>')

    doi = paper.get("doi")
    if doi and not str(doi).lower().startswith("10.48550/arxiv"):
        doi_url = f"https://doi.org/{doi}"
        links.append(f'<a href="{html.escape(doi_url, quote=True)}">DOI / 期刊</a>')

    if not links:
        links.append(f'<a href="{html.escape(str(paper["url"]), quote=True)}">来源</a>')
    return " · ".join(links)


def render_html_tags(entry: dict[str, Any]) -> str:
    tags = [*entry.get("arxiv_categories", [])[:2], *entry.get("structure_tags", [])[:2]]
    return " ".join(f"<code>{html.escape(str(tag))}</code>" for tag in tags)


def render_frontier_entry(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    authors = ", ".join(paper["authors"])
    signal_label = SIGNAL_LABELS[entry["signal_type"]]
    tags = render_html_tags(entry)
    tag_paragraph = f'  <p class="radar-paper-tags">{tags}</p>\n' if tags else ""
    return (
        '<article class="radar-paper-card radar-paper-card--native" data-radar-native="true">\n'
        f'  <p class="radar-paper-date"><time datetime="{html.escape(entry["signal_date"], quote=True)}">'
        f'{html.escape(entry["signal_date"])}</time> · {html.escape(signal_label)}</p>\n'
        f"{tag_paragraph}"
        f'  <h3>{html.escape(str(paper["title"]))}</h3>\n'
        f'  <p class="radar-paper-meta">{html.escape(authors)} · {source_links_html(paper)}</p>\n'
        f'  <p class="radar-paper-overview">{html.escape(compact(entry["summary"]))}</p>\n'
        '  <details class="radar-paper-details">\n'
        '    <summary>展开研究内容与创新</summary>\n'
        '    <div class="radar-paper-detail-grid">\n'
        '      <section>\n'
        '        <h4>研究问题与主要结果</h4>\n'
        f'        <p>{html.escape(compact(entry["main_result"]))}</p>\n'
        '      </section>\n'
        '      <section>\n'
        '        <h4>可积结构与方法</h4>\n'
        f'        <p>{html.escape(compact(entry["integrable_structure"]))}</p>\n'
        '      </section>\n'
        '      <section>\n'
        '        <h4>创新</h4>\n'
        f'        <p>{html.escape(compact(entry["innovation"]))}</p>\n'
        '      </section>\n'
        '    </div>\n'
        '  </details>\n'
        '</article>'
    )


def frontier_week_id(entry: dict[str, Any]) -> str:
    if entry.get("week"):
        return str(entry["week"])
    signal_date = parse_iso_date(entry["signal_date"], "signal_date")
    iso_year, iso_week, _ = signal_date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def visible_frontier_entries(frontier: dict[str, Any], papers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    entries = validate_frontier(frontier, papers)
    latest_value = frontier.get("generated_through") or max(entry["signal_date"] for entry in entries)
    latest = parse_iso_date(str(latest_value), "frontier.generated_through")
    window_days = int(frontier.get("window_days", 30))
    if window_days < 1:
        raise ValueError("frontier.window_days must be positive")
    first = latest - timedelta(days=window_days - 1)
    return sorted(
        (entry for entry in entries if first <= parse_iso_date(entry["signal_date"], "signal_date") <= latest),
        key=lambda entry: (entry["signal_date"], entry["paper_id"]),
        reverse=True,
    )


def render_frontier_home(data: dict[str, Any], papers: dict[str, dict[str, Any]]) -> str:
    frontier = data["frontier"]
    entries = visible_frontier_entries(frontier, papers)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[frontier_week_id(entry)].append(entry)

    week_map = {week["id"]: week for week in data.get("weeks", [])}
    window_days = int(frontier.get("window_days", 30))
    lines = [
        "# 可积系统研究雷达",
        "",
        "面向可积系统读者，关注最近出现的强创新、新方向和新方法。主题边界保持宽松，但每篇都必须能够说明可积结构怎样参与主要结果。",
        "",
        f"当前显示最近 {window_days} 天的论文事件；日期指首次公开、重大修订或首次正式在线发表，而不是本站收录日期。",
        "",
        "论文说明由自动流程整理，并经元数据核验；除特别标注外，不代表编辑已经完整阅读或逐句审校。",
        "",
        "[研究雷达归档](radar/index.md) · [资源](resources.md) · [核心主题](topics.md) · [课题组相关](group-work.md)",
        "",
    ]
    for week_id in sorted(grouped, reverse=True):
        week = week_map.get(week_id, {})
        heading = week.get("date_range", week_id)
        lines.extend([f"## {week_id} · {heading}", "", f"{len(grouped[week_id])} 篇", ""])
        for entry in grouped[week_id]:
            lines.extend([render_frontier_entry(papers[entry["paper_id"]], entry), ""])
    return "\n".join(lines).rstrip() + "\n"


def screening_note(screening: dict[str, Any]) -> list[str]:
    if not screening:
        return []
    lines = ["## 本周筛选说明", ""]
    sources = screening.get("sources_checked", [])
    if sources:
        lines.extend(["检查来源：" + "；".join(compact(source) for source in sources) + "。", ""])
    count_fields = [
        ("raw_candidates", "去重候选"),
        ("title_screened", "标题筛选"),
        ("abstract_screened", "摘要筛选"),
        ("selected", "最终收录"),
    ]
    counts = [f"{label} {screening[field]}" for field, label in count_fields if field in screening]
    if counts:
        lines.extend(["；".join(counts) + "。", ""])
    if screening.get("coverage_note"):
        lines.extend([compact(screening["coverage_note"]), ""])
    return lines


def render_frontier_week(
    week: dict[str, Any], entries: list[dict[str, Any]], papers: dict[str, dict[str, Any]]
) -> str:
    lines = [
        f"# 研究雷达归档 · {week['id']}",
        "",
        "[全部归档](index.md) · [返回首页](../index.md)",
        "",
        f"{week.get('date_range', week['id'])} · {compact(week.get('summary', ''))}",
        "",
        f"本周收录 {len(entries)} 篇。",
        "",
    ]
    for entry in sorted(entries, key=lambda item: (item["signal_date"], item["paper_id"]), reverse=True):
        lines.extend([render_frontier_entry(papers[entry["paper_id"]], entry), ""])
    lines.extend(screening_note(week.get("screening", {})))
    return "\n".join(lines).rstrip() + "\n"


def render_frontier_archive_index(
    weeks: list[dict[str, Any]], entries: list[dict[str, Any]]
) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[frontier_week_id(entry)].append(entry)
    week_map = {week["id"]: week for week in weeks}
    lines = [
        "# 研究雷达归档",
        "",
        "归档按论文实际事件日期分周组织。周页面只展示最终收录论文和聚合筛选信息。",
        "",
        "[返回首页](../index.md)",
        "",
    ]
    by_year: dict[str, list[str]] = defaultdict(list)
    for week_id in grouped:
        by_year[week_id.split("-W", 1)[0]].append(week_id)
    for year in sorted(by_year, reverse=True):
        lines.extend([f"## {year}", ""])
        for week_id in sorted(by_year[year], reverse=True):
            week = week_map.get(week_id, {})
            date_range = week.get("date_range", week_id)
            summary = compact(week.get("summary", ""))
            lines.extend(
                [
                    f"### {week_id} · {date_range}",
                    "",
                    f"{len(grouped[week_id])} 篇",
                    "",
                ]
            )
            if summary:
                lines.extend([summary, ""])
            lines.extend([f"[查看本周论文]({week_id}.md)", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_frontier_latest(entries: list[dict[str, Any]]) -> str:
    latest = max(entries, key=lambda entry: (entry["signal_date"], entry["paper_id"]))
    week_id = frontier_week_id(latest)
    return (
        "# 最新研究雷达条目\n\n"
        "最新论文直接显示在首页；这里仅保留旧链接的兼容入口。\n\n"
        f"当前最新事件日期为 {latest['signal_date']}，见 [{week_id}]({week_id}.md)。\n\n"
        "也可以查看 [研究雷达归档](index.md) 或返回 [首页](../index.md)。\n"
    )


def expected_outputs() -> dict[Path, str]:
    data = load_yaml(EDITIONS_PATH)
    papers = paper_map()

    if data.get("frontier"):
        entries = visible_frontier_entries(data["frontier"], papers)
        weeks = data.get("weeks", [])
        outputs = {
            HOME_PATH: render_frontier_home(data, papers),
            ARCHIVE_INDEX_PATH: render_frontier_archive_index(weeks, entries),
            LATEST_PATH: render_frontier_latest(entries),
        }
        entries_by_week: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in entries:
            entries_by_week[frontier_week_id(entry)].append(entry)
        week_map = {week["id"]: week for week in weeks}
        for week_id, week_entries in entries_by_week.items():
            week = week_map.get(week_id, {"id": week_id, "date_range": week_id, "summary": ""})
            path = ROOT / "docs" / "radar" / f"{week_id}.md"
            outputs[path] = render_frontier_week(week, week_entries, papers)
        return outputs

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
