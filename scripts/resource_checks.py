"""Shared link inventory and offline validation for source Markdown and YAML."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
import yaml

from validate_radar import validate_url


@dataclass(frozen=True)
class Link:
    source: str
    field: str
    url: str


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        if tag in {'a', 'img'}:
            url = values.get('href' if tag == 'a' else 'src')
            if url is not None:
                self.urls.append(url)


def parse_markdown(path: Path) -> Links:
    parser = Links()
    parser.feed(markdown.markdown(path.read_text(encoding='utf-8'), extensions=['extra', 'toc']))
    return parser


def inventory(root: Path) -> list[Link]:
    for directory in ('docs', 'data'):
        if not (root / directory).is_dir():
            raise ValueError(f'{root / directory}: missing source directory')
    links = []
    for path in sorted((root / 'docs').rglob('*.md')):
        links.extend(Link(path.relative_to(root).as_posix(), 'href', url) for url in parse_markdown(path).urls)

    def walk(value, source, field):
        if isinstance(value, dict):
            label = value.get('id') or value.get('paper_id')
            if label:
                field += f'[{label}]'
            for key, child in value.items():
                child_field = f'{field}.{key}'
                if key in {'url', 'homepage', 'event_source'} and child is not None:
                    links.append(Link(source, child_field, child))
                else:
                    walk(child, source, child_field)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, source, f'{field}[{index}]')

    for path in sorted((root / 'data').glob('*.yml')):
        walk(yaml.safe_load(path.read_text(encoding='utf-8')), path.relative_to(root).as_posix(), '$')
    return links


def validate_links(root: Path) -> list[str]:
    errors = []
    anchors = {}
    docs = (root / 'docs').resolve()
    for link in inventory(root):
        label = f'{link.source}:{link.field}'
        try:
            if not isinstance(link.url, str) or not link.url.strip():
                raise ValueError(f'{label}: empty or non-string link')
            parts = urlsplit(link.url)
            if parts.scheme in {'http', 'https'}:
                validate_url(link.url, label)
            elif parts.scheme == 'mailto':
                if '@' not in parts.path or any(c.isspace() for c in link.url):
                    raise ValueError(f'{label}: malformed mailto link')
            elif parts.scheme or parts.netloc or not link.source.endswith('.md'):
                raise ValueError(f'{label}: unsupported or missing link scheme: {link.url}')
            else:
                target = (root / link.source).parent / unquote(parts.path) if parts.path else root / link.source
                target = target.resolve()
                if not target.is_relative_to(docs):
                    raise ValueError(f'{label}: link escapes docs: {link.url}')
                if target.is_dir():
                    target = target / 'index.md'
                elif not target.exists() and not target.suffix and target.with_suffix('.md').is_file():
                    target = target.with_suffix('.md')  # MkDocs directory-style URLs.
                if not target.is_file():
                    raise ValueError(f'{label}: missing local target: {link.url}')
                if parts.fragment and target.suffix == '.md':
                    if target not in anchors:
                        anchors[target] = parse_markdown(target).ids
                    if unquote(parts.fragment) not in anchors[target]:
                        raise ValueError(f'{label}: missing anchor: {link.url}')
        except ValueError as exc:
            errors.append(str(exc))
    return errors
