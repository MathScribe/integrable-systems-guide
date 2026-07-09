#!/usr/bin/env python3
"""Generate a candidate daily research radar update.

The script is conservative about publishing: it uses broad public metadata
searches for recall, but only writes public daily-brief pages when a new
high-confidence paper passes the scoring rubric. Weaker items are stored in
`data/candidates.yml` so they are not suggested again every day.

Sources currently used:
- arXiv API (`export.arxiv.org/api/query`), mostly nlin.SI/math-ph/math.AP;
- Crossref API, mainly for journal/DOI metadata;
- OpenAlex API, as a supplementary public metadata source.

The output is a discovery draft, not mathematical verification.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PAPER_REGISTRY = ROOT / "data" / "papers.yml"
CANDIDATE_REGISTRY = ROOT / "data" / "candidates.yml"
DOCS_INDEX = ROOT / "docs" / "index.md"
RADAR_DIR = ROOT / "docs" / "radar"
LATEST_PAGE = RADAR_DIR / "latest.md"
SUMMARY_DIR = ROOT / ".radar"
SUMMARY_JSON = SUMMARY_DIR / "summary.json"
SUMMARY_MD = SUMMARY_DIR / "summary.md"

ARXIV_QUERIES = [
    'cat:nlin.SI AND all:"derivative nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"derivative NLS"',
    'cat:nlin.SI AND all:"DNLS"',
    'cat:nlin.SI AND all:"coupled derivative nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"Gerdjikov Ivanov"',
    'cat:nlin.SI AND all:"coupled Gerdjikov Ivanov"',
    'cat:nlin.SI AND all:"Fokas Lenells"',
    'cat:nlin.SI AND all:"Kaup Newell"',
    'cat:nlin.SI AND all:"Chen Lee Liu"',
    'cat:nlin.SI AND all:"coupled nonlinear Schrodinger"',
    'cat:nlin.SI AND all:"Manakov"',
    'cat:nlin.SI AND all:"multi-component NLS"',
    'cat:nlin.SI AND all:"two-component NLS"',
    'cat:nlin.SI AND all:"inverse scattering"',
    'cat:nlin.SI AND all:"Riemann Hilbert"',
    'cat:nlin.SI AND all:"dbar"',
    'cat:nlin.SI AND all:"Deift Zhou"',
    'cat:nlin.SI AND all:"long-time asymptotics"',
    'cat:nlin.SI AND all:"nonlinear steepest descent"',
    'cat:nlin.SI AND all:"Marchenko"',
    'cat:nlin.SI AND all:"Jost solutions"',
    'cat:nlin.SI AND all:"Lax pair"',
    'cat:nlin.SI AND all:"zero curvature"',
    'cat:nlin.SI AND all:"Darboux"',
    'cat:nlin.SI AND all:"Backlund"',
    'cat:nlin.SI AND all:"dressing method"',
    'cat:nlin.SI AND all:"Hirota bilinear"',
    'cat:nlin.SI AND all:"squared eigenfunctions"',
    'cat:nlin.SI AND all:"finite-gap"',
    'cat:nlin.SI AND all:"algebro-geometric"',
    'cat:nlin.SI AND all:"theta functions"',
    'cat:nlin.SI AND all:"Whitham"',
    'cat:nlin.SI AND all:"modulational instability"',
    'cat:nlin.SI AND all:"spectral stability"',
    'cat:nlin.SI AND all:"orbital stability"',
    'cat:nlin.SI AND all:"rogue wave"',
    'cat:nlin.SI AND all:"breather"',
    'cat:nlin.SI AND all:"elliptic background"',
    'cat:nlin.SI AND all:"elliptic localized"',
    'cat:nlin.SI AND all:"soliton gas"',
    'cat:nlin.SI AND all:"complex mKdv"',
    'cat:nlin.SI AND all:"modified Korteweg"',
    'cat:nlin.SI AND all:"complex short pulse"',
    'cat:nlin.SI AND all:"short pulse equation"',
    'cat:nlin.SI AND all:"Ablowitz Ladik"',
    'cat:nlin.SI AND all:"Davey Stewartson"',
    'cat:nlin.SI AND all:"Yajima Oikawa"',
    'cat:nlin.SI AND all:"Landau Lifshitz"',
    'cat:nlin.SI AND all:"sine Gordon"',
    'cat:nlin.SI AND all:"Toda lattice"',
    'cat:math-ph AND all:"inverse scattering"',
    'cat:math-ph AND all:"Riemann Hilbert"',
    'cat:math.AP AND all:"long-time asymptotics"',
    'cat:math.AP AND all:"derivative nonlinear Schrodinger"',
]

CROSSREF_QUERIES = [
    "derivative nonlinear Schrodinger soliton gas",
    "coupled derivative nonlinear Schrodinger inverse scattering",
    "coupled Gerdjikov Ivanov inverse scattering",
    "Fokas Lenells elliptic localized solutions",
    "coupled nonlinear Schrodinger orbital stability breather",
    "multi-component nonlinear Schrodinger Darboux rogue wave",
    "Riemann Hilbert long-time asymptotics derivative NLS",
    "finite-gap solutions modified Korteweg de Vries theta functions",
    "algebro-geometric solutions nonlinear Schrodinger hierarchy",
    "Ablowitz Ladik Riemann Hilbert asymptotics",
]

OPENALEX_QUERIES = [
    "derivative nonlinear Schrodinger inverse scattering",
    "coupled Gerdjikov Ivanov equations",
    "Fokas Lenells Darboux transformation",
    "coupled nonlinear Schrodinger breather orbital stability",
    "Riemann Hilbert long time asymptotics integrable systems",
    "finite-gap algebro-geometric nonlinear waves theta functions",
    "soliton gas derivative NLS",
]

TERM_GROUPS: dict[str, dict[str, int]] = {
    "core_system": {
        "derivative nonlinear schrodinger": 22,
        "derivative nls": 20,
        "dnls": 20,
        "gerdjikov ivanov": 22,
        "fokas lenells": 20,
        "kaup newell": 18,
        "chen lee liu": 17,
        "coupled derivative nonlinear schrodinger": 24,
        "coupled nls": 18,
        "coupled nonlinear schrodinger": 18,
        "vector nonlinear schrodinger": 16,
        "multi-component nls": 16,
        "multicomponent nls": 16,
        "two-component nls": 16,
        "manakov": 15,
        "nls hierarchy": 12,
        "akns hierarchy": 12,
    },
    "method": {
        "inverse scattering transform": 18,
        "inverse scattering": 17,
        "riemann hilbert": 17,
        "riemann-hilbert": 17,
        "rhp": 14,
        "dbar": 14,
        "barpartial": 14,
        "deift zhou": 14,
        "steepest descent": 12,
        "long-time asymptotics": 13,
        "long time asymptotics": 13,
        "marchenko": 13,
        "jost": 12,
        "lax pair": 10,
        "zero curvature": 10,
        "darboux": 13,
        "backlund": 11,
        "dressing method": 11,
        "hirota": 8,
        "bilinear": 7,
        "squared eigenfunction": 14,
        "squared eigenfunctions": 14,
        "finite gap": 12,
        "finite-gap": 12,
        "algebro geometric": 12,
        "algebro-geometric": 12,
        "theta function": 10,
        "theta functions": 10,
        "whitham": 10,
        "modulational instability": 10,
        "spectral stability": 12,
        "orbital stability": 14,
        "recursion operator": 8,
        "hamiltonian hierarchy": 8,
        "tau function": 8,
    },
    "adjacent_system": {
        "modified korteweg": 10,
        "mkdv": 10,
        "complex mkdv": 12,
        "short pulse equation": 9,
        "complex short pulse": 11,
        "ablowitz ladik": 11,
        "sine gordon": 8,
        "sinh gordon": 8,
        "toda lattice": 8,
        "landau lifshitz": 8,
        "davey stewartson": 9,
        "yajima oikawa": 9,
        "melnikov": 7,
        "massive thirring": 9,
        "wadati konno ichikawa": 9,
        "camassa holm": 7,
    },
    "object": {
        "rogue wave": 11,
        "rogue waves": 11,
        "breather": 11,
        "breathers": 11,
        "vector soliton": 10,
        "vector solitons": 10,
        "soliton gas": 14,
        "elliptic background": 12,
        "elliptic solution": 9,
        "elliptic localized": 11,
        "localized solution": 8,
        "localized solutions": 8,
        "finite-gap solution": 10,
        "finite-gap solutions": 10,
        "lump": 5,
        "dark soliton": 6,
        "bright soliton": 6,
    },
    "negative": {
        "machine learning": -16,
        "neural network": -16,
        "physics-informed": -12,
        "experiment": -10,
        "experimental": -10,
        "material": -9,
        "skyrmion": -13,
        "magnetic": -10,
        "spin-current": -12,
        "plasma": -10,
        "traffic": -12,
        "biological": -10,
        "epidemiological": -10,
        "topological insulator": -10,
    },
}

WATCH_AUTHORS = {
    "liming ling",
    "dmitry pelinovsky",
    "dmitry e pelinovsky",
    "guo-fu yu",
    "guofu yu",
    "bao-feng feng",
    "baofeng feng",
    "ken-ichi maruno",
    "yasuhiro ohta",
    "huajie su",
}

DIRECTION_KEYWORDS = {
    "稳定性与动力学机制": ["stability", "orbital", "spectral stability", "krein", "modulational", "squared eigenfunction", "whitham"],
    "IST / RHP 与渐近分析": ["inverse scattering", "riemann hilbert", "riemann-hilbert", "rhp", "marchenko", "jost", "long-time", "long time", "asymptotic", "steepest descent", "soliton gas", "dbar", "barpartial", "deift zhou"],
    "精确解与特殊背景": ["darboux", "backlund", "dressing", "hirota", "rogue", "breather", "elliptic", "finite-gap", "finite gap", "theta", "weierstrass", "localized solution", "algebro-geometric"],
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
    arxiv_id: str | None = None
    score: int = 0
    status: str = "rejected"
    level: str = "观察"
    reason: str = ""
    directions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    hits: dict[str, list[str]] = field(default_factory=dict)
    title_fingerprint: str = ""
    key: str = ""
    sources_seen: list[str] = field(default_factory=list)


@dataclass
class RegistryIndex:
    ids: set[str] = field(default_factory=set)
    arxiv_ids: set[str] = field(default_factory=set)
    dois: set[str] = field(default_factory=set)
    title_fingerprints: set[str] = field(default_factory=set)


@dataclass
class CandidateRecord:
    key: str
    title: str
    arxiv_id: str | None
    doi: str | None
    title_fingerprint: str
    authors: list[str]
    sources_seen: list[str]
    first_seen: str
    last_seen: str
    seen_count: int
    status: str
    level: str
    score: int
    reason: str
    directions: list[str]
    tags: list[str]
    source_url: str
    appeared_in: list[str] = field(default_factory=list)


def fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "MathScribe research radar"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def ascii_fold(text: str) -> str:
    text = text.replace("∂̄", " dbar ").replace("∂bar", " dbar ").replace("\\bar\\partial", " dbar ")
    text = text.replace("–", "-").replace("—", "-")
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def search_text(text: str) -> str:
    text = ascii_fold(text).lower()
    text = re.sub(r"[{}$\\_^]", " ", text)
    return normalize_space(text)


def title_fingerprint(title: str) -> str:
    text = search_text(title)
    text = text.replace("non-linear", "nonlinear")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    stop = {"a", "an", "the", "of", "for", "on", "and", "with", "to", "in", "associated", "via"}
    words = [w for w in text.split() if w not in stop]
    return " ".join(words)


def normalize_arxiv_id(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().rstrip("/").split("/")[-1]
    value = re.sub(r"v\d+$", "", value)
    return value or None


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    value = value.replace("doi:", "").strip()
    return value or None


def real_doi(value: str | None) -> str | None:
    doi = normalize_doi(value)
    if doi and not doi.startswith("10.48550/arxiv."):
        return doi
    return None


def canonical_key(paper: Paper) -> str:
    if paper.arxiv_id:
        return f"arxiv:{paper.arxiv_id}"
    if paper.doi:
        return f"doi:{paper.doi}"
    return f"title:{paper.title_fingerprint}"


def q(value: str | None) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def yaml_list(items: Iterable[str], indent: int = 4) -> str:
    pad = " " * indent
    values = [x for x in items if x]
    if not values:
        return f"{pad}[]"
    return "\n".join(f"{pad}- {q(x)}" for x in values)


def clean_arxiv_id(raw_id: str) -> str:
    return normalize_arxiv_id(raw_id) or ""


def extract_abstract(inv: dict[str, list[int]] | None) -> str:
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for idx in idxs:
            positions.append((idx, word))
    positions.sort()
    return normalize_space(" ".join(word for _, word in positions))


def published_from_crossref(item: dict) -> str | None:
    for key in ["published-online", "published-print", "created", "issued"]:
        parts = ((item.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            date_parts = [str(x) for x in parts[0]]
            while len(date_parts) < 3:
                date_parts.append("01")
            return "-".join(date_parts[:3])
    return None


def fetch_arxiv(max_results_per_query: int = 8, delay_seconds: float = 3.1) -> list[Paper]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers: list[Paper] = []
    for query_index, query in enumerate(ARXIV_QUERIES):
        if query_index > 0 and delay_seconds > 0:
            time.sleep(delay_seconds)
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
            if not arxiv_id:
                continue
            papers.append(Paper(
                id=f"arxiv:{arxiv_id}",
                title=normalize_space(entry.findtext("atom:title", default="", namespaces=ns)),
                authors=[normalize_space(a.findtext("atom:name", default="", namespaces=ns)) for a in entry.findall("atom:author", ns)],
                url=f"https://arxiv.org/abs/{arxiv_id}",
                source_type="arxiv",
                published=entry.findtext("atom:published", default="", namespaces=ns)[:10] or None,
                summary=normalize_space(entry.findtext("atom:summary", default="", namespaces=ns)),
                arxiv_id=arxiv_id,
                sources_seen=["arxiv"],
            ))
    return papers


def fetch_crossref(from_date: str, rows: int = 6) -> list[Paper]:
    papers: list[Paper] = []
    for query in CROSSREF_QUERIES:
        params = urllib.parse.urlencode({
            "query.bibliographic": query,
            "filter": f"from-pub-date:{from_date}",
            "rows": rows,
            "select": "DOI,title,author,published-print,published-online,created,issued,container-title,URL,abstract",
        })
        try:
            payload = json.loads(fetch_text(f"https://api.crossref.org/works?{params}"))
        except Exception as exc:
            print(f"warning: Crossref query failed: {query}: {exc}", file=sys.stderr)
            continue
        for item in payload.get("message", {}).get("items", []):
            doi = real_doi(item.get("DOI"))
            titles = item.get("title") or []
            if not doi or not titles:
                continue
            authors = []
            for author in item.get("author") or []:
                name = " ".join(x for x in [author.get("given"), author.get("family")] if x)
                if name:
                    authors.append(normalize_space(name))
            papers.append(Paper(
                id=f"doi:{doi}",
                title=normalize_space(html.unescape(titles[0])),
                authors=authors,
                url=item.get("URL") or f"https://doi.org/{doi}",
                source_type="journal",
                published=published_from_crossref(item),
                summary=normalize_space(html.unescape(re.sub("<[^>]+>", " ", item.get("abstract") or ""))),
                doi=doi,
                sources_seen=["crossref"],
            ))
    return papers


def fetch_openalex(from_date: str, rows: int = 6) -> list[Paper]:
    papers: list[Paper] = []
    for query in OPENALEX_QUERIES:
        params = urllib.parse.urlencode({
            "search": query,
            "filter": f"from_publication_date:{from_date}",
            "per-page": rows,
            "sort": "publication_date:desc",
        })
        try:
            payload = json.loads(fetch_text(f"https://api.openalex.org/works?{params}"))
        except Exception as exc:
            print(f"warning: OpenAlex query failed: {query}: {exc}", file=sys.stderr)
            continue
        for item in payload.get("results", []):
            title = normalize_space(item.get("title") or "")
            if not title:
                continue
            doi = real_doi(item.get("doi"))
            arxiv_id = None
            for loc in item.get("locations") or []:
                landing = ((loc or {}).get("landing_page_url") or "")
                if "arxiv.org/abs/" in landing:
                    arxiv_id = normalize_arxiv_id(landing)
                    break
            authors = []
            for authorship in item.get("authorships") or []:
                display = ((authorship or {}).get("author") or {}).get("display_name")
                if display:
                    authors.append(normalize_space(display))
            primary = item.get("primary_location") or {}
            source_url = primary.get("landing_page_url") or item.get("doi") or item.get("id") or ""
            papers.append(Paper(
                id=f"arxiv:{arxiv_id}" if arxiv_id else (f"doi:{doi}" if doi else f"openalex:{item.get('id', title)}"),
                title=title,
                authors=authors,
                url=source_url,
                source_type="openalex",
                published=item.get("publication_date"),
                summary=extract_abstract(item.get("abstract_inverted_index")),
                doi=doi,
                arxiv_id=arxiv_id,
                sources_seen=["openalex"],
            ))
    return papers


def prepare_paper(paper: Paper) -> Paper:
    paper.title_fingerprint = title_fingerprint(paper.title)
    paper.doi = real_doi(paper.doi)
    paper.arxiv_id = normalize_arxiv_id(paper.arxiv_id)
    paper.key = canonical_key(paper)
    return paper


def merge_papers(papers: Iterable[Paper]) -> list[Paper]:
    merged: list[Paper] = []
    for paper in papers:
        prepare_paper(paper)
        match: Paper | None = None
        for old in merged:
            same_arxiv = paper.arxiv_id and old.arxiv_id == paper.arxiv_id
            same_doi = paper.doi and old.doi == paper.doi
            same_title = paper.title_fingerprint and old.title_fingerprint == paper.title_fingerprint and len(paper.title_fingerprint) >= 24
            if same_arxiv or same_doi or same_title:
                match = old
                break
        if match is None:
            merged.append(paper)
            continue
        if paper.arxiv_id and not match.arxiv_id:
            match.arxiv_id = paper.arxiv_id
            match.id = f"arxiv:{paper.arxiv_id}"
        if paper.doi and not match.doi:
            match.doi = paper.doi
        if paper.url and (not match.url or match.source_type == "openalex"):
            match.url = paper.url
        if len(paper.summary) > len(match.summary):
            match.summary = paper.summary
        for author in paper.authors:
            if author and author not in match.authors:
                match.authors.append(author)
        for source in paper.sources_seen:
            if source not in match.sources_seen:
                match.sources_seen.append(source)
        if match.source_type != paper.source_type:
            match.source_type = "mixed"
        match.key = canonical_key(match)
    return merged


def load_registry_index() -> RegistryIndex:
    idx = RegistryIndex()
    if not PAPER_REGISTRY.exists():
        return idx
    text = PAPER_REGISTRY.read_text(encoding="utf-8")
    idx.ids.update(re.findall(r'^- id:\s+"([^"]+)"', text, flags=re.M))
    idx.arxiv_ids.update(normalize_arxiv_id(x) or "" for x in re.findall(r'arxiv_id:\s+"?([^"\n]+)"?', text))
    idx.arxiv_ids.discard("null")
    idx.arxiv_ids.discard("")
    idx.dois.update(filter(None, (real_doi(x) for x in re.findall(r'doi:\s+"?([^"\n]+)"?', text))))
    for title in re.findall(r'title:\s+"([^"]+)"', text):
        fp = title_fingerprint(title)
        if fp:
            idx.title_fingerprints.add(fp)
    for fp in re.findall(r'title_fingerprint:\s+"([^"]+)"', text):
        if fp:
            idx.title_fingerprints.add(fp)
    return idx


def is_known_paper(paper: Paper, idx: RegistryIndex) -> bool:
    return (
        paper.id in idx.ids
        or (paper.arxiv_id is not None and paper.arxiv_id in idx.arxiv_ids)
        or (paper.doi is not None and paper.doi in idx.dois)
        or (paper.title_fingerprint in idx.title_fingerprints and len(paper.title_fingerprint) >= 24)
    )


def split_registry_blocks(text: str) -> tuple[str, list[str]]:
    starts = [m.start() for m in re.finditer(r'(?m)^- id:', text)]
    if not starts:
        return text, []
    header = text[:starts[0]]
    blocks = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        blocks.append(text[start:end])
    return header, blocks


def registry_block_info(block: str) -> dict[str, str | None]:
    def one(pattern: str) -> str | None:
        m = re.search(pattern, block, flags=re.M)
        return m.group(1).strip() if m else None

    title = one(r'^\s+title:\s+"([^"]+)"') or ""
    arxiv = one(r'^\s+arxiv_id:\s+"?([^"\n]+)"?')
    doi = one(r'^\s+doi:\s+"?([^"\n]+)"?')
    fp = one(r'^\s+title_fingerprint:\s+"([^"]+)"') or title_fingerprint(title)
    return {
        "title": title,
        "arxiv_id": None if arxiv in {None, "null"} else normalize_arxiv_id(arxiv),
        "doi": None if doi in {None, "null"} else normalize_doi(doi),
        "real_doi": None if doi in {None, "null"} else real_doi(doi),
        "title_fingerprint": fp,
    }


def paper_matches_registry_block(paper: Paper, info: dict[str, str | None]) -> bool:
    same_arxiv = paper.arxiv_id and info.get("arxiv_id") == paper.arxiv_id
    same_doi = paper.doi and info.get("real_doi") == paper.doi
    same_title = paper.title_fingerprint and info.get("title_fingerprint") == paper.title_fingerprint and len(paper.title_fingerprint) >= 24
    return bool(same_arxiv or same_doi or same_title)


def update_known_paper_metadata(papers: list[Paper], date: str) -> tuple[int, list[Paper]]:
    if not PAPER_REGISTRY.exists():
        return 0, []
    text = PAPER_REGISTRY.read_text(encoding="utf-8")
    header, blocks = split_registry_blocks(text)
    if not blocks:
        return 0, []
    changed = 0
    updated_papers: list[Paper] = []
    new_blocks = []
    for block in blocks:
        info = registry_block_info(block)
        replacement = block
        for paper in papers:
            prepare_paper(paper)
            if not paper.doi or not paper_matches_registry_block(paper, info):
                continue
            if info.get("real_doi") == paper.doi:
                continue
            replacement = re.sub(r'(?m)^(\s+doi:\s+)(?:null|"[^"]*"|[^\n]+)$', r'\1' + q(paper.doi), replacement, count=1)
            if 'last_metadata_update:' in replacement:
                replacement = re.sub(r'(?m)^(\s+last_metadata_update:\s+)(?:"[^"]*"|[^\n]+)$', r'\1' + q(date), replacement, count=1)
            else:
                replacement = re.sub(r'(?m)^(\s+review_status:\s+"[^"]+")$', r'\1\n  last_metadata_update: ' + q(date), replacement, count=1)
            if paper.source_type in {"journal", "mixed", "openalex"}:
                replacement = re.sub(r'(?m)^(\s+type:\s+)"arxiv"$', r'\1"mixed"', replacement, count=1)
            changed += 1
            paper.status = "metadata-updated"
            paper.level = "元数据更新"
            paper.reason = f"已发现正式 DOI 或跨源元数据：{paper.doi}"
            updated_papers.append(paper)
            break
        new_blocks.append(replacement)
    if changed:
        PAPER_REGISTRY.write_text(header + "".join(new_blocks), encoding="utf-8")
    return changed, updated_papers


def _section_items(block: str, section: str) -> list[str]:
    pattern = rf"\n\s+{re.escape(section)}:\n((?:\s+-\s+\"[^\"]+\"\n?|\s+\[\]\n?)+)"
    m = re.search(pattern, block)
    if not m:
        return []
    return re.findall(r'\s+-\s+"([^"]+)"', m.group(1))


def load_candidate_records() -> dict[str, CandidateRecord]:
    if not CANDIDATE_REGISTRY.exists():
        return {}
    text = CANDIDATE_REGISTRY.read_text(encoding="utf-8")
    records: dict[str, CandidateRecord] = {}
    for block in re.findall(r'(?ms)^- key:.*?(?=\n- key:|\Z)', text):
        def one(pattern: str, default: str | None = None) -> str | None:
            m = re.search(pattern, block)
            return m.group(1) if m else default

        key = one(r'^- key:\s+"([^"]+)"', None)
        if not key:
            continue
        title = one(r'\n\s+title:\s+"([^"]*)"', "") or ""
        arxiv_id = one(r'\n\s+arxiv_id:\s+"?([^"\n]+)"?', None)
        doi = one(r'\n\s+doi:\s+"?([^"\n]+)"?', None)
        fp = one(r'\n\s+title_fingerprint:\s+"([^"]*)"', "") or ""
        first_seen = one(r'\n\s+first_seen:\s+"([^"]+)"', "") or ""
        last_seen = one(r'\n\s+last_seen:\s+"([^"]+)"', first_seen) or first_seen
        status = one(r'\n\s+status:\s+"([^"]+)"', "candidate") or "candidate"
        level = one(r'\n\s+level:\s+"([^"]+)"', "观察") or "观察"
        score_s = one(r'\n\s+score:\s+(\d+)', "0") or "0"
        seen_s = one(r'\n\s+seen_count:\s+(\d+)', "1") or "1"
        reason = one(r'\n\s+reason:\s+"([^"]*)"', "") or ""
        source_url = one(r'\n\s+source_url:\s+"([^"]*)"', "") or ""
        records[key] = CandidateRecord(
            key=key,
            title=title,
            arxiv_id=None if arxiv_id in {None, "null"} else normalize_arxiv_id(arxiv_id),
            doi=None if doi in {None, "null"} else real_doi(doi),
            title_fingerprint=fp,
            authors=_section_items(block, "authors"),
            sources_seen=_section_items(block, "sources_seen"),
            first_seen=first_seen,
            last_seen=last_seen,
            seen_count=int(seen_s),
            status=status,
            level=level,
            score=int(score_s),
            reason=reason,
            directions=_section_items(block, "directions"),
            tags=_section_items(block, "tags"),
            source_url=source_url,
            appeared_in=_section_items(block, "appeared_in"),
        )
    return records


def candidate_record_from_paper(paper: Paper, date: str, week: str, status: str | None = None) -> CandidateRecord:
    final_status = status or paper.status
    appeared = [f"docs/radar/{week}.md", "docs/radar/latest.md"] if final_status == "recommended" else []
    return CandidateRecord(
        key=paper.key,
        title=paper.title,
        arxiv_id=paper.arxiv_id,
        doi=paper.doi,
        title_fingerprint=paper.title_fingerprint,
        authors=paper.authors[:8],
        sources_seen=paper.sources_seen or [paper.source_type],
        first_seen=date,
        last_seen=date,
        seen_count=1,
        status=final_status,
        level=paper.level,
        score=paper.score,
        reason=paper.reason,
        directions=paper.directions,
        tags=paper.tags[:10],
        source_url=paper.url,
        appeared_in=appeared,
    )


def render_candidate_records(records: dict[str, CandidateRecord]) -> str:
    lines = [
        "# Candidate lifecycle registry for the research radar.",
        "#",
        "# Status values:",
        "#   recommended: promoted into a public daily brief or long-term registry.",
        "#   candidate: seen by the broad recall layer but not strong enough for public posting yet.",
        "#   rejected: explicitly suppressed to prevent repeated weak recommendations.",
        "#   metadata-updated: known paper seen again with cross-source metadata.",
        "",
    ]
    order = {"recommended": 0, "candidate": 1, "metadata-updated": 2, "rejected": 3}
    sorted_records = sorted(records.values(), key=lambda r: (r.first_seen, -r.score, order.get(r.status, 9), r.key), reverse=True)
    for r in sorted_records:
        lines += [
            f"- key: {q(r.key)}",
            f"  title: {q(r.title)}",
            "  identifiers:",
            f"    arxiv_id: {q(r.arxiv_id)}",
            f"    doi: {q(r.doi)}",
            f"    title_fingerprint: {q(r.title_fingerprint)}",
            "  authors:",
            yaml_list(r.authors),
            "  sources_seen:",
            yaml_list(sorted(set(r.sources_seen))),
            f"  first_seen: {q(r.first_seen)}",
            f"  last_seen: {q(r.last_seen)}",
            f"  seen_count: {r.seen_count}",
            f"  status: {q(r.status)}",
            f"  level: {q(r.level)}",
            f"  score: {r.score}",
            f"  reason: {q(r.reason)}",
            "  directions:",
            yaml_list(r.directions),
            "  tags:",
            yaml_list(r.tags),
            f"  source_url: {q(r.source_url)}",
            "  appeared_in:",
            yaml_list(r.appeared_in),
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def hit_terms(haystack: str, group: str) -> list[str]:
    return [term for term in TERM_GROUPS[group] if term in haystack]


def score_and_classify(paper: Paper) -> None:
    haystack = search_text(f"{paper.title} {paper.summary}")
    author_text = search_text(" ".join(paper.authors))
    hits = {group: hit_terms(haystack, group) for group in TERM_GROUPS}
    score = sum(TERM_GROUPS[group][term] for group, terms in hits.items() for term in terms)
    watch_hits = [name for name in WATCH_AUTHORS if name in author_text]
    if watch_hits:
        score += 18
        hits["watch_author"] = sorted(watch_hits)
    core = bool(hits.get("core_system"))
    method = bool(hits.get("method"))
    adjacent = bool(hits.get("adjacent_system"))
    obj = bool(hits.get("object"))
    negative = bool(hits.get("negative"))
    if core and method:
        score += 12
    if core and obj:
        score += 8
    if method and obj:
        score += 6
    if adjacent and method:
        score += 7
    if len(hits.get("method", [])) >= 2:
        score += 5
    paper.score = max(score, 0)
    paper.hits = hits
    positive_tags = []
    for group in ["core_system", "method", "adjacent_system", "object", "watch_author"]:
        positive_tags.extend(hits.get(group, []))
    paper.tags = positive_tags[:10]
    directions = []
    for name, terms in DIRECTION_KEYWORDS.items():
        if any(term in haystack for term in terms):
            directions.append(name)
    paper.directions = [d for d in DIRECTION_ORDER if d in directions] or ["精确解与特殊背景"]
    if paper.score >= 42 and ((core and (method or obj)) or (adjacent and method and obj) or (watch_hits and (method or core))):
        paper.status = "recommended"
        paper.level = "重点关注" if paper.score >= 58 else "值得关注"
        paper.reason = "强相关组合命中：" + ", ".join(paper.tags[:6])
    elif paper.score >= 24 and (core or method or adjacent or obj):
        paper.status = "candidate"
        paper.level = "候选"
        paper.reason = "有相关信号但未达到公开简报门槛：" + ", ".join(paper.tags[:6])
    else:
        paper.status = "rejected"
        paper.level = "不推荐"
        if negative and not (core or method):
            paper.reason = "负向或泛应用信号较强，且缺少核心模型/方法匹配。"
        else:
            paper.reason = "未形成核心模型与方法/对象的有效组合命中。"


def primary_direction(paper: Paper) -> str:
    for direction in DIRECTION_ORDER:
        if direction in paper.directions:
            return direction
    return paper.directions[0] if paper.directions else "精确解与特殊背景"


def md_link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def render_card(paper: Paper) -> str:
    authors = "；".join([a for a in paper.authors if a][:8]) or "未列出"
    tags = ", ".join(paper.tags[:8]) or "待补充"
    source_label = f"arXiv:{paper.arxiv_id}" if paper.arxiv_id else (f"doi:{paper.doi}" if paper.doi else paper.id)
    return "\n".join([
        f"#### [{paper.level}] {paper.title}",
        "",
        f"作者：{authors}  ",
        f"来源：{md_link(source_label, paper.url)}  ",
        f"标签：{tags}",
        "",
        f"简评：{paper.reason}。这是自动候选简报条目，仍需检查摘要、Introduction 和主定理后再决定是否纳入长期文献图谱。",
    ])


def render_daily(date: str, papers: list[Paper]) -> str:
    lines = [f"## {date}", ""]
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


def extract_date_blocks(text: str) -> list[tuple[dt.date, str]]:
    pattern = re.compile(r"(?:^|\n---\n\n)(## (\d{4}-\d{2}-\d{2})\n.*?)(?=\n---\n\n## |\Z)", re.S)
    blocks: list[tuple[dt.date, str]] = []
    for block, date_s in pattern.findall(text):
        try:
            blocks.append((dt.date.fromisoformat(date_s), block.rstrip()))
        except ValueError:
            continue
    return blocks


def recent_date_blocks(weekly_text: str, limit: int = 3) -> list[str]:
    blocks = extract_date_blocks(weekly_text)
    blocks.sort(key=lambda item: item[0], reverse=True)
    return [block for _, block in blocks[:limit]]


def recent_date_blocks_from_radar(limit: int = 3) -> list[str]:
    blocks: list[tuple[dt.date, str]] = []
    for path in RADAR_DIR.glob("*.md"):
        if not re.fullmatch(r"\d{4}-W\d{2}\.md", path.name):
            continue
        try:
            blocks.extend(extract_date_blocks(path.read_text(encoding="utf-8")))
        except OSError:
            continue
    blocks.sort(key=lambda item: item[0], reverse=True)
    return [block for _, block in blocks[:limit]]


def render_latest(week: str, daily_block: str) -> str:
    return f"""# 最新每日简报

