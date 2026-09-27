#!/usr/bin/env python3
"""Capture dated arXiv Catchup listings (new, cross-list and replacement events).

Official Catchup retains roughly90 days and omits journal-reference-only changes
and replacements beyond v5. Completion describes these listings, not every update.
"""
from __future__ import annotations

import argparse
import concurrent.futures
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re
import time
from typing import Any

from fetch_arxiv_candidates import (
    TOKEN_RE, atomic_write_json, clean_text, configured_core_categories,
    DEFAULT_CONFIG, merge_candidate, parse_entry, parse_heading, request_text,
)

LIMITATION = "Official Catchup omits journal-reference-only changes and replacements beyond v5."


def catchup_url(category: str, day: str, page: int = 1) -> str:
    if not re.fullmatch(r"[A-Za-z-]+(?:\.[A-Za-z-]+)?", category):
        raise ValueError("invalid arXiv category")
    date.fromisoformat(day)
    return f"https://arxiv.org/catchup/{category}/{day}?abs=False&page={page}"


def parse_catchup(text: str, category: str, day: str) -> tuple[list[dict[str, Any]], int]:
    heading = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if not heading or parse_heading(heading[1]).isoformat() != day:
        raise ValueError("Catchup date heading missing or differs from requested day")
    total_match = re.search(r"Total of\s+([\d,]+)\s+entries", clean_text(text), re.I)
    if not total_match:
        raise ValueError("Catchup total missing; an error page is not an empty result")
    total = int(total_match[1].replace(",", ""))
    kind = None
    records = []
    for token in TOKEN_RE.finditer(text):
        if token.group("heading"):
            title = clean_text(token.group("heading")).lower()
            if title.startswith("new submissions"): kind = "new"
            elif title.startswith("cross"): kind = "cross"
            elif title.startswith("replacement"): kind = "replacement"
            else: raise ValueError(f"Unknown Catchup section: {title}")
        elif token.group("entry"):
            if kind is None: raise ValueError("Catchup entry precedes its section")
            item = parse_entry(token.group("entry"), date.fromisoformat(day), category)
            item.update(listing_type=kind, listing_types={category:kind}, evidence_url=catchup_url(category,day))
            records.append(item)
    if len(records) != min(total,2000):
        raise ValueError(f"Catchup parsed {len(records)} entries; expected {min(total,2000)}")
    if total > 2000:
        raise ValueError("Catchup exceeds the bounded per-category daily page; narrow the source scope")
    return records,total


def fetch_manifest(categories: list[str], days: list[str], *, cache_dir: Path,
                   timeout: int=30, workers: int=2, progress=print,
                   fetch_text=request_text) -> dict[str, Any]:
    jobs=[(c,d) for c in dict.fromkeys(categories) for d in sorted(set(days))]
    if not jobs or len(jobs)>250: raise ValueError("Catchup requires1–250 bounded category/date requests")
    if not 1<=workers<=2: raise ValueError("Use at most two Catchup workers")
    cache_dir.mkdir(parents=True,exist_ok=True)
    def fetch(job):
        category,day=job
        url=catchup_url(category,day)
        raw=cache_dir/f"catchup-{category}-{day}.html"
        try:
            cached=raw.exists()
            text=raw.read_text(encoding="utf-8") if cached else fetch_text(url,timeout=timeout)
            if not cached:
                raw.write_text(text,encoding="utf-8")
                time.sleep(.4)
            records,total=parse_catchup(text,category,day)
            return records,dict(category=category,date=day,url=url,status="complete",count=total,cached=cached)
        except Exception as exc:
            return [],dict(category=category,date=day,url=url,status="failed",error=f"{type(exc).__name__}: {exc}")
    events={};reports=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for items,report in pool.map(fetch,jobs):
            reports.append(report)
            progress(f"{len(reports)}/{len(jobs)} {report['category']} {report['date']} {report['status']} {report.get('count','')}")
            for item in items:
                key=(item['arxiv_id'],item['announcement_date'])
                if key in events:
                    old=events[key];merge_candidate(old,item)
                    old['listing_types'].update(item['listing_types'])
                    kinds=set(old['listing_types'].values())
                    old['listing_type']='new' if 'new' in kinds else 'cross' if 'cross' in kinds else 'replacement'
                    old['evidence_urls']=sorted(set(old.get('evidence_urls',[old['evidence_url']]))|{item['evidence_url']})
                else:events[key]=item
    failed=sum(r['status']=='failed' for r in reports)
    return dict(schema_version=1,source="arxiv-catchup",status="partial" if failed else "complete",
                dates=sorted(set(days)),categories=categories,limitation=LIMITATION,
                generated_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
                failed_request_count=failed,sources=reports,candidate_count=len(events),
                candidates=sorted(events.values(),key=lambda x:(x['announcement_date'],x['arxiv_id'])))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from',dest='start',required=True)
    parser.add_argument('--until',dest='end',required=True)
    parser.add_argument('--category',action='append',dest='categories')
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--cache-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=30)
    args=parser.parse_args()
    start,end=date.fromisoformat(args.start),date.fromisoformat(args.end)
    if not 0<=(end-start).days<=30:parser.error('Use a window of at most31 days')
    days=[(start+timedelta(days=n)).isoformat() for n in range((end-start).days+1)]
    result=fetch_manifest(args.categories or configured_core_categories(args.config),days,
                          cache_dir=args.cache_dir,timeout=args.timeout)
    atomic_write_json(args.output,result)
    if result['status']!='complete':raise SystemExit('Catchup incomplete; do not advance failed coverage')


if __name__=='__main__':main()
