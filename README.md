# Integrable Systems Research Radar

A selective, AI-assisted radar for recent research in integrable systems and related mathematical physics.

**Public site:** https://mathscribe.github.io/integrable-systems-guide/

The radar is designed for researchers familiar with integrable PDEs, spectral methods, nonlinear waves, and adjacent areas of mathematical physics. It highlights recent papers in which integrability is central to a substantive new structure, method, or result. It is neither a comprehensive literature database nor a personalized reading list.

## What the site provides

- The homepage defaults to the latest ISO week.
- Readers can browse earlier weeks or switch to a searchable cumulative view grouped by month.
- Each paper card includes verified bibliographic metadata, official arXiv categories, up to two controlled structure tags, and a concise overview.
- Expandable notes explain the research question and main results, the role of the integrable structure and methods, and the paper's specific advance over prior work.
- New preprints, qualifying major revisions, and first formal journal publications are treated as distinct research events.

The radar is checked daily, but publication is event-driven: there is no daily or weekly quota, and a completed screening pass may select no papers.

## Editorial approach

Discovery is intentionally broad; inclusion is selective. Thematic relevance is only the first gate. A paper is included when its integrable structure plays a substantive role and the source material supports a clear, nontrivial advance.

AI assists with candidate discovery, deduplication, metadata cleanup, initial screening, annotation drafting, page generation, and consistency checks. Primary sources are used for verification, every repository change remains reviewable, and the maintainer retains editorial and merge responsibility. Public annotations summarize the available evidence; they do not independently validate mathematical proofs or priority claims.

## Authoritative data

- `data/papers.yml` stores one current bibliographic record per paper.
- `data/editions.yml` stores the cumulative `frontier` events and weekly summaries. Superseded reading-chain editions remain available through Git history rather than the active data file.
- `data/tags.yml` contains the controlled public structure-tag vocabulary.
- Generated Markdown in `docs/index.md` must not be edited by hand.

`maintenance/radar-state.yml` records independent source watermarks. Public
event dates remain in `data/editions.yml`; a source watermark advances only
after that source's bounded discovery pass completes successfully.

One paper has one public frontier entry. When a selected preprint receives a qualifying major revision or its first formal journal publication, update its existing paper and frontier records rather than adding a duplicate card. Git history preserves the earlier state.

## Maintenance workflow

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

## Scope

The radar covers integrable systems broadly. Integrable geometry, probability, random matrices, quantum many-body systems, statistical physics, gravity, and optics may be included when integrability is central to the main conclusion. Public annotations use neutral, evidence-grounded language and do not publish paper-by-paper assessments of work that was not selected.

## Publication policy

CI success is not merge approval. Local Codex prepares a reviewable branch and PR; the owner decides whether to merge.

## License

Original site content and annotations are licensed under CC BY-SA 4.0. Configuration, scripts, and workflows are licensed under the MIT License. External resources remain under their original authors' or publishers' terms.
