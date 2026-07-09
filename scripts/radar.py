#!/usr/bin/env python3
"""Generate a draft daily research brief for the site.

The script fetches candidate papers from arXiv and Crossref, applies a
Ling-group-oriented keyword rubric, checks `data/papers.yml` to avoid repeated
"new paper" entries, and writes:

- `docs/index.md`: homepage with the full latest daily brief and site links;
- `docs/radar/latest.md`: fixed latest daily brief mirror;
- `docs/radar/YYYY-WXX.md`: weekly archive file.

The output is a discovery draft, not mathematical verification.

Usage:
    python scripts/radar.py --date 2026-07-09 --dry-run
    python scripts/radar.py --date 2026-07-09 --write
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

ARXIV_QUERIES = [
    'cat:nlin.SI AND all:"derivative nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"DNLS"',
    'cat:nlin.SI AND all:"coupled derivative nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"two-component"',
    'cat:nlin.SI AND all:"multi-component"',
    'cat:nlin.SI AND all:"multicomponent"',
    'cat:nlin.SI AND all:"Gerdjikov Ivanov"',
    'cat:nlin.SI AND all:"coupled Gerdjikov Ivanov"',
    'cat:nlin.SI AND all:"Fokas Lenells"',
    'cat:nlin.SI AND all:"Kaup Newell"',
    'cat:nlin.SI AND all:"Chen Lee Liu"',
    'cat:nlin.SI AND all:"coupled nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"Darboux"',
    'cat:nlin.SI AND all:"rogue wave"',
    'cat:nlin.SI AND all:"breather"',
    'cat:nlin.SI AND all:"elliptic localized"',
    'cat:nlin.SI AND all:"inverse scattering"',
    'cat:nlin.SI AND all:"Riemann Hilbert"',
    'cat:nlin.SI AND all:"long-time asymptotics"',
    'cat:nlin.SI AND all:"soliton gas"',
    'cat:math.AP AND all:"derivative nonlinear Schrodinger"',
    'cat:math-ph AND all:"inverse scattering"',
]

CROSSREF_QUERIES = [
    "derivative nonlinear Schrodinger soliton gas",
    "coupled derivative nonlinear Schrodinger inverse scattering",
    "coupled Gerdjikov Ivanov inverse scattering",
    "coupled nonlinear Schrodinger orbital stability breather",
    "multi-component nonlinear Schrodinger Darboux rogue wave",
    "Fokas Lenells elliptic localized solutions",
    "Riemann Hilbert long-time asymptotics derivative NLS",
]

WEIGHTS = {
    "derivative nonlinear schrodinger": 12,
    "dnls": 10,
    "gerdjikov": 10,
    "fokas": 9,
    "lenells": 9,
    "kaup": 9,
    "newell": 9,
    "chen lee liu": 8,
    "chen-lee-liu": 8,
    "coupled": 9,
    "two-component": 9,
    "multi-component": 9,
    "multi component": 9,
    "multicomponent": 9,
    "vector": 6,
    "manakov": 7,
    "inverse scattering": 10,
    "riemann-hilbert": 10,
    "riemann hilbert": 10,
    "marchenko": 9,
    "jost": 8,
    "long-time": 8,
    "long time": 8,
    "asymptotic": 6,
    "soliton gas": 10,
    "dbar": 7,
    "barpartial": 7,
    "darboux": 8,
    "backlund": 7,
    "rogue wave": 7,
    "breather": 8,
    "elliptic": 7,
    "finite-gap": 6,
    "theta": 5,
    "stability": 8,
    "spectral stability": 8,
    "orbital stability": 9,
    "squared eigenfunction": 9,
}

DIRECTION_KEYWORDS = {
    "稳定性与动力学机制": ["stability", "orbital", "spectral stability", "krein", "modulational", "squared eigenfunction"],
    "IST / RHP 与渐近分析": ["inverse scattering", "riemann-hilbert", "riemann hilbert", "marchenko", "jost", "long-time", "long time", "asymptotic", "steepest descent", "soliton gas", "dbar", "barpartial"],
    "精确解与特殊背景": ["darboux", "backlund", "rogue", "breather", "elliptic", "finite-gap", "theta", "weierstrass", "localized solution", "soliton solution"],
}
DIRECTION_ORDER = ["精确解与特殊背景", "稳定性与动力学机制", "IST / RHP 与渐近分析"]


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
    return set(re.findall(r'^- id:\s+"([^"]+)"', PAPER_REGISTRY.read_text(encoding="utf-8"), flags=re.M))


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_arxiv_id(raw_id: str) -> str:
    return raw_id.rstrip("/").split("/")[-1]


def score_and_tag(paper: Paper) -> None:
    haystack = f"{paper.title} {paper.summary}".lower()
    paper.score = sum(weight for term, weight in WEIGHTS.items() if term in haystack)
    paper.tags = sorted({term for term in WEIGHTS if term in haystack}, key=lambda x: (-WEIGHTS[x], x))[:8]
    paper.directions = [name for name, terms in DIRECTION_KEYWORDS.items() if any(t in haystack for t in terms)] or ["精确解与特殊背景"]


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
        try:
            root = ET.fromstring(fetch_text(f"https://export.arxiv.org/api/query?{params}"))
        except Exception as exc:
            print(f"warning: arXiv query failed: {query}: {exc}", file=sys.stderr)
            continue
        for entry in root.findall("atom:entry", ns):
            arxiv_id = clean_arxiv_id(entry.findtext("atom:id", default="", namespaces=ns))
            paper = Paper(
                id=f"arxiv:{arxiv_id}",
                title=normalize_space(entry.findtext("atom:title", default="", namespaces=ns)),
                authors=[normalize_space(a.findtext("atom:name", default="", namespaces=ns)) for a in entry.findall("atom:author", ns)],
                url=f"https://arxiv.org/abs/{arxiv_id}",
                source_type="arxiv",
                published=entry.findtext("atom:published", default="", namespaces=ns)[:10] or None,
                summary=normalize_space(entry.findtext("atom:summary", default="", namespaces=ns)),
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
        try:
            payload = json.loads(fetch_text(f"https://api.crossref.org/works?{params}"))
        except Exception as exc:
            print(f"warning: Crossref query failed: {query}: {exc}", file=sys.stderr)
            continue
        for item in payload.get("message", {}).get("items", []):
            doi = item.get("DOI")
            titles = item.get("title") or []
            if not doi or not titles:
                continue
            authors = []
            for author in item.get("author") or []:
                name = " ".join(x for x in [author.get("given"), author.get("family")] if x)
                if name:
                    authors.append(name)
            paper = Paper(
                id=f"doi:{doi.lower()}",
                title=normalize_space(html.unescape(titles[0])),
                authors=authors,
                url=item.get("URL") or f"https://doi.org/{doi}",
                source_type="journal",
                summary=normalize_space(html.unescape(re.sub("<[^>]+>", " ", item.get("abstract") or ""))),
                doi=doi,
            )
            score_and_tag(paper)
            papers[paper.id] = paper
    return list(papers.values())


def primary_direction(paper: Paper) -> str:
    for direction in DIRECTION_ORDER:
        if direction in paper.directions:
            return direction
    return paper.directions[0]


def relevance_label(score: int) -> str:
    if score >= 32:
        return "重点关注"
    if score >= 22:
        return "值得关注"
    if score >= 12:
        return "背景参考"
    return "观察"


def select_papers(papers: Iterable[Paper], seen: set[str], limit: int) -> list[Paper]:
    fresh = [p for p in papers if p.id not in seen and p.score >= 12]
    fresh.sort(key=lambda p: (p.score, p.published or ""), reverse=True)
    return fresh[:limit]


def md_link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def render_card(paper: Paper) -> str:
    authors = "；".join([a for a in paper.authors if a][:8]) or "未列出"
    tags = ", ".join(paper.tags[:7]) or "待补充"
    return "\n".join([
        f"#### [{relevance_label(paper.score)}] {paper.title}",
        "",
        f"作者：{authors}  ",
        f"来源：{md_link(paper.id, paper.url)}  ",
        f"标签：{tags}",
        "",
        "简评：与本栏目关键词匹配度较高；建议人工检查摘要、Introduction 和主定理后再决定是否保留为长期文献图谱条目。",
    ])


def render_daily(date: str, papers: list[Paper]) -> str:
    lines = [f"## {date}", ""]
    if not papers:
        return "\n".join(lines + ["今日未筛到强相关新条目。", ""])
    for direction in DIRECTION_ORDER:
        group = [p for p in papers if primary_direction(p) == direction]
        if not group:
            continue
        lines += [f"### {direction}", ""]
        for paper in group:
            lines += [render_card(paper), ""]
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


def render_latest(week: str, daily_block: str) -> str:
    return f"""# 最新每日简报

