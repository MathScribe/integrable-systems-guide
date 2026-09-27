# Local Codex daily radar prompt and workflow

This file is the canonical operating procedure for maintaining the research radar from a local Codex workspace. Repository documentation, local execution, and future scheduled tasks must follow this file rather than reconstructing policy from chat history.

## Objective

Maintain a cumulative radar focused on integrable nonlinear waves, inverse scattering, spectral methods and concrete new directions connected to these research interests.

Run discovery every day, but publish only qualifying research events. Zero-paper days are acceptable. Do not create a reading chain, fill a quota, or add old background papers merely to produce an update.

## Accepted research events

- `new-preprint`: first public release of a new preprint;
- `major-revision`: a revision adding a main theorem, core method, experiment, substantial new analysis, or a material change to the main conclusion;
- `journal-publication`: first formal online journal publication.

Routine wording, bibliography, formatting, author-order, metadata, and minor-correction updates are not major revisions.

## Daily discovery

Discovery and selection are separate stages.

1. Read `data/papers.yml`, `data/editions.yml`,
   `maintenance/radar-state.yml`, `maintenance/radar-selection-policy.md`, and
   this file before searching.
2. Determine each discovery interval from that source's last successful
   watermark in `maintenance/radar-state.yml`. Never infer Crossref or
   publisher coverage from the latest public paper date.
3. Check arXiv `nlin.SI` and `nlin.PS` new and replacement listings separately.
   Use official dated Catchup pages for missing recent batches (up to90 days),
   saving raw evidence and checking page dates and complete entry counts with
   `scripts/fetch_arxiv_catchup.py`. Catchup excludes journal-reference-only
   updates and replacements beyond v5; inspect current version histories for
   selected/high-priority papers to cover known risks outside those listings.
4. Run bounded cross-category searches for concrete connections to the research focus in mathematical physics, probability, geometry, quantum theory, optics and related areas. Broad discovery is not a promise to cover each field comprehensively.
5. Use both structure terms and result terms. Useful result terms include classification, arbitrary-order families, asymptotics, transition regimes, inverse problems, control, tomography, exact distributions, transport, topology, experiments, and data-driven integrability.
6. Author, group, and specialist pages may be used for manual gap checking. Do not mirror or ingest their feeds.

Discovery should favor recall: uncertain candidates may remain in the working notes, but discovery alone never authorizes publication.

Record the run's actual queries, source status, candidates, evidence depth, and
decision in a local audit artifact. A source failure is not a zero-result run and
must not advance that source's watermark.

Read `maintenance/radar-candidates.yml` before new discovery. Resolve concrete
pending checks without redoing the completed broad search. Record titles, full
authors, primary links, last-check date and next action for unresolved candidates.
Remove resolved items from the queue; detailed exclusion judgments stay private.
Close current-run exclusions and owner-deferred historical items in the private
audit instead of keeping them in an active retry queue. Missing optional journal
metadata alone is not an unresolved candidate; reconcile it opportunistically.

For every journal-only candidate that reaches detailed review, also record the
venue authority tier (`A`, `B`, or `C`) and the evidence supporting that tier,
using `maintenance/radar-selection-policy.md`. Venue tier is internal editorial
evidence, never a public label, and never replaces the content threshold.

## Weekly publication check

At least once per ISO week:

1. run the configured Crossref ranked-title backstop over an overlapping
   first-online window, and the separate five-phrase registered-DOI pass using
   `--date-basis created`. Keep their statuses and watermarks independent. A DOI
   creation timestamp can reveal a paper but never establish its publication date.
   Preserve year/month date precision; never fill an unknown day with the first.
   Do not paginate broad terms as if mirroring Crossref;
2. query Crossref by exact title and author for recently selected or previously
   registered arXiv papers that do not yet have verified journal metadata;
3. inspect publisher pages only for strong candidates, known metadata conflicts,
   or a documented high-risk source gap; do not enumerate journal homepages as
   the primary discovery method;
4. verify journal bibliography using publisher records or publisher-deposited Crossref metadata; inspect the DOI target for material conflicts or claims beyond that evidence. An unavailable publisher page does not require repeated retries;
5. distinguish first online publication from later issue assignment, which is not a new research event;
6. review whether a source outage or narrow query caused an obvious coverage gap.

General web search may be used with exact-title, site-restricted, structure-term, and `published online` queries to find missing candidates. It is a gap-checking tool, not final evidence. Google Scholar is not required and must not be treated as a complete or stable automated source.

