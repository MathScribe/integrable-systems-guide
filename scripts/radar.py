#!/usr/bin/env python3
"""Generate the AI-assisted research-radar scaffold.

This script is intentionally lightweight and dependency-free. It fetches candidate
papers from arXiv and Crossref, applies a simple topic-weighting rubric, checks
`data/papers.yml` for duplicate identifiers, and renders Markdown blocks for the
homepage, the fixed latest page, and the current weekly archive file.

The script does not claim to verify mathematical results. It produces a draft
that can be edited by a maintainer or by an AI coding assistant before commit.

Usage examples:

    python scripts/radar.py --date 2026-07-09 --dry-run
    python scripts/radar.py --date 2026-07-09 --write

The `--write` mode edits local files. Commit the resulting changes after review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PAPER_REGISTRY = ROOT / "data" / "papers.yml"
DOCS_INDEX = ROOT / "docs" / "index.md"
RADAR_DIR = ROOT / "docs" / "radar"
LATEST_PAGE = RADAR_DIR / "latest.md"

# Keep the first version deliberately focused on Ling-group adjacent topics.
ARXIV_QUERIES = [
    'cat:nlin.SI AND all:"derivative nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"DNLS"',
    'cat:nlin.SI AND all:"Gerdjikov Ivanov"',
    'cat:nlin.SI AND all:"Fokas Lenells"',
    'cat:nlin.SI AND all:"Kaup Newell"',
    'cat:nlin.SI AND all:"coupled nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"multi-component"',
    'cat:nlin.SI AND all:"Darboux"',
    'cat:nlin.SI AND all:"rogue wave"',
    'cat:nlin.SI AND all:"breather"',
    'cat:nlin.SI AND all:"elliptic localized"',
    'cat:nlin.SI AND all:"Riemann Hilbert"',
    'cat:nlin.SI AND all:"long-time asymptotics"',
    'cat:nlin.SI AND all:"soliton gas"',
    'cat:math.AP AND all:"derivative nonlinear Schrodinger"',
    'cat:math-ph AND all:"inverse scattering"',
]

CROSSREF_QUERIES = [
    "derivative nonlinear Schrodinger soliton gas",
    "coupled Gerdjikov Ivanov inverse scattering",
    "coupled nonlinear Schrodinger orbital stability breather",
    "Darboux transformation rogue wave coupled NLS",
    "Fokas Lenells elliptic localized solutions",
    "Riemann Hilbert long-time asymptotics derivative NLS",
]

# Multi-component/coupled terms are intentionally high weight.
WEIGHTS = {
    "derivative nonlinear schrodinger": 10,
    "dnls": 9,
    "gerdjikov": 9,
    "fokas": 8,
    "lenells": 8,
    "kaup": 8,
    "newell": 8,
    "chen-lee-liu": 8,
    "coupled": 7,
    "multi-component": 7,
    "multicomponent": 7,
    "vector": 5,
    "manakov": 6,
    "inverse scattering": 8,
    "riemann-hilbert": 8,
    "riemann hilbert": 8,
    "marchenko": 7,
    "long-time": 7,
    "long time": 7,
    "asymptotic": 6,
    "soliton gas": 8,
    "dbar": 6,
    "barpartial": 6,
    "darboux": 7,
    "backlund": 6,
    "rogue wave": 6,
    "breather": 7,
    "elliptic": 6,
    "finite-gap": 5,
    "theta": 5,
    "stability": 7,
    "spectral stability": 7,
    "orbital stability": 8,
    "squared eigenfunction": 8,
}

DIRECTION_KEYWORDS = {
    "精确解与特殊背景": [
        "darboux", "backlund", "rogue", "breather", "elliptic", "finite-gap",
        "theta", "weierstrass", "localized solution", "soliton solution",
    ],
    "稳定性与动力学机制": [
        "stability", "orbital", "spectral stability", "krein", "modulational",
        "squared eigenfunction", "linearized",
    ],
    "IST / RHP 与渐近分析": [
        "inverse scattering", "riemann-hilbert", "riemann hilbert", "marchenko",
        "long-time", "long time", "asymptotic", "steepest descent", "soliton gas",
        "dbar", "barpartial",
    ],
}


@dataclass
class Paper:
    id: str
    title: str
    authors: list[str]
    url: str
    source_type: str
    published: str | None = None
    summary: str = ""
    doi: str | None = None
    score: int = 0
    directions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


def fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "MathScribe research radar"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def existing_ids() -> set[str]:
    if not PAPER_REGISTRY.exists():
        return set()
    text = PAPER_REGISTRY.read_text(encoding="utf-8")
    return set(re.findall(r'^- id:\s+"([^"]+)"', text, flags=re.M))


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_arxiv_id(raw_id: str) -> str:
    return raw_id.rstrip("/").split("/")[-1]


def fetch_arxiv(max_results_per_query: int = 12) -> list[Paper]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers: dict[str, Paper] = {}
    for query in ARXIV_QUERIES:
        params = urllib.parse.urlencode({
            "search_query": query,
            "start": 0,
            "max_results": max_results_per_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
        url = f"https://export.arxiv.org/api/query?{params}"
        try:
            xml_text = fetch_text(url)
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"warning: arXiv query failed: {query}: {exc}", file=sys.stderr)
            continue
        root = ET.fromstring(xml_text)
        for entry in root.findall("atom:entry", ns):
            raw_id = entry.findtext("atom:id", default="", namespaces=ns)
            arxiv_id = clean_arxiv_id(raw_id)
            title = normalize_space(entry.findtext("atom:title", default="", namespaces=ns))
            summary = normalize_space(entry.findtext("atom:summary", default="", namespaces=ns))
            published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
            authors = [normalize_space(a.findtext("atom:name", default="", namespaces=ns)) for a in entry.findall("atom:author", ns)]
            paper = Paper(
                id=f"arxiv:{arxiv_id}",
                title=title,
                authors=[a for a in authors if a],
                url=f"https://arxiv.org/abs/{arxiv_id}",
                source_type="arxiv",
                published=published or None,
                summary=summary,
                doi=f"10.48550/arXiv.{arxiv_id}",
            )
            score_and_tag(paper)
            papers[paper.id] = paper
    return list(papers.values())


def fetch_crossref(from_date: str, rows: int = 8) -> list[Paper]:
    papers: dict[str, Paper] = {}
    for query in CROSSREF_QUERIES:
        params = urllib.parse.urlencode({
            "query.bibliographic": query,
            "filter": f"from-pub-date:{from_date}",
            "rows": rows,
            "select": "DOI,title,author,published-print,published-online,container-title,URL,abstract",
        })
        url = f"https://api.crossref.org/works?{params}"
        try:
            payload = json.loads(fetch_text(url))
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"warning: Crossref query failed: {query}: {exc}", file=sys.stderr)
            continue
        for item in payload.get("message", {}).get("items", []):
            doi = item.get("DOI")
            titles = item.get("title") or []
            if not doi or not titles:
                continue
            title = normalize_space(html.unescape(titles[0]))
            authors = []
            for a in item.get("author") or []:
                name = " ".join(x for x in [a.get("given"), a.get("family")] if x)
                if name:
                    authors.append(name)
            abstract = re.sub("<[^>]+>", " ", item.get("abstract") or "")
            abstract = normalize_space(html.unescape(abstract))
            date_parts = (item.get("published-print") or item.get("published-online") or {}).get("date-parts") or []
            published = "-".join(f"{part:02d}" for part in date_parts[0]) if date_parts else None
            paper = Paper(
                id=f"doi:{doi.lower()}",
                title=title,
                authors=authors,
                url=item.get("URL") or f"https://doi.org/{doi}",
                source_type="journal",
                published=published,
                summary=abstract,
                doi=doi,
            )
            score_and_tag(paper)
            papers[paper.id] = paper
    return list(papers.values())


def score_and_tag(paper: Paper) -> None:
    haystack = f"{paper.title} {paper.summary}".lower()
    score = 0
    tags = []
    for term, weight in WEIGHTS.items():
        if term in haystack:
            score += weight
            tags.append(term)
    paper.score = score
    paper.tags = sorted(set(tags), key=lambda x: (-WEIGHTS.get(x, 0), x))[:8]
    directions = []
    for direction, terms in DIRECTION_KEYWORDS.items():
        if any(term in haystack for term in terms):
            directions.append(direction)
    paper.directions = directions or ["精确解与特殊背景"]


def relevance_label(score: int) -> str:
    if score >= 28:
        return "重点关注"
    if score >= 18:
        return "值得关注"
    if score >= 10:
        return "背景参考"
    return "观察"


def select_papers(papers: Iterable[Paper], seen: set[str], limit: int) -> list[Paper]:
    fresh = [p for p in papers if p.id not in seen and p.score >= 10]
    fresh.sort(key=lambda p: (p.score, p.published or ""), reverse=True)
    return fresh[:limit]


def md_link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def render_daily(date: str, papers: list[Paper]) -> str:
    lines = [f"## {date}", ""]
    if not papers:
        lines += ["今日未筛到强相关新条目。", ""]
        return "\n".join(lines)
    lines += [
        "本期由脚本根据 arXiv、Crossref 与关键词/分类规则生成候选条目；维护者或 AI 助手可在提交前继续压缩、改写或删除弱相关条目。",
        "",
    ]
    for direction in ["精确解与特殊背景", "稳定性与动力学机制", "IST / RHP 与渐近分析"]:
        group = [p for p in papers if direction in p.directions]
        if not group:
            continue
        lines += [f"### {direction}", ""]
        for p in group:
            authors = "；".join(p.authors[:6]) if p.authors else "未列出"
            tags = ", ".join(p.tags[:6]) if p.tags else "待补充"
            lines += [
                f"- **{p.title}**  ",
                f"  作者：{authors}  ",
                f"  来源：{md_link(p.id, p.url)}  ",
                f"  标签：{tags}  ",
                f"  相关性：**{relevance_label(p.score)}**  ",
                f"  简评：与本栏目关键词匹配度较高；建议人工检查摘要和主定理后再决定是否保留为长期文献图谱条目。",
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"


def week_id(date: dt.date) -> str:
    year, week, _ = date.isocalendar()
    return f"{year}-W{week:02d}"


def replace_date_block(weekly_text: str, date: str, block: str) -> str:
    pattern = re.compile(rf"\n---\n\n## {re.escape(date)}\n.*?(?=\n---\n\n## |\Z)", re.S)
    replacement = "\n---\n\n" + block.rstrip() + "\n"
    if pattern.search(weekly_text):
        return pattern.sub(replacement, weekly_text)
    return weekly_text.rstrip() + replacement


def render_latest(date: str, week: str, daily_block: str) -> str:
    return f"""# 最新每日简报

