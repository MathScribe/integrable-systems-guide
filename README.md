# Integrable Systems Research Guide

A compact research guide and AI-assisted research brief for integrable systems, inverse scattering transform, Riemann--Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

This repository is not intended to be a generic awesome list or an automated recommendation engine. The goal is to maintain a small research guide with stable links, concise annotations, transparent editorial choices, and a lightweight daily-brief workflow.

## Project principles

1. Keep the public navigation short.
2. Recommend a useful reading set rather than merely listing papers uploaded that day.
3. A daily recommendation date does not imply that every paper was published that day.
4. Mix recent papers with missed papers, older high-relevance work, formal journal versions, group-adjacent work, and useful method/background papers when the reading logic benefits from it.
5. Separate current bibliographic metadata from the site's recommendation history.
6. Treat AI-assisted research briefs as discovery aids, not as mathematical verification.
7. Automate only mechanical validation; keep paper selection and annotation reviewable.

## Research-brief workflow

The brief is maintained editorially rather than by a scheduled paper-ranking GitHub Action:

1. manually search current primary sources, including arXiv and version histories, journal/DOI records, author or research-group publication pages, references from current reading, and a small human-selected backlog;
2. compare arXiv IDs, DOIs, and titles against `data/papers.yml`;
3. refresh the current title, full author list, version, revision date, DOI, journal information, and source link for papers being considered or displayed;
4. select roughly 3--7 papers, with the number determined by quality rather than a fixed quota;
5. build a coherent reading set that may combine recent work, recently missed work, older high-relevance papers, formal journal versions, group-related work, and method/background papers; do not default to an arXiv-only list without an editorial reason;
6. write concise, abstract-based annotations explaining what each paper does and why it is worth reading now;
7. update the daily page, weekly archive, homepage, and `data/papers.yml` in one pull request;
8. let GitHub Actions validate registry identity fields, check that titles/authors/links agree across the registry and published pages, and run `mkdocs build --strict`;
9. review the complete pull-request diff before publication.

An existing arXiv ID is not recommended again merely because a new version appears. Its metadata is refreshed in place. `featured_on` records the site's historical recommendation date, while `authors`, `title`, `updated`, and `version` describe the current known record. Pull-request descriptions should list new recommendations and metadata-only changes separately.

When an arXiv abstract page and the latest versioned PDF disagree because of cache lag, use the latest versioned source/PDF for the current metadata and record the discrepancy in `metadata_note` or the pull-request description.

## Publication phases

The workflow is intentionally staged:

- **Current phase:** the assistant performs search, selection, editing, metadata refresh, PR review, and CI repair; the repository owner reviews the finished PR and gives explicit merge approval.
- **Later stable phase:** automatic merge/publication may be enabled only after the repository owner explicitly confirms that several editions have been consistently accurate and useful. CI success alone is never sufficient; the assistant must also complete the editorial review.

## Contributing

The easiest way to help is to open a GitHub Issue:

- use `Resource suggestion` for a useful course page, lecture note, survey, workshop page, researcher homepage, software page, or reading list;
- use `Paper suggestion` for a paper that should be considered for the research brief or long-term reading maps;
- use `Broken link` for a dead, moved, login-only, or outdated URL;
- open a pull request only if you want to edit files under `docs/` directly.

Short annotations and verified links are more useful at this stage than large unreviewed lists.

## Current site structure

```text
docs/index.md                  # Homepage and recent recommendations
docs/radar/latest.md           # Current research brief
docs/radar/index.md            # Research brief archive
docs/radar/YYYY-WXX.md         # Weekly files with dated entries
docs/resources.md              # Learning resources and search links
docs/group-work.md             # Local group-related links and public notes
docs/topics.md                 # Compact topic scope
docs/about.md                  # Curation policy, design references, AI use, license

data/papers.yml                # Published-paper deduplication and metadata registry
.github/workflows/quality.yml   # Registry/page consistency and strict MkDocs build
```

Only files under `docs/` are published by MkDocs.

## Local preview

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Then open the local URL printed by MkDocs.

## Curation status

This repository is in an early `v0.1` stage. The current goal is a clean, useful entry point rather than broad coverage.

## License

Original site content and annotations are licensed under CC BY-SA 4.0. Configuration and workflows are licensed under the MIT License.

External resources linked from this guide remain under their original authors' or publishers' terms.
