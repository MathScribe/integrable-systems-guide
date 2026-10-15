# Content quality checks

## Before committing

Install the repository-local hook once per checkout:

```powershell
git config --local core.hooksPath .githooks
```

The hook runs `scripts/check_staged.py` with the checkout's virtual environment.
It exports the Git index into a temporary tree and validates that tree, including
partially staged files. Unstaged corrections cannot conceal errors in the commit.
The temporary tree is removed when the check finishes. No network calls occur.

Run the same quick checks on working-tree files with:

```powershell
.venv\Scripts\python.exe scripts\validate_content.py
```

Checks cover duplicate IDs, normalized DOI/arXiv/title identities, blank or
placeholder authors, journal years, preprint submission dates, malformed dates,
future event/intake/check dates, submission timestamp consistency, URL syntax,
and missing local link targets/anchors. Errors identify the source and record or
field. Journal issue years up to two years ahead and reduced-precision publication
dates remain valid; they are not inferred first-online event dates. Exact future
first-online dates are rejected. Unknown journal event dates remain valid when the
required bibliography, event source and intake date are present.

Before opening a PR, regenerate changed data and run the complete check:

```powershell
.venv\Scripts\python.exe scripts\render_radar.py
.venv\Scripts\python.exe scripts\check_project.py
```

The existing PR workflow runs this complete check, including the new regression
tests. Git hooks are local conveniences; CI supplies the shared verification.
Repository branch-protection settings determine whether this check is required to
merge; this patch does not change those settings.

## Online maintenance audit

```powershell
.venv\Scripts\python.exe scripts\audit_resources.py --output .radar-audit\links.json
.venv\Scripts\python.exe scripts\audit_resources.py --publication-search --output .radar-audit\bibliography.json
```

The second command additionally checks arXiv version histories and known DOIs,
and searches Crossref by title and author for records without a DOI. This is a
bounded audit of existing records, not discovery of new recommendations.

The tool inherits process proxy settings; it never changes network configuration.
Requests use timeouts, per-host pacing, bounded workers and a 24-hour local cache.
Use `--max-age 0` only for a deliberate refresh. Reports retain actual check times
and distinguish cached results. A 404/410 is a missing-link candidate requiring
confirmation; 403/429, timeouts and TLS failures are unverified. Even a successful
HTTP response or redirect requires content/identity review before a replacement.

The audit never edits YAML. It reports similar titles without merging them, and
records publication-search candidates without treating them as confirmed matches.
Verify title, full authors, publication type and DOI before applying corrections.
SSRN/other preprint DOIs are not journal publication evidence. Books and chapters
need an explicit bibliography model rather than being labelled as journals.
Ordinary arXiv revisions and newly found journal metadata do not change the
existing public event date or create another recommendation.

Online checks are deliberately separate from commit hooks and PR tests. They do
not block commits on external outages. No recurring schedule is installed by this
patch; the command is available for maintenance runs.
