#!/usr/bin/env python3
"""Capture official arXiv category-list events and their announcement dates."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "maintenance" / "radar-sources.yml"
USER_AGENT = (
    "integrable-systems-guide/1.0 "
    "(https://github.com/MathScribe/integrable-systems-guide)"
)
HEADING_RE = re.compile(r"<h3>(.*?)</h3>", flags=re.DOTALL | re.IGNORECASE)
TOKEN_RE = re.compile(
    r"(?P<heading><h3>.*?</h3>)|"
    r"(?P<entry><dt>.*?</dt>\s*<dd>.*?</dd>)",
    flags=re.DOTALL | re.IGNORECASE,
)
ENTRY_RE = re.compile(
    r"<dt>(?P<dt>.*?)</dt>\s*<dd>(?P<dd>.*?)</dd>",
    flags=re.DOTALL | re.IGNORECASE,
)
DIV_RE_TEMPLATE = r"<div\s+class=['\"]{class_name}[^'\"]*['\"]>(.*?)</div>"
TAG_RE = re.compile(r"<[^>]+>")
ARXIV_ID_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5})", flags=re.IGNORECASE)
DATE_RE = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+(\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4})"
)
CATEGORY_RE = re.compile(r"\(([A-Za-z0-9.-]+)\)")

UrlOpen = Callable[..., Any]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", value))).strip()


def div_text(fragment: str, class_name: str) -> str:
    match = re.search(
        DIV_RE_TEMPLATE.format(class_name=re.escape(class_name)),
        fragment,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return ""
    text = clean_text(match.group(1))
    return re.sub(r"^(?:Title|Comments|Subjects):\s*", "", text, flags=re.IGNORECASE)


def parse_heading(fragment: str) -> date:
    text = clean_text(fragment)
    match = DATE_RE.search(text)
    if not match:
        raise ValueError(f"cannot parse arXiv announcement heading: {text!r}")
    return datetime.strptime(match.group(1), "%d %b %Y").date()


def parse_entry(fragment: str, announcement_date: date, source_category: str) -> dict[str, Any]:
    match = ENTRY_RE.fullmatch(fragment.strip())
    if not match:
        raise ValueError("cannot parse arXiv list entry")
    dt = match.group("dt")
    dd = match.group("dd")
    arxiv_match = ARXIV_ID_RE.search(dt)
    if not arxiv_match:
        raise ValueError("arXiv list entry has no identifier")
    arxiv_id = arxiv_match.group(1)
    title = div_text(dd, "list-title")
    authors_text = div_text(dd, "list-authors")
    subjects_text = div_text(dd, "list-subjects")
    if not title or not authors_text:
        raise ValueError(f"arXiv:{arxiv_id} is missing title or authors")
    authors = [part.strip() for part in authors_text.split(",") if part.strip()]
    categories = CATEGORY_RE.findall(subjects_text)
    cross_list_match = re.search(r"\(cross-list from ([^)]+)\)", clean_text(dt))
    return {
        "id": f"arxiv:{arxiv_id}",
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "announcement_date": announcement_date.isoformat(),
        "source_categories": [source_category],
        "official_categories": categories,
        "cross_list_from": cross_list_match.group(1) if cross_list_match else None,
        "comments": div_text(dd, "list-comments"),
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "evidence_url": f"https://arxiv.org/list/{source_category}/pastweek?show=2000",
    }


def parse_category_page(
    text: str,
    *,
    source_category: str,
    start: date,
    end: date,
) -> tuple[list[dict[str, Any]], date, date]:
    current_date: date | None = None
    observed_dates: list[date] = []
    candidates: list[dict[str, Any]] = []
    for token in TOKEN_RE.finditer(text):
        heading = token.group("heading")
        if heading is not None:
            current_date = parse_heading(heading)
            observed_dates.append(current_date)
            continue
        entry = token.group("entry")
        if entry is None:
            continue
        if current_date is None:
            raise ValueError("arXiv entry appeared before an announcement heading")
        if start <= current_date <= end:
            candidates.append(parse_entry(entry, current_date, source_category))
    if not observed_dates:
        raise ValueError(f"arXiv {source_category} page contained no announcement dates")
    return candidates, min(observed_dates), max(observed_dates)


def request_text(
    url: str,
    *,
    timeout: int,
    urlopen: UrlOpen = urllib.request.urlopen,
) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def merge_candidate(existing: dict[str, Any], incoming: dict[str, Any]) -> None:
    existing["source_categories"] = sorted(
        set(existing["source_categories"]) | set(incoming["source_categories"])
    )
    existing["official_categories"] = sorted(
        set(existing["official_categories"]) | set(incoming["official_categories"])
    )


def fetch_manifest(
    categories: list[str],
    *,
    start: str,
    end: str,
    timeout: int = 30,
    urlopen: UrlOpen = urllib.request.urlopen,
) -> dict[str, Any]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if start_date > end_date:
        raise ValueError("from date cannot be after until date")
    if not categories:
        raise ValueError("at least one arXiv category is required")

    candidates: dict[str, dict[str, Any]] = {}
    source_reports: list[dict[str, Any]] = []
    complete = True
    for category in categories:
        url = f"https://arxiv.org/list/{category}/pastweek?show=2000"
        text = request_text(url, timeout=timeout, urlopen=urlopen)
        items, earliest, latest = parse_category_page(
            text,
            source_category=category,
            start=start_date,
            end=end_date,
        )
        category_complete = earliest <= start_date and latest >= end_date
        complete = complete and category_complete
        source_reports.append(
            {
                "category": category,
                "url": url,
                "earliest_heading": earliest.isoformat(),
                "latest_heading": latest.isoformat(),
                "requested_window_complete": category_complete,
                "candidate_items": len(items),
            }
        )
        for item in items:
            if item["arxiv_id"] in candidates:
                merge_candidate(candidates[item["arxiv_id"]], item)
            else:
                candidates[item["arxiv_id"]] = item

    return {
        "schema_version": 1,
        "source": "arxiv-category-lists",
        "status": "complete" if complete else "partial",
        "window": {"from": start, "until": end},
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": source_reports,
        "candidate_count": len(candidates),
        "candidates": sorted(
            candidates.values(),
            key=lambda item: (item["announcement_date"], item["arxiv_id"]),
        ),
    }


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def configured_core_categories(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    categories = (data.get("arxiv") or {}).get("core_categories") if isinstance(data, dict) else None
    if not isinstance(categories, list) or not all(isinstance(item, str) for item in categories):
        raise ValueError(f"{path} has no valid arxiv.core_categories list")
    return categories


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--from", dest="start", required=True, help="inclusive announcement date")
    result.add_argument("--until", dest="end", required=True, help="inclusive announcement date")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--category", action="append", dest="categories")
    result.add_argument("--timeout", type=int, default=30)
    result.add_argument(
        "--allow-partial",
        action="store_true",
        help="return success for a captured window older than the available official list",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    categories = args.categories or configured_core_categories(args.config)
    manifest = fetch_manifest(
        categories,
        start=args.start,
        end=args.end,
        timeout=args.timeout,
    )
    atomic_write_json(args.output, manifest)
    print(
        f"wrote {manifest['candidate_count']} arXiv candidates "
        f"with status {manifest['status']} to {args.output}"
    )
    if manifest["status"] != "complete" and not args.allow_partial:
        raise SystemExit(
            "requested arXiv interval is not fully present in the official pastweek lists; "
            "watermarks must not advance"
        )


if __name__ == "__main__":
    main()

