#!/usr/bin/env python3
"""Render the compact 30-day research radar from YAML data."""

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
BASE_PAPERS_PATH = ROOT / "data" / "papers.yml"
RADAR_PAPERS_PATH = ROOT / "data" / "radar_papers.yml"
RADAR_PATH = ROOT / "data" / "radar.yml"
RADAR_ENTRIES_DIR = ROOT / "data" / "radar_entries"
TAGS_PATH = ROOT / "data" / "radar_tags.yml"
HOME_PATH = ROOT / "docs" / "index.md"
ARCHIVE_INDEX_PATH = ROOT / "docs" / "radar" / "index.md"
LATEST_PATH = ROOT / "docs" / "radar" / "latest.md"

SIGNAL_LABELS = {
    "new-preprint": "新预印本",
    "major-revision": "重大修订",
    "journal-publication": "期刊发表",
}


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_radar_data() -> dict[str, Any]:
    data = load_yaml(RADAR_PATH)
    entries: list[dict[str, Any]] = []
    for path in sorted(RADAR_ENTRIES_DIR.glob("*.yml")):
        entries.extend(load_yaml(path) or [])
    data["entries"] = entries
    return data


def paper_map() -> dict[str, dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for path in (BASE_PAPERS_PATH, RADAR_PAPERS_PATH):
        records = load_yaml(path) or []
        for paper in records:
            combined[paper["id"]] = paper
    return combined


def compact(text: str) -> str:
    value = " ".join(str(text).split())
    return re.sub(
        r"(?<=[\u3400-\u9fff，。；：！？、）】》]) (?=[\u3400-\u9fff（【《])",
        "",
        value,
    )


def esc(text: Any) -> str:
    return html.escape(compact(str(text)), quote=True)


def anchor_for(paper_id: str, signal_date: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", f"{signal_date}-{paper_id}").strip("-").lower()


def validate_data(data: dict[str, Any], papers: dict[str, dict[str, Any]]) -> None:
    allowed_tags = set((load_yaml(TAGS_PATH) or {}).get("allowed_tags", []))
    weeks = {week["id"] for week in data.get("weeks", [])}
    seen_events: set[tuple[str, str, str]] = set()

    required = {
        "paper_id",
        "week",
        "signal_date",
        "signal_type",
        "review_status",
        "arxiv_categories",
        "structure_tags",
        "summary",
        "main_result",
        "integrable_structure",
        "innovation",
    }
    for index, entry in enumerate(data.get("entries", []), start=1):
        missing = sorted(required - set(entry))
        if missing:
            raise ValueError(f"entry {index} missing fields: {', '.join(missing)}")
        if entry["paper_id"] not in papers:
            raise ValueError(f"unknown paper_id: {entry['paper_id']}")
        if entry["week"] not in weeks:
            raise ValueError(f"unknown week: {entry['week']}")
        if entry["signal_type"] not in SIGNAL_LABELS:
            raise ValueError(f"unknown signal_type: {entry['signal_type']}")
        date.fromisoformat(entry["signal_date"])
        event_key = (entry["paper_id"], entry["signal_date"], entry["signal_type"])
        if event_key in seen_events:
            raise ValueError(f"duplicate radar event: {event_key}")
        seen_events.add(event_key)

        categories = entry["arxiv_categories"]
        if not categories or len(categories) > 2:
            raise ValueError(f"{entry['paper_id']}: expected one or two arXiv categories")
        for category in categories:
            if not re.fullmatch(r"[a-z-]+(?:\.[A-Za-z-]+)?", category):
                raise ValueError(f"{entry['paper_id']}: invalid arXiv category {category!r}")

        tags = entry["structure_tags"]
        if not tags or len(tags) > 2:
            raise ValueError(f"{entry['paper_id']}: expected one or two structure tags")
        unknown = sorted(set(tags) - allowed_tags)
        if unknown:
            raise ValueError(f"{entry['paper_id']}: uncontrolled tags: {', '.join(unknown)}")

        for field in ("summary", "main_result", "integrable_structure", "innovation"):
            if not compact(entry[field]):
                raise ValueError(f"{entry['paper_id']}: empty {field}")

    as_of = date.fromisoformat(data["as_of"])
    if data.get("window_days", 0) <= 0:
        raise ValueError("window_days must be positive")
    if any(date.fromisoformat(entry["signal_date"]) > as_of for entry in data["entries"]):
        raise ValueError("radar event occurs after as_of")


def link_button(url: str, label: str) -> str:
    return f'<a class="radar-link" href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'


def source_buttons(paper: dict[str, Any]) -> str:
    buttons: list[str] = []
    arxiv_id = paper.get("arxiv_id")
    if arxiv_id:
        buttons.append(link_button(f"https://arxiv.org/abs/{arxiv_id}", "arXiv"))
        buttons.append(link_button(f"https://arxiv.org/pdf/{arxiv_id}", "PDF"))
    journal_url = paper.get("journal_url")
    doi = paper.get("doi")
    if journal_url:
        buttons.append(link_button(journal_url, "期刊"))
    elif doi and not str(doi).lower().startswith("10.48550/arxiv"):
        buttons.append(link_button(f"https://doi.org/{doi}", "DOI"))
    return "".join(buttons)


def metadata_line(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    signal = SIGNAL_LABELS[entry["signal_type"]]
    parts = [f'<time datetime="{entry["signal_date"]}">{esc(entry["signal_date"])}</time>', esc(signal)]
    if entry["signal_type"] == "journal-publication" and paper.get("submitted"):
        parts.append(f'arXiv 首次公开 {esc(paper["submitted"])}')
    return '<span class="radar-meta-sep"> · </span>'.join(parts)


def tag_badges(entry: dict[str, Any]) -> str:
    categories = "".join(
        f'<span class="radar-tag radar-tag--category">{esc(category)}</span>'
        for category in entry["arxiv_categories"]
    )
    structures = "".join(
        f'<span class="radar-tag radar-tag--structure">{esc(tag)}</span>'
        for tag in entry["structure_tags"]
    )
    return categories + structures


def render_entry(paper: dict[str, Any], entry: dict[str, Any]) -> str:
    authors = ", ".join(paper["authors"])
    anchor = anchor_for(entry["paper_id"], entry["signal_date"])
    return "\n".join(
        [
            f'<article class="radar-card" id="{anchor}">',
            '  <div class="radar-card__date">',
            f'    <div class="radar-card__day">{esc(entry["signal_date"][8:10])}</div>',
            f'    <div class="radar-card__month">{esc(entry["signal_date"][5:7])} 月</div>',
            '  </div>',
            '  <div class="radar-card__body">',
            f'    <div class="radar-card__meta">{metadata_line(paper, entry)}</div>',
            f'    <div class="radar-tags">{tag_badges(entry)}</div>',
            f'    <div class="radar-authors">{esc(authors)}</div>',
            f'    <h3 class="radar-title">{esc(paper["title"])}</h3>',
            f'    <p class="radar-summary">{esc(entry["summary"])}</p>',
            f'    <div class="radar-links">{source_buttons(paper)}</div>',
            '    <details class="radar-details">',
            '      <summary>展开研究内容与创新</summary>',
            '      <div class="radar-details__content">',
            '        <section>',
            '          <h4>研究问题与主要结果</h4>',
            f'          <p>{esc(entry["main_result"])}</p>',
            '        </section>',
            '        <section>',
            '          <h4>可积结构与方法</h4>',
            f'          <p>{esc(entry["integrable_structure"])}</p>',
            '        </section>',
            '        <section>',
            '          <h4>创新</h4>',
            f'          <p>{esc(entry["innovation"])}</p>',
            '        </section>',
            '      </div>',
            '    </details>',
            '  </div>',
            '</article>',
        ]
    )


def week_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {week["id"]: week for week in data["weeks"]}


def entries_by_week(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[entry["week"]].append(entry)
    for week_entries in grouped.values():
        week_entries.sort(key=lambda item: (item["signal_date"], item["paper_id"]), reverse=True)
    return grouped


def render_screening(week: dict[str, Any]) -> str:
    screening = week.get("screening", {})
    sources = "；".join(screening.get("sources_checked", []))
    return "\n".join(
        [
            '<aside class="radar-screening">',
            '  <h2>本周筛选说明</h2>',
            f'  <p><strong>最终收录：</strong>{screening.get("selected", 0)} 篇。</p>',
            f'  <p><strong>检查来源：</strong>{esc(sources)}。</p>',
            f'  <p><strong>覆盖说明：</strong>{esc(screening.get("coverage_note", ""))}</p>',
            '</aside>',
        ]
    )


def render_week(
    week: dict[str, Any],
    entries: list[dict[str, Any]],
    papers: dict[str, dict[str, Any]],
) -> str:
    lines = [
        f"# 研究雷达归档 · {week['id']}",
        "",
        "[全部归档](index.md) · [返回首页](../index.md)",
        "",
        f"**{week['date_range']}** · {week['summary']}",
        "",
        "论文说明由自动流程整理，并经元数据核验；除特别标注外，不代表编辑已经完整阅读或逐句审校。",
        "",
    ]
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_date[entry["signal_date"]].append(entry)
    for signal_date in sorted(by_date, reverse=True):
        lines.extend([f"## {signal_date}", ""])
        for entry in by_date[signal_date]:
            lines.extend([render_entry(papers[entry["paper_id"]], entry), ""])
    lines.extend([render_screening(week), ""])
    return "\n".join(lines).rstrip() + "\n"


def window_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    as_of = date.fromisoformat(data["as_of"])
    cutoff = as_of - timedelta(days=int(data["window_days"]) - 1)
    return [
        entry
        for entry in data["entries"]
        if cutoff <= date.fromisoformat(entry["signal_date"]) <= as_of
    ]


def render_home(data: dict[str, Any], papers: dict[str, dict[str, Any]]) -> str:
    selected = window_entries(data)
    weeks = week_map(data)
    grouped = entries_by_week(selected)
    as_of = date.fromisoformat(data["as_of"])
    cutoff = as_of - timedelta(days=int(data["window_days"]) - 1)
    lines = [
        "# 可积系统研究雷达",
        "",
        "面向可积系统读者，筛选最近出现的强创新、新方向和新方法。主题相关性采用宽松边界；可积结构在主要结果中的作用和创新强度是核心判断。",
        "",
        f"**当前窗口：{cutoff.isoformat()} 至 {as_of.isoformat()} · {len(selected)} 篇**",
        "",
        "论文说明由自动流程整理，并经元数据核验；除特别标注外，不代表编辑已经完整阅读或逐句审校。",
        "",
        "[研究雷达归档](radar/index.md) · [资源](resources.md) · [关于选稿](about.md)",
        "",
    ]
    for week_id in sorted(grouped, reverse=True):
        week = weeks[week_id]
        lines.extend(
            [
                f"## {week_id} · {week['date_range']}",
                "",
                f"{len(grouped[week_id])} 篇 · {week['summary']}",
                "",
            ]
        )
        for entry in grouped[week_id]:
            lines.extend([render_entry(papers[entry["paper_id"]], entry), ""])
        lines.extend([f"[查看 {week_id} 周归档](radar/{week_id}.md)", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_archive_index(data: dict[str, Any]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for entry in data["entries"]:
        counts[entry["week"]] += 1
    lines = [
        "# 研究雷达归档",
        "",
        "归档按论文实际研究事件日期分周组织。周页面只展示最终选择和聚合筛选说明，不公开未收录名单。",
        "",
        "[返回首页](../index.md)",
        "",
    ]
    by_year: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for week in data["weeks"]:
        by_year[week["id"].split("-W", 1)[0]].append(week)
    for year in sorted(by_year, reverse=True):
        lines.extend([f"## {year}", ""])
        for week in sorted(by_year[year], key=lambda item: item["id"], reverse=True):
            lines.extend(
                [
                    f"### {week['id']} · {week['date_range']}",
                    "",
                    f"**{counts[week['id']]} 篇** · {week['summary']}",
                    "",
                    f"[查看本周归档]({week['id']}.md)",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def render_latest(data: dict[str, Any]) -> str:
    latest = max(data["entries"], key=lambda item: (item["signal_date"], item["paper_id"]))
    return (
        "# 最新研究雷达条目\n\n"
        "本站不维护一份与首页和周归档重复的独立最新简报。\n\n"
        f"最新研究事件：[{latest['signal_date']}]({latest['week']}.md"
        f"#{anchor_for(latest['paper_id'], latest['signal_date'])})。\n\n"
        "也可以直接查看 [研究雷达归档](index.md) 或返回 [首页](../index.md)。\n"
    )


def expected_outputs() -> dict[Path, str]:
    data = load_radar_data()
    papers = paper_map()
    validate_data(data, papers)
    grouped = entries_by_week(data["entries"])
    outputs = {
        HOME_PATH: render_home(data, papers),
        ARCHIVE_INDEX_PATH: render_archive_index(data),
        LATEST_PATH: render_latest(data),
    }
    for week in data["weeks"]:
        outputs[ROOT / "docs" / "radar" / f"{week['id']}.md"] = render_week(
            week, grouped.get(week["id"], []), papers
        )
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
