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
    "日期为本站整理日期。简报主要依据题名、摘要、分类、关键词和公开元数据筛选；"
    "推荐表示相关性和阅读优先级，不代表论文正确性已经核验。数学结论请以原论文为准。"
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


def tag_line(tags: list[str]) -> str:
    """Render a short inline tag sequence."""
    clean = [tag.replace("`", "").strip() for tag in tags if tag.strip()]
    return " ".join(f"`{tag}`" for tag in clean[:6])


def render_compact_card(paper: radar.Paper) -> str:
    """Render one scan-friendly paper entry without repeated field labels."""
    authors = ", ".join(author for author in paper.authors if author) or "Authors not listed"
    metadata = [authors, source_link(paper)]
    date_text = publication_label(paper.published)
    if date_text:
        metadata.append(date_text)
    tags = tag_line(paper.tags)
    reason = paper.reason.strip().rstrip(".。")
    lines = [f"**{paper.title}**", "", " · ".join(metadata) + "  "]
    if tags:
        lines.append(tags)
    if reason:
        lines += ["", reason + "。"]
    return "\n".join(lines)


def compact_home_block(block: str, limit: int = 6) -> str:
    """Reduce a full daily block to title-and-metadata bullets for the homepage."""
    output: list[str] = []
    count = 0
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("### "):
            output += [line, ""]
            continue
        if not (line.startswith("**") and line.endswith("**")) or count >= limit:
            continue
        metadata = ""
        tags = ""
        for following in lines[index + 1 :]:
            if following.startswith(("## ", "### ", "**")):
                break
            stripped = following.strip()
            if not stripped:
                continue
            if not metadata:
                metadata = stripped.removesuffix("  ")
            elif stripped.startswith("`"):
                tags = stripped
                break
        output.append(f"- {line}  ")
        detail = " · ".join(part for part in [metadata, tags] if part)
        if detail:
            output.append(f"  {detail}")
        output.append("")
        count += 1
    return "\n".join(output).rstrip()


def render_compact_latest(week: str, daily_block: str) -> str:
    return f"""# 最新研究简报

[返回首页](../index.md) · [本周归档]({week}.md) · [全部归档](index.md)

!!! note "AI 生成说明"
    {AI_NOTE}

{daily_block.rstrip()}
"""


def render_compact_home(week: str, blocks: list[str]) -> str:
    latest = compact_home_block(blocks[0]) if blocks else "尚无公开简报。"
    return f"""# 可积系统研究简报

面向可积系统、反散射、黎曼--希尔伯特方法、非线性波和相关课题组资料的研究向入口。

[最新简报](radar/latest.md) · [简报归档](radar/index.md) · [资源](resources.md) · [核心主题](topics.md)

!!! note "AI 生成说明"
    {AI_NOTE}

{latest}

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
