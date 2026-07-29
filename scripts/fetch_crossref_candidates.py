#!/usr/bin/env python3
"""Fetch bounded Crossref candidates with local exact matching and an audit manifest."""

from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "maintenance" / "radar-sources.yml"
API_URL = "https://api.crossref.org/works"
USER_AGENT = (
    "integrable-systems-guide/1.0 "
    "(https://github.com/MathScribe/integrable-systems-guide)"
)
TAG_RE = re.compile(r"<[^>]+>")

UrlOpen = Callable[..., Any]
Sleep = Callable[[float], None]


def parse_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date: {value!r}") from exc


def load_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{path} must use radar source schema_version 1")
    crossref = data.get("crossref")
    if not isinstance(crossref, dict):
        raise ValueError(f"{path} is missing crossref configuration")
    queries = crossref.get("queries")
    if not isinstance(queries, list) or not queries:
        raise ValueError("crossref.queries must be a non-empty list")
    seen: set[str] = set()
    for query in queries:
        if not isinstance(query, dict):
            raise ValueError("each Crossref query must be a mapping")
        for field in ("id", "field", "term", "patterns"):
            if not query.get(field):
                raise ValueError(f"Crossref query is missing {field}")
        if query["id"] in seen:
            raise ValueError(f"duplicate Crossref query id: {query['id']}")
        seen.add(query["id"])
        if query["field"] not in {"title", "bibliographic"}:
            raise ValueError(f"{query['id']}.field must be title or bibliographic")
        if not isinstance(query["patterns"], list):
            raise ValueError(f"{query['id']}.patterns must be a list")
        for pattern in query["patterns"]:
            re.compile(str(pattern), flags=re.IGNORECASE)
    return data


def crossref_date(item: dict[str, Any], field: str) -> str | None:
    value = item.get(field)
    if not isinstance(value, dict):
        return None
    parts = value.get("date-parts")
    if not isinstance(parts, list) or not parts or not isinstance(parts[0], list):
        return None
    numbers = parts[0]
    if not numbers:
        return None
    year = int(numbers[0])
    month = int(numbers[1]) if len(numbers) > 1 else 1
    day = int(numbers[2]) if len(numbers) > 2 else 1
    return date(year, month, day).isoformat()


