# Research radar selection policy

Policy version 2, approved by the owner during the September 2026 historical
rescreening. This policy defines the editorial objective used after broad discovery. It is
versioned independently from any one daily run so that quiet or busy days do not
move the threshold.

## Editorial promise

Maintain a focused reading radar for research on integrable nonlinear waves,
inverse scattering and spectral methods. The reference research interests include
Liming Ling's work on multicomponent NLS/DNLS, solitons, breathers, rogue waves,
stability, Riemann–Hilbert asymptotics, finite-gap backgrounds and soliton gases.
This is a thematic reference, not an author whitelist or a group publication feed.

The radar does not promise a fixed number of papers. It must not add old papers,
routine work, or weaker candidates to make a day or week look full. An unusually
strong batch may contain more papers than usual; a quiet batch may contain none.

## Freshness gate

Freshness is an eligibility condition, not a ranking signal.

- A new preprint must belong to an unprocessed official arXiv announcement batch.
- A major revision must belong to an unprocessed replacement batch and add a main
  theorem, core method, substantial analysis, experiment, or material conclusion.
- A journal-only discovery must have a first-online date in the unprocessed
  publication window.
- A delayed index record keeps its real event date. It is not relabelled as a
  current recommendation merely because the radar observed it later.
- A previously selected preprint that later receives routine journal publication
  is updated bibliographically but is not recommended again.
- Companion papers announcing the same result are represented by the most
  complete and informative version unless they contain genuinely distinct results.

## Research focus and useful new directions

Prioritize integrable PDEs and lattices, IST and spectral theory, Riemann–Hilbert
and dbar methods, well-posedness, stability, long-time asymptotics, nonlinear-wave
interactions, finite-gap solutions, Painlevé/isomonodromy, and random soliton sets.
Useful numerical or experimental advances on these problems are eligible.

Scope alone never authorizes selection. A candidate must clearly pass at least
one of the following tests:

1. **Direct research relevance:** a concrete, substantive advance on a problem,
   model or method within the focus above. A useful well-posedness or stability
   theorem need not introduce a new integrable structure or be a field-wide
   breakthrough. Related nonintegrable perturbations are eligible when the
   connection and new insight for nonlinear waves can be stated precisely.
2. **A useful new direction:** a specific methodological or problem connection
   to that focus, supported by primary evidence. Examples include probability
   for random scattering data and soliton ensembles, microscopic-to-hydrodynamic
   limits, spectral reconstruction, or numerical/experimental access to soliton
   dynamics. State what could be learned or transferred, not merely a discipline.

Quantum theory, probability, geometry, combinatorics and gravity are searched
selectively as possible sources of such connections. The radar does not promise
comprehensive coverage of these fields. A specialized observable, algebraic
construction or random-matrix statistic is not sufficient without a concrete
connection to the research focus. General structural criteria and reusable
spectral/Hamiltonian methods remain eligible when that connection is clear.

Strong evidence includes a new general classification, reusable method, Lax or
Hamiltonian mechanism, arbitrary-order or arbitrary-parameter family, rigorous
asymptotic regime or critical transition, inverse result, exact distribution,
transport structure, experimental method, or important application whose main
conclusion would not survive without integrability.

Normally exclude:

- incidental mentions of integrability or isolated structure terms;
- routine transfer of Darboux, Hirota, symmetry, or similar machinery to one more
  equation;
- a few low-order examples, explicit solutions, parameter plots, or numerical
  collisions without a broader mechanism;
- a review, conference overview, minor correction, or metadata-only revision;
- a technically correct but incremental result whose value cannot be stated
  concretely from primary evidence.

## Evidence and authority

Title-only evidence cannot support selection. An abstract may support a cautious
decision; formula-level mechanisms, proof claims, and comparisons beyond the
abstract require inspection of the paper.

For journal-only discoveries, classify venue authority internally before making
the editorial decision:

- **Tier A — authoritative field venue:** an established general mathematics
  journal, leading subject journal, or core mathematical-physics venue with
  demonstrated editorial competence in the paper's area. This is a strong
  reliability signal, but the paper must still pass the same novelty and
  integrability tests.
- **Tier B — reliable specialist venue:** an established specialist journal with
  relevant peer-review competence. This is a supporting signal; selection
  requires a clearly identifiable structural or methodological advance rather
  than publication status alone.
- **Tier C — no authority bonus:** a broad high-volume venue, a venue remote from
  the mathematical subject, an unfamiliar or weakly evidenced venue, or a record
  known only from an index or aggregator. Select only when primary paper evidence
  independently establishes an unusually strong result and the publisher record
  verifies the publication event.

An unclassified venue defaults to Tier C until evidence supports a higher tier.
Determine the tier from the full journal identity, field fit, publisher record,
and established editorial and review role—not from an author's reputation or a
publisher brand alone. Do not maintain a supposedly exhaustive journal whitelist
or enumerate journal homepages as the discovery method; specialized high-quality
mathematics venues must remain eligible.

For every journal-only candidate that reaches detailed review, record the tier
and a short basis in the internal run audit. The tier is not a public badge and
must not appear on the paper card. Venue authority is evidence of review
reliability, not a substitute for content: do not select an incidental paper
because its venue is prestigious, and do not reject an important structural
result merely because it appears in a specialist venue.

Author reputation may trigger closer inspection but never determines selection.

## Decision order

Apply the gates in this order:

1. Is this a new eligible event?
2. Does either the direct-research or useful-new-direction test clearly pass?
3. Is the concrete addition substantive rather than routine within that context?
4. Does primary evidence support the claim?
5. Is the identity, date, and publication metadata verified?

There is no numerical quota or hard maximum. If selections remain unusually
numerous over several runs, audit the threshold and discovery noise rather than
truncating the list mechanically.

Review workload depends on the elapsed discovery interval. Do not apply a daily
review-count target to a historical catch-up or reject a paper to smooth weekly
counts. Audit noisy queries and repeated relevance errors instead.

## Calibration and policy changes

Detailed rejected-paper judgments belong in local audit artifacts, not on the
public site. A policy change must identify a recurring false positive, false
negative, freshness error, or evidence problem; rerun the same frozen candidate
set; and record the before/after effect.

Do not change the live threshold during a daily run. Calibrate on a separate
infrastructure branch, validate against captured runs, then submit the policy and
code change for review.

Operational repairs such as timeouts, source fallbacks, identity matching, and
format validation may improve automatically when they do not alter editorial
outcomes. A change that would alter the field boundary or value threshold must
show a recurring error pattern against the frozen calibration set and be
confirmed by the repository owner before it becomes the live policy.
