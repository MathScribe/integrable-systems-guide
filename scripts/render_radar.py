#!/usr/bin/env python3
"""Render the radar homepage and supporting pages."""

from __future__ import annotations

import argparse
import html
import json
import re
from functools import lru_cache
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


@lru_cache(maxsize=1)
def research_directions() -> dict[str, str]:
    return load_yaml(ROOT / "data" / "tags.yml")["frontier_directions"]


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

    directions = entry.get("directions", [])
    if not isinstance(directions, list) or not 1 <= len(directions) <= 2:
        raise ValueError(f"{paper_id} requires one or two research directions")
    if any(not isinstance(direction, str) or direction not in research_directions() for direction in directions):
        raise ValueError(f"{paper_id} has invalid research directions")
    if len(set(directions)) != len(directions):
        raise ValueError(f"{paper_id} has duplicate research directions")

    note = entry.get("reading_note")
    if note is not None:
        if not isinstance(note, dict) or any(
            not isinstance(note.get(field), str) or not compact(note[field])
            for field in ("lead", "detail", "method_scope")
        ):
            raise ValueError(f"{paper_id}.reading_note requires lead, detail and method_scope")


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

    if "checked_through" in frontier:
        raise ValueError(
            "frontier.checked_through is obsolete; source watermarks belong in "
            "maintenance/radar-state.yml"
        )
    return entries


