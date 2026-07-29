#!/usr/bin/env python3
"""Regression tests for bounded source discovery and editorial calibration."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


crossref = load_module("fetch_crossref_candidates", "scripts/fetch_crossref_candidates.py")
arxiv = load_module("fetch_arxiv_candidates", "scripts/fetch_arxiv_candidates.py")


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False


class FakeUrlOpen:
    def __init__(self, payloads: list[dict]):
        self.payloads = iter(payloads)
        self.urls: list[str] = []

    def __call__(self, request, timeout: int):
        self.urls.append(request.full_url)
        return FakeResponse(json.dumps(next(self.payloads)).encode("utf-8"))


class FailingUrlOpen:
    def __call__(self, request, timeout: int):
        raise TimeoutError("simulated source timeout")


def crossref_item(doi: str, title: str) -> dict:
    return {
        "DOI": doi,
        "title": [title],
        "author": [{"given": "Ada", "family": "Example"}],
        "container-title": ["Journal of Tests"],
        "publisher": "Test Publisher",
        "type": "journal-article",
        "created": {"date-parts": [[2026, 7, 28]]},
        "published-online": {"date-parts": [[2026, 7, 27]]},
        "URL": f"https://doi.org/{doi}",
    }


def crossref_config(queries: list[dict], *, workers: int = 1) -> dict:
    return {
        "schema_version": 1,
        "crossref": {
            "rows_per_page": 10,
            "concurrent_queries": workers,
            "timeout_seconds": 1,
            "max_retries": 0,
            "queries": queries,
        },
    }


def test_crossref_ranked_title_filter() -> None:
    query = {
        "id": "yang-baxter",
        "field": "title",
        "term": "Yang-Baxter",
        "patterns": [r"\bYang[-\s]+Baxter\b"],
    }
    fake = FakeUrlOpen(
        [
            {
                "message": {
                    "total-results": 2,
                    "items": [
                        crossref_item("10.1/relevant", "A Yang-Baxter construction"),
                        crossref_item("10.1/noise", "A Baxter lattice experiment"),
                    ],
                }
            }
        ]
    )
    manifest = crossref.fetch_manifest(
        crossref_config([query]),
        start="2026-07-27",
        end="2026-07-28",
        mailto=None,
        urlopen=fake,
        sleep=lambda _: None,
    )
    assert manifest["status"] == "complete"
    assert [item["doi"] for item in manifest["candidates"]] == ["10.1/relevant"]
    assert len(fake.urls) == 1
    assert "from-online-pub-date%3A2026-07-27" in fake.urls[0]


def test_crossref_deduplication_and_failure_degradation() -> None:
    queries = [
        {
            "id": "integrability",
            "field": "title",
            "term": "integrable",
            "patterns": [r"\bintegrable\b"],
        },
        {
            "id": "lax",
            "field": "title",
            "term": "Lax",
            "patterns": [r"\bLax\s+pairs?\b"],
        },
    ]
    duplicate = crossref_item("10.1/same", "Integrable model with a Lax pair")
    fake = FakeUrlOpen(
        [
            {"message": {"total-results": 1, "items": [duplicate]}},
            {"message": {"total-results": 1, "items": [duplicate]}},
        ]
    )
    manifest = crossref.fetch_manifest(
        crossref_config(queries),
        start="2026-07-27",
        end="2026-07-28",
        mailto=None,
        urlopen=fake,
        sleep=lambda _: None,
    )
    assert manifest["candidate_count"] == 1
    assert manifest["candidates"][0]["matched_queries"] == ["integrability", "lax"]

    failed = crossref.fetch_manifest(
        crossref_config(queries[:1]),
        start="2026-07-27",
        end="2026-07-28",
        mailto=None,
        urlopen=FailingUrlOpen(),
        sleep=lambda _: None,
    )
    assert failed["status"] == "partial"
    assert failed["failed_query_count"] == 1
    assert failed["candidate_count"] == 0


def test_arxiv_dates_and_cross_category_deduplication() -> None:
    template = """
    <h3>Tue, 28 Jul 2026 (showing 1 of 1 entries)</h3>
    <dl>
      <dt><a href="/abs/2607.23422">arXiv:2607.23422</a>{cross_list}</dt>
      <dd><div class="meta">
        <div class="list-title mathjax"><span>Title:</span>Loop Algebra Splitting</div>
        <div class="list-authors"><a>Ziqi Li</a>, <a>Zhiwei Wu</a></div>
        <div class="list-subjects"><span>Subjects:</span>
          Mathematical Physics (math-ph); Exactly Solvable and Integrable Systems (nlin.SI)
        </div>
      </div></dd>
    </dl>
    <h3>Mon, 27 Jul 2026 (showing 0 of 0 entries)</h3>
    """
    pages = {
        "nlin.SI": template.format(cross_list=""),
        "math-ph": template.format(cross_list=" (cross-list from nlin.SI)"),
    }

    def fake_urlopen(request, timeout: int):
        category = request.full_url.split("/list/", 1)[1].split("/", 1)[0]
        return FakeResponse(pages[category].encode("utf-8"))

    manifest = arxiv.fetch_manifest(
        ["nlin.SI", "math-ph"],
        start="2026-07-27",
        end="2026-07-28",
        urlopen=fake_urlopen,
    )
    assert manifest["status"] == "complete"
    assert manifest["candidate_count"] == 1
    candidate = manifest["candidates"][0]
    assert candidate["announcement_date"] == "2026-07-28"
    assert candidate["source_categories"] == ["math-ph", "nlin.SI"]
    assert candidate["authors"] == ["Ziqi Li", "Zhiwei Wu"]

    partial = arxiv.fetch_manifest(
        ["nlin.SI"],
        start="2026-07-15",
        end="2026-07-28",
        urlopen=lambda request, timeout: FakeResponse(
            b"<h3>Tue, 28 Jul 2026 (showing 0 of 0 entries)</h3>"
        ),
    )
    assert partial["status"] == "partial"


def test_frozen_editorial_calibration_set() -> None:
    data = yaml.safe_load(
        (ROOT / "maintenance" / "radar-calibration.yml").read_text(encoding="utf-8")
    )
    candidates = data["candidates"]
    assert data["schema_version"] == 1
    assert len(candidates) == 17
    assert len({item["id"] for item in candidates}) == 17
    assert all(
        data["window"]["from"] <= item["event_date"] <= data["window"]["until"]
        for item in candidates
    )
    counts = {
        decision: sum(item["decision"] == decision for item in candidates)
        for decision in {"selected", "excluded", "borderline"}
    }
    assert counts == {"selected": 6, "excluded": 9, "borderline": 2}


def main() -> None:
    test_crossref_ranked_title_filter()
    test_crossref_deduplication_and_failure_degradation()
    test_arxiv_dates_and_cross_category_deduplication()
    test_frozen_editorial_calibration_set()
    print("bounded discovery and editorial calibration tests passed")


if __name__ == "__main__":
    main()