[本周完整记录]({week}.md) · [简报归档](index.md) · [返回首页](../index.md)

!!! note "AI 生成说明"
    本页为固定的最新简报入口。每日更新时，自动化流程应覆盖本页内容，并同时把同一批条目追加到本周归档文件。简报主要依据题名、摘要、分类、关键词和公开元数据筛选；条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。

{daily_block.rstrip()}
"""


def render_registry_entries(papers: list[Paper], date: str, week: str) -> str:
    chunks = []
    for p in papers:
        authors = "\n".join(f'    - "{a.replace(chr(34), chr(39))}"' for a in p.authors)
        tags = "\n".join(f'    - "{t.replace(chr(34), chr(39))}"' for t in p.tags)
        directions = "\n".join(f'    - "{d}"' for d in p.directions)
        chunks.append(f'''- id: "{p.id}"
  title: "{p.title.replace(chr(34), chr(39))}"
  authors:
{authors or '    []'}
  source:
    type: "{p.source_type}"
    url: "{p.url}"
    arxiv_id: {json.dumps(p.id.split(':', 1)[1]) if p.id.startswith('arxiv:') else 'null'}
    doi: {json.dumps(p.doi) if p.doi else 'null'}
  first_seen: "{date}"
  first_week: "{week}"
  directions:
{directions}
  tags:
{tags or '    []'}
  relevance: "{relevance_label(p.score)}"
  review_status: "script-screened"
  appeared_in:
    - "docs/radar/{week}.md"
    - "docs/radar/latest.md"
''')
    return "\n".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--days", type=int, default=45, help="Crossref lookback window")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    date_obj = dt.date.fromisoformat(args.date)
    week = week_id(date_obj)
    from_date = (date_obj - dt.timedelta(days=args.days)).isoformat()

    seen = existing_ids()
    candidates = fetch_arxiv() + fetch_crossref(from_date)
    selected = select_papers(candidates, seen, args.limit)
    daily_block = render_daily(args.date, selected)

    if args.dry_run or not args.write:
        print(daily_block)
        return

    RADAR_DIR.mkdir(parents=True, exist_ok=True)
    week_path = RADAR_DIR / f"{week}.md"
    if not week_path.exists():
        week_path.write_text(
            f"# 可积系统研究简报 · {week}\n\n"
            "本页为 AI 辅助生成的研究简报，主要面向 Ling Liming 课题组相关方向，跟踪可积系统、非线性波、精确解、稳定性、IST/RHP 与长时间渐近分析中的近期论文和研究线索。\n\n"
            "筛选主要依据题名、摘要、arXiv 分类、关键词和公开元数据。条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。除特别标注外，条目尚未经过人工逐篇验证；数学结论请以原论文为准。\n\n"
            "本周文件用于连续记录每日发现。周末或每周整理时，可在本文顶部补充“本周重点关注”。\n",
            encoding="utf-8",
        )
    weekly_text = week_path.read_text(encoding="utf-8")
    week_path.write_text(replace_date_block(weekly_text, args.date, daily_block), encoding="utf-8")
    LATEST_PAGE.write_text(render_latest(args.date, week, daily_block), encoding="utf-8")

    if selected:
        registry_text = PAPER_REGISTRY.read_text(encoding="utf-8") if PAPER_REGISTRY.exists() else ""
        if registry_text.strip() == "[]":
            registry_text = ""
        registry_text = registry_text.rstrip() + "\n\n" + render_registry_entries(selected, args.date, week)
        PAPER_REGISTRY.write_text(registry_text.lstrip(), encoding="utf-8")

    print(f"wrote {len(selected)} papers to {week_path.relative_to(ROOT)} and {LATEST_PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