def source_links_html(paper: dict[str, Any], *, new_tab: bool = False) -> str:
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
    result = " · ".join(links)
    if new_tab:
        result = result.replace('<a href=', '<a target="_blank" rel="noopener noreferrer" href=')
    return result


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
    short_authors = authors if len(paper["authors"]) <= 3 else ", ".join(paper["authors"][:2]) + ", et al."
    signal_label = SIGNAL_LABELS[entry["signal_type"]]
    note = entry.get("reading_note") or {
        "lead": entry["summary"],
        "detail": entry["main_result"],
        "method_scope": entry["integrable_structure"],
    }
    anchor = f'paper-{html_id(entry["paper_id"])}'
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
    tags_data = html.escape(json.dumps(entry.get("structure_tags", []), ensure_ascii=False), quote=True)
    directions_data = html.escape(json.dumps(entry.get("directions", [])), quote=True)
    date_description = f'{signal_label} · {entry["signal_date"]}'
    if source_date_note:
        date_description += re.sub(r"<[^>]+>", "", source_date_note)
    if paper.get("version"):
        date_description += f' · {paper["version"]}'
    date_description = html.escape(html.unescape(date_description), quote=True)
    author_html = html.escape(authors)
    if short_authors != authors:
        author_html = (
            f'<span class="radar-authors-short">{html.escape(short_authors)}</span>'
            f'<span class="radar-authors-full">{html.escape(authors)}</span>'
        )
    # Keep the editorial record searchable even when the reading view is shorter.
    search_text = html.escape(" ".join([
        *entry.get("arxiv_categories", []), *entry.get("structure_tags", []),
        *(str(entry[field]) for field in ("summary", "main_result", "integrable_structure", "innovation")),
    ]), quote=True)
    return (
        f'### {html.escape(str(paper["title"]))} {{#{anchor} .radar-search-heading}}\n\n'
        f'<article class="radar-paper-card radar-paper-card--native" data-radar-native="true" '
        f'data-radar-anchor="{anchor}" '
        f'data-radar-month="{html.escape(month_id, quote=True)}" '
        f'data-radar-date="{entry["signal_date"]}" data-radar-tags="{tags_data}" '
        f'data-radar-directions="{directions_data}" '
        f'data-radar-search="{search_text}">\n'
        '  <details class="radar-paper-details">\n'
        '    <summary class="radar-row-summary">\n'
        f'      <span class="radar-row-heading"><span class="radar-paper-title">{render_rich_text(paper["title"])}</span>'
        f'<a class="radar-permalink" href="#{anchor}" aria-label="此论文固定链接" title="此论文固定链接">#</a>'
        '<span class="radar-expand-icon" aria-hidden="true">⌄</span></span>\n'
        '      <span class="radar-row-meta">'
        f'<span class="radar-row-authors" title="{html.escape(authors, quote=True)}">{author_html}</span>'
        f'<span class="radar-row-sources">{source_links_html(paper, new_tab=True)}</span>'
        f'<time datetime="{entry["signal_date"]}" title="{date_description}" aria-label="{date_description}">{entry["signal_date"]}</time></span>\n'
        '    </summary>\n'
        '    <div class="radar-expanded-content">\n'
        f'    <p class="radar-paper-overview"><strong>{render_rich_text(note["lead"])}</strong></p>\n'
        f'    <p class="radar-reading-detail">{render_rich_text(note["detail"])}</p>\n'
        f'    <p class="radar-reading-method"><span class="radar-reading-label">方法与范围：</span>{render_rich_text(note["method_scope"])}</p>\n'
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


def render_frontier_home(data: dict[str, Any], papers: dict[str, dict[str, Any]]) -> str:
    frontier = data["frontier"]
    entries = all_frontier_entries(frontier, papers)
    earliest = min(entry["signal_date"] for entry in entries)
    latest = max(entry["signal_date"] for entry in entries)
    coverage = f'{earliest[:7].replace("-", ".")}—{latest[:7].replace("-", ".")}'
    direction_options = ''.join(
        f'<option value="{html.escape(key, quote=True)}">{html.escape(label)}</option>'
        for key, label in research_directions().items()
    )
    lines = [
        '---\ntitle: 可积系统研究雷达\nhide:\n  - toc\n---\n',
        '<header class="radar-hero">',
        '  <p class="radar-eyebrow">INTEGRABLE SYSTEMS <span>RESEARCH RADAR</span></p>',
        '  <h1 id="research-radar">可积系统研究雷达<span class="radar-title-dot">.</span></h1>',
        '  <p class="radar-hero-intro">这里精选近期可积系统的研究进展，关注具体问题，也寻找新的研究方向。</p>',
        '  <div class="radar-hero-bottom">',
        f'    <p class="radar-collection-size">精选论文 · 按公开日期倒序</p>',
        '    <nav class="radar-hero-links" aria-label="探索网站"><a href="topics/">研究主题 <span>↗</span></a><a href="group-work/">课题组论文 <span>↗</span></a></nav>',
        '  </div>',
        '</header>',
        "",
        '<div class="radar-browse-controls" data-default-period="all" '
        f'data-total-count="{len(entries)}" data-earliest-date="{earliest}">',
        '  <div class="radar-browse-heading"><h2>论文浏览</h2><span class="radar-search-count" role="status" aria-live="polite"></span></div>',
        '  <div class="radar-filter-bar">',
        '  <div class="radar-local-search" role="search">',
        '    <label class="radar-visually-hidden" for="radar-paper-search">搜索论文</label>',
        '    <span class="radar-search-icon" aria-hidden="true">⌕</span>',
        '    <input id="radar-paper-search" type="search" placeholder="搜索论文、作者、方程或方法" autocomplete="off">',
        '  </div>',
        '    <select id="radar-time-filter" aria-label="时间范围"><option value="all">全部已收录</option><option value="30">最近 30 天</option><option value="90">最近 3 个月</option><option value="custom">自定义时间</option></select>',
        f'    <select id="radar-topic-filter" aria-label="研究方向"><option value="">全部方向</option>{direction_options}</select>',
        '  </div>',
        f'  <div class="radar-custom-dates" hidden><label>从 <input type="date" id="radar-date-from" value="{earliest}"></label><label>至 <input type="date" id="radar-date-to"></label></div>',
        f'  <div class="radar-filter-footer"><span>当前收录：{coverage}</span><button type="button" data-radar-action="reset" hidden>清除筛选 ×</button></div>',
        "</div>",
        '<p class="radar-empty-state" hidden>没有找到匹配论文。试试其他关键词，或清除筛选。</p>',
        "",
    ]
    for entry in entries:
        lines.extend([render_frontier_entry(papers[entry["paper_id"]], entry), ""])
    lines.extend([
        '<nav class="radar-pagination" aria-label="论文分页"><span data-radar-page-info></span><div><button type="button" data-radar-action="previous" disabled>← 上一页</button><span data-radar-page></span><button type="button" data-radar-action="next">下一页 →</button></div></nav>',
        "",
    ])
    lines.extend(
        [
            "## 站内导航",
            "",
            "- [Core topics / 核心主题](topics.md)：当前关注的方程、方法与研究问题。",
            "- [Resources / 资源](resources.md)：论文检索、课程与专题资料。",
            "- [Group work / 课题组相关](group-work.md)：查询相关论文与公开资料。",
            "- [About / 关于](about.md)：选稿原则、数据来源与 AI 使用说明。",
            "",
            "## 数据来源与筛选",
            "",
            "论文来自 arXiv 与期刊记录，并通过 Crossref 等来源补漏。按研究相关性与具体进展筛选，不设置固定篇数。",
            "",
            "论文按首次公开、重大修订或正式发表日期排序。内容由自动流程整理，数学结论请以原论文为准。",
            "",
            "[数据来源](sources.md) · [数据与筛选方法](editorial-policy.md)",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_group_work(group: dict[str, str]) -> str:
    name = html.escape(group["name"], quote=True)
    orcid = group["orcid"]
    if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", orcid):
        raise ValueError("group-work.orcid must be an ORCID identifier")
    return f'''# Group work / 课题组相关

查询凌黎明及合作者的可积系统相关论文。

<section class="group-papers" data-group-papers data-author="{name}" data-orcid="{orcid}">
  <div class="group-papers-header">
    <div><p class="group-papers-eyebrow">PUBLICATIONS</p><h2>{html.escape(group["display_name"])}</h2></div>
    <a class="group-profile-link" href="{html.escape(group["homepage"], quote=True)}" target="_blank" rel="noopener noreferrer">个人主页 ↗</a>
  </div>
  <div class="group-papers-controls">
    <label class="group-search-label"><span class="group-visually-hidden">搜索论文标题、作者或期刊</span><input type="search" data-paper-query placeholder="搜索标题、作者或期刊" autocomplete="off"></label>
    <label><span class="group-visually-hidden">发表年份</span><select data-paper-year aria-label="发表年份"><option value="">全部年份</option></select></label>
  </div>
  <div class="group-papers-toolbar"><span data-paper-status role="status" aria-live="polite">正在查询论文…</span><button type="button" data-paper-retry hidden>重新查询</button></div>
  <div class="group-papers-results" data-paper-results aria-busy="true"></div>
  <div class="group-papers-footer">
    <span class="group-papers-source">来自 <a href="https://search.crossref.org/?q={name.replace(' ', '%20')}" target="_blank" rel="noopener noreferrer">Crossref</a> · 相关期刊论文</span>
    <nav class="group-pagination" aria-label="论文翻页"><button type="button" data-paper-prev disabled aria-label="上一页">←</button><span data-paper-page></span><button type="button" data-paper-next disabled aria-label="下一页">→</button></nav>
  </div>
  <noscript><p>请启用 JavaScript 查询论文，或前往 <a href="https://search.crossref.org/?q={name.replace(' ', '%20')}">Crossref</a>。</p></noscript>
</section>

## 作者与文献入口

保留不同数据库的检索入口，便于查看预印本、引用信息和更多相关工作。

<div class="group-resource-links">
  <a href="{html.escape(group["homepage"], quote=True)}"><strong>凌黎明 / Liming Ling</strong><span>华南理工大学数学学院主页 ↗</span></a>
  <a href="https://mathscinet.ams.org/mathscinet/publications-search?query=Liming%20Ling&amp;page=1&amp;size=20&amp;sort=newest&amp;facets"><strong>MathSciNet</strong><span>论文与数学评论 ↗</span></a>
  <a href="https://arxiv.org/search/?query=Liming+Ling&amp;searchtype=author"><strong>arXiv</strong><span>预印本与最新版本 ↗</span></a>
  <a href="https://scholar.google.com/scholar?q=%22Liming+Ling%22"><strong>Google Scholar</strong><span>论文与引用检索 ↗</span></a>
  <a href="https://www.semanticscholar.org/search?q=Liming%20Ling&amp;sort=relevance"><strong>Semantic Scholar</strong><span>文献关联与引用 ↗</span></a>
</div>

## Public notes / 公开笔记

[killlakill/courseNotes](https://codeberg.org/killlakill/courseNotes) · 公开课程笔记与学习资料。

## Reading projects / 读书项目

后续在这里整理读书项目与相关笔记。
'''


def render_sources() -> str:
    return '''# 数据来源

本站从 arXiv 和期刊记录中发现论文，并依据研究问题、方法与结果筛选。

| 来源 | 用途 |
| --- | --- |
| [arXiv](https://arxiv.org/) | 新预印本与修订，重点关注可积系统、非线性波及相关分析方法 |
| [Crossref](https://www.crossref.org/) 与 [zbMATH](https://zbmath.org/) | 期刊论文检索、DOI 匹配与文献补漏 |
| 出版商页面与原论文 | 核对正式发表信息、摘要与研究内容 |

论文条目提供 arXiv 或 DOI 原文入口。日期区分预印本公告、首次在线发表和期刊卷期；卷期年份可能晚于首次上线年份。

课题组页面的查询组件直接读取 Crossref，展示相关期刊论文；查询结果受其收录和作者信息完整度影响，不等同于首页精选。

[筛选方法](editorial-policy.md) · [返回首页](index.md)
'''


def expected_outputs() -> dict[Path, str]:
    data = load_yaml(EDITIONS_PATH)
    papers = paper_map()

    if not data.get("frontier"):
        raise ValueError("data/editions.yml requires frontier data")

    return {
        HOME_PATH: render_frontier_home(data, papers),
        ROOT / "docs" / "group-work.md": render_group_work(load_yaml(ROOT / "data" / "group-work.yml")),
        ROOT / "docs" / "sources.md": render_sources(),
    }


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
