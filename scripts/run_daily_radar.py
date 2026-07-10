#!/usr/bin/env python3
"""Run the radar with a strict publication-date gate for public briefs.

The broad source lookback remains available for candidate/backlog and metadata
updates. Only papers whose publication date falls inside the daily window may
retain ``recommended`` status and reach the public brief.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections.abc import Callable

import radar


def publication_eligible(published: str | None, brief_date: dt.date, window_days: int) -> bool:
    """Return whether a metadata publication date is inside the public window."""
    if not published or window_days < 1:
        return False
    try:
        publication_date = dt.date.fromisoformat(published[:10])
    except (TypeError, ValueError):
        return False
    start = brief_date - dt.timedelta(days=window_days - 1)
    return start <= publication_date <= brief_date


def install_publication_gate(brief_date: dt.date, window_days: int) -> None:
    """Downgrade stale/undated recommendations while preserving backlog records."""
    original: Callable[[radar.Paper], None] = radar.score_and_classify

    def guarded_score_and_classify(paper: radar.Paper) -> None:
        original(paper)
        if paper.status != "recommended":
            return
        if publication_eligible(paper.published, brief_date, window_days):
            return
        paper.status = "candidate"
        paper.level = "观察"
        date_note = paper.published or "unknown"
        paper.reason = (
            f"{paper.reason}; excluded from daily brief because publication date "
            f"{date_note} is outside the {window_days}-day window ending {brief_date.isoformat()}"
        ).strip("; ")

    radar.score_and_classify = guarded_score_and_classify


def parse_wrapper_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument(
        "--publication-window-days",
        type=int,
        default=2,
        help="inclusive calendar-day window for papers allowed in the public daily brief",
    )
    args, remaining = parser.parse_known_args(argv)
    if args.publication_window_days < 1:
        parser.error("--publication-window-days must be at least 1")
    return args, remaining


def main() -> None:
    args, remaining = parse_wrapper_args(sys.argv[1:])
    brief_date = dt.date.fromisoformat(args.date)
    install_publication_gate(brief_date, args.publication_window_days)
    sys.argv = [sys.argv[0], "--date", args.date, *remaining]
    radar.main()


if __name__ == "__main__":
    main()
