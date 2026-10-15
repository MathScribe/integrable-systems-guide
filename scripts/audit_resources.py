#!/usr/bin/env python3
"""Read-only online link/metadata audit. Never edits authoritative data or fails CI on outages."""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import yaml

from resource_checks import inventory
from validate_radar import normalize_doi, normalize_arxiv, normalize_title

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'integrable-systems-guide/1.0 (https://github.com/MathScribe/integrable-systems-guide)'


def classify(status, url, final_url):
    if status in {404, 410}:
        return 'missing-candidate'
    if status in {200, 206}:
        return 'redirected' if url != final_url else 'reachable'
    return 'unverified'  # Includes 403, 429, TLS errors and timeouts.


class Client:
    def __init__(self, cache: Path, *, timeout=15, max_age=86400, opener=urlopen):
        self.cache, self.timeout, self.max_age, self.opener = cache, timeout, max_age, opener
        cache.mkdir(parents=True, exist_ok=True)
        self.guard = threading.Lock()
        self.hosts = {}

    def get(self, url):
        path = self.cache / (hashlib.sha256(url.encode()).hexdigest() + '.json')
        if path.exists() and time.time() - path.stat().st_mtime < self.max_age:
            result = json.loads(path.read_text(encoding='utf-8'))
            return {**result, 'cached': True}
        host = urlsplit(url).hostname
        with self.guard:
            lock, previous = self.hosts.setdefault(host, (threading.Lock(), [0.0]))
        with lock:
            delay = 3 if host in {'arxiv.org', 'export.arxiv.org'} else 0.5
            time.sleep(max(0, delay - (time.monotonic() - previous[0])))
            result = {'url': url, 'checked_at': datetime.now(timezone.utc).isoformat(), 'cached': False}
            try:
                request = Request(url, headers={'User-Agent': USER_AGENT})
                with self.opener(request, timeout=self.timeout) as response:
                    result.update(status=response.status, final_url=response.url,
                                  content_type=response.headers.get('Content-Type', ''))
                    if 'pdf' not in result['content_type'].lower():
                        result['body'] = response.read(3_000_000).decode('utf-8', errors='replace')
            except HTTPError as exc:
                result.update(status=exc.code, final_url=exc.url, error=str(exc))
            except (URLError, TimeoutError, OSError) as exc:
                result.update(status=None, error=str(exc))
            finally:
                previous[0] = time.monotonic()
        result['state'] = classify(result.get('status'), url, result.get('final_url'))
        path.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
        return result


def link_summary(result):
    result = dict(result)
    body = result.pop('body', '')
    title = re.search(r'<title[^>]*>(.*?)</title>', body, re.I | re.S)
    result['page_title'] = re.sub(r'\s+', ' ', title.group(1)).strip() if title else None
    if result.get('page_title') and re.search(r'access denied|just a moment|captcha|checking.*browser', result['page_title'], re.I):
        result['state'] = 'unverified'
    return result


def arxiv_entries(body):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
    root = ET.fromstring(body)
    return [{
        'url': entry.findtext('a:id', namespaces=ns),
        'title': entry.findtext('a:title', namespaces=ns),
        'published': entry.findtext('a:published', namespaces=ns),
        'updated': entry.findtext('a:updated', namespaces=ns),
        'doi': entry.findtext('x:doi', namespaces=ns),
        'journal_ref': entry.findtext('x:journal_ref', namespaces=ns),
        'comment': entry.findtext('x:comment', namespaces=ns),
        'summary': entry.findtext('a:summary', namespaces=ns),
        'authors': [author.text for author in entry.findall('a:author/a:name', ns)],
    } for entry in root.findall('a:entry', ns)]


def similar_titles(papers):
    suggestions = []
    titles = [(paper['id'], normalize_title(paper['title'])) for paper in papers]
    for index, (paper_id, title) in enumerate(titles):
        if len(title) < 40:
            continue
        for other_id, other in titles[index + 1:]:
            if abs(len(title) - len(other)) > max(len(title), len(other)) * 0.1:
                continue
            ratio = SequenceMatcher(None, title, other).ratio()
            if ratio >= 0.94:
                suggestions.append({'paper_ids': [paper_id, other_id], 'similarity': round(ratio, 4)})
    return suggestions  # Advisory only: part I/II and related papers may be distinct.


