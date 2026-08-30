#!/usr/bin/env python3
"""Validate bibliographic identities used by the research radar."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"v[1-9]\d*")
DATE_FIELDS = ("submitted", "updated", "published", "metadata_checked_at")


def load(path: str) -> Any:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.casefold(), flags=re.UNICODE).strip()


def parse_date(value: Any, field: str, *, allow_reduced: bool = False) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date string")
    normalized = value
    if allow_reduced and re.fullmatch(r"\d{4}-\d{2}", value):
        normalized = f"{value}-01"
    elif allow_reduced and re.fullmatch(r"\d{4}", value):
        normalized = f"{value}-01-01"
    try:
        return date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date: {value!r}") from exc


def validate_papers(papers: Any) -> int:
    if not isinstance(papers, list):
        raise ValueError("data/papers.yml must contain a YAML list")

    paper_ids: set[str] = set()
    arxiv_ids: dict[str, str] = {}
    dois: dict[str, str] = {}
    titles: dict[str, str] = {}

    for index, paper in enumerate(papers, start=1):
        for field in ("id", "title", "authors", "url"):
            if not paper.get(field):
                raise ValueError(f"paper #{index} is missing {field}")

        paper_id = str(paper["id"])
        if paper_id in paper_ids:
            raise ValueError(f"duplicate paper id: {paper_id}")
        paper_ids.add(paper_id)

        if not isinstance(paper["authors"], list) or not all(paper["authors"]):
            raise ValueError(f"{paper_id}: authors must be a non-empty list")

        title_key = normalize_title(str(paper["title"]))
        if title_key in titles:
            raise ValueError(f"duplicate normalized title: {paper['title']} / {titles[title_key]}")
        titles[title_key] = paper_id

        arxiv_id = paper.get("arxiv_id")
        if arxiv_id:
            arxiv_id = str(arxiv_id)
            if arxiv_id in arxiv_ids:
                raise ValueError(f"duplicate arXiv id: {arxiv_id}")
            arxiv_ids[arxiv_id] = paper_id
        if paper_id.startswith("arxiv:") and arxiv_id != paper_id.split(":", 1)[1]:
            raise ValueError(f"{paper_id}: arxiv_id does not match id")

        doi = paper.get("doi")
        if doi:
            doi_key = str(doi).casefold()
            if doi_key in dois:
                raise ValueError(f"duplicate DOI: {doi}")
            dois[doi_key] = paper_id
        if paper_id.startswith("doi:") and str(doi).casefold() != paper_id.split(":", 1)[1].casefold():
            raise ValueError(f"{paper_id}: doi does not match id")

        if paper.get("published") and not paper.get("journal"):
            raise ValueError(f"{paper_id}: published journal record is missing journal")

        parsed_dates = {
            field: parse_date(
                paper[field],
                f"{paper_id}.{field}",
                allow_reduced=field == "published",
            )
            for field in DATE_FIELDS
            if paper.get(field) is not None
        }
        if (
            "submitted" in parsed_dates
            and "updated" in parsed_dates
            and parsed_dates["updated"] < parsed_dates["submitted"]
        ):
            raise ValueError(f"{paper_id}: updated date precedes submitted date")

        version = paper.get("version")
        if version is not None:
            if not arxiv_id:
                raise ValueError(f"{paper_id}: version requires arxiv_id")
            if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
                raise ValueError(f"{paper_id}: invalid arXiv version: {version!r}")

    return len(papers)


def main() -> None:
    try:
        count = validate_papers(load("data/papers.yml"))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"validated {count} paper identities")


if __name__ == "__main__":
    main()