For every strong daily candidate, DOI and publication metadata should still be checked immediately; the weekly pass is the systematic backstop.

Crossref and publisher checks have independent state. The Crossref title pass is
a selective backstop, not a claim that every Crossref record was inspected.
Its failure must not block publication of already verified arXiv events, and a
successful arXiv run must not be described as successful Crossref coverage.
Prefer the latest successful artifact from the repository's weekly Crossref
backstop workflow. Do not make the interactive daily run wait repeatedly on an
unresponsive Crossref endpoint.

## Biweekly mathematics-index check

Every two weeks, use the configured zbMATH backstop to catch journal papers that
may lack a strong title phrase:

1. query only journal articles from the current and next issue years in the
   configured integrable-systems MSC classes, catching next-year issue assignments
   that are already online; this does not make the issue year an event date;
2. exhaust the bounded result set up to the configured hard cap, then retain
   only records newly indexed inside the overlapping datestamp window;
3. apply the same cheap relevance filter and strict value threshold used for
   other sources;
4. verify each surviving DOI from the publisher or its Crossref deposit. Use a
   known first-online date; an unknown date stays null under the bibliography-first rule.

This pass is deliberately based on mathematical classification rather than a
journal whitelist. Its successful status means the bounded MSC query completed;
it does not mean all of zbMATH or every mathematics journal was inspected.

## Selection

Apply the focused research and useful-new-direction tests in policy version 2 consistently. Judge both relevance and the concrete advance; do not substitute a field label, author name or journal prestige for either.

Use `maintenance/radar-selection-policy.md` as the detailed, versioned editorial
contract. Freshness, identity, and non-duplication are hard eligibility gates.
There is no fixed daily or weekly count, minimum, or maximum.

Internally ask:

1. Does the paper make a substantive advance on a problem, model or method directly relevant to the research focus?
2. If not, does it establish a concrete new methodological or problem connection worth following from that focus?

A paper may pass when either answer is clearly yes. Relevant well-posedness, stability and asymptotic results are eligible alongside new integrable structures, inverse methods and statistical or experimental connections. The new contribution must be explainable from primary evidence.

Do not select a paper when integrability is incidental, method transfer is routine, the result is limited to a few low-order examples or parameter plots, or the innovation cannot be explained reliably from primary sources.

These are internal selection rules. Public pages and PR descriptions must not publish negative paper-by-paper judgments.

## Verification and identity

For papers already saved by the owner, check Zotero's local attachments before
declaring abstract/full-text evidence unavailable. Read local PDFs or saved
publisher snapshots without modifying the Zotero library. For publisher access,
prefer the owner's local campus-network route; GitHub's proxy instructions do
not prescribe a publisher-access route. Do not change system proxy or network
components without confirmation. If evidence is still inaccessible, report the
exact title/DOI and ask the owner for the local attachment path instead of
repeated fetches or an unnecessary alternate card design. A failed fetch means
the agent could not retrieve the evidence, not that the paper lacks it.

Before editing data:

- deduplicate by arXiv ID, DOI, and normalized title;
- verify the title and full author list;
- verify the event type and available event date; preserve unknown journal dates as null;
- verify the current arXiv version, submission date, revision date, and official categories when applicable;
- check withdrawal/retraction banners and version comments explicitly. Retain a
  withdrawn/retracted bibliographic record with its status, but remove it from
  the public selection and report the exact title, authors and primary evidence;
- verify the abstract and specific statements supporting any annotation; omit the
  reading note when only reliable bibliography is available;
- verify DOI, journal name, volume, issue, pages or article number, year, and first online publication date when applicable;
- use arXiv, the paper PDF, DOI records, and publisher pages as final evidence.

Keep bibliographic timestamps separate from the public event date. For an arXiv `new-preprint`, preserve the UTC submission timestamp in `papers.yml`, but use the official listing's announcement date as `signal_date`. For a `major-revision`, use the official replacement-list date. For a `journal-publication`, use the publisher's first-online date. Record the primary `event_source` URL for each newly selected event. The scan timestamp never changes the paper's event date. An OAI modification timestamp alone is not announcement evidence.

