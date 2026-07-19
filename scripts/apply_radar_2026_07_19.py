from pathlib import Path

root = Path(__file__).resolve().parents[1]
papers = root / 'data/papers.yml'
editions = root / 'data/editions.yml'

paper_block = r'''

- id: "doi:10.1016/j.physd.2025.134706"
  title: "On the multi-component Fokas–Lenells system: KP reductions and various soliton solutions"
  authors:
    - "Han-Han Sheng"
    - "Bao-Feng Feng"
    - "Guo-Fu Yu"
  url: "https://doi.org/10.1016/j.physd.2025.134706"
  arxiv_id: null
  doi: "10.1016/j.physd.2025.134706"
  journal: "Physica D: Nonlinear Phenomena"
  article_number: "134706"
  year: 2025
  metadata_checked_at: "2026-07-19"
  tags:
    - "multi-component Fokas--Lenells system"
    - "KP--Toda reduction"
    - "Gram determinants"
    - "dark solitons"
    - "resonant breathers"

- id: "doi:10.1016/j.physd.2024.134111"
  title: "Rogue waves and their patterns for the coupled Fokas-Lenells equations"
  authors:
    - "Liming Ling"
    - "Huajie Su"
  url: "https://doi.org/10.1016/j.physd.2024.134111"
  arxiv_id: "2307.02008"
  doi: "10.1016/j.physd.2024.134111"
  journal: "Physica D: Nonlinear Phenomena"
  volume: "461"
  article_number: "134111"
  year: 2024
  published: "2024-05"
  submitted: "2023-07-05"
  version: "v1"
  metadata_checked_at: "2026-07-19"
  tags:
    - "coupled Fokas--Lenells equation"
    - "rogue-wave patterns"
    - "Darboux transformation"
    - "Okamoto polynomials"
    - "asymptotic decomposition"

- id: "doi:10.1098/rspa.2018.0806"
  title: "General rogue wave solutions of the coupled Fokas–Lenells equations and non-recursive Darboux transformation"
  authors:
    - "Yanlin Ye"
    - "Yi Zhou"
    - "Shihua Chen"
    - "Fabio Baronio"
    - "Philippe Grelu"
  url: "https://doi.org/10.1098/rspa.2018.0806"
  arxiv_id: null
  doi: "10.1098/rspa.2018.0806"
  journal: "Proceedings of the Royal Society A"
  volume: "475"
  issue: "2224"
  article_number: "20180806"
  year: 2019
  published: "2019-04-17"
  metadata_checked_at: "2026-07-19"
  tags:
    - "coupled Fokas--Lenells equation"
    - "non-recursive Darboux transformation"
    - "higher-order rogue waves"
    - "double and triple roots"
    - "Peregrine solitons"

- id: "doi:10.1016/j.nonrwa.2016.06.006"
  title: "Solitons, breathers and rogue waves for the coupled Fokas–Lenells system via Darboux transformation"
  authors:
    - "Yong Zhang"
    - "Jia-Wen Yang"
    - "Kwok Wing Chow"
    - "Chi-Fai Wu"
  url: "https://doi.org/10.1016/j.nonrwa.2016.06.006"
  arxiv_id: null
  doi: "10.1016/j.nonrwa.2016.06.006"
  journal: "Nonlinear Analysis: Real World Applications"
  volume: "33"
  pages: "237-252"
  year: 2017
  published: "2017-02"
  metadata_checked_at: "2026-07-19"
  tags:
    - "coupled Fokas--Lenells system"
    - "n-fold Darboux transformation"
    - "higher-order solitons"
    - "breathers"
    - "rogue waves"
'''

