# Integrable Systems Research Guide

A compact research guide for integrable systems, inverse scattering transform, Riemann-Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

This repository is not intended to be a generic awesome list. The goal is to maintain a small research guide with stable links, local group context, and concise annotations.

## Project principles

1. Keep the public navigation short.
2. Prefer stable course pages, lecture notes, researcher homepages, search links, and public group materials over long unreviewed lists.
3. Record why a resource is included.
4. Separate external resources from local group-related material.
5. Expand only when there is enough reviewed material to justify a new page.

## Current site structure

```text
docs/index.md          # Homepage
docs/resources.md      # Learning resources, researcher/resource pages, search links
docs/group-work.md     # Local group-related links and public notes
docs/topics.md         # Compact topic scope
docs/about.md          # Curation policy, design references, comments, license notes

data/                  # Structured YAML metadata and seed candidates
maintenance/           # Link checks, review logs, dead links, and curation notes
.github/workflows/     # Optional GitHub Pages deployment workflow
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

License terms are not finalized yet. Until a license is added, do not assume permission to reuse the original annotations beyond normal GitHub viewing and contribution workflows. External resources remain governed by their original authors' terms.
