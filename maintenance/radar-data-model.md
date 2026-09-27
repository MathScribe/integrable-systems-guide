# Radar data and source responsibilities

Schema2 removes unused weekly aggregates and duplicated prose. Public presentation
is generated; raw source pages and editorial judgments are not copied into the site.

| Location | Responsibility |
| --- | --- |
| `data/papers.yml` | One current bibliography per work: ID, title, complete authors, primary URL, arXiv ID, journal DOI and citation, original/updated dates, version, verification date, optional status, categories and keywords |
| `data/editions.yml` | Public selection: paper ID, event date/type, optional intake date, one or two directions, optional single reading note, and primary evidence source |
| `data/tags.yml` | Only the four approved direction IDs and labels |
| `maintenance/radar-sources.yml` | Bounded discovery categories, query phrases, caps and date-basis configuration |
| `maintenance/radar-state.yml` | Independent successful new/replacement, online/registration and index progress; explicit gaps and source limitations |
| `maintenance/radar-candidates.yml` | Active unresolved candidates with identity, sources and next action; closed/deferred decisions remain in private audits |
| `.radar-audit/` | Ignored raw responses, detailed screening and comparison evidence, failed requests, private review reports |

## Retired and retained fields

- Retired: `frontier_weeks` and `week`; counts/date groups can be derived if needed.
- Retired: `summary`, `main_result`, `integrable_structure`, `innovation`; all selected
  annotations use `reading_note.lead/detail/method_scope`, the sole prose source.
- Merged: paper `tags` and entry `structure_tags` become paper `keywords`; categories
  also move to the bibliography. Keywords remain searchable, not extra UI filters.
- Retained: `signal_date` and `signal_type`, because new, revised and published events
  differ. The record's submitted/updated/published dates have separate meanings.
- Retained: `metadata_checked_at`, `metadata_note` and optional exact `submitted_at`
  preserve verification context. They are not shown as recommendation badges.
- Journal DOI is retained. An arXiv-issued DOI is derivable and no longer duplicated.
- `status: withdrawn` or `retracted` retains identity while preventing public selection.

## Evidence boundaries

Catchup pages provide day-level official events for roughly90 days. A cross-list
is not automatically a first announcement. Its server omits journal-reference-only
changes and replacements beyond v5, so current primary histories are checked for
selected/high-priority papers where that limitation matters. An OAI record's last
modification is not a substitute for a first announcement date.

Crossref's online and registered-DOI passes use separate watermarks. Registration
finds records missing published-online metadata, but never supplies a publication
date. Preserve year/month precision; no synthetic January1 or first-of-month dates.
The zbMATH issue-year window includes the following year and uses index timestamps
only for discovery. Publisher first-online evidence determines journal events.

Verified journal bibliography may be selected without a reading note. It renders
as a compact row with primary links and no empty expander. Missing online dates
are explicit `signal_date: null`, allowed only with journal DOI, citation year,
primary `event_source` and valid `added_on`. A publisher's Crossref deposit is an
acceptable primary metadata source. `added_on` is the actual site intake date,
not a claim about first discovery or publication. Ordering and time filters use
`signal_date` when known, otherwise `added_on`; the fallback is never printed as
a publication date. Known event dates are never replaced by newer intake dates.
Keep issue years (including next-year assignments) in the citation. Reconcile
missing optional fields on a later successful source pass, without repeated
publisher retries or an active pending item solely for those fields.

The migration preserves all identities, event dates, selection and reading notes.
Old fields remain recoverable from the pre-migration Git commit. Only verified
content updates in a separate commit change the public selection.
