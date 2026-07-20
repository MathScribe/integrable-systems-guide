#!/usr/bin/env python3
"""Render the cumulative research-radar homepage."""

from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "data" / "papers.yml"
EDITIONS_PATH = ROOT / "data" / "editions.yml"
HOME_PATH = ROOT / "docs" / "index.md"

SIGNAL_LABELS = {
    "new-preprint": "新预印本",
    "major-revision": "重大修订",
    "journal-publication": "正式发表",
}

ARXIV_CATEGORY_RE = re.compile(r"^[a-z-]+(?:\.(?:[A-Z]{2}|[a-z-]+))?$")
MATH_TOKEN_RE = re.compile(r"(\\\(.+?\\\)|\\\[.+?\\\]|(?<!\\)\$(?!\$).+?(?<!\\)\$)")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def paper_map() -> dict[str, dict[str, Any]]:
    papers = load_yaml(PAPERS_PATH)
    return {paper["id"]: paper for paper in papers}


def compact(text: str) -> str:
    value = " ".join(str(text).split())
    return re.sub(
        r"(?<=[\u3400-\u9fff，。；：！？、）】》]) (?=[\u3400-\u9fff（【《])",
        "",
        value,
    )


# ---------------------------------------------------------------------------
# Cumulative frontier schema
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

    checked_through = parse_iso_date(frontier.get("checked_through"), "frontier.checked_through")
    latest_signal = max(parse_iso_date(entry["signal_date"], "signal_date") for entry in entries)
    if checked_through < latest_signal:
        raise ValueError("frontier.checked_through cannot precede the latest signal_date")
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
        journal = compact(str(paper.get("journal") or "DOI / 期刊"))
        citation_parts = [str(value) for value in (paper.get("volume"), paper.get("article_number") or paper.get("pages")) if value]
        citation = ", ".join(citation_parts)
        year = paper.get("year")
        journal_label = journal
        if citation:
            journal_label += f" {citation}"
        if year:
            journal_label += f" ({year})"
        links.append(
            f'<a href="{html.escape(doi_url, quote=True)}">{html.escape(journal_label)}</a>'
        )

    if not links:
        links.append(f'<a href="{html.escape(str(paper["url"]), quote=True)}">来源</a>')
    return " · ".join(links)


def render_html_tags(entry: dict[str, Any]) -> str:
    tags = [*entry.get("arxiv_categories", [])[:2], *entry.get("structure_tags", [])[:2]]
    return " ".join(f"<code>{html.escape(str(tag))}</code>" for tag in tags)


def render_rich_text(value: Any) -> str:
    """Escape prose while preserving MathJax delimiters inside raw HTML cards."""
    text = compact(str(value))
    parts = MATH_TOKEN_RE.split(text)
    return "".join(
        f'<span class="arithmatex">{html.escape(part)}</span>'
        if MATH_TOKEN_RE.fullmatch(part)
        else html.escape(part)
        for part in parts
    )


def html_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def short_date_range(value: str) -> str:
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2}) 至 \d{4}-(\d{2})-(\d{2})", value)
    if not match:
        return value
    _, start_month, start_day, end_month, end_day = match.groups()
    if start_month == end_month:
        return f"{int(start_month)} 月 {int(start_day)}–{int(end_day)} 日"
    return f"{int(start_month)} 月 {int(start_day)} 日–{int(end_month)} 月 {int(end_day)} 日"


