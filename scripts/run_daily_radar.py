#!/usr/bin/env python3
"""Run the research radar with recency filtering and compact public rendering.

Broad source lookback remains available for candidate/backlog records and
metadata updates. Recent high-confidence papers may reach the public brief;
older relevant items remain available for manual backlog curation. Public
Markdown is deliberately compact so the brief remains easy to scan.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections.abc import Callable

import radar

AI_NOTE = (
    "日期为本站整理日期。简报由 AI 辅助检索和整理，主要依据题名、摘要、分类、关键词和公开元数据筛选；"
    "推荐表示相关性和阅读优先级，不代表论文正确性已经核验。除特别标注外，条目尚未完成全文审读，"
    "数学结论请以原论文为准。"
)

TAG_ALIASES = {
    "coupled nonlinear schrodinger": "coupled NLS",
    "coupled nls": "coupled NLS",
    "multi-component nls": "multicomponent NLS",
    "multicomponent nls": "multicomponent NLS",
    "manakov": "Manakov system",
    "rogue wave": "rogue waves",
    "rogue waves": "rogue waves",
    "breather": "breathers",
    "breathers": "breathers",
    "riemann hilbert": "Riemann--Hilbert problem",
    "riemann-hilbert": "Riemann--Hilbert problem",
    "rhp": "Riemann--Hilbert problem",
    "dbar": "∂̄ method",
    "barpartial": "∂̄ method",
}

INTERNAL_REASON_PREFIXES = (
    "强相关组合命中：",
    "有相关信号但未达到公开简报门槛：",
    "达到推荐分数但超过当日公开推荐数量上限",
)


def publication_eligible(published: str | None, edition_date: dt.date, window_days: int) -> bool:
    """Return whether a metadata publication date is inside the recent window."""
    if not published or window_days < 1:
        return False
    try:
        publication_date = dt.date.fromisoformat(published[:10])
    except (TypeError, ValueError):
        return False
    start = edition_date - dt.timedelta(days=window_days - 1)
    return start <= publication_date <= edition_date


def install_publication_gate(edition_date: dt.date, window_days: int) -> None:
    """Keep recent recommendations public and retain older items as candidates."""
    original: Callable[[radar.Paper], None] = radar.score_and_classify

    def guarded_score_and_classify(paper: radar.Paper) -> None:
        original(paper)
        if paper.status != "recommended":
            return
        if publication_eligible(paper.published, edition_date, window_days):
            return
        paper.status = "candidate"
        paper.level = "值得补读候选"
        date_note = paper.published or "unknown"
        paper.reason = (
            f"{paper.reason}; retained for backlog review because publication date "
            f"{date_note} is outside the {window_days}-day recent window ending "
            f"{edition_date.isoformat()}"
        ).strip("; ")

    radar.score_and_classify = guarded_score_and_classify


def publication_label(published: str | None) -> str:
    """Return a compact year-month publication label when possible."""
    if not published:
        return ""
    if re.match(r"^\d{4}-\d{2}", published):
        return published[:7]
    if re.match(r"^\d{4}", published):
        return published[:4]
    return published[:10]


def source_link(paper: radar.Paper) -> str:
    """Link the source identifier rather than the paper title."""
    if paper.arxiv_id:
        label = f"arXiv:{paper.arxiv_id}"
    elif paper.doi:
        label = f"doi:{paper.doi}"
    else:
        label = paper.id or "source"
    return radar.md_link(label, paper.url) if paper.url else label


def _append_unique(items: list[str], value: str) -> None:
    key = value.casefold()
    if value and all(item.casefold() != key for item in items):
        items.append(value)


def display_tags(paper: radar.Paper, limit: int = 6) -> list[str]:
    """Return concise, deduplicated public tags with title-derived method terms."""
    text = radar.search_text(f"{paper.title} {paper.summary}")
    tags: list[str] = []

    if "dimensional reduction" in text:
        _append_unique(tags, "dimensional reduction")
    if "conformal lifting" in text:
        _append_unique(tags, "conformal lifting")
    if "multicomponent" in text or "multi-component" in text:
        _append_unique(tags, "multicomponent NLS")

    for raw_tag in paper.tags:
        clean = raw_tag.replace("`", "").strip()
        if not clean:
            continue
        normalized = TAG_ALIASES.get(radar.search_text(clean), clean)
        _append_unique(tags, normalized)
        if len(tags) >= limit:
            break
    return tags[:limit]


def tag_line(paper: radar.Paper) -> str:
    """Render a short inline tag sequence."""
    return " ".join(f"`{tag}`" for tag in display_tags(paper))


def compact_annotation(paper: radar.Paper, max_chars: int = 280) -> str:
    """Use the abstract rather than internal scoring text as the public annotation."""
    summary = radar.normalize_space(paper.summary)
    if summary:
        sentences = re.split(r"(?<=[.!?])\s+", summary)
        text = sentences[0]
        if len(text) < 120 and len(sentences) > 1:
            text = f"{text} {sentences[1]}"
    else:
        reason = radar.normalize_space(paper.reason).rstrip(".。")
        if not reason or reason.startswith(INTERNAL_REASON_PREFIXES):
            return ""
        text = reason

    if len(text) > max_chars:
        shortened = text[: max_chars - 1].rsplit(" ", 1)[0]
        text = (shortened or text[: max_chars - 1]).rstrip("，,;:：") + "…"
    return text.rstrip(".。") + "。"


def render_compact_card(paper: radar.Paper) -> str:
    """Render one scan-friendly paper entry without repeated field labels."""
    authors = ", ".join(author for author in paper.authors if author) or "Authors not listed"
    metadata = [authors, source_link(paper)]
    date_text = publication_label(paper.published)
    if date_text:
        metadata.append(date_text)
    tags = tag_line(paper)
    annotation = compact_annotation(paper)
    lines = [f"**{paper.title}**", "", " · ".join(metadata) + "  "]
    if tags:
        lines.append(tags)
    if annotation:
        lines += ["", annotation]
    return "\n".join(lines)


def compact_home_block(block: str, limit: int = 7) -> str:
    """Reduce one full date block to title-and-metadata bullets for the homepage."""
    output: list[str] = []
    lines = block.splitlines()
    date_heading = ""
    section_heading = ""
    written_date = False
    written_section = ""
    count = 0
    index = 0

    while index < len(lines) and count < limit:
        line = lines[index]
        if line.startswith("## "):
            date_heading = line
            section_heading = ""
            index += 1
            continue
        if line.startswith("### "):
            section_heading = line
            index += 1
            continue
        if not (line.startswith("**") and line.endswith("**")):
            index += 1
            continue

        metadata = ""
        tags = ""
        cursor = index + 1
        while cursor < len(lines):
            following = lines[cursor]
            if following.startswith(("## ", "### ", "**")):
                break
            stripped = following.strip()
            if stripped:
                if not metadata:
                    metadata = stripped.removesuffix("  ")
                elif stripped.startswith("`"):
                    tags = stripped
                    break
            cursor += 1

        if not written_date and date_heading:
            output += [date_heading, ""]
            written_date = True
        if section_heading and written_section != section_heading:
            output += [section_heading, ""]
            written_section = section_heading
        output.append(f"- {line}  ")
        detail = " · ".join(part for part in [metadata, tags] if part)
        if detail:
            output.append(f"  {detail}")
        output.append("")
        count += 1
        index = cursor

    return "\n".join(output).rstrip()


def compact_home_blocks(blocks: list[str], limit: int = 7) -> str:
    """Keep several recent editions on the homepage without duplicating comments."""
    rendered: list[str] = []
    remaining = limit
    for block in blocks:
        if remaining < 1:
            break
        compact = compact_home_block(block, limit=remaining)
        used = compact.count("\n- **") + int(compact.startswith("- **"))
        if compact and used:
            rendered.append(compact)
            remaining -= used
    return "\n\n---\n\n".join(rendered)


def render_compact_latest(week: str, daily_block: str) -> str:
    return f"""# 最新研究简报

