# Zotero seed map

This page summarizes the first import from the Zotero resource dump. It is not a link dump: the purpose is to identify which seeds should be promoted into curated entries, which should remain background references, and which need manual verification.

The raw Zotero export reports 148 resource-like seeds in one summary file and a larger dump with 139 resource-like seeds plus 316 bibliography or topic-signal items. The export explicitly warns that Zotero dates are often access/save dates and that links were not checked online in that pass.

## Promotion policy

Use `data/zotero-priority-resources.yml` as the intermediate layer between raw Zotero metadata and curated records. A resource should be moved into `data/resources.yml` only after a manual check confirms the URL, the author or institution, the type of material available, and the reason it belongs in a research-training guide.

## Highest-priority additions

### IST, RHP, and long-time asymptotics

These are the most urgent seeds for the guide.

| Resource | Status | Why it matters |
|---|---|---|
| Peter Perry lectures page | verified online | Recent inverse-scattering lecture PDFs, including Lax representations, defocusing NLS asymptotics, Davey-Stewartson II, and KP-I asymptotics. |
| Peter D. Miller Math 651 Winter 2018 | verified online | Detailed course page on integrable systems and Riemann-Hilbert problems, with lecture notes, homework, notebooks, NLS, Toda, RHP theory, and dbar steepest descent. |
| KIT IST seminar, Summer 2023 | needs verification | Directly matches the guide's IST theme; verify PDF references and course structure before promotion. |
| Fields Institute nonlinear dispersive PDE / inverse scattering workshop | needs manual browser check | Likely a central workshop source, but automated fetching had redirect issues. |
| Tom Trogdon homepage | verified online | Contains RHP masterclass materials, notebooks, RHPackage links, and numerical RHP resources. |

### PDE and analysis background

These resources should be used to build prerequisite paths rather than mixed into the IST core.

| Resource | Status | Use |
|---|---|---|
| Monica Visan notes | verified online | Nonlinear dispersive PDE, critical NLS, scattering, and concentration compactness. |
| Terence Tao teaching archive and blog notes | verified online | Fourier analysis, real analysis, complex analysis, PDE, Sobolev spaces, and dispersive background. |
| Michael Taylor notes | verified online | Broad PDE and analysis background, including downloadable notes by subject area. |
| KIT Fourier Analysis, Dispersive Equations, Functional Analysis | needs verification | Candidate course pages for prerequisite repair; extract notes and problem sets if accessible. |
| Laugesen Harmonic Analysis notes | needs verification | Candidate background resource for Fourier/harmonic analysis. |
| Linares--Ponce nonlinear dispersive PDE textbook | needs verification | Standard textbook reference for PDE-side reading paths. |

### Stability and nonlinear waves

These seeds should support the soliton-stability and soliton-resolution parts of the guide.

| Resource | Status | Use |
|---|---|---|
| Dmitry Pelinovsky homepage | reachable, needs content review | Soliton stability, spectral theory, NLS/DNLS, nonlinear waves. |
| Todd Kapitula homepage | verified online | Spectral and dynamical stability of nonlinear waves; book and research links. |
| Mathew Johnson homepage | verified online | Nonlinear waves, existence, stability, dynamics, and lecture notes on PDE/stability. |
| Jianke Yang, *Nonlinear Waves in Integrable and Nonintegrable Systems* | needs verification | Reference for nonlinear waves, solitons, and computational examples. |

### Finite-gap and algebro-geometric methods

These are valuable, but most are advanced references rather than first-reading resources.

| Resource | Status | Use |
|---|---|---|
| Belokolos et al., *Algebro-geometric approach to nonlinear integrable equations* | needs verification | Major finite-gap reference; verify stable access. |
| Gesztesy--Holden, *Soliton Equations and their Algebro-Geometric Solutions* | needs verification | Core finite-gap reference, best used after Riemann-surface preparation. |
| Dubrovin, *Theta functions and non-linear equations* | needs verification | Classical conceptual reference for theta functions and integrable systems. |
| Krichever--Shiota, *Soliton equations and the Riemann-Schottky problem* | needs verification | Advanced algebraic-geometric signal, not a first training resource. |
| Trogdon--Deconinck finite-genus KdV RHP article | needs verification | Bridge between finite-genus solutions and numerical RHP. |

## What not to promote yet

Do not promote items that are merely bibliography signals unless they serve a specific reading path. Examples include isolated research papers with no expository role, entries without URLs, local attachments, paywalled book pages without open companion material, and general-purpose math hubs such as broad awesome lists.

## Immediate next actions

1. Promote the verified Perry lectures page, Trogdon homepage, and Miller Math 651 page into `data/resources.yml`.
2. Verify KIT course pages manually; automated fetches can fail on KIT pages.
3. Create topic-page cross-links from IST, RHP, nonlinear steepest descent, DNLS/NLS, and finite-gap pages into the relevant resources.
4. Add archive URLs for fragile course and workshop pages.
5. Keep the full Zotero dump as a seed source, but do not treat it as curated data.