def render_frontier_entry(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    authors = ", ".join(paper["authors"])
    signal_label = SIGNAL_LABELS[entry["signal_type"]]
    tags = render_html_tags(entry)
    tag_paragraph = f'  <p class="radar-paper-tags">{tags}</p>\n' if tags else ""
    anchor = f'paper-{html_id(entry["paper_id"])}'
    week_id = frontier_week_id(entry)
    month_id = entry["signal_date"][:7]
    source_date_note = ""
    if (
        entry["signal_type"] == "new-preprint"
        and paper.get("submitted")
        and paper["submitted"] != entry["signal_date"]
    ):
        source_date_note = (
            f' · arXiv 提交日期 <time datetime="{html.escape(str(paper["submitted"]), quote=True)}">'
            f'{html.escape(str(paper["submitted"]))}</time>（UTC）'
        )
    elif (
        entry["signal_type"] == "major-revision"
        and paper.get("updated")
        and paper["updated"] != entry["signal_date"]
    ):
        source_date_note = (
            f' · arXiv 修订日期 <time datetime="{html.escape(str(paper["updated"]), quote=True)}">'
            f'{html.escape(str(paper["updated"]))}</time>（UTC）'
        )
    return (
        f'<article id="{anchor}" class="radar-paper-card radar-paper-card--native" data-radar-native="true" '
        f'data-radar-week="{html.escape(week_id, quote=True)}" '
        f'data-radar-month="{html.escape(month_id, quote=True)}">\n'
        f'  <p class="radar-paper-date"><time datetime="{html.escape(entry["signal_date"], quote=True)}">'
        f'{html.escape(entry["signal_date"])}</time> · {html.escape(signal_label)}{source_date_note}</p>\n'
        f"{tag_paragraph}"
        f'  <h3>{render_rich_text(paper["title"])}</h3>\n'
        f'  <p class="radar-paper-meta">{html.escape(authors)} · {source_links_html(paper)}</p>\n'
        f'  <p class="radar-paper-overview">{render_rich_text(entry["summary"])}</p>\n'
        '  <details class="radar-paper-details">\n'
        '    <summary>展开研究内容与创新</summary>\n'
        '    <div class="radar-paper-detail-grid">\n'
        '      <section>\n'
        '        <h4>研究问题与主要结果</h4>\n'
        f'        <p>{render_rich_text(entry["main_result"])}</p>\n'
        '      </section>\n'
        '      <section>\n'
        '        <h4>可积结构与方法</h4>\n'
        f'        <p>{render_rich_text(entry["integrable_structure"])}</p>\n'
        '      </section>\n'
        '      <section>\n'
        '        <h4>创新</h4>\n'
        f'        <p>{render_rich_text(entry["innovation"])}</p>\n'
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


def all_frontier_entries(frontier: dict[str, Any], papers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        validate_frontier(frontier, papers),
        key=lambda entry: (entry["signal_date"], entry["paper_id"]),
        reverse=True,
    )


def render_screening_details(week: dict[str, Any]) -> str:
    screening = week.get("screening", {})
    if not screening:
        return ""
    paragraphs: list[str] = []
    if week.get("summary"):
        paragraphs.append(compact(week["summary"]))
    body = " ".join(render_rich_text(paragraph) for paragraph in paragraphs)
    week_id = str(week["id"])
    return (
        f'<p class="radar-week-overview" data-radar-screening-week="{html.escape(week_id, quote=True)}" hidden>'
        f'<strong>本周概览：</strong>{body}</p>'
    )


def render_frontier_home(data: dict[str, Any], papers: dict[str, dict[str, Any]]) -> str:
    frontier = data["frontier"]
    entries = all_frontier_entries(frontier, papers)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[frontier_week_id(entry)].append(entry)

    week_map = {week["id"]: week for week in data.get("frontier_weeks", data.get("weeks", []))}
    week_ids = sorted(grouped, reverse=True)
    week_metadata = "\n".join(
        f'  <span hidden data-radar-week-option="{html.escape(week_id, quote=True)}" '
        f'data-label="{html.escape(week_id.replace("-W", " 年第 ") + " 周 · " + short_date_range(week_map.get(week_id, {}).get("date_range", week_id)), quote=True)}" '
        f'data-count="{len(grouped[week_id])}"></span>'
        for week_id in week_ids
    )
    lines = [
        "# 可积系统研究雷达",
        "",
        "这里精选近期可积系统及相关数学物理方向的新论文，重点呈现值得关注的新结构、新方法和新结果。",
        "",
        "论文按首次公开、重大修订或正式发表日期排序。每条包括简要概览和可展开说明；内容由自动流程整理，数学结论请以原论文为准。",
        "",
        "候选来源：[arXiv nlin.SI](https://arxiv.org/list/nlin.SI/recent) · [arXiv nlin.PS](https://arxiv.org/list/nlin.PS/recent)，并通过跨分类检索、Crossref、期刊 online-first 页面和出版商记录补充与核验。",
        "",
        f'<div class="radar-week-navigation" data-default-week="{html.escape(week_ids[0], quote=True)}" '
        f'data-total-count="{len(entries)}">',
        '  <button type="button" data-radar-action="older">← 较早一周</button>',
        '  <span class="radar-week-current" aria-live="polite"></span>',
        '  <button type="button" data-radar-action="newer">较新一周 →</button>',
        '  <button type="button" class="radar-show-all" data-radar-action="all">查看全部</button>',
        '  <div class="radar-local-search" role="search">',
        '    <label for="radar-paper-search">搜索论文</label>',
        '    <input id="radar-paper-search" type="search" placeholder="搜索标题、作者、标签或内容" autocomplete="off">',
        '    <span class="radar-search-count" aria-live="polite"></span>',
        '  </div>',
        f"{week_metadata}",
        "</div>",
        "",
    ]
    for week_id in week_ids:
        screening = render_screening_details(week_map.get(week_id, {"id": week_id}))
        if screening:
            lines.extend([screening, ""])

    rendered_month: str | None = None
    for week_id in week_ids:
        for entry in grouped[week_id]:
            month_id = entry["signal_date"][:7]
            if month_id != rendered_month:
                year, month = month_id.split("-", 1)
                lines.extend(
                    [
                        f'<p id="month-{month_id}" class="radar-month-label" '
                        f'data-radar-month-group="{month_id}">{int(year)} 年 {int(month)} 月</p>',
                        "",
                    ]
                )
                rendered_month = month_id
            lines.extend([render_frontier_entry(papers[entry["paper_id"]], entry), ""])
    lines.extend(
        [
            "## 站内导航",
            "",
            "- [Core topics / 核心主题](topics.md)：当前关注的方程、方法与研究问题。",
            "- [Resources / 资源](resources.md)：论文检索、课程与专题资料。",
            "- [Group work / 课题组相关](group-work.md)：公开笔记与研究链接。",
            "- [About / 关于](about.md)：选稿原则、数据来源与 AI 使用说明。",
            "",
            "## 数据来源与筛选",
            "",
            "论文通过 arXiv 分类与跨分类检索、Crossref、期刊 online-first 页面及出版商记录发现和核验。候选按 arXiv ID、DOI 和题名去重，再依据可积结构在研究中的实际作用和创新强度筛选；普通网页搜索只用于查漏，不作为最终依据。",
            "",
            "日期沿用来源记录：arXiv 版本页保留 UTC 提交与修订日期，新预印本按官方 announcement date 排序和分周；期刊采用出版商标注的首次在线发表日期。每日检索按北京时间执行。",
            "",
            "每日执行检索，但不要求每天发布，也不设置固定篇数。更多信息见[数据与筛选方法](editorial-policy.md)。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def expected_outputs() -> dict[Path, str]:
    data = load_yaml(EDITIONS_PATH)
    papers = paper_map()

    if not data.get("frontier"):
        raise ValueError("data/editions.yml requires frontier data")

    return {HOME_PATH: render_frontier_home(data, papers)}


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
