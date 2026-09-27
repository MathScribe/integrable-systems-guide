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
                "javascripts/radar.js", "javascripts/group-papers.js"}
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


if __name__ == "__main__":
    main()
