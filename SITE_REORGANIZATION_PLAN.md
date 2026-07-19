# 可积系统研究雷达调整计划

**状态：** W28--W29 修订名单已确认；继续完成 30 天样本，再实施公开页面  
**最后更新：** 2026-07-19

相关名单见 [`W28_W29_RETROSPECTIVE_SCREENING_REPORT.md`](W28_W29_RETROSPECTIVE_SCREENING_REPORT.md)。

## 1. 网站目标

本站面向可积系统研究者，提供一个轻量、精选、可解释的近期论文雷达。

它不试图判断一篇论文是否属于某个狭窄子领域，而是帮助读者回答：

1. 最近出现了什么值得关注的新方向、结构或方法？
2. 可积结构在论文中起了什么实际作用？
3. 论文的创新是否足够清楚、足够强，值得进一步阅读？

主题相关性只作为宽松入口。只要与可积系统存在可解释的结构联系，且创新明确，就可以收录。引力、概率、随机矩阵、几何、量子多体、统计物理、光学和实验方向不因距离经典可积 PDE 较远而自动排除。

本站不建设 arXiv 镜像、完整论文数据库、全历史语义检索、作者优先系统或自动旧文阅读链。

## 2. 选稿原则

### 2.1 决定性标准是创新

候选论文原则上满足：

1. 可积性是核心结构、核心方法或不可替代的解释工具；
2. 有清楚、可核验的创新；
3. 能从 arXiv、论文正文、DOI 或出版商页面准确说明；
4. 能向可积系统读者解释其方法或方向为什么值得关注；
5. 提供超过直接浏览标题和摘要的编辑价值。

优先关注：

- 新的或实质扩展的 Lax pair、谱问题、层级、Hamiltonian/Poisson 结构；
- 新 RHP、tau function、谱曲线、Painlevé、Yang--Baxter 或可积离散化；
- 已有可积方法产生的系统新分类、任意阶解族、新渐近、新拓扑或新物理机制；
- 新反演、控制、实验、统计或宏观动力学方法；
- 把可积结构带入新领域，并形成明确、可复用的方法桥梁。

### 2.2 不要求每篇都提出全新的可积结构

内部审核时回答两个问题：

1. 论文是否提出、揭示或实质扩展了可积结构或方法？
2. 即使结构已有，它是否不可替代地产生了清楚、可核验的创新？

满足其中一种强路径即可。两个问题只用于审核，不生成公开分类或 badge，也不要求把论文硬分成唯一类型。

### 2.3 通常不收录

- 标准变换的机械套用；
- 只有少量低阶显式解和参数图；
- 没有结构性结论的数值展示；
- 熟悉方法几乎无概念变化地迁移；
- 可积性只在引言或背景出现；
- 无法可靠说明研究问题、结构作用和创新。

论文不能因为某周数量较少而降低门槛；但也不能因为主题不属于经典可积 PDE，或没有提出新的 Lax pair，就被过早排除。

## 3. 发现与筛选必须分开

论文数量少可能来自两种原因：

1. 候选很多，但严格筛选后只剩少数；
2. 发现范围过窄，论文根本没有进入候选池。

因此流程固定为：

```text
广覆盖发现
    ↓
候选池与元数据核验
    ↓
摘要或正文级判断
    ↓
最终公开论文
```

发现阶段优先覆盖率，允许候选多和噪声高；筛选阶段再保证解释准确和收录克制。

## 4. 候选发现方式

### 4.1 每日基础发现

每日完整检查目标日期内的：

- `nlin.SI`；
- `nlin.PS`。

同时做少量跨分类检索，覆盖数学物理、概率、几何、组合、量子、统计物理、引力和光学。

检索同时使用结构词与结果词。

结构词包括：

- Lax pair；
- inverse scattering；
- Riemann--Hilbert；
- Painlevé；
- tau function；
- Darboux/Bäcklund；
- Yang--Baxter；
- Bethe Ansatz；
- finite-gap；
- integrable probability；
- generalized hydrodynamics。

结果词包括：

- classification；
- asymptotics；
- inverse problem；
- exact distribution；
- transport；
- experiment；
- stability；
- topology；
- discretization；
- reconstruction；
- deformation；
- conservation law。

### 4.2 每周补充发现

每周额外检查：

- Crossref 和 DOI 元数据；
- 少量重点期刊的 online-first 页面；
- 旧预印本首次正式发表事件；
- 少量成熟专题资源用于人工查漏。

Leonid Petrov 的网站只作为 integrable probability 资源入口和偶尔查漏来源，不自动同步其 feed，不镜像其数据库。

### 4.3 最终核验

最终论文必须回到 primary sources：

- 官方 arXiv 页面；
- 论文 PDF；
- DOI 或出版商页面。

不能只依赖搜索摘要或第三方转述。

## 5. W28--W29 修订结果

扩展发现和近遗漏复核后，W28--W29 名单确认保留 20 篇：

- W28：15 篇；
- W29：5 篇；
- 新预印本事件：14 篇；
- 正式期刊发表事件：6 篇。

本轮新增内容主要来自：

- 补查正式期刊 online-first；
- 复核摘要阶段过早排除的论文；
- 更重视“已有可积结构产生强创新”的工作；
- 放宽主题边界，但没有取消创新门槛。

这 20 篇视为 W28--W29 的确认名单。后续只有发现明确的漏项、重复项或元数据错误时才调整。

## 6. 时间与首页窗口

公开排序依据：

- 首次公开日期；
- 重大修订日期；
- 首次正式在线期刊发表日期。

本站收录日期只属于编辑历史，不参与首页排序。

旧预印本首次正式在线发表时，可以重新进入首页。页面同时显示：

