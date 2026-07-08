# Integrable Systems Research Guide

A curated, annotated research guide for integrable systems, inverse scattering transform (IST), Riemann-Hilbert problems, nonlinear steepest descent, DNLS/NLS, nonlinear dispersive PDE, soliton resolution, and long-time asymptotic analysis.

This repository is not intended to be a generic awesome list. The goal is to maintain a reviewable research-training guide: every important resource should have a topic placement, learning use, prerequisites, quality assessment, and maintenance status.

## Project principles

1. Prefer researcher homepages, course pages, lecture notes, seminar pages, summer school pages, workshop pages, and open book drafts over disconnected PDF links.
2. Record why a resource is useful, not merely where it lives.
3. Track link health, archive status, version/date information, and known limitations.
4. Separate structured metadata from narrative reading guides.
5. Keep the initial core small and high quality before expanding.

## Repository structure

```text
docs/                 # Website/source guide pages in Markdown
docs/topics/          # Topic-level reading guides
docs/resources/       # Resource-type views: people, courses, workshops, notes, software
data/                 # Structured YAML metadata and seed candidates
maintenance/          # Link checks, review logs, dead links, and curation notes
.github/workflows/    # Optional GitHub Pages deployment workflow
```

## Local preview

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Then open the local URL printed by MkDocs.

## Curation status

This repository is currently at the scaffold stage. The first substantive milestone is `v0.1`: a small set of verified core resources with complete metadata and short annotations.

## License

License terms are not finalized yet. Until a license is added, do not assume permission to reuse the original annotations beyond normal GitHub viewing and contribution workflows. External resources remain governed by their original authors' terms.
