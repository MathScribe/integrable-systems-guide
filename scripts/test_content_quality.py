#!/usr/bin/env python3
"""Behavioral regression tests; all network responses are simulated."""
from __future__ import annotations

from datetime import date
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.error import HTTPError, URLError

import yaml

from audit_resources import Client, arxiv_entries, classify, link_summary, similar_titles, metadata
from check_staged import check_staged
from resource_checks import inventory, validate_links
from validate_content import validate
from validate_radar import validate_papers, validate_url

TODAY = date(2026, 10, 15)
ROOT = Path(__file__).resolve().parents[1]


def paper(**changes):
    return {'id': 'arxiv:2607.12345', 'title': 'An integrable equation',
            'authors': ['Ada Example'], 'arxiv_id': '2607.12345',
            'url': 'https://arxiv.org/abs/2607.12345', 'submitted': '2026-07-01', **changes}


def fixture(root):
    (root / 'data').mkdir()
    (root / 'docs').mkdir()
    shutil.copyfile(ROOT / 'data/tags.yml', root / 'data/tags.yml')
    (root / 'data/papers.yml').write_text(yaml.safe_dump([paper()]), encoding='utf-8')
    editions = {'schema_version': 2, 'frontier': {'entries': [{
        'paper_id': 'arxiv:2607.12345', 'signal_type': 'new-preprint',
        'signal_date': '2026-07-02', 'directions': ['waves'],
        'reading_note': {'lead': 'Result', 'detail': 'Detail', 'method_scope': 'Scope'},
    }]}}
    (root / 'data/editions.yml').write_text(yaml.safe_dump(editions), encoding='utf-8')
    (root / 'docs/index.md').write_text('# Home\n[Guide](guide/#section)\n', encoding='utf-8')
    (root / 'docs/guide.md').write_text('# Section\n', encoding='utf-8')