[返回首页](../index.md) · [本周归档]({week}.md) · [全部归档](index.md)

!!! note "AI 生成说明"
    本页为固定的最新简报入口。每日更新时，自动化流程应覆盖本页内容，并同时把同一批条目追加到本周归档文件。简报主要依据题名、摘要、分类、关键词和公开元数据筛选；条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。

{daily_block.rstrip()}
"""


def render_home(week: str, blocks: list[str]) -> str:
    recent_briefs = "\n\n---\n\n".join(blocks).rstrip()
    return f"""# 可积系统研究简报

本页显示最近三天的 AI 辅助研究简报，最新日期在最上方。简报面向 Ling Liming 课题组相关方向，重点关注可积系统中的精确解与特殊背景、稳定性与动力学机制、IST/RHP 与渐近分析。

[本周归档](radar/{week}.md) · [全部归档](radar/index.md)

!!! note "AI 生成说明"
    简报主要依据题名、摘要、arXiv 分类、关键词和公开元数据筛选。条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。除特别标注外，条目尚未经过人工逐篇验证；数学结论请以原论文为准。

{recent_briefs}

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
        authors = yaml_list(p.authors, indent=4)
        tags = yaml_list(p.tags, indent=4)
        directions = yaml_list(p.directions, indent=4)
        chunks.append(f'''- id: {q(p.key)}
  title: {q(p.title)}
  title_fingerprint: {q(p.title_fingerprint)}
  authors:
{authors}
  source:
    type: {q(p.source_type)}
    url: {q(p.url)}
    arxiv_id: {q(p.arxiv_id)}
    doi: {q(p.doi)}
  first_seen: {q(date)}
  first_week: {q(week)}
  directions:
{directions}
  tags:
{tags}
  relevance: {q(p.level)}
  review_status: "script-screened"
  appeared_in:
    - "docs/radar/{week}.md"
    - "docs/radar/latest.md"
''')
    return "\n".join(chunks)


