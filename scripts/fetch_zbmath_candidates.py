#!/usr/bin/env python3
"""Fetch a bounded recent zbMATH journal candidate manifest by MSC code."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "maintenance" / "radar-sources.yml"
API_URL = "https://api.zbmath.org/v1/document/_search"
USER_AGENT = (
    "integrable-systems-guide/1.0 "
    "(https://github.com/MathScribe/integrable-systems-guide)"
)

UrlOpen = Callable[..., Any]
Sleep = Callable[[float], None]


def parse_utc_timestamp(value: str, field: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"{field} must end in Z: {value!r}")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO timestamp: {value!r}") from exc


def load_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{path} must use radar source schema_version 1")
    config = data.get("zbmath")
    if not isinstance(config, dict):
        raise ValueError(f"{path} is missing zbmath configuration")
    codes = config.get("msc_codes")
    if not isinstance(codes, list) or not codes:
        raise ValueError("zbmath.msc_codes must be a non-empty list")
    if len(codes) != len(set(str(code) for code in codes)):
        raise ValueError("zbmath.msc_codes contains duplicates")
    return data


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
                raise RuntimeError("zbMATH returned a non-object JSON payload")
            return payload
        except urllib.error.HTTPError as exc:
            retryable = exc.code in {429, 500, 502, 503, 504}
            if not retryable or attempt >= max_retries:
                raise
            sleep(min(2**attempt, 20))
        except (urllib.error.URLError, TimeoutError):
            if attempt >= max_retries:
                raise
            sleep(min(2**attempt, 20))
    raise AssertionError("unreachable retry loop")


def build_search_string(start: datetime, end: datetime, codes: list[str]) -> str:
    if start.year == end.year:
        year_clause = str(end.year)
    else:
        year_clause = f"{start.year} - {end.year}"
    code_clause = " | ".join(str(code) for code in codes)
    return f"dt:j & py:{year_clause} & cc:({code_clause})"


def build_url(query: str, *, page: int, rows: int) -> str:
    params = {
        "search_string": query,
        "page": str(page),
        "results_per_page": str(rows),
    }
    return f"{API_URL}?{urllib.parse.urlencode(params)}"


def link_identifier(item: dict[str, Any], kind: str) -> str | None:
    for link in item.get("links") or []:
        if isinstance(link, dict) and link.get("type") == kind and link.get("identifier"):
            return str(link["identifier"])
    return None


def title_text(item: dict[str, Any]) -> str:
    title = item.get("title")
    if not isinstance(title, dict):
        return ""
    parts = (title.get("title"), title.get("subtitle"), title.get("addition"))
    return " ".join(str(part).strip() for part in parts if part).strip()


def author_names(item: dict[str, Any]) -> list[str]:
    contributors = item.get("contributors")
    if not isinstance(contributors, dict):
        return []
    result: list[str] = []
    for author in contributors.get("authors") or []:
        if isinstance(author, dict) and author.get("name"):
            result.append(str(author["name"]).strip())
    return result


def journal_name(item: dict[str, Any]) -> str:
    source = item.get("source")
    if not isinstance(source, dict):
        return ""
    for series in source.get("series") or []:
        if isinstance(series, dict) and series.get("title"):
            return str(series["title"]).strip()
    return ""


def normalized_candidate(item: dict[str, Any]) -> dict[str, Any] | None:
    identifier = item.get("id")
    title = title_text(item)
    datestamp = item.get("datestamp")
    if identifier is None or not title or not isinstance(datestamp, str):
        return None
    source = item.get("source")
    msc_codes = [
        str(value["code"])
        for value in item.get("msc") or []
        if isinstance(value, dict) and value.get("code")
    ]
    doi = link_identifier(item, "doi")
    arxiv_id = link_identifier(item, "arxiv")
    return {
        "id": f"zbmath:{identifier}",
        "zbmath_id": str(identifier),
        "title": title,
        "authors": author_names(item),
        "journal": journal_name(item),
        "source": str(source.get("source", "")).strip() if isinstance(source, dict) else "",
        "year": str(item.get("year") or ""),
        "msc": msc_codes,
        "doi": doi.lower() if doi else None,
        "arxiv_id": arxiv_id,
        "datestamp": datestamp,
        "url": str(item.get("zbmath_url") or f"https://zbmath.org/?q=an:{identifier}"),
    }


def fetch_manifest(
    config: dict[str, Any],
    *,
    start_value: str,
    end_value: str,
    urlopen: UrlOpen = urllib.request.urlopen,
    sleep: Sleep = time.sleep,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    start = parse_utc_timestamp(start_value, "from-datestamp")
    end = parse_utc_timestamp(end_value, "until-datestamp")
    if start > end:
        raise ValueError("from-datestamp cannot be after until-datestamp")

    source = config["zbmath"]
    rows = int(source.get("rows_per_page", 100))
    max_pages = int(source.get("max_pages", 6))
    timeout = int(source.get("timeout_seconds", 20))
    max_retries = int(source.get("max_retries", 2))
    if rows < 1 or rows > 100:
        raise ValueError("zbmath.rows_per_page must be between 1 and 100")
    if max_pages < 1 or max_pages > 20:
        raise ValueError("zbmath.max_pages must be between 1 and 20")

    codes = [str(code) for code in source["msc_codes"]]
    query = build_search_string(start, end, codes)
    candidates: dict[str, dict[str, Any]] = {}
    raw_items = 0
    pages_fetched = 0
    total_results: int | None = None
    status = "complete"
    error: str | None = None

    try:
        for page in range(max_pages):
            payload = request_json(
                build_url(query, page=page, rows=rows),
                timeout=timeout,
                max_retries=max_retries,
                urlopen=urlopen,
                sleep=sleep,
            )
            api_status = payload.get("status")
            items = payload.get("result")
            if not isinstance(api_status, dict) or not api_status.get("execution_bool"):
                raise RuntimeError("zbMATH reported an unsuccessful query")
            if not isinstance(items, list):
                raise RuntimeError("zbMATH returned no result list")
            total_results = int(api_status.get("nr_total_results", len(items)))
            pages_fetched += 1
            raw_items += len(items)
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get("datestamp"), str):
                    continue
                datestamp = parse_utc_timestamp(str(item["datestamp"]), "item.datestamp")
                if not (start <= datestamp <= end):
                    continue
                candidate = normalized_candidate(item)
                if candidate is not None:
                    candidates[candidate["zbmath_id"]] = candidate
            if progress is not None:
                progress(f"zbMATH page {page + 1}: {len(items)} records")
            if raw_items >= total_results or len(items) < rows:
                break
        if total_results is not None and raw_items < total_results:
            status = "partial"
            error = (
                f"bounded query stopped after {raw_items} of {total_results} records; "
                "increase zbmath.max_pages only after reviewing query scope"
            )
    except Exception as exc:
        status = "partial"
        error = f"{type(exc).__name__}: {exc}"

    return {
        "schema_version": 1,
        "source": "zbmath",
        "status": status,
        "coverage": "bounded-msc-journal-backstop",
        "window": {"from_datestamp": start_value, "until_datestamp": end_value},
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "query": {
            "search_string": query,
            "msc_codes": codes,
            "total_results": total_results,
            "pages_fetched": pages_fetched,
            "raw_items": raw_items,
            "result_set_exhausted": total_results is not None and raw_items >= total_results,
        },
        "error": error,
        "candidate_count": len(candidates),
        "candidates": sorted(
            candidates.values(), key=lambda item: (item["datestamp"], item["title"])
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


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--from-datestamp", required=True)
    result.add_argument("--until-datestamp", required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return result


def main() -> None:
    args = parser().parse_args()
    manifest = fetch_manifest(
        load_config(args.config),
        start_value=args.from_datestamp,
        end_value=args.until_datestamp,
        progress=lambda message: print(message, flush=True),
    )
    atomic_write_json(args.output, manifest)
    print(
        f"wrote {manifest['candidate_count']} zbMATH candidates from "
        f"{manifest['query']['raw_items']} bounded records to {args.output}"
    )
    if manifest["status"] != "complete":
        raise SystemExit(f"zbMATH backstop incomplete: {manifest['error']}")


if __name__ == "__main__":
    main()
