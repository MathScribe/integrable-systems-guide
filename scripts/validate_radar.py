#!/usr/bin/env python3
"""Validate paper identities, edition history, and homepage selection rules."""

from __future__ import annotations

import datetime as dt
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROLE_VALUES = {
    "recent",
    "missed-recent",
    "journal-version",
    "group-adjacent",
    "method-background",
    "review-map",
    "backlog-core",
    "adjacent",
}


def load(path: str) -> Any:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.casefold(), flags=re.UNICODE).strip()


def main() -> None:
    papers = load("data/papers.yml")
    edition_data = load("data/editions.yml")
    if not isinstance(papers, list):
        raise SystemExit("data/papers.yml must contain a YAML list")
    if not isinstance(edition_data, dict):
        raise SystemExit("data/editions.yml must contain a YAML mapping")

    paper_by_id: dict[str, dict[str, Any]] = {}
    arxiv_ids: dict[str, str] = {}
    dois: dict[str, str] = {}
    titles: dict[str, str] = {}
    for index, paper in enumerate(papers, start=1):
        for field in ("id", "title", "authors", "url"):
            if not paper.get(field):
                raise SystemExit(f"paper #{index} is missing {field}")
        if not isinstance(paper["authors"], list) or not all(paper["authors"]):
            raise SystemExit(f"{paper['id']}: authors must be a non-empty list")
        if paper["id"] in paper_by_id:
            raise SystemExit(f"duplicate paper id: {paper['id']}")
        paper_by_id[paper["id"]] = paper

        title_key = normalize_title(paper["title"])
        if title_key in titles:
            raise SystemExit(f"duplicate normalized title: {paper['title']} / {titles[title_key]}")
        titles[title_key] = paper["id"]

        arxiv_id = paper.get("arxiv_id")
        if arxiv_id:
            if arxiv_id in arxiv_ids:
                raise SystemExit(f"duplicate arXiv id: {arxiv_id}")
            arxiv_ids[arxiv_id] = paper["id"]
        if paper["id"].startswith("arxiv:") and arxiv_id != paper["id"].split(":", 1)[1]:
            raise SystemExit(f"{paper['id']}: arxiv_id does not match id")

        doi = paper.get("doi")
        if doi:
            doi_key = str(doi).casefold()
            if doi_key in dois:
                raise SystemExit(f"duplicate DOI: {doi}")
            dois[doi_key] = paper["id"]
        if paper["id"].startswith("doi:") and str(doi).casefold() != paper["id"].split(":", 1)[1].casefold():
            raise SystemExit(f"{paper['id']}: doi does not match id")

    weeks = edition_data.get("weeks")
    editions = edition_data.get("editions")
    if not isinstance(weeks, list) or not isinstance(editions, list):
        raise SystemExit("data/editions.yml requires weeks and editions lists")
    week_ids = {week["id"] for week in weeks}
    if len(week_ids) != len(weeks):
        raise SystemExit("duplicate week id")

    dates: set[str] = set()
    historical_dates: dict[str, list[str]] = defaultdict(list)
    for edition in editions:
        date_text = str(edition.get("date", ""))
        date = dt.date.fromisoformat(date_text)
        if date_text in dates:
            raise SystemExit(f"duplicate edition date: {date_text}")
        dates.add(date_text)
        expected_week = f"{date.isocalendar().year}-W{date.isocalendar().week:02d}"
        if edition.get("week") != expected_week:
            raise SystemExit(f"{date_text}: week must be {expected_week}")
        if expected_week not in week_ids:
            raise SystemExit(f"{date_text}: missing week metadata for {expected_week}")
        if not edition.get("summary"):
            raise SystemExit(f"{date_text}: missing summary")
        entries = edition.get("entries")
        if not isinstance(entries, list) or not entries:
            raise SystemExit(f"{date_text}: entries must be a non-empty list")

        seen_papers: set[str] = set()
        ranks: set[int] = set()
        for entry in entries:
            paper_id = entry.get("paper_id")
            if paper_id not in paper_by_id:
                raise SystemExit(f"{date_text}: unknown paper_id {paper_id}")
            if paper_id in seen_papers:
                raise SystemExit(f"{date_text}: duplicate paper {paper_id}")
            seen_papers.add(paper_id)
            historical_dates[paper_id].append(date_text)
            if entry.get("role") not in ROLE_VALUES:
                raise SystemExit(f"{date_text}/{paper_id}: invalid role {entry.get('role')}")
            for field in ("what_it_does", "why_read"):
                if not str(entry.get(field, "")).strip():
                    raise SystemExit(f"{date_text}/{paper_id}: missing {field}")
            rank = entry.get("homepage_rank")
            if rank is not None:
                if not isinstance(rank, int) or rank < 1 or rank > 3:
                    raise SystemExit(f"{date_text}/{paper_id}: homepage_rank must be 1..3")
                if rank in ranks:
                    raise SystemExit(f"{date_text}: duplicate homepage_rank {rank}")
                ranks.add(rank)

    # During the migration, featured_on remains a compatibility mirror. The
    # renderer and archive use editions.yml as the authoritative history.
    for paper_id, paper in paper_by_id.items():
        if "featured_on" in paper:
            old_dates = sorted(str(value) for value in paper["featured_on"])
            new_dates = sorted(historical_dates.get(paper_id, []))
            if old_dates != new_dates:
                raise SystemExit(f"{paper_id}: featured_on differs from data/editions.yml")

    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    if "radar/latest.md" in mkdocs:
        raise SystemExit("mkdocs navigation must not expose radar/latest.md")

    print(f"validated {len(papers)} papers across {len(editions)} editions")


if __name__ == "__main__":
    main()