[返回首页](../index.md) · [本周归档]({week}.md) · [全部归档](index.md)

!!! note "AI 生成说明"
    {AI_NOTE}

{daily_block.rstrip()}
"""


def render_compact_home(week: str, blocks: list[str]) -> str:
    recent = compact_home_blocks(blocks, limit=7) if blocks else "尚无公开简报。"
    return f"""# 可积系统研究简报

面向可积系统、反散射、黎曼--希尔伯特方法、非线性波和相关课题组资料的研究向入口。

[最新简报](radar/latest.md) · [简报归档](radar/index.md) · [资源](resources.md) · [核心主题](topics.md)

!!! note "AI 生成说明"
    {AI_NOTE}

{recent}

[查看完整简报](radar/latest.md)

## 其他入口

- [Resources / 资源](resources.md)：课程、讲义、研究者主页和检索入口。
- [Group work / 课题组相关](group-work.md)：本地研究背景、公开笔记和相关链接。
- [Core topics / 核心主题](topics.md)：本站目前关注的方程、方法和非线性波主题。
- [About / 关于](about.md)：策展原则、设计参考、AI 使用和许可证说明。
"""


def install_compact_rendering() -> None:
    """Use compact paper cards on generated public pages."""
    radar.render_card = render_compact_card
    radar.render_latest = render_compact_latest
    radar.render_home = render_compact_home


def parse_wrapper_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument(
        "--publication-window-days",
        type=int,
        default=30,
        help="inclusive recent-publication window for automatic public recommendations",
    )
    args, remaining = parser.parse_known_args(argv)
    if args.publication_window_days < 1:
        parser.error("--publication-window-days must be at least 1")
    return args, remaining


def main() -> None:
    args, remaining = parse_wrapper_args(sys.argv[1:])
    edition_date = dt.date.fromisoformat(args.date)
    install_publication_gate(edition_date, args.publication_window_days)
    install_compact_rendering()
    sys.argv = [sys.argv[0], "--date", args.date, *remaining]
    radar.main()


if __name__ == "__main__":
    main()