Bibliography-first rule (owner approved 2026-09-27): a directly relevant journal
record with verified title, full authors, journal, year and DOI may be included
without an abstract or exact first-online date. A publisher's Crossref deposit is
valid evidence; do not require a second successful publisher-page fetch. Omit
unsupported reading notes, use `signal_date: null` when the day is unknown, and
record `added_on` as the actual intake date. Ordering and time filtering fall back
to intake only when the event date is absent; never print intake as publication.
An existing verified arXiv announcement remains usable when journal first-online
metadata is missing. Do not infer chronology from DOI creation or issue assignment.
This rule does not authorize historical backfill or claims based only on a title.

arXiv normally has no Friday or Saturday announcements. A paper submitted before the Friday 14:00 US Eastern cutoff can therefore carry a Friday UTC submission date while appearing in the following Monday category list. Preserve both dates and let the rendered card explain the distinction whenever they differ.

`data/papers.yml` contains one current bibliographic record per paper. Do not create separate arXiv and DOI records for the same work.

`data/editions.yml` contains one public `frontier` entry per paper. If a selected paper later has a qualifying major revision, update the existing paper and frontier entries:

- retain the original arXiv ID and submission date;
- change `signal_type` and `signal_date` to the new qualifying event;
- update the annotation only where the new event changes the result;
- do not append a duplicate public card.

Git history preserves the earlier event state.

If a selected preprint later receives routine first journal publication, add or
refresh its DOI and journal metadata without changing `signal_type`,
`signal_date`, or its position as a new recommendation. A journal publication is
a public radar event only for a newly discovered work that has not already been
recommended, or when the formal version itself adds a separately qualifying
major result.

## Data entry

`papers.yml` stores identity, current bibliography, verified submission/version
dates, optional withdrawal/retraction status, official `arxiv_categories` and
searchable `keywords`. Store a journal DOI when known; the arXiv-issued DOI is
derivable from arXiv ID and is not duplicated.

Schema2 `editions.yml` stores `paper_id`, nullable journal `signal_date`, `signal_type`,
optional `added_on` (required for an unknown event date), one or two approved
`directions`, an optional three-part `reading_note`, and the primary
`event_source` URL for newly verified events. The four direction labels live in
`tags.yml`; individual model/method keywords have no artificial two-tag limit.

Retired fields must not be restored: `frontier_weeks`, per-paper `week`, the four
old prose fields, entry-level `structure_tags`, and registry `tags`. Old prose and
weekly records remain recoverable in Git history; they are not hidden search text.
Keep dates distinct and preserve source precision. Historical entries without a
captured event URL may remain, but do not invent evidence for them.

When only an abstract has been checked, keep the reading note within its scope;
inspect the paper before adding technical mechanisms, priority claims or detailed
comparisons absent from the abstract. See `maintenance/radar-data-model.md`.

After a successful source run, advance only that source's watermark in
`maintenance/radar-state.yml`, even when no paper is selected. A check-only
change does not need its own daily PR; carry the state forward with the next
content change or weekly maintenance PR. Never create or restore a unified
`frontier.checked_through` field.

Do not use public contribution classes such as core/adjacent or structure advance. Do not add per-paper `自动整理` badges, BibTeX buttons, recommendation dates, title-fragment tags, or invented terminology.

Record actual source coverage and unresolved gaps in `radar-state.yml`, not weekly
publication aggregates. New announcements and replacements, Crossref online dates
and DOI registrations each retain independent progress. Counts are derived from
the selected records when needed.

The public homepage defaults to a compact cumulative list with 20 papers per page.
Date, research direction, and full-collection text search narrow this list;
pagination never changes editorial selection. No weekly archive or weekly overview
is displayed. Time choices are all collected papers, last 30 days, last 3 months,
and a custom interval defaulting to the earliest collected event through today.
Show the actual collection's month span, without implying exhaustive coverage.
Collapsed rows show only the
title and bibliography. Expanded rows present the main finding, supporting detail,
and methods/scope in a compact reading view, without repeating bibliography or
displaying a separate innovation section. Bibliography-only rows have no empty
expander. When supported by an abstract or full text, maintain a `reading_note`
mapping with `lead`, `detail` and `method_scope`. The lead
states the concrete result; detail supplies the distinguishing advance; methods/scope
retains material assumptions and distinguishes numerical evidence from theorems.
Keep these paragraphs complementary. Omit version bookkeeping, generic praise,
unsupported priority claims and generic warnings about unrelated cases. Length may
vary with the result; never discard a critical condition to meet a character target.
The reading note is the only prose source for display and search; do not maintain
parallel hidden descriptions.

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