def metadata(client, papers, *, publication_search=False):
    records = []
    by_arxiv = {normalize_arxiv(p['arxiv_id']): p for p in papers if p.get('arxiv_id')}
    ids = sorted({normalize_arxiv(p['arxiv_id']) for p in papers if p.get('arxiv_id')})
    for start in range(0, len(ids), 40):
        batch = ids[start:start + 40]
        url = 'https://export.arxiv.org/api/query?' + urlencode({'id_list': ','.join(batch), 'max_results': 40})
        result = client.get(url)
        try:
            entries = arxiv_entries(result.get('body', ''))
            actual = {normalize_arxiv(e['url'].split('/abs/')[-1]) for e in entries if e.get('url')}
            for entry in entries:
                identifier = normalize_arxiv((entry.get('url') or '').split('/abs/')[-1])
                paper = by_arxiv.get(identifier)
                if paper is None:
                    continue
                version = re.search(r'v[1-9]\d*$', entry['url'])
                remote = {'version': version.group() if version else None,
                          'submitted': (entry.get('published') or '')[:10] or None,
                          'updated': (entry.get('updated') or '')[:10] or None,
                          'doi': entry.get('doi')}
                entry['paper_id'] = paper['id']
                entry['differences'] = {key: {'current': paper.get(key), 'remote': value}
                                        for key, value in remote.items()
                                        if value and paper.get(key) != value}
                comment = entry.get('comment') or ''
                if re.search(r'withdraw|retract', comment, re.I):
                    entry['status_notice_for_review'] = comment
            records.append({'source': url, 'kind': 'arxiv', 'records': entries,
                            'missing_ids': sorted(set(batch) - actual)})
        except ET.ParseError:
            records.append({'source': url, 'kind': 'arxiv', 'missing_ids': batch,
                            'error': result.get('error', 'unparseable response')})
    discovered = {normalize_arxiv(e['url'].split('/abs/')[-1]): e.get('doi')
                  for batch in records for e in batch.get('records', []) if e.get('url')}
    for index, paper in enumerate(papers, 1):
        doi = paper.get('doi') or discovered.get(normalize_arxiv(paper.get('arxiv_id', '') or ''))
        if doi:
            url = 'https://api.crossref.org/works/' + quote(normalize_doi(doi), safe='/')
        elif publication_search:
            url = 'https://api.crossref.org/works?' + urlencode({
                'query.title': paper['title'], 'query.author': paper['authors'][0], 'rows': 3})
        else:
            continue
        result = client.get(url)
        try:
            message = json.loads(result.get('body', ''))['message']
            records.append({'paper_id': paper['id'], 'source': url,
                            'kind': 'crossref-doi' if doi else 'crossref-candidates',
                            'current_bibliography': {key: paper.get(key) for key in
                                ('title', 'authors', 'doi', 'journal', 'year', 'volume', 'issue', 'pages', 'article_number', 'published')},
                            'record': message})
        except (ValueError, KeyError):
            records.append({'paper_id': paper['id'], 'source': url, 'kind': 'crossref',
                            'error': result.get('error', 'unparseable response')})
        if index % 25 == 0:
            print(f'Metadata: {index}/{len(papers)}', flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cache', type=Path, default=ROOT / '.radar-audit/http-cache')
    parser.add_argument('--max-age', type=int, default=86400, help='Cache lifetime in seconds; 0 forces refresh')
    parser.add_argument('--workers', type=int, choices=range(1, 9), default=4)
    parser.add_argument('--timeout', type=float, default=15)
    parser.add_argument('--metadata', action='store_true')
    parser.add_argument('--publication-search', action='store_true', help='Also search titles without a known DOI (implies --metadata)')
    args = parser.parse_args()
    client = Client(args.cache, timeout=args.timeout, max_age=args.max_age)
    papers = yaml.safe_load((ROOT / 'data/papers.yml').read_text(encoding='utf-8'))
    links = inventory(ROOT)
    urls = sorted({link.url for link in links if link.url.startswith(('http://', 'https://'))})
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'links': [],
              'similar_titles': similar_titles(papers)}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, result in enumerate(pool.map(client.get, urls), 1):
            row = link_summary(result)
            row['sources'] = sorted({f'{link.source}:{link.field}' for link in links if link.url == result['url']})
            report['links'].append(row)
            if index % 25 == 0:
                print(f'Links: {index}/{len(urls)}', flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.metadata or args.publication_search:
        report['metadata'] = metadata(client, papers, publication_search=args.publication_search)
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {args.output}; HTTP success requires identity/content review before any correction.')


if __name__ == '__main__':
    main()