edition_block = r'''  - date: "2026-07-19"
    week: "2026-W29"
    summary: >-
      本期按“多分量 KP--Toda 约化—coupled FL 高阶 rogue-wave 通式—Okamoto 多项式控制的
      图案渐近—n-fold Darboux 解族基线”组织，集中比较行列式结构、谱分支重数与极端波形分解。
    entries:
      - paper_id: "doi:10.1016/j.physd.2025.134706"
        role: "journal-version"
        homepage_rank: 1
        what_it_does: >-
          从 KP--Toda hierarchy 的双线性方程与 Gram determinant 解出发约化多分量
          Fokas--Lenells 系统，并由 discrete KP 的 Miwa transformation 重建双线性结构；
          给出 dark solitons、Akhmediev/Kuznetsov--Ma 型 breathers 及三、四重 resonant breathers。
        why_read: >-
          它把 coupled FL 的显式波形放回可扩展到任意分量的层级约化框架，特别适合对照
          Darboux 方法中的谱参数构造与 KP reduction 中的 determinant/共振条件。
      - paper_id: "doi:10.1016/j.physd.2024.134111"
        role: "group-adjacent"
        homepage_rank: 2
        what_it_does: >-
          对 coupled Fokas--Lenells 方程构造高阶 rogue-wave determinant formula，并分析
          三重分支点生成的解在大内部参数极限下如何分裂成若干一阶外部 rogue waves 与较低阶内部核心；
          外部位置和内部阶数由 Okamoto polynomial hierarchies 控制。
        why_read: >-
          这是 Liming Ling 课题组相关的正式版本，把“高阶显式解”推进为可预测的图案渐近；
          对理解大参数分解、特殊多项式零点与 rogue-wave 几何之间的联系最直接。
      - paper_id: "doi:10.1098/rspa.2018.0806"
        role: "backlog-core"
        homepage_rank: 3
        what_it_does: >-
          构造非递归 Darboux transformation，分别处理谱特征方程的 double-root 与 triple-root 情形，
          得到 coupled Fokas--Lenells 的一般 n 阶有理 rogue waves，并展示共存 rogue waves、
          anomalous Peregrine solitons 以及包含完整背景场参数的基本和二阶动力学。
        why_read: >-
          它是三重分支点 rogue-wave 族的通式基线，可用于辨认 2024 年图案分解中哪些结构来自
          分支重数、哪些来自大参数极限，并补足一般 n 阶构造而非只看若干低阶图形。
      - paper_id: "doi:10.1016/j.nonrwa.2016.06.006"
        role: "method-background"
        what_it_does: >-
          对 vector/coupled Fokas--Lenells 系统建立 n-fold Darboux transformation，构造高阶
          solitons、breathers 与 rogue waves，并讨论这些孤立波解随参数变化的动力学特征。
        why_read: >-
          这是本期最早的统一 Darboux 解族基线；先读它能看清后续非递归公式、分支点退化和
          Okamoto 图案分析是在怎样的 n-fold dressing 框架上逐步增加结构。

'''

ptext = papers.read_text(encoding='utf-8')
for key in ['10.1016/j.physd.2025.134706','10.1016/j.physd.2024.134111','10.1098/rspa.2018.0806','10.1016/j.nonrwa.2016.06.006']:
    if key in ptext:
        raise SystemExit(f'already registered: {key}')
papers.write_text(ptext.rstrip() + paper_block + '\n', encoding='utf-8')

etext = editions.read_text(encoding='utf-8')
old_summary = '''      本周从 non-Abelian DNLS、fully discrete Gerdjikov--Ivanov、Manakov vector breathers、
      shifted nonlocal reductions 与谱数据操控，推进到 Fokas--Lenells 的非零背景 IST、
      全线纯辐射渐近、含孤子 soliton resolution 和半线初边值渐近。'''
new_summary = '''      本周从 non-Abelian DNLS、fully discrete Gerdjikov--Ivanov、Manakov vector breathers、
      shifted nonlocal reductions 与谱数据操控，推进到 Fokas--Lenells 的散射渐近、
      多分量 KP--Toda 约化、coupled rogue-wave 通式及 Okamoto 图案分解。'''
if old_summary not in etext:
    raise SystemExit('week summary anchor missing')
etext = etext.replace(old_summary, new_summary, 1)
etext = etext.replace('      - "spectral data"\n', '      - "spectral data"\n      - "KP--Toda reduction"\n      - "rogue-wave patterns"\n      - "Okamoto polynomials"\n', 1)
anchor = 'editions:\n'
if anchor not in etext:
    raise SystemExit('editions anchor missing')
etext = etext.replace(anchor, anchor + edition_block, 1)
editions.write_text(etext, encoding='utf-8')