- 期刊在线发表日期；
- 原始 arXiv 首次公开日期。

下一步补筛 2026-06-20 至 2026-07-05，与已确认的 W28--W29 合并成 2026-06-20 至 2026-07-19 的完整 30 天样本，再判断 30 天首页窗口是否合适。

## 7. 页面设计

### 7.1 每篇论文默认显示

1. 实际研究事件日期；
2. 一到两个官方 arXiv 分类；
3. 最多两个受控结构或主题标签；
4. 作者和标题；
5. 约 100--180 个汉字的论文概览；
6. arXiv、PDF、DOI 或期刊页面链接；
7. “展开研究内容与创新”入口。

不显示：

- “核心/相邻前沿”；
- “结构推进/结构驱动创新”；
- BibTeX 按钮；
- 逐篇“自动整理”标签；
- 自由生成的模糊标签；
- “推荐于某日”。

### 7.2 展开说明

统一使用：

- **研究问题与主要结果**
- **可积结构与方法**
- **创新**

每部分通常写 2--4 句，总长度约 350--600 个汉字。内容要足以让可积系统读者看懂论文为什么值得关注，而不是只给一句抽象判断。

### 7.3 首页与归档

首页：

- 最近 30 天；
- 按周分组；
- 每篇显示准确日期；
- 第一版不做逐日日期筛选；
- 第一版不做贡献类别筛选；
- 所有详细说明默认折叠。

Radar 归档首页只显示周目录。每周页面复用首页的论文条目组件，并在底部展示聚合筛选说明。

`Core topics` 和 `Group work` 暂不改。`About` 补充选稿原则和自动整理说明。`Resources` 增加一条 Leonid Petrov 网站链接，不接入 feed。

## 8. 标签规则

### 8.1 arXiv 分类

直接使用官方分类，不翻译、不改写。默认显示 primary category，必要时再显示一个重要 cross-list 分类。

### 8.2 结构和主题标签

标签来自固定词表。第一版可包括：

- Lax pair；
- inverse scattering；
- Riemann--Hilbert problem；
- nonlinear steepest descent；
- Hamiltonian structure；
- conservation laws；
- tau function；
- Darboux transformation；
- finite-gap；
- spectral curve；
- Painlevé；
- isomonodromy；
- Yang--Baxter equation；
- Bethe Ansatz；
- integrable discretization；
- soliton gas；
- generalized hydrodynamics；
- integrable probability；
- inverse problem；
- loop equations；
- Pfaffian structure；
- topological vector potential；
- superintegrability；
- Chern--Simons theory；
- matrix model。

每篇默认最多显示两个标签。禁止模型临时创造“谱控制”之类来源不清、含义不稳定的术语。新增标签必须能在论文或领域正式用语中找到依据，并先加入词表。

## 9. 数据维护

不使用 SQL 数据库，也不手工分别维护首页和周页面。`data/papers.yml` 和 `data/editions.yml` 继续作为轻量结构化数据源，自动流程更新 YAML，人工通过 PR 审核，renderer 统一生成公开页面。

试运行字段：

```yaml
- paper_id: "arxiv:xxxx.xxxxx"
  signal_date: "2026-07-19"
  signal_type: "new-preprint"
  review_status: "automated"
  arxiv_categories:
    - "nlin.SI"
  structure_tags:
    - "Darboux transformation"
  summary: >-
    默认显示的论文概览。
  main_result: >-
    研究问题与主要结果。
  integrable_structure: >-
    可积结构与方法。
  innovation: >-
    创新。
```

内部两个筛选问题保存在审核记录或 PR 说明中，不写入公开分类字段。

验证脚本检查：

- `paper_id`、arXiv ID、DOI 和规范化标题去重；
- 日期和必填说明存在；
- arXiv 分类格式合法；
- 标签来自固定词表；
- 首页和周页面排序一致；
- renderer 重复运行结果一致。

## 10. 自动内容说明

不再给每篇论文重复显示“自动整理”。首页和周页面顶部统一说明：

> 论文说明由自动流程整理，并经元数据核验；除特别标注外，不代表编辑已经完整阅读或逐句审校。

数据中继续保留 `review_status`。

## 11. 实施顺序

### Phase 0：政策和 W28--W29 复核

- [x] 确定网站定位；
- [x] 取消个人方程、作者和课题组优先级；
- [x] 区分候选发现和编辑筛选；
- [x] 完成 W28--W29 扩展发现和近遗漏复核；
- [x] 确认 W28--W29 的 20 篇名单；
- [x] 确定紧凑论文列表、折叠详情和标签规则。

### Phase 1：完成 30 天样本

- [ ] 补筛 2026-06-20 至 2026-07-05；
- [ ] 合并为 2026-06-20 至 2026-07-19 的完整样本；
- [ ] 测量最终数量和周分布；
- [ ] 确认最近 30 天窗口。

此阶段只提交筛选报告，不修改公开网站。

### Phase 2：页面与数据实现

- [ ] 在 `data/editions.yml` 增加最少字段；
- [ ] 建立受控标签词表和验证；
- [ ] 首页改为最近 30 天、按周分组的紧凑论文流；
- [ ] 周页面复用同一组件；
- [ ] Radar 首页改为周目录；
- [ ] 更新 About 和 Resources；
- [ ] 完成 renderer check、registry validation 和 `mkdocs build --strict`。

### Phase 3：调整日常自动化

- [ ] 将每日阅读链生成改为每日候选筛选；
- [ ] 允许空缺日期；
- [ ] 每周补查正式发表；
- [ ] 继续只创建 reviewable PR；
- [ ] 不自动合并，不启用 auto-merge。
