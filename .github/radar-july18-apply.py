from pathlib import Path
import re

papers_path = Path("data/papers.yml")
papers = papers_path.read_text(encoding="utf-8")
new_ids = [
    "doi:10.2991/jnmp.k.200922.003",
    "doi:10.1016/j.jde.2015.02.046",
    "doi:10.1016/j.jde.2021.11.045",
    "arxiv:1710.06563",
]
new_arxiv_ids = ["1912.12400", "1308.0755", "2010.08714", "1710.06563"]
new_titles = [
    "Inverse Scattering Transformation for the Fokas–Lenells Equation with Nonzero Boundary Conditions",
    "Long-time asymptotics for the Fokas–Lenells equation with decaying initial value problem: Without solitons",
    "Long-time asymptotics for the focusing Fokas-Lenells equation in the solitonic region of space-time",
    "Long-time asymptotics for initial-boundary value problems of integrable Fokas-Lenells equation on the half-line",
]
for paper_id in new_ids:
    if f'id: "{paper_id}"' in papers:
        raise SystemExit(f"paper already present: {paper_id}")
for arxiv_id in new_arxiv_ids:
    if f'arxiv_id: "{arxiv_id}"' in papers:
        raise SystemExit(f"arXiv id already present: {arxiv_id}")
for title in new_titles:
    if title.casefold() in papers.casefold():
        raise SystemExit(f"title already present: {title}")

papers_block = r'''- id: "doi:10.2991/jnmp.k.200922.003"
  title: "Inverse Scattering Transformation for the Fokas–Lenells Equation with Nonzero Boundary Conditions"
  authors:
    - "Yi Zhao"
    - "Engui Fan"
  url: "https://doi.org/10.2991/jnmp.k.200922.003"
  arxiv_id: "1912.12400"
  doi: "10.2991/jnmp.k.200922.003"
  journal: "Journal of Nonlinear Mathematical Physics"
  volume: "28"
  issue: "1"
  pages: "38-52"
  year: 2021
  published: "2020-12-10"
  submitted: "2019-12-28"
  updated: "2019-12-28"
  version: "v1"
  metadata_checked_at: "2026-07-18"
  tags:
    - "Fokas--Lenells equation"
    - "nonzero boundary conditions"
    - "inverse scattering"
    - "Riemann--Hilbert problem"
    - "Jost solutions"
    - "N-soliton solutions"

- id: "doi:10.1016/j.jde.2015.02.046"
  title: "Long-time asymptotics for the Fokas–Lenells equation with decaying initial value problem: Without solitons"
  authors:
    - "Jian Xu"
    - "Engui Fan"
  url: "https://doi.org/10.1016/j.jde.2015.02.046"
  arxiv_id: "1308.0755"
  doi: "10.1016/j.jde.2015.02.046"
  journal: "Journal of Differential Equations"
  volume: "259"
  issue: "3"
  pages: "1098-1148"
  year: 2015
  published: "2015-08-05"
  submitted: "2013-08-03"
  updated: "2013-08-03"
  version: "v1"
  metadata_checked_at: "2026-07-18"
  metadata_note: "The arXiv preprint is titled 'Leading-order temporal asymptotics of the Fokas-Lenells Equation without solitons'; the registry uses the version-of-record journal title."
  tags:
    - "Fokas--Lenells equation"
    - "solitonless sector"
    - "Riemann--Hilbert problem"
    - "Deift--Zhou method"
    - "long-time asymptotics"
    - "continuous spectrum"

- id: "doi:10.1016/j.jde.2021.11.045"
  title: "Long-time asymptotics for the focusing Fokas-Lenells equation in the solitonic region of space-time"
  authors:
    - "Qiaoyuan Cheng"
    - "Engui Fan"
  url: "https://doi.org/10.1016/j.jde.2021.11.045"
  arxiv_id: "2010.08714"
  doi: "10.1016/j.jde.2021.11.045"
  journal: "Journal of Differential Equations"
  volume: "309"
  pages: "883-948"
  year: 2022
  published: "2022-02-05"
  submitted: "2020-10-17"
  updated: "2022-03-02"
  version: "v3"
  metadata_checked_at: "2026-07-18"
  tags:
    - "focusing Fokas--Lenells equation"
    - "soliton resolution"
    - "Riemann--Hilbert problem"
    - "dbar steepest descent"
    - "long-time asymptotics"
    - "discrete spectrum"

- id: "arxiv:1710.06563"
  title: "Long-time asymptotics for initial-boundary value problems of integrable Fokas-Lenells equation on the half-line"
  authors:
    - "Shuyan Chen"
    - "Zhenya Yan"
  url: "https://arxiv.org/abs/1710.06563"
  arxiv_id: "1710.06563"
  doi: "10.48550/arXiv.1710.06563"
  submitted: "2017-10-18"
  updated: "2017-12-13"
  version: "v2"
  metadata_checked_at: "2026-07-18"
  tags:
    - "Fokas--Lenells equation"
    - "half-line"
    - "initial-boundary value problem"
    - "Riemann--Hilbert problem"
    - "nonlinear steepest descent"
    - "long-time asymptotics"
'''
papers_path.write_text(papers.rstrip() + "\n\n" + papers_block.strip() + "\n", encoding="utf-8")

