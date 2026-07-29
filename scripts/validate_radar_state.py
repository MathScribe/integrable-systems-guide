#!/usr/bin/env python3
"""Validate independent discovery-source watermarks and their public-data bounds."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "maintenance" / "radar-state.yml"
EDITIONS_PATH = ROOT / "data" / "editions.yml"

ARXIV_SOURCES = ("arxiv_nlin_si", "arxiv_nlin_ps", "arxiv_cross_category")
ALLOWED_STATUSES = {
    "complete",
    "partial",
    "failed",
    "not-established",
    "not-configured",
    "candidate-only",
}


def require_mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    return value


def parse_date(value: object, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date: {value!r}") from exc


def parse_utc_timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO timestamp ending in Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO timestamp: {value!r}") from exc


def validate_status(source: dict[str, Any], field: str) -> str:
    status = source.get("last_status")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"{field}.last_status is invalid: {status!r}")
    return str(status)


def main() -> None:
    state = require_mapping(yaml.safe_load(STATE_PATH.read_text(encoding="utf-8")), "radar state")
    if state.get("schema_version") != 1:
        raise ValueError("maintenance/radar-state.yml schema_version must be 1")
    sources = require_mapping(state.get("sources"), "sources")

    editions = require_mapping(
        yaml.safe_load(EDITIONS_PATH.read_text(encoding="utf-8")), "editions"
    )
    frontier = require_mapping(editions.get("frontier"), "frontier")
    if "checked_through" in frontier:
        raise ValueError(
            "frontier.checked_through conflates independent sources; remove it and use radar-state.yml"
        )
    entries = frontier.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("frontier.entries must be a non-empty list")

    arxiv_watermarks: list[date] = []
    for source_name in ARXIV_SOURCES:
        source = require_mapping(sources.get(source_name), f"sources.{source_name}")
        if source.get("kind") != "arxiv-announcement":
            raise ValueError(f"sources.{source_name}.kind must be arxiv-announcement")
        status = validate_status(source, f"sources.{source_name}")
        watermark = parse_date(
            source.get("announced_through"), f"sources.{source_name}.announced_through"
        )
        if status != "complete":
            raise ValueError(
                f"sources.{source_name} must remain complete at its last successful watermark"
            )
        arxiv_watermarks.append(watermark)

    latest_public_arxiv = max(
        parse_date(entry["signal_date"], f"{entry['paper_id']}.signal_date")
        for entry in entries
        if entry.get("signal_type") in {"new-preprint", "major-revision"}
    )
    if min(arxiv_watermarks) < latest_public_arxiv:
        raise ValueError(
            "the common arXiv announcement watermark cannot precede a public arXiv event"
        )

    crossref = require_mapping(sources.get("crossref"), "sources.crossref")
    if crossref.get("kind") != "ranked-title-backstop":
        raise ValueError("sources.crossref.kind must be ranked-title-backstop")
    crossref_status = validate_status(crossref, "sources.crossref")
    overlap_days = crossref.get("overlap_days")
    if not isinstance(overlap_days, int) or overlap_days < 1:
        raise ValueError("sources.crossref.overlap_days must be a positive integer")
    title_query_through = crossref.get("title_query_through")
    if title_query_through is not None:
        parse_date(title_query_through, "sources.crossref.title_query_through")
    reconciliation_checked_at = crossref.get("reconciliation_checked_at")
    if reconciliation_checked_at is not None:
        parse_utc_timestamp(
            reconciliation_checked_at, "sources.crossref.reconciliation_checked_at"
        )
    if crossref.get("reconciliation_cadence") != "weekly":
        raise ValueError("Crossref registry reconciliation cadence must be weekly")
    if crossref_status == "complete" and title_query_through is None:
        raise ValueError("a complete Crossref title backstop requires a query watermark")

    zbmath = require_mapping(sources.get("zbmath"), "sources.zbmath")
    validate_status(zbmath, "sources.zbmath")
    if zbmath.get("kind") != "mathematical-index-backstop":
        raise ValueError("sources.zbmath.kind must be mathematical-index-backstop")
    if zbmath.get("cadence") not in {"weekly", "biweekly"}:
        raise ValueError("sources.zbmath.cadence must be weekly or biweekly")

    publisher = require_mapping(
        sources.get("publisher_verification"), "sources.publisher_verification"
    )
    validate_status(publisher, "sources.publisher_verification")
    if publisher.get("kind") != "candidate-verification":
        raise ValueError("publisher verification is candidate evidence, not a coverage watermark")

    print(
        "validated independent radar source state; "
        f"arXiv announced through {min(arxiv_watermarks).isoformat()}, "
        f"Crossref status {crossref_status}"
    )


if __name__ == "__main__":
    main()
