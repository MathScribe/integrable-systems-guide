#!/usr/bin/env python3
"""Validate bibliographic identities used by the research radar."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> Any:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.casefold(), flags=re.UNICODE).strip()


def main() -> None:
    papers = load("data/papers.yml")
    if not isinstance(papers, list):
        raise SystemExit("data/papers.yml must contain a YAML list")

    paper_ids: set[str] = set()
    arxiv_ids: dict[str, str] = {}
    dois: dict[str, str] = {}
    titles: dict[str, str] = {}

    for index, paper in enumerate(papers, start=1):
        for field in ("id", "title", "authors", "url"):
            if not paper.get(field):
                raise SystemExit(f"paper #{index} is missing {field}")

        paper_id = str(paper["id"])
        if paper_id in paper_ids:
            raise SystemExit(f"duplicate paper id: {paper_id}")
        paper_ids.add(paper_id)

        if not isinstance(paper["authors"], list) or not all(paper["authors"]):
            raise SystemExit(f"{paper_id}: authors must be a non-empty list")

        title_key = normalize_title(str(paper["title"]))
        if title_key in titles:
            raise SystemExit(f"duplicate normalized title: {paper['title']} / {titles[title_key]}")
        titles[title_key] = paper_id

        arxiv_id = paper.get("arxiv_id")
        if arxiv_id:
            arxiv_id = str(arxiv_id)
            if arxiv_id in arxiv_ids:
                raise SystemExit(f"duplicate arXiv id: {arxiv_id}")
            arxiv_ids[arxiv_id] = paper_id
        if paper_id.startswith("arxiv:") and arxiv_id != paper_id.split(":", 1)[1]:
            raise SystemExit(f"{paper_id}: arxiv_id does not match id")

        doi = paper.get("doi")
        if doi:
            doi_key = str(doi).casefold()
            if doi_key in dois:
                raise SystemExit(f"duplicate DOI: {doi}")
            dois[doi_key] = paper_id
        if paper_id.startswith("doi:") and str(doi).casefold() != paper_id.split(":", 1)[1].casefold():
            raise SystemExit(f"{paper_id}: doi does not match id")

        if paper.get("published") and not paper.get("journal"):
            raise SystemExit(f"{paper_id}: published journal record is missing journal")

    print(f"validated {len(papers)} paper identities")


if __name__ == "__main__":
    main()
