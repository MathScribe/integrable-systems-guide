#!/usr/bin/env python3
"""Validate bibliographic identities used by the research radar."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"v[1-9]\d*")
CATEGORY_RE = re.compile(r"^[a-z-]+(?:\.(?:[A-Z]{2}|[a-z-]+))?$")
DATE_FIELDS = ("submitted", "updated", "published", "metadata_checked_at")
DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)
ARXIV_RE = re.compile(r"(?:\d{2}(?:0[1-9]|1[0-2])\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{2}(?:0[1-9]|1[0-2])\d{3})(?:v[1-9]\d*)?")
PLACEHOLDER_AUTHORS = {"unknown", "unknown author", "unknown authors", "author metadata unavailable", "n/a"}


def today_shanghai() -> date:
    return datetime.now(timezone(timedelta(hours=8))).date()


def normalize_doi(value: str) -> str:
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).casefold()


def normalize_arxiv(value: str) -> str:
    return re.sub(r"v[1-9]\d*$", "", value.strip())


def validate_url(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or re.search(r"[\s<>\x00-\x1f]", value):
        raise ValueError(f"{field}: invalid URL characters")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"{field}: invalid URL: {value}") from exc
    if parts.scheme not in {"https", "http"} or not parts.hostname or parts.username or parts.password:
        raise ValueError(f"{field}: expected an absolute HTTP(S) URL: {value}")
    if re.search(r"%(?![0-9a-fA-F]{2})", value) or "\\" in value:
        raise ValueError(f"{field}: malformed URL escaping: {value}")
    if parts.hostname in {"doi.org", "dx.doi.org"} and not DOI_RE.fullmatch(parts.path.lstrip("/")):
        raise ValueError(f"{field}: invalid DOI URL: {value}")
    if parts.hostname in {"arxiv.org", "export.arxiv.org"} and parts.path.startswith(("/abs/", "/pdf/")):
        identifier = re.sub(r"\.pdf$", "", parts.path.split("/", 2)[2])
        if not ARXIV_RE.fullmatch(identifier):
            raise ValueError(f"{field}: invalid arXiv URL: {value}")


def load(path: str) -> Any:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", unicodedata.normalize("NFKC", title).casefold(), flags=re.UNICODE).strip()


def parse_date(value: Any, field: str, *, allow_reduced: bool = False) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date string")
    normalized = value
    if allow_reduced and re.fullmatch(r"\d{4}-\d{2}", value):
        normalized = f"{value}-01"
    elif allow_reduced and re.fullmatch(r"\d{4}", value):
        normalized = f"{value}-01-01"
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
        raise ValueError(f"{field} must be an ISO date: {value!r}")
    try:
        return date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date: {value!r}") from exc


def validate_papers(papers: Any, *, today: date | None = None) -> int:
    today = today or today_shanghai()
    if not isinstance(papers, list):
        raise ValueError("data/papers.yml must contain a YAML list")

    paper_ids: set[str] = set()
    arxiv_ids: dict[str, str] = {}
    dois: dict[str, str] = {}
    titles: dict[str, str] = {}

    for index, paper in enumerate(papers, start=1):
        if not isinstance(paper, dict):
            raise ValueError(f"paper #{index} must be a mapping")
        for field in ("id", "title", "authors", "url"):
            if not paper.get(field):
                raise ValueError(f"paper #{index} is missing {field}")

        paper_id = str(paper["id"])
        for field in ("id", "title"):
            if not isinstance(paper[field], str) or not paper[field].strip():
                raise ValueError(f"paper #{index}: {field} must be a non-empty string")
        if paper_id != paper_id.strip():
            raise ValueError(f"paper #{index}: id has surrounding whitespace")
        validate_url(paper["url"], f"{paper_id}.url")
        if "tags" in paper:
            raise ValueError(f"{paper_id}: tags is retired; use keywords")
        if paper.get("status", "active") not in {"active", "withdrawn", "retracted"}:
            raise ValueError(f"{paper_id}: invalid bibliographic status")
        keywords = paper.get("keywords", [])
        if not isinstance(keywords, list) or any(not isinstance(k,str) or not k.strip() for k in keywords):
            raise ValueError(f"{paper_id}: keywords must be a string list")
        if len(keywords) != len(set(keywords)):
            raise ValueError(f"{paper_id}: duplicate keywords")
        categories = paper.get("arxiv_categories", [])
        if not isinstance(categories,list) or any(not isinstance(c,str) or not CATEGORY_RE.fullmatch(c) for c in categories):
            raise ValueError(f"{paper_id}: invalid arXiv categories")
        if paper_id in paper_ids:
            raise ValueError(f"duplicate paper id: {paper_id}")
        paper_ids.add(paper_id)

        if not isinstance(paper["authors"], list) or not paper["authors"] or any(
            not isinstance(author, str) or not author.strip() or author.strip().casefold() in PLACEHOLDER_AUTHORS
            for author in paper["authors"]
        ):
            raise ValueError(f"{paper_id}: authors must be a non-empty list")

        title_key = normalize_title(str(paper["title"]))
        if not title_key:
            raise ValueError(f"{paper_id}: title has no searchable text")
        if title_key in titles:
            raise ValueError(f"duplicate normalized title: {paper['title']} / {titles[title_key]}")
        titles[title_key] = paper_id

        arxiv_id = paper.get("arxiv_id")
        if arxiv_id:
            if not isinstance(arxiv_id, str) or not ARXIV_RE.fullmatch(arxiv_id):
                raise ValueError(f"{paper_id}: invalid arXiv id: {arxiv_id}")
            arxiv_id = normalize_arxiv(arxiv_id)
            if arxiv_id in arxiv_ids:
                raise ValueError(f"duplicate arXiv id: {arxiv_id}")
            if paper['arxiv_id'] != arxiv_id:
                raise ValueError(f"{paper_id}: store the unversioned arXiv id and use the version field")
            arxiv_ids[arxiv_id] = paper_id
        if paper_id.startswith("arxiv:") and arxiv_id != normalize_arxiv(paper_id.split(":", 1)[1]):
            raise ValueError(f"{paper_id}: arxiv_id does not match id")

        doi = paper.get("doi")
        if doi:
            if not isinstance(doi, str) or not DOI_RE.fullmatch(normalize_doi(doi)):
                raise ValueError(f"{paper_id}: invalid DOI: {doi}")
            doi_key = normalize_doi(doi)
            if doi_key.startswith("10.48550/arxiv."):
                raise ValueError(f"{paper_id}: the arXiv-issued DOI is derived; store only a journal DOI here")
            if doi_key in dois:
                raise ValueError(f"duplicate DOI: {doi}")
            if doi.strip().casefold() != doi_key or doi != doi.strip():
                raise ValueError(f"{paper_id}: store a bare DOI without URL/prefix or surrounding whitespace")
            dois[doi_key] = paper_id
        if paper_id.startswith("doi:") and normalize_doi(str(doi)) != normalize_doi(paper_id.split(":", 1)[1]):
            raise ValueError(f"{paper_id}: doi does not match id")

        if paper.get("published") and not paper.get("journal"):
            raise ValueError(f"{paper_id}: published journal record is missing journal")
        year = paper.get("year")
        if paper.get("journal") and year is None:
            raise ValueError(f"{paper_id}: journal record is missing year")
        if year is not None and (type(year) is not int or not 1000 <= year <= today.year + 2):
            raise ValueError(f"{paper_id}: invalid bibliography year: {year!r}")

        parsed_dates = {
            field: parse_date(
                paper[field],
                f"{paper_id}.{field}",
                allow_reduced=field == "published",
            )
            for field in DATE_FIELDS
            if paper.get(field) is not None
        }
        for field, parsed in parsed_dates.items():
            if (field != "published" or len(paper[field]) == 10) and parsed > today:
                raise ValueError(f"{paper_id}.{field}: date is in the future")
        if paper.get("submitted_at") is not None:
            try:
                timestamp = datetime.fromisoformat(paper['submitted_at'].replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    raise ValueError('timezone required')
            except (TypeError, AttributeError, ValueError) as exc:
                raise ValueError(f'{paper_id}.submitted_at: expected an ISO timestamp with timezone') from exc
            if timestamp.astimezone(timezone.utc).date() != parsed_dates.get('submitted'):
                raise ValueError(f'{paper_id}.submitted_at: UTC date must match submitted')
        if arxiv_id and "submitted" not in parsed_dates:
            raise ValueError(f"{paper_id}: preprint is missing submitted date")
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
