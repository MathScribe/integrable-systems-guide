"""Check changed journal bibliography against the last release under the old policy."""
import argparse
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

import yaml

from audit_resources import Client
from validate_radar import normalize_doi, parse_date, validate_url

ROOT = Path(__file__).resolve().parents[1]
# Historical cards retain the evidence and precision available when published.
POLICY_BASE = "b41ab566c308e3ecc3d48a7d1535850b12087ba4"
CITATION_FIELDS = ("title", "authors", "doi", "journal", "year", "published",
                   "volume", "issue", "pages", "article_number", "first_online_evidence")


def load_records(revision=None):
    def read(name):
        if revision:
            raw = subprocess.check_output(["git", "show", f"{revision}:data/{name}.yml"], cwd=ROOT)
        else:
            raw = (ROOT / "data" / f"{name}.yml").read_bytes()
        return yaml.safe_load(raw)

    return ({p["id"]: p for p in read("papers")},
            {e["paper_id"]: e for e in read("editions")["frontier"]["entries"]})


def release_errors(previous, current):
    old_papers, old_entries = previous
    papers, entries = current
    errors = []
    for key, paper in papers.items():
        entry = entries.get(key, {})
        journal_event = entry.get("signal_type") == "journal-publication"
        if paper.get("status") in {"withdrawn", "retracted"}:
            continue
        if not (journal_event or paper.get("journal") or paper.get("doi") or paper.get("published")):
            continue
        old = old_papers.get(key, {})
        if old_entries.get(key, {}) == entry and all(old.get(k) == paper.get(k) for k in CITATION_FIELDS):
            continue
        missing = [k for k in ("title", "authors", "doi", "journal", "year") if not paper.get(k)]
        try:
            parse_date(paper.get("published"), "first-online date")
        except ValueError:
            missing.append("exact published date (YYYY-MM-DD)")
        if journal_event and (not entry.get("signal_date") or entry["signal_date"] != paper.get("published")):
            missing.append("journal signal_date matching published")
        evidence = paper.get("first_online_evidence")
        if not isinstance(evidence, dict):
            evidence = {}
        try:
            validate_url(evidence.get("url"), "date source")
        except ValueError:
            missing.append("first_online_evidence.url")
        if not isinstance(evidence.get("statement"), str) or not evidence["statement"].strip():
            missing.append("first_online_evidence.statement (source date label and value)")
        if not paper.get("published") or evidence.get("date") != paper.get("published"):
            missing.append("first_online_evidence.date matching published")
        # Some publishers omit issues or publish ahead of volume/page assignment.
        absent = {field for field in ("volume", "issue") if not str(paper.get(field) or "").strip()}
        if not any(str(paper.get(field) or "").strip() for field in ("pages", "article_number")):
            absent.add("locator")
        unassigned = evidence.get("unassigned", [])
        if not isinstance(unassigned, list) or not all(isinstance(v, str) for v in unassigned):
            missing.append("first_online_evidence.unassigned must list unassigned citation fields")
        elif set(unassigned) != absent:
            missing.append("supply assigned citation fields or confirm unassigned: " + str(sorted(absent)))
        if missing:
            errors.append(f"{key} | {paper.get('title')} | " + ", ".join(missing))
    return errors


def lookup(client, doi):
    doi = normalize_doi(doi)
    publisher = "https://doi.org/" + doi
    url = "https://api.crossref.org/works/" + quote(doi, safe="/")
    validate_url(publisher, "DOI")
    print(f"Publisher browser link: {publisher}")
    print(f"Crossref deposit: {url}")
    response = client.get(url)
    if not response.get("body"):
        raise ValueError(f"Crossref unavailable: {response.get('error', response.get('status'))}")
    item = json.loads(response["body"])["message"]
    if normalize_doi(item["DOI"]) != doi or item.get("type") != "journal-article":
        raise ValueError("DOI or journal-article identity mismatch")
    for field in ("title", "author", "container-title", "volume", "issue", "page",
                  "article-number", "published-online", "published-print", "issued", "resource", "link"):
        if field in item:
            print(f"{field}: {json.dumps(item[field], ensure_ascii=False)}")
    parts = item.get("published-online", {}).get("date-parts") or [[]]
    if len(parts[0]) != 3:
        print("Exact online date missing from deposit. Inspect article history or publisher PDF in browser.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookup", metavar="DOI", action="append", help="look up a specific journal DOI")
    args = parser.parse_args()
    if args.lookup:
        client = Client(ROOT / ".radar-audit/http-cache")
        failures = []
        for doi in args.lookup:
            try:
                lookup(client, doi)
            except (ValueError, KeyError) as exc:
                failures.append(f"{doi}: {exc}")
        if failures:
            raise SystemExit("\n".join(failures))
        return
    errors = release_errors(load_records(POLICY_BASE), load_records())
    if errors:
        raise SystemExit("Publication on hold for this batch:\n" + "\n".join(errors))
    print("Journal bibliography release check passed.")


if __name__ == "__main__":
    main()