def clean_text(value: object) -> str:
    if isinstance(value, list):
        value = " ".join(str(part) for part in value)
    text = html.unescape(TAG_RE.sub(" ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()


def item_title_text(item: dict[str, Any]) -> str:
    fields = (item.get("title", []), item.get("subtitle", []))
    return " ".join(clean_text(value) for value in fields)


def local_match(item: dict[str, Any], patterns: Iterable[str]) -> bool:
    haystack = item_title_text(item)
    return any(re.search(pattern, haystack, flags=re.IGNORECASE) for pattern in patterns)


def author_names(item: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for author in item.get("author") or []:
        if not isinstance(author, dict):
            continue
        literal = clean_text(author.get("name"))
        if literal:
            result.append(literal)
            continue
        name = " ".join(
            part for part in (clean_text(author.get("given")), clean_text(author.get("family"))) if part
        )
        if name:
            result.append(name)
    return result


def normalized_candidate(item: dict[str, Any], query_id: str) -> dict[str, Any] | None:
    doi = clean_text(item.get("DOI")).lower()
    title = clean_text(item.get("title"))
    if not doi or not title:
        return None
    return {
        "id": f"doi:{doi}",
        "doi": doi,
        "title": title,
        "authors": author_names(item),
        "container_title": clean_text(item.get("container-title")),
        "publisher": clean_text(item.get("publisher")),
        "type": clean_text(item.get("type")),
        "created": crossref_date(item, "created"),
        "updated": crossref_date(item, "deposited") or crossref_date(item, "indexed"),
        "published_online": crossref_date(item, "published-online"),
        "published_print": crossref_date(item, "published-print"),
        "url": clean_text(item.get("URL")) or f"https://doi.org/{doi}",
        "matched_queries": [query_id],
    }


def merge_candidate(existing: dict[str, Any], incoming: dict[str, Any]) -> None:
    existing["matched_queries"] = sorted(
        set(existing["matched_queries"]) | set(incoming["matched_queries"])
    )
    for field in (
        "authors",
        "container_title",
        "publisher",
        "created",
        "updated",
        "published_online",
        "published_print",
        "url",
    ):
        if not existing.get(field) and incoming.get(field):
            existing[field] = incoming[field]


def request_json(
    url: str,
    *,
    timeout: int,
    max_retries: int,
    urlopen: UrlOpen = urllib.request.urlopen,
    sleep: Sleep = time.sleep,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    for attempt in range(max_retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise RuntimeError("Crossref returned a non-object JSON payload")
            return payload
        except urllib.error.HTTPError as exc:
            retryable = exc.code in {429, 500, 502, 503, 504}
            if not retryable or attempt >= max_retries:
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
            sleep(min(delay, 30))
        except (urllib.error.URLError, TimeoutError):
            if attempt >= max_retries:
                raise
            sleep(min(2**attempt, 30))
    raise AssertionError("unreachable retry loop")


def build_url(
    query: dict[str, Any],
    *,
    start: str,
    end: str,
    rows: int,
    mailto: str | None,
) -> str:
    params = {
        "filter": (
            f"from-online-pub-date:{start},until-online-pub-date:{end},"
            "type:journal-article"
        ),
        f"query.{query['field']}": query["term"],
        "rows": str(rows),
        "select": (
            "DOI,title,subtitle,author,container-title,publisher,type,created,"
            "deposited,indexed,published-online,published-print,URL,abstract,subject"
        ),
    }
    if mailto:
        params["mailto"] = mailto
    return f"{API_URL}?{urllib.parse.urlencode(params)}"


def fetch_query(
    query: dict[str, Any],
    *,
    start: str,
    end: str,
    rows: int,
    timeout: int,
    max_retries: int,
    mailto: str | None,
    urlopen: UrlOpen = urllib.request.urlopen,
    sleep: Sleep = time.sleep,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    url = build_url(
        query,
        start=start,
        end=end,
        rows=rows,
        mailto=mailto,
    )
    payload = request_json(
        url,
        timeout=timeout,
        max_retries=max_retries,
        urlopen=urlopen,
        sleep=sleep,
    )
    message = payload.get("message")
    if not isinstance(message, dict):
        raise RuntimeError(f"Crossref query {query['id']} returned no message object")
    items = message.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"Crossref query {query['id']} returned no items list")
    total_results = int(message.get("total-results", len(items)))
    matched: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or not local_match(item, query["patterns"]):
            continue
        candidate = normalized_candidate(item, str(query["id"]))
        if candidate is not None:
            matched.append(candidate)

    return matched, {
        "id": query["id"],
        "status": "complete",
        "field": query["field"],
        "term": query["term"],
        "total_results": total_results,
        "raw_items": len(items),
        "matched_items": len(matched),
        "result_set_exhausted": len(items) >= total_results,
        "ranked_page_only": len(items) < total_results,
    }


def fetch_manifest(
    config: dict[str, Any],
    *,
    start: str,
    end: str,
    mailto: str | None,
    urlopen: UrlOpen = urllib.request.urlopen,
    sleep: Sleep = time.sleep,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    parse_iso_date(start, "from")
    parse_iso_date(end, "until")
    if start > end:
        raise ValueError("from date cannot be after until date")

    crossref = config["crossref"]
    rows = int(crossref.get("rows_per_page", 200))
    concurrent_queries = int(crossref.get("concurrent_queries", 4))
    timeout = int(crossref.get("timeout_seconds", 30))
    max_retries = int(crossref.get("max_retries", 4))
    if rows < 1 or rows > 1000:
        raise ValueError("crossref.rows_per_page must be between 1 and 1000")
    if concurrent_queries < 1 or concurrent_queries > 8:
        raise ValueError("crossref.concurrent_queries must be between 1 and 8")

    candidates: dict[str, dict[str, Any]] = {}
    query_reports: list[dict[str, Any]] = []
    raw_matches = 0
    failures = 0

    def run_query(query: dict[str, Any]):
        return fetch_query(
            query,
            start=start,
            end=end,
            rows=rows,
            timeout=timeout,
            max_retries=max_retries,
            mailto=mailto,
            urlopen=urlopen,
            sleep=sleep,
        )

    worker_count = min(concurrent_queries, len(crossref["queries"]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(run_query, query): query
            for query in crossref["queries"]
        }
        for future in concurrent.futures.as_completed(futures):
            query = futures[future]
            try:
                matches, report = future.result()
            except Exception as exc:
                failures += 1
                report = {
                    "id": query["id"],
                    "status": "failed",
                    "field": query["field"],
                    "term": query["term"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
                matches = []
            query_reports.append(report)
            if progress is not None:
                progress(
                    f"{query['id']}: {report['status']}"
                    + (
                        f", {report.get('matched_items', 0)} exact title matches"
                        if report["status"] == "complete"
                        else ""
                    )
                )
            raw_matches += len(matches)
            for candidate in matches:
                key = candidate["doi"]
                if key in candidates:
                    merge_candidate(candidates[key], candidate)
                else:
                    candidates[key] = candidate

    query_reports.sort(key=lambda report: str(report["id"]))

    return {
        "schema_version": 1,
        "source": "crossref",
        "status": "complete" if failures == 0 else "partial",
        "coverage": "ranked-title-backstop",
        "window": {"from": start, "until": end},
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "queries": query_reports,
        "raw_matched_items": raw_matches,
        "all_result_sets_exhausted": all(
            report.get("result_set_exhausted", False) for report in query_reports
        ),
        "failed_query_count": failures,
        "candidate_count": len(candidates),
        "candidates": sorted(candidates.values(), key=lambda item: (item["title"], item["doi"])),
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


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--from", dest="start", required=True, help="inclusive ISO date")
    result.add_argument("--until", dest="end", required=True, help="inclusive ISO date")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument(
        "--mailto",
        default=os.environ.get("RADAR_CROSSREF_MAILTO"),
        help="Crossref polite-pool contact; defaults to RADAR_CROSSREF_MAILTO",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    config = load_config(args.config)
    manifest = fetch_manifest(
        config,
        start=args.start,
        end=args.end,
        mailto=args.mailto,
        progress=lambda message: print(message, flush=True),
    )
    atomic_write_json(args.output, manifest)
    print(
        f"wrote {manifest['candidate_count']} Crossref candidates from "
        f"{sum(query.get('raw_items', 0) for query in manifest['queries'])} raw records "
        f"to {args.output}"
    )
    if manifest["status"] != "complete":
        raise SystemExit(
            f"Crossref backstop incomplete: {manifest['failed_query_count']} queries failed"
        )


if __name__ == "__main__":
    main()
