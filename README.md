# Integrable Systems Research Guide

A compact, annotated research-training guide for integrable systems, inverse scattering transform, Riemann-Hilbert problems, nonlinear steepest descent, nonlinear waves, finite-gap methods, and related spectral/geometric techniques.

This repository is not intended to be a generic awesome list. The goal is to maintain a reviewable research guide: important resources should have a clear mathematical role, learning use, prerequisites, quality assessment, and maintenance status.

## Project principles

1. Keep the public navigation small until there is enough reviewed material to justify more pages.
2. Prefer researcher homepages, course pages, lecture notes, seminar pages, summer school pages, workshop pages, and open book drafts over disconnected PDF links.
3. Record why a resource is useful, not merely where it lives.
4. Track link health, archive status, version/date information, and known limitations.
5. Separate external curated resources from public group/member material.

## Current site structure

```text
docs/index.md          # Homepage
docs/start-here.md     # Usage rules, resource levels, quality grades
docs/routes.md         # Short research-training routes
docs/topics.md         # Compact topic map
docs/resources.md      # Main consolidated resource table
docs/group-work.md     # Public group/member material
docs/about.md          # Curation policy, inspiration, comments, license notes

docs/*/                # Older scaffold pages kept as source material
data/                  # Structured YAML metadata and seed candidates
maintenance/           # Link checks, review logs, dead links, and curation notes
.github/workflows/     # Optional GitHub Pages deployment workflow
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

This repository is in an early `v0.1` stage. The first substantive milestone is a small set of verified core resources with short annotations, plus a clean site structure that can later support group reading projects and richer metadata.

## License

License terms are not finalized yet. Until a license is added, do not assume permission to reuse the original annotations beyond normal GitHub viewing and contribution workflows. External resources remain governed by their original authors' terms.
