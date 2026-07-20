# Local Codex daily radar prompt and workflow

This file is the canonical operating procedure for maintaining the research radar from a local Codex workspace. Repository documentation, local execution, and future scheduled tasks must follow this file rather than reconstructing policy from chat history.

## Objective

Maintain a cumulative, innovation-focused radar for researchers familiar with integrable PDEs, spectral methods, and related mathematical physics.

Run discovery every day, but publish only qualifying research events. Zero-paper days are acceptable. Do not create a reading chain, fill a quota, or add old background papers merely to produce an update.

## Accepted research events

- `new-preprint`: first public release of a new preprint;
- `major-revision`: a revision adding a main theorem, core method, experiment, substantial new analysis, or a material change to the main conclusion;
- `journal-publication`: first formal online journal publication.

Routine wording, bibliography, formatting, author-order, metadata, and minor-correction updates are not major revisions.

## Daily discovery

Discovery and selection are separate stages.

1. Read `data/papers.yml`, `data/editions.yml`, and this file before searching.
2. Use `frontier.checked_through` as the last successful coverage date. Search from that date through the current date, with a short overlap when practical so delayed announcements are not missed.
3. Check complete recent coverage of arXiv `nlin.SI` and `nlin.PS`.
4. Run bounded cross-category searches in mathematical physics, probability, geometry, combinatorics, quantum many-body physics, statistical physics, gravity, optics, and related areas.
5. Use both structure terms and result terms. Useful result terms include classification, arbitrary-order families, asymptotics, transition regimes, inverse problems, control, tomography, exact distributions, transport, topology, experiments, and data-driven integrability.
6. Author, group, and specialist pages may be used for manual gap checking. Do not mirror or ingest their feeds.

Discovery should favor recall: uncertain candidates may remain in the working notes, but discovery alone never authorizes publication.

## Weekly publication check

At least once per ISO week:

1. query Crossref by the target publication window and bounded structure terms;
2. query Crossref by exact title and author for selected or previously registered arXiv papers that do not yet have verified journal metadata;
3. inspect the Latest articles or Online first pages of relevant journals for records that Crossref may not yet expose reliably;
4. open the DOI target on the publisher site and verify the full journal name, author list, volume, issue, pages or article number, and first online publication date;
5. distinguish first online publication from later issue assignment, which is not a new research event;
6. review whether a source outage or narrow query caused an obvious coverage gap.

General web search may be used with exact-title, site-restricted, structure-term, and `published online` queries to find missing candidates. It is a gap-checking tool, not final evidence. Google Scholar is not required and must not be treated as a complete or stable automated source.

For every strong daily candidate, DOI and publication metadata should still be checked immediately; the weekly pass is the systematic backstop.

## Selection

Thematic relevance is a broad gate; innovation strength is decisive. Apply the same field-wide criteria to every candidate.

Internally ask:

1. Does the paper introduce, reveal, or substantially extend an integrable structure or method?
2. If not, does an existing integrable structure indispensably produce a clear, systematic, nontrivial innovation?

A paper may pass when either answer is clearly yes. Examples include a new classification, an arbitrary-order or arbitrary-parameter family, a new asymptotic regime or critical transition, a new topology or geometry mechanism, a new inverse/control/experimental method, a new statistical or transport structure, or a genuinely new application in which integrability is central.

Do not select a paper when integrability is incidental, method transfer is routine, the result is limited to a few low-order examples or parameter plots, or the innovation cannot be explained reliably from primary sources.

These are internal selection rules. Public pages and PR descriptions must not publish negative paper-by-paper judgments.

## Verification and identity

Before editing data:

- deduplicate by arXiv ID, DOI, and normalized title;
- verify the title and full author list;
- verify the event date and event type;
- verify the current arXiv version, submission date, revision date, and official categories when applicable;
- verify the abstract and the specific statements supporting the annotation;
- verify DOI, journal name, volume, issue, pages or article number, year, and first online publication date when applicable;
- use arXiv, the paper PDF, DOI records, and publisher pages as final evidence.