class BibliographyTests(unittest.TestCase):
    def test_duplicate_identity_variants(self):
        pairs = [
            (paper(doi='10.1000/ABC'), paper(id='another', title='Another title', arxiv_id=None,
                                           doi=' https://doi.org/10.1000/abc ')),
            (paper(), paper(id='another', title='Another title', arxiv_id='2607.12345v2')),
            (paper(), paper(id='another', title='AN integrable—equation!', arxiv_id=None)),
        ]
        for pair in pairs:
            with self.subTest(pair=pair), self.assertRaisesRegex(ValueError, 'duplicate'):
                validate_papers(list(pair), today=TODAY)

    def test_invalid_bibliography(self):
        for changes in ({'authors': [' ']}, {'authors': [42]}, {'authors': ['Unknown author']},
                        {'authors': 'Ada'}, {'title': ' '}, {'journal': 'Journal'},
                        {'year': True}, {'year': '2026'}, {'year': 26026},
                        {'submitted': '2026-02-30'}, {'submitted': '20260701'},
                        {'submitted': '2026-10-16'}, {'updated': '2026-06-30'},
                        {'metadata_checked_at': '2026-10-16'}, {'submitted': None},
                        {'submitted_at': '2026-07-02T00:00:00Z'},
                        {'submitted_at': '2026-07-01T00:00:00'},
                        {'published': '2026-10-16', 'journal': 'Journal', 'year': 2026},
                        {'doi': 'not-a-doi'}, {'arxiv_id': '2613.12345'},
                        {'doi': 'https://doi.org/10.1000/test'}, {'arxiv_id': '2607.12345v2'},
                        {'url': 'https:///broken'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_papers([paper(**changes)], today=TODAY)

    def test_valid_precision_and_future_issue_year(self):
        for published in ('2026', '2026-10', '2026-10-01', '2027'):
            self.assertEqual(validate_papers([paper(journal='Journal', year=2027, published=published)], today=TODAY), 1)
        legacy = paper(id='arxiv:solv-int/9701001', arxiv_id='solv-int/9701001',
                       url='https://arxiv.org/abs/solv-int/9701001', submitted='1997-01-01')
        self.assertEqual(validate_papers([legacy], today=TODAY), 1)
        self.assertEqual(validate_papers([paper(submitted_at='2026-07-01T23:59:00Z')], today=TODAY), 1)

    def test_bad_links(self):
        for url in ('javascript:alert(1)', 'https://', 'https://example.org/a b',
                    'https://example.org/%ZZ', 'https://doi.org/missing',
                    'https://arxiv.org/abs/2600.12345', 'https://user:password@example.org',
                    'https://example.org:bad/path'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url, 'fixture.url')
        validate_url('https://doi.org/10.1007/jhep06(2026)173', 'fixture.url')


class SourceTests(unittest.TestCase):
    def test_dates_and_links(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
            root = Path(directory)
            fixture(root)
            self.assertEqual(validate(root, today=TODAY), [])
            path = root / 'data/editions.yml'
            data = yaml.safe_load(path.read_text())
            data['frontier']['entries'][0]['signal_date'] = '2026-10-16'
            path.write_text(yaml.safe_dump(data), encoding='utf-8')
            self.assertTrue(any('signal_date' in error for error in validate(root, today=TODAY)))
            (root / 'docs/guide.md').write_text('# Different\n[Broken](missing.md)\n', encoding='utf-8')
            errors = validate_links(root)
            self.assertTrue(any('missing anchor' in error for error in errors))
            self.assertTrue(any('missing local target' in error for error in errors))

    def test_unknown_date_is_valid(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
            root = Path(directory)
            fixture(root)
            p = paper(doi='10.1000/test', journal='Journal', year=2027)
            (root / 'data/papers.yml').write_text(yaml.safe_dump([p]), encoding='utf-8')
            path = root / 'data/editions.yml'
            data = yaml.safe_load(path.read_text())
            data['frontier']['entries'][0].update(signal_date=None, signal_type='journal-publication',
                                                 added_on='2026-10-15', event_source='https://doi.org/10.1000/test')
            path.write_text(yaml.safe_dump(data), encoding='utf-8')
            self.assertEqual(validate(root, today=TODAY), [])
            data['frontier']['entries'][0]['added_on'] = '2026-10-16'
            path.write_text(yaml.safe_dump(data), encoding='utf-8')
            self.assertTrue(any('added_on' in error for error in validate(root, today=TODAY)))

    def test_url_inventory_preserves_parentheses(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
            root = Path(directory)
            fixture(root)
            url = 'https://doi.org/10.1007/jhep06(2026)173'
            (root / 'docs/guide.md').write_text(f'# Guide\n[DOI](<{url}>)\n<a href="https://example.org/?a=1&amp;b=2">Query</a>', encoding='utf-8')
            urls = {link.url for link in inventory(root)}
            self.assertIn(url, urls)
            self.assertIn('https://example.org/?a=1&b=2', urls)

    def test_staged_snapshot_does_not_use_unstaged_fix(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
            root = Path(directory)
            fixture(root)
            (root / 'scripts').mkdir()
            for filename in ('validate_content.py', 'validate_radar.py', 'resource_checks.py', 'render_radar.py'):
                shutil.copyfile(ROOT / 'scripts' / filename, root / 'scripts' / filename)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            path = root / 'data/papers.yml'
            good = path.read_text()
            path.write_text(yaml.safe_dump([paper(authors=[' '])]), encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            path.write_text(good, encoding='utf-8')
            self.assertNotEqual(check_staged(root), 0)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            self.assertEqual(check_staged(root), 0)


class NetworkTests(unittest.TestCase):
    def test_status_classification(self):
        self.assertEqual(classify(200, 'a', 'b'), 'redirected')
        self.assertEqual(classify(200, 'a', 'a'), 'reachable')
        for code in (404, 410):
            self.assertEqual(classify(code, 'a', 'a'), 'missing-candidate')
        for code in (202, 204, 403, 429, 500, None):
            self.assertEqual(classify(code, 'a', 'a'), 'unverified')
        self.assertEqual(link_summary({'state': 'reachable', 'body': '<title>Just a moment...</title>'})['state'], 'unverified')

    def test_similar_titles_are_advisory(self):
        papers = [paper(title='Integrable nonlinear equations and spectral theory part I'),
                  paper(id='second', title='Integrable nonlinear equations and spectral theory part II', arxiv_id=None)]
        self.assertEqual(validate_papers(papers, today=TODAY), 2)
        self.assertEqual(len(similar_titles(papers)), 1)

    def test_transport_and_cache(self):
        class Response(io.BytesIO):
            status, url = 200, 'https://example.org/new'
            headers = {'Content-Type': 'text/html'}
        calls = []
        def opener(request, timeout):
            calls.append(request.full_url)
            return Response(b'<title>Example</title>')
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
            client = Client(Path(directory), opener=opener)
            first = client.get('https://example.org/old')
            cached = client.get('https://example.org/old')
            self.assertEqual(first['state'], 'redirected')
            self.assertTrue(cached['cached'])
            self.assertEqual(len(calls), 1)
            self.assertEqual(cached['checked_at'], first['checked_at'])
        for error in (HTTPError('https://example.org', 404, 'Missing', {}, None),
                      HTTPError('https://example.org', 403, 'Forbidden', {}, None),
                      HTTPError('https://example.org', 429, 'Limited', {}, None),
                      URLError('timeout'), TimeoutError('timeout')):
            def fail(request, timeout):
                raise error
            with tempfile.TemporaryDirectory(dir=ROOT, prefix='.staged-check-') as directory:
                result = Client(Path(directory), opener=fail).get('https://example.org')
                self.assertIn(result['state'], {'missing-candidate', 'unverified'})

    def test_arxiv_parse(self):
        xml = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2607.12345v2</id><title>Paper</title><updated>2026-07-02T00:00:00Z</updated><author><name>Ada</name></author></entry></feed>'
        entry, = arxiv_entries(xml)
        self.assertEqual(entry['authors'], ['Ada'])
        self.assertTrue(entry['url'].endswith('v2'))

    def test_metadata_reports_changes_without_mutating_records(self):
        xml = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2607.12345v2</id><updated>2026-07-02T00:00:00Z</updated><published>2026-07-01T00:00:00Z</published></entry></feed>'
        class FakeClient:
            def get(self, url):
                return {'body': xml}
        original = paper(version='v1')
        report = metadata(FakeClient(), [original])
        self.assertEqual(report[0]['missing_ids'], [])
        self.assertEqual(report[0]['records'][0]['differences']['version'], {'current': 'v1', 'remote': 'v2'})
        self.assertEqual(original['version'], 'v1')


if __name__ == '__main__':
    unittest.main()
