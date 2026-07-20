# Integrable Systems Research Guide

A compact, AI-assisted research radar for integrable systems and related mathematical physics.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

The site is designed for researchers already familiar with integrable PDEs, spectral methods, and nonlinear waves. It selectively records recent papers whose integrable structure or integrability-driven result is sufficiently innovative to merit attention. It is neither an arXiv mirror nor a personalized reading list.

## Public model

- The homepage defaults to the latest ISO week.
- Readers can move between weeks or open a searchable cumulative view grouped by month.
- Each paper shows bibliographic metadata, official arXiv categories, at most two controlled structure tags, and a concise overview.
- Details expand into `研究问题与主要结果`, `可积结构与方法`, and `创新`.
- The homepage is the single paper browser; week navigation, search, and the cumulative view stay on that page.

## Authoritative data

- `data/papers.yml` stores one current bibliographic record per paper.
- `data/editions.yml` stores the cumulative `frontier` events and weekly summaries. Superseded reading-chain editions remain available through Git history rather than the active data file.
- `data/tags.yml` contains the controlled public structure-tag vocabulary.
- Generated Markdown in `docs/index.md` must not be edited by hand.

`frontier.checked_through` records the latest date for which the bounded discovery pass completed successfully. It is a maintenance checkpoint, not a public recommendation date.

One paper has one public frontier entry. When a selected preprint receives a qualifying major revision or its first formal journal publication, update its existing paper and frontier records rather than adding a duplicate card. Git history preserves the earlier state.

## Local Codex workflow

The canonical reusable prompt and maintenance instructions are in [maintenance/daily-radar-workflow.md](maintenance/daily-radar-workflow.md). The public-facing account of discovery, Crossref and publisher verification, selection, and annotation is in [docs/editorial-policy.md](docs/editorial-policy.md).

In short:

1. Discover recent candidates broadly; do not fill a quota.
2. Separate discovery from selection.
3. Verify selected candidates against primary sources.
4. Update structured YAML only.
5. Render pages deterministically.
6. Run the complete local check.
7. Inspect the diff and open one reviewable PR only when there is a real change.
8. Never merge or enable auto-merge without explicit owner approval.

Daily maintenance means checking every day, not publishing every day. Zero-paper days are valid. Old background papers, method primers, and missed backlog items do not enter the public radar merely to maintain output.

## Commands

```powershell
.venv\Scripts\python.exe scripts\render_radar.py
.venv\Scripts\python.exe scripts\check_project.py
.venv\Scripts\python.exe -m mkdocs serve
```

On macOS or Linux, use the active environment's `python` executable instead.

## Repository structure

```text
data/papers.yml                 Bibliographic registry and deduplication identities
data/editions.yml               Cumulative frontier entries and weekly summaries
data/tags.yml                   Controlled public structure tags

scripts/render_radar.py         Deterministic page renderer
scripts/validate_radar.py       Bibliographic identity validation
scripts/validate_frontier_data.py
                                 Frontier text and controlled-tag validation
scripts/test_radar.py           Radar component and dataset regression tests
scripts/check_project.py        Single local validation entry point

maintenance/daily-radar-workflow.md
                                 Canonical Codex discovery, selection, and PR procedure

docs/index.md                   Generated main radar page
docs/about.md                   Public explanation of scope and AI use
docs/editorial-policy.md        Public discovery, selection, event, and metadata policy
docs/resources.md               Curated external resources

.github/workflows/quality.yml   Pull-request validation
.github/workflows/deploy-mkdocs.yml
                                 GitHub Pages deployment after merge
```

## Editorial boundary

Thematic relevance is a broad gate; innovation strength is decisive. Integrable geometry, probability, random matrices, quantum many-body systems, statistical physics, gravity, and optics may be included when integrability is central to the conclusion. Public annotations use neutral, evidence-grounded language and do not publish negative assessments of papers that were not selected.

## Publication policy

CI success is not merge approval. Local Codex prepares a reviewable branch and PR; the owner decides whether to merge.

## License

Original site content and annotations are licensed under CC BY-SA 4.0. Configuration, scripts, and workflows are licensed under the MIT License. External resources remain under their original authors' or publishers' terms.
