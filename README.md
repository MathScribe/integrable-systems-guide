# Integrable Systems Research Guide

A compact research guide and AI-assisted research radar for integrable systems, inverse scattering transform, Riemann-Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

This repository is not intended to be a generic awesome list. The goal is to maintain a small research guide with stable links, local group context, concise annotations, and a lightweight research-brief workflow.

## Project principles

1. Keep the public navigation short.
2. Prefer stable course pages, lecture notes, researcher homepages, search links, and public group materials over long unreviewed lists.
3. Record why a resource is included.
4. Separate external resources from local group-related material.
5. Expand only when there is enough reviewed material to justify a new page.
6. Treat AI-generated research briefs as discovery aids, not as mathematical verification.

## Contributing

The easiest way to help is to open a GitHub Issue:

- use `Resource suggestion` for a useful course page, lecture note, survey, workshop page, researcher homepage, software page, or reading list;
- use `Paper suggestion` for a paper that should be considered for the research radar or long-term reading maps;
- use `Broken link` for a dead, moved, login-only, or outdated URL;
- open a pull request only if you want to edit files under `docs/` directly.

Short annotations and verified links are more useful at this stage than large unreviewed lists.

## Current site structure

```text
docs/index.md                  # Homepage and latest daily research brief summary
docs/radar/latest.md           # Fixed latest research brief page
docs/radar/index.md            # Research brief archive
docs/radar/YYYY-WXX.md         # Weekly files with daily entries
docs/resources.md              # Learning resources, researcher/resource pages, search links
docs/group-work.md             # Local group-related links and public notes
docs/topics.md                 # Compact topic scope
docs/about.md                  # Curation policy, design references, comments, license notes

data/papers.yml                # Canonical paper registry for deduplication and later reading maps
data/                          # Structured YAML metadata and seed candidates
maintenance/                   # Link checks, review logs, dead links, and curation notes
.github/workflows/             # Optional GitHub Pages deployment workflow
```

Only files under `docs/` are published by MkDocs. Legacy scaffold pages were removed from `docs/` so that they do not appear in the website search index.

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

Original site content and annotations are licensed under CC BY-SA 4.0. Code, scripts, configuration, and workflows are licensed under the MIT License.

External resources linked from this guide remain under their original authors' or publishers' terms.
