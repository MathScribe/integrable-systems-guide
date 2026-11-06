"""Check cache invalidation and rendered asset URLs, including nested pages."""

from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import sys

from version_assets import versioned_url


class AssetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.urls.append(attrs["href"])
        elif tag == "script" and attrs.get("src"):
            self.urls.append(attrs["src"])


class ProblemLinks(HTMLParser):
    """Check copy targets stay inside their cards and retain math/source text."""
    def __init__(self):
        super().__init__()
        self.card = None
        self.article_stack = []
        self.targets = {}
        self.texts = {}
        self.active_text = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article':
            self.article_stack.append('problem-card' in attrs.get('class', '').split())
        if tag == 'article' and 'problem-card' in attrs.get('class', '').split():
            assert self.card is None, 'Nested problem cards'
            self.card = attrs['id']
            self.targets[self.card] = []
        elif tag == 'button' and 'data-copy-target' in attrs:
            assert self.card, 'Copy action outside its problem card'
            self.targets[self.card].append(attrs['data-copy-target'])
        elif tag == 'textarea' and self.card:
            self.active_text = attrs['id']
            assert self.active_text not in self.texts, 'Duplicate copy target'
            self.texts[self.active_text] = ''
        if tag == 'a':
            target = urlsplit(attrs.get('href', ''))
            if not target.scheme and not target.netloc:
                assert not target.path.endswith('.md'), attrs
            assert 'download' not in attrs, 'Obsolete research-note download'

    def handle_data(self, data):
        if self.active_text:
            self.texts[self.active_text] += data

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.active_text = None
        if tag == 'article':
            assert self.article_stack, 'Unmatched closing article'
            if self.article_stack.pop():
                assert self.card, 'Unmatched closing problem card'
                self.card = None


def main():
    # A content change must invalidate cache; rebuilding must not append more v's.
    with patch.object(Path, "read_bytes", return_value=b"one\r\n"):
        first = versioned_url("stylesheets/radar.css?theme=light#x", ".")
        assert versioned_url(first, ".") == first
    with patch.object(Path, "read_bytes", return_value=b"one\n"):
        assert versioned_url("stylesheets/radar.css?theme=light#x", ".") == first
    with patch.object(Path, "read_bytes", return_value=b"two\n"):
        assert versioned_url("stylesheets/radar.css?theme=light#x", ".") != first
    remote = "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js"
    assert versioned_url(remote, ".") == remote

    site = Path(sys.argv[1]).resolve()
    pages = list(site.rglob("*.html"))
    assert pages, "No built HTML pages to validate"
    expected = {"stylesheets/radar.css", "stylesheets/group-papers.css",
                "javascripts/mathjax.js", "javascripts/goatcounter.js",
                "javascripts/radar.js", "javascripts/group-papers.js",
                "stylesheets/problems.css", "javascripts/problems.js"}
    checked = 0
    for page in pages:
        parser = AssetLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        found = set()
        for url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            path = parts.path.lstrip("/")
            # MkDocs emits site_url-rooted links for its 404 page.
            if parts.path.startswith("/integrable-systems-guide/"):
                target = site / path.removeprefix("integrable-systems-guide/")
            else:
                target = (page.parent / parts.path).resolve()
            relative = target.relative_to(site).as_posix()
            if relative not in expected:
                continue
            found.add(relative)
            content = target.read_bytes().replace(b"\r\n", b"\n")
            assert parse_qs(parts.query).get("v") == [sha256(content).hexdigest()[:16]], (page, url)
            checked += 1
        assert found == expected, (page, expected - found)
    print(f"Validated {checked} versioned asset links across {len(pages)} pages")
    problem_page = site / 'topics/index.html'
    problems = ProblemLinks()
    problems.feed(problem_page.read_text(encoding='utf-8'))
    assert problems.card is None
    assert problems.targets
    for problem_id, targets in problems.targets.items():
        assert targets == [f'description-{problem_id}', f'prompt-{problem_id}']
        statement, prompt = (problems.texts[target] for target in targets)
        assert len(statement) > 400 and 'https://' in statement and '$$' in statement
        assert prompt.startswith(statement) and '建议的本轮任务' in prompt
        assert '不编造' in prompt and len(prompt) > len(statement) + 200
    assert len(problems.texts) == 2 * len(problems.targets)
    print(f'Validated {len(problems.targets)} problem descriptions and complete AI prompt copy targets')


if __name__ == "__main__":
    main()
