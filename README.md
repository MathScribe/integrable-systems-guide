# Integrable Systems Research Guide

A compact research guide and AI-assisted research radar for integrable systems, inverse scattering transform, Riemann--Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

The site is a maintained reading radar rather than a same-day paper feed. The homepage shows a rolling selection from recent editions; weekly archive pages are the permanent recommendation record.

## Project principles

1. Keep the public navigation short.
2. Recommend a useful reading set rather than merely listing papers uploaded that day.
3. Treat the edition date as recommendation history, not as a publication-date claim.
4. Mix recent papers with missed papers, older high-relevance work, formal journal versions, group-adjacent work, and method/background papers when useful.
5. Prefer formal journal/DOI records for older work.
6. Keep current bibliographic facts separate from editorial recommendation history.
7. Treat AI-assisted curation as a discovery aid, not as mathematical verification.
8. Automate rendering and consistency checks, while keeping paper selection and annotation reviewable.

## Data and rendering model

- `data/papers.yml` stores current bibliographic metadata and stable identities.
- `data/editions.yml` stores recommendation dates, reading roles, homepage priority, and annotations.
- `scripts/render_radar.py` generates the homepage, weekly archives, archive index, and the short latest-compatibility page.
- `scripts/validate_radar.py` validates paper identities, edition references, roles, week numbers, homepage ranks, and the temporary `featured_on` compatibility mirror.

During the migration, `featured_on` remains in `data/papers.yml` as a compatibility mirror. `data/editions.yml` is the authoritative source for rendered recommendation history.

## Editorial workflow

1. Search current primary sources manually, including arXiv versions, DOI/journal records, author or group pages, references from current reading, and selected backlog material.
2. Deduplicate by arXiv ID, DOI, and normalized title against `data/papers.yml`.
3. Refresh the current full author list, title, source links, submission and revision dates, version, DOI, and journal information.
4. Select roughly 3--7 papers according to quality and research relevance.
5. Add edition entries with a stable role, an abstract-grounded “what it does” note, and a “why read” note.
6. Assign `homepage_rank` only to the small subset that should appear in the rolling homepage view.
7. Run the renderer and validators, review the complete diff, and open or update one pull request.
8. Keep the PR open for explicit owner review; do not merge or enable auto-merge without approval.

An existing arXiv ID is not recommended again merely because a new version appears. Its current metadata is refreshed in place. Metadata-only changes and new recommendations remain separate in the PR description.

## Current site structure

```text
docs/index.md                  # Rolling recommendations from recent editions
docs/radar/index.md            # Weekly archive index
docs/radar/latest.md           # Short compatibility pointer only
docs/radar/YYYY-WXX.md         # Permanent weekly files with dated editions
docs/resources.md              # Learning resources and search links
docs/group-work.md             # Local group-related links and public notes
docs/topics.md                 # Compact topic scope
docs/about.md                  # Site model, curation policy, metadata, AI use

data/papers.yml                # Current bibliographic metadata registry
data/editions.yml              # Recommendation history and annotations
scripts/render_radar.py        # Deterministic page renderer
scripts/validate_radar.py      # Registry and edition validation
.github/workflows/quality.yml  # Rendering checks and strict MkDocs build
```

Only files under `docs/` are published by MkDocs.

## Local preview

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_radar.py
python scripts/render_radar.py --check
mkdocs serve
```

## Publication phases

The current phase requires explicit owner review and merge approval. Automatic publication may be enabled only after the owner confirms that the reviewed process has been stable enough. CI success alone is not merge approval.

## License

Original site content and annotations are licensed under CC BY-SA 4.0. Configuration, scripts, and workflows are licensed under the MIT License. External resources remain under their original authors' or publishers' terms.
