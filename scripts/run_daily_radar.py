#!/usr/bin/env python3
"""Run the research radar with a recent-publication gate.

Broad source lookback remains available for candidate/backlog records and
metadata updates. Papers inside the recent window may retain ``recommended``
status. Older high-value papers remain available for manual backlog/core
curation instead of being presented as newly published work.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections.abc import Callable

import radar


def publication_eligible(published: str | None, edition_date: dt.date, window_days: int) -> bool:
    """Return whether a metadata publication date is inside the recent window."""
    if not published or window_days < 1:
        return False
    try:
        publication_date = dt.date.fromisoformat(published[:10])
    except (TypeError, ValueError):
        return False
    start = edition_date - dt.timedelta(days=window_days - 1)
    return start <= publication_date <= edition_date


def install_publication_gate(edition_date: dt.date, window_days: int) -> None:
    """Keep recent recommendations public and retain older items as candidates."""
    original: Callable[[radar.Paper], None] = radar.score_and_classify

    def guarded_score_and_classify(paper: radar.Paper) -> None:
        original(paper)
        if paper.status != "recommended":
            return
        if publication_eligible(paper.published, edition_date, window_days):
            return
        paper.status = "candidate"
        paper.level = "值得补读候选"
        date_note = paper.published or "unknown"
        paper.reason = (
            f"{paper.reason}; retained for backlog review because publication date "
            f"{date_note} is outside the {window_days}-day recent window ending "
            f"{edition_date.isoformat()}"
        ).strip("; ")

    radar.score_and_classify = guarded_score_and_classify


def parse_wrapper_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument(
        "--publication-window-days",
        type=int,
        default=30,
        help="inclusive recent-publication window for automatic public recommendations",
    )
    args, remaining = parser.parse_known_args(argv)
    if args.publication_window_days < 1:
        parser.error("--publication-window-days must be at least 1")
    return args, remaining


def main() -> None:
    args, remaining = parse_wrapper_args(sys.argv[1:])
    edition_date = dt.date.fromisoformat(args.date)
    install_publication_gate(edition_date, args.publication_window_days)
    sys.argv = [sys.argv[0], "--date", args.date, *remaining]
    radar.main()


if __name__ == "__main__":
    main()