editions_path = Path("data/editions.yml")
editions = editions_path.read_text(encoding="utf-8")
if 'date: "2026-07-18"' in editions:
    raise SystemExit("2026-07-18 edition already present")

week_block = r'''  - id: "2026-W29"
    date_range: "2026-07-13 至 2026-07-19"
    summary: >-
      本周从 non-Abelian DNLS、fully discrete Gerdjikov--Ivanov、Manakov vector breathers、
      shifted nonlocal reductions 与谱数据操控，推进到 Fokas--Lenells 的非零背景 IST、
      全线纯辐射渐近、含孤子 soliton resolution 和半线初边值渐近。
    tags:
      - "DNLS"
      - "Gerdjikov--Ivanov equation"
      - "Manakov system"
      - "Fokas--Lenells equation"
      - "nonzero boundary conditions"
      - "inverse scattering"
      - "Riemann--Hilbert problem"
      - "nonlinear steepest descent"
      - "soliton resolution"
      - "half-line"
      - "Darboux transformation"
      - "spectral data"
'''
pattern = re.compile(r'(?ms)^  - id: "2026-W29"\n.*?(?=^  - id: "2026-W28")')
editions, count = pattern.subn(week_block.rstrip() + "\n", editions, count=1)
if count != 1:
    raise SystemExit(f"expected one W29 block, replaced {count}")

edition_block = r'''  - date: "2026-07-18"
    week: "2026-W29"
    summary: >-
      本期按“非零背景 direct/inverse scattering—全线无孤子辐射—含离散谱 soliton resolution—
      半线初边值渐近”组织，形成 Fokas--Lenells 从谱问题建立到 nonlinear steepest descent 的阅读链。
    entries:
      - paper_id: "doi:10.2991/jnmp.k.200922.003"
        role: "journal-version"
        homepage_rank: 1
        what_it_does: >-
          在非零边界条件下分析 Fokas--Lenells Lax pair 的 Jost solutions 与散射矩阵，
          给出解析性、对称性以及 k→0 和 k→∞ 的渐近结构；据此建立广义 Riemann--Hilbert
          问题、重构公式，并在 reflectionless 情形求得 N-soliton 解。
        why_read: >-
          这是非零背景 FL 谱分析的正式期刊基线，可把平面波或椭圆背景上的 Darboux 精确解
          放回完整的 direct/inverse scattering 框架，并明确离散谱、连续谱与重构之间的关系。
      - paper_id: "doi:10.1016/j.jde.2015.02.046"
        role: "backlog-core"
        homepage_rank: 2
        what_it_does: >-
          对衰减初值的全线 Fokas--Lenells Cauchy 问题，在无离散谱情形应用 Deift--Zhou
          nonlinear steepest descent，得到纯辐射解的主阶长时渐近，其衰减尺度为 t^{-1/2}。
        why_read: >-
          它把连续谱贡献单独剥离出来，是理解后续含孤子渐近中辐射项、相位修正和局部模型的
          最干净起点，也便于与 DNLS、coupled NLS 的纯辐射 RHP 分析逐项比较。
      - paper_id: "doi:10.1016/j.jde.2021.11.045"
        role: "journal-version"
        homepage_rank: 3
        what_it_does: >-
          对支持 bright solitons 的一般 Sobolev 初值，在固定时空锥中用 dbar nonlinear
          steepest descent 分离离散谱与连续谱：主项为 N(I)-soliton，辐射为 O(t^{-1/2})，
          总余项控制到 O(t^{-3/4})，并处理 k=0 谱奇点和四个驻相点。
        why_read: >-
          这篇正式论文把 2015 年纯辐射基线推进到真正的 soliton resolution，展示 FL 特有的
          谱奇点和驻相几何如何改变标准 NLS/DNLS steepest-descent 模板。
      - paper_id: "arxiv:1710.06563"
        role: "method-background"
        what_it_does: >-
          对半线上的 Schwartz 类 Fokas--Lenells 初边值问题建立相应 Riemann--Hilbert 表述，
          并用 Deift--Zhou nonlinear steepest descent 推导 t→∞ 的长时渐近。
        why_read: >-
          它把同一套渐近方法从整线散射推广到受边界约束的谱问题，适合作为研究 FL/DNLS
          半线问题、边界谱数据和初边值相容性的直接方法背景。
'''
marker = "editions:\n"
if marker not in editions:
    raise SystemExit("editions marker not found")
editions = editions.replace(marker, marker + edition_block.rstrip() + "\n\n", 1)
editions_path.write_text(editions, encoding="utf-8")