Keep bibliographic timestamps separate from the public event date. For an arXiv `new-preprint`, preserve the UTC submission timestamp in `papers.yml`, but use the official arXiv listing's announcement date as `signal_date`; this is the date on which the paper enters the public radar and determines its ISO week. For a `major-revision`, use the official replacement-list date. For a `journal-publication`, use the publisher's first-online date. The Beijing-time scan timestamp is operational metadata and never changes the public event date.

arXiv normally has no Friday or Saturday announcements. A paper submitted before the Friday 14:00 US Eastern cutoff can therefore carry a Friday UTC submission date while appearing in the following Monday category list. Preserve both dates and let the rendered card explain the distinction whenever they differ.

`data/papers.yml` contains one current bibliographic record per paper. Do not create separate arXiv and DOI records for the same work.

`data/editions.yml` contains one public `frontier` entry per paper. If a selected paper later has a qualifying major revision or first journal publication, update the existing paper and frontier entries:

- retain the original arXiv ID and submission date;
- add or refresh journal metadata;
- change `signal_type` and `signal_date` to the new qualifying event;
- update the annotation only where the new event changes the result;
- do not append a duplicate public card.

Git history preserves the earlier event state.

## Data entry

For every selected paper, maintain in `frontier.entries`:

- `paper_id`;
- `signal_date`;
- `signal_type`;
- `week`;
- up to two official arXiv categories when applicable;
- at most two structure tags selected from `data/tags.yml` under `frontier_structure_tags`;
- `summary`: a compact but intelligible overview for deciding whether to read;
- `main_result`: 研究问题与主要结果;
- `integrable_structure`: 可积结构与方法;
- `innovation`: 创新，即相对于已有工作的具体新增内容，不作宣传性推断。

Derive `week` from `signal_date`; do not derive it from the arXiv UTC submission timestamp or from the local scan date.

The four prose fields have different jobs:

- `summary` compresses the research object, main result, and most notable point into two or three readable sentences;
- `main_result` explains the question, the hierarchy of results, and the analytical, numerical, or experimental evidence;
- `integrable_structure` explains what the integrable structure actually does in the argument rather than listing method names;
- `innovation` states the source-supported comparison with prior scope or capability.

Do not reuse a complete sentence across fields. In particular, `main_result` must not repeat `summary`, and `innovation` must not merely restate the last sentence of either field. When only an abstract has been checked, keep the annotation within what the abstract supports; inspect the PDF before adding formula-level mechanisms, proof details, priority claims, or comparisons that are not explicit in the abstract.

After a successful complete discovery run, advance `frontier.checked_through` even when no paper is selected. A check-only change does not need its own daily PR; carry the date forward with the next content change or the weekly maintenance PR.

Do not use public contribution classes such as core/adjacent or structure advance. Do not add per-paper `自动整理` badges, BibTeX buttons, recommendation dates, title-fragment tags, or invented terminology.

For the current ISO week, create or update exactly one `frontier_weeks` record containing:

- `id` and `date_range`;
- one concise, non-repetitive weekly `summary`;
- the current `selected` count;
- source types actually checked and any material coverage limitation.

The public homepage displays only the current week's short overview in weekly mode and hides weekly overviews in the cumulative view.

## Rendering and validation

Never hand-edit generated radar pages.

After changing YAML:

```powershell
.venv\Scripts\python.exe scripts\render_radar.py
.venv\Scripts\python.exe scripts\check_project.py
```

The complete check validates identities, frontier fields, controlled tags, generated-page consistency, JavaScript syntax, and `mkdocs build --strict`.

Inspect the full diff after rendering. Remove annotation residue, repeated prose, temporary helpers, logs, generated preview directories, and diagnostics before review.

## Pull-request policy

- Create or update one reviewable PR only when there are qualifying events or necessary metadata/site corrections.
- Do not create an empty PR.
- Separate new research events, metadata-only corrections, sources checked, and unresolved uncertainty in the PR description.
- Never merge the PR and never enable auto-merge.
- Present the finished PR for explicit owner approval.
- A temporary infrastructure failure must not disable, delete, or reschedule the maintenance procedure.

## Suggested local invocation

Use this file as the canonical prompt. A daily task only needs the short invocation:

> 按 `maintenance/daily-radar-workflow.md` 完成今天的研究雷达检查。先广覆盖发现，再筛选和核验；有实际变更才准备 PR，不要合并。
