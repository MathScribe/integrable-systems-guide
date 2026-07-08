# Contributing

This repository is intended to become a curated research-training knowledge base, not a generic link list.

## If you do not know Git

Use GitHub Issues.

1. Open a new issue.
2. Paste the resource link.
3. Explain why the resource is useful.
4. Mention the topic: IST, RHP, DNLS/NLS, nonlinear dispersive PDE, soliton stability, finite-gap methods, or background analysis.
5. Submit the issue and wait for a maintainer to review it.

You do not need to edit YAML files or run MkDocs.

## If you can edit Markdown

Edit files under `docs/` and open a pull request. Good first contributions include:

- improving topic-page explanations;
- adding reading-order comments;
- reporting broken links;
- clarifying prerequisites;
- adding short annotations for already reviewed resources.

## If you are a maintainer

Promote a resource into `data/resources.yml` only after checking:

- the canonical URL;
- author or institution;
- resource type;
- notes, slides, videos, problem sets, software, or reading lists available;
- mathematical topic coverage;
- prerequisites and level;
- strengths and limitations;
- quality grade;
- link status and last checked date.

## ChatGPT prompt for contributors

Use this prompt to prepare a clean issue comment:

```text
Please turn the following mathematical resource into a candidate entry for an integrable-systems research guide. Do not invent missing information.

Resource URL:
[PASTE LINK]

Please output:
1. Title
2. Author or maintainer
3. Institution
4. Resource type
5. Main topics
6. Equations or methods covered
7. Prerequisites
8. Suitable level
9. Why it is useful
10. Limitations or things to verify
```