def make_summary(date: str, week: str, counts: dict[str, int], recommended: list[Paper], state_changed: bool, public_docs_changed: bool) -> dict:
    return {
        "date": date,
        "week": week,
        "recommended": len(recommended),
        "candidate": counts.get("candidate", 0),
        "rejected": counts.get("rejected", 0),
        "metadata_updates": counts.get("metadata-updated", 0),
        "skipped_known": counts.get("skipped_known", 0),
        "skipped_seen": counts.get("skipped_seen", 0),
        "state_changed": state_changed,
        "public_docs_changed": public_docs_changed,
        "recommended_titles": [p.title for p in recommended],
    }


def write_summary(summary: dict, recommended: list[Paper]) -> None:
    SUMMARY_DIR.mkdir(exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"Automated research-radar update for {summary['date']}.",
        "",
        "This PR is generated by GitHub Actions as a candidate/state update. It should be reviewed before merging.",
        "",
        "Summary:",
        f"- recommended for public brief: {summary['recommended']}",
        f"- recorded as candidate only: {summary['candidate']}",
        f"- recorded as rejected/suppressed: {summary['rejected']}",
        f"- metadata updates for known papers: {summary['metadata_updates']}",
        f"- skipped because already known in papers.yml: {summary['skipped_known']}",
        f"- skipped because already present in candidates.yml: {summary['skipped_seen']}",
        f"- public docs changed: {str(summary['public_docs_changed']).lower()}",
        "",
    ]
    if recommended:
        lines.append("Recommended entries:")
        for p in recommended:
            lines.append(f"- {p.title} — {p.reason}")
        lines.append("")
    lines += [
        "Review priority:",
        "DNLS, coupled/multi-component systems, Gerdjikov--Ivanov, Fokas--Lenells, coupled NLS, IST/RHP, long-time asymptotics, soliton gas, Darboux transformations, rogue waves, breathers, finite-gap/algebro-geometric solutions, and stability mechanisms.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_candidates(papers: list[Paper], date: str, week: str, limit: int, max_state_records: int) -> tuple[list[Paper], dict[str, CandidateRecord], dict[str, int], bool]:
    registry = load_registry_index()
    records = load_candidate_records()
    counts = {"candidate": 0, "rejected": 0, "metadata-updated": 0, "skipped_known": 0, "skipped_seen": 0}
    state_changed = False
    recommended: list[Paper] = []
    for p in papers:
        prepare_paper(p)
        score_and_classify(p)
    papers.sort(key=lambda p: (p.score, p.published or ""), reverse=True)
    considered = 0
    for p in papers:
        if is_known_paper(p, registry):
            counts["skipped_known"] += 1
            continue
        existing = records.get(p.key)
        if existing is not None:
            counts["skipped_seen"] += 1
            if existing.status == "candidate" and p.status == "recommended" and len(recommended) < limit:
                records[p.key] = candidate_record_from_paper(p, date, week, status="recommended")
                recommended.append(p)
                state_changed = True
            continue
        if considered >= max_state_records:
            continue
        considered += 1
        status = p.status
        if status == "recommended" and len(recommended) >= limit:
            status = "candidate"
            p.reason = "达到推荐分数但超过当日公开推荐数量上限，暂存候选池。"
        records[p.key] = candidate_record_from_paper(p, date, week, status=status)
        state_changed = True
        if status == "recommended":
            recommended.append(p)
        elif status == "candidate":
            counts["candidate"] += 1
        elif status == "rejected":
            counts["rejected"] += 1
        else:
            counts["metadata-updated"] += 1
    return recommended, records, counts, state_changed


def apply_metadata_records(records: dict[str, CandidateRecord], papers: list[Paper], date: str, week: str) -> bool:
    changed = False
    for paper in papers:
        prepare_paper(paper)
        record = candidate_record_from_paper(paper, date, week, status="metadata-updated")
        old = records.get(record.key)
        if old is None or old.status != "metadata-updated" or old.doi != record.doi:
            records[record.key] = record
            changed = True
    return changed


def ensure_week_file(week_path: Path, week: str) -> None:
    if week_path.exists():
        return
    week_path.write_text(
        f"# 可积系统研究简报 · {week}\n\n"
        "本页为 AI 辅助生成的研究简报，主要面向 Ling Liming 课题组相关方向，跟踪可积系统、非线性波、精确解、稳定性、IST/RHP 与长时间渐近分析中的近期论文和研究线索。\n\n"
        "筛选主要依据题名、摘要、arXiv 分类、关键词和公开元数据。条目分级表示相关性和阅读优先级，不代表对论文正确性的审查。除特别标注外，条目尚未经过人工逐篇验证；数学结论请以原论文为准。\n\n"
        "本周文件用于连续记录每日发现。周末或每周整理时，可在本文顶部补充“本周重点关注”。\n",
        encoding="utf-8",
    )


def update_public_docs(date: str, week: str, recommended: list[Paper]) -> bool:
    if not recommended:
        return False
    RADAR_DIR.mkdir(parents=True, exist_ok=True)
    week_path = RADAR_DIR / f"{week}.md"
    ensure_week_file(week_path, week)
    daily_block = render_daily(date, recommended)
    updated_weekly_text = replace_date_block(week_path.read_text(encoding="utf-8"), date, daily_block)
    week_path.write_text(updated_weekly_text, encoding="utf-8")
    LATEST_PAGE.write_text(render_latest(week, daily_block), encoding="utf-8")
    DOCS_INDEX.write_text(render_home(week, recent_date_blocks_from_radar(limit=3)), encoding="utf-8")
    registry_text = PAPER_REGISTRY.read_text(encoding="utf-8") if PAPER_REGISTRY.exists() else ""
    if registry_text.strip() == "[]":
        registry_text = ""
    registry_text = registry_text.rstrip() + "\n\n" + render_registry_entries(recommended, date, week)
    PAPER_REGISTRY.write_text(registry_text.lstrip(), encoding="utf-8")
    return True


def fetch_all_sources(from_date: str, include_openalex: bool) -> list[Paper]:
    papers = fetch_arxiv() + fetch_crossref(from_date)
    if include_openalex:
        papers += fetch_openalex(from_date)
    return merge_papers(papers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--days", type=int, default=60, help="Crossref/OpenAlex lookback window")
    parser.add_argument("--limit", type=int, default=8, help="maximum public recommendations per day")
    parser.add_argument("--max-state-records", type=int, default=80, help="maximum new candidate/rejected records to add per run")
    parser.add_argument("--no-openalex", action="store_true", help="disable OpenAlex supplementary metadata search")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    date_obj = dt.date.fromisoformat(args.date)
    week = week_id(date_obj)
    from_date = (date_obj - dt.timedelta(days=args.days)).isoformat()
    candidates = fetch_all_sources(from_date, include_openalex=not args.no_openalex)
    metadata_updates, metadata_papers = update_known_paper_metadata(candidates, args.date)
    recommended, records, counts, state_changed = process_candidates(
        candidates,
        date=args.date,
        week=week,
        limit=args.limit,
        max_state_records=args.max_state_records,
    )
    counts["metadata-updated"] += metadata_updates
    if metadata_papers:
        state_changed = apply_metadata_records(records, metadata_papers, args.date, week) or state_changed
    if args.dry_run or not args.write:
        print(json.dumps(make_summary(args.date, week, counts, recommended, state_changed, False), ensure_ascii=False, indent=2))
        if recommended:
            print(render_daily(args.date, recommended))
        return
    CANDIDATE_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if state_changed:
        CANDIDATE_REGISTRY.write_text(render_candidate_records(records), encoding="utf-8")
    public_docs_changed = update_public_docs(args.date, week, recommended)
    summary = make_summary(args.date, week, counts, recommended, state_changed, public_docs_changed)
    write_summary(summary, recommended)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
