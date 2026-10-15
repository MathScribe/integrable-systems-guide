#!/usr/bin/env python3
"""Fast, network-free bibliography/date/link checks, also usable on a staged tree."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from resource_checks import validate_links
from validate_radar import parse_date, today_shanghai, validate_papers
from render_radar import validate_frontier


def validate(root: Path, *, today=None) -> list[str]:
    today = today or today_shanghai()
    errors = []
    papers = yaml.safe_load((root / 'data/papers.yml').read_text(encoding='utf-8'))
    try:
        validate_papers(papers, today=today)
    except ValueError as exc:
        errors.append(f'data/papers.yml: {exc}')
    editions = yaml.safe_load((root / 'data/editions.yml').read_text(encoding='utf-8'))
    try:
        entries = validate_frontier(editions['frontier'], {p['id']: p for p in papers})
        for entry in entries:
            for field in ('signal_date', 'added_on'):
                if entry.get(field) is not None and parse_date(entry[field], field) > today:
                    errors.append(f'data/editions.yml: {entry["paper_id"]}.{field}: date is in the future')
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f'data/editions.yml: {exc}')
    errors.extend(validate_links(root))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Offline bibliography, date and source-link checks passed.')


if __name__ == '__main__':
    main()
