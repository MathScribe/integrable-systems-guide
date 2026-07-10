# Integrable Systems Research Guide

A compact research guide and AI-assisted research brief for integrable systems, inverse scattering transform, Riemann--Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

This repository is not intended to be a generic awesome list or an automated recommendation engine. The goal is to maintain a small research guide with stable links, concise annotations, transparent editorial choices, and a lightweight daily-brief workflow.

## Project principles

1. Keep the public navigation short.
2. Recommend a small number of papers that are useful for the current research directions.
3. A daily recommendation date does not imply that every paper was published that day.
4. Separate current bibliographic metadata from the site's recommendation history.
5. Treat AI-generated research briefs as discovery aids, not as mathematical verification.
6. Automate only mechanical validation; keep paper selection and annotation reviewable.

## Research-brief workflow

The brief is maintained editorially rather than by a scheduled paper-ranking action:

1. search recent papers and useful backlog items;
2. compare arXiv IDs and DOIs against `data/papers.yml`;
3. refresh the current title, author list, version, and update date for papers being considered or displayed;
4. select roughly 3--5 papers and write concise, abstract-based annotations;
5. update the daily page, weekly archive, homepage, and `data/papers.yml` in one pull request;
6. let GitHub Actions validate the registry and run `mkdocs build --strict`;
7. merge only after editorial review.

An existing arXiv ID is not recommended again merely because a new version appears. Its metadata is refreshed in place. `featured_on` records the site's historical recommendation date, while `authors`, `title`, `updated`, and `version` describe the current known record. Each editorial update should report new recommendations and metadata-only changes separately in the pull-request description.

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
.github/workflows/quality.yml   # Registry validation and strict MkDocs build
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