[返回首页](../index.md) · [本周归档]({week}.md) · [全部归档](index.md)

!!! note "AI 生成说明"
    本页为固定的最新简报入口。每日更新时，自动化流程应覆盖本页内容，并同时把同一批条目追加到本周归档文件。简报主要依据题名、摘要、分类、关键词和公开元数据筛选；条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。

{daily_block.rstrip()}
"""


def render_home(week: str, daily_block: str) -> str:
    return f"""# 可积系统研究简报

本页显示最新的 AI 辅助研究简报，面向 Ling Liming 课题组相关方向，重点关注可积系统中的精确解与特殊背景、稳定性与动力学机制、IST/RHP 与渐近分析。

[本周归档](radar/{week}.md) · [全部归档](radar/index.md)

!!! note "AI 生成说明"
    简报主要依据题名、摘要、arXiv 分类、关键词和公开元数据筛选。条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。除特别标注外，条目尚未经过人工逐篇验证；数学结论请以原论文为准。

{daily_block.rstrip()}

## 其他入口

- [本周归档](radar/{week}.md): 保存本周每日简报的完整记录。
- [全部归档](radar/index.md): 按周回看历史简报。
- [Resources / 资源](resources.md): selected courses, lecture notes, homepages, and search links.
- [Group work / 课题组相关](group-work.md): local research context, public notes, and group-facing links.
- [Core topics / 核心主题](topics.md): current scope of the guide.
- [About / 关于](about.md): curation policy, design references, and license notes.
"""


def render_registry_entries(papers: list[Paper], date: str, week: str) -> str:
    chunks = []
    for p in papers:
        authors = "\n".join(f'    - "{a.replace(chr(34), chr(39))}"' for a in p.authors if a)
        tags = "\n".join(f'    - "{t.replace(chr(34), chr(39))}"' for t in p.tags)
        direction = f'    - "{primary_direction(p)}"'
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
{direction}
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
    week_path.write_text(replace_date_block(week_path.read_text(encoding="utf-8"), args.date, daily_block), encoding="utf-8")
    LATEST_PAGE.write_text(render_latest(week, daily_block), encoding="utf-8")
    DOCS_INDEX.write_text(render_home(week, daily_block), encoding="utf-8")

    if selected:
        registry_text = PAPER_REGISTRY.read_text(encoding="utf-8") if PAPER_REGISTRY.exists() else ""
        if registry_text.strip() == "[]":
            registry_text = ""
        registry_text = registry_text.rstrip() + "\n\n" + render_registry_entries(selected, args.date, week)
        PAPER_REGISTRY.write_text(registry_text.lstrip(), encoding="utf-8")

    print(f"wrote {len(selected)} papers to homepage, latest page, and {week_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
