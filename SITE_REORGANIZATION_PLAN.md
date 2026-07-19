# 可积系统研究雷达调整计划

**状态：** 主要编辑政策已确定；等待回溯名单确认后实施  
**最后更新：** 2026-07-19

相关筛选结果见 [`W28_W29_RETROSPECTIVE_SCREENING_REPORT.md`](W28_W29_RETROSPECTIVE_SCREENING_REPORT.md)。

## 1. 为什么需要调整

当前网站混合了：

1. 最近公开的研究成果；
2. 自动流程发现的论文；
3. 为组成阅读链而补入的旧论文；
4. GPT 生成的背景说明；
5. 编辑真正读过并认可的内容。

混合展示会造成两个误解：旧论文因“今天推荐”而看起来像最新成果；自动生成的阅读建议看起来像人工认可的学术判断。

调整目标不是扩大网站，而是让每条内容的时间含义、入选原因和审核状态清楚。

## 2. 网站定位

公开网站定位为：

> 面向熟悉可积 PDE 和谱方法的研究者，有选择地追踪新的可积结构，以及这些结构带来的新数学或物理结果。

网站不应成为：

- arXiv 最新列表的中文镜像；
- 整个可积系统领域的百科全书；
- 有固定每日篇数的推荐器；
- 未经人工审核的阅读笔记集合；
- 将自动背景链包装成人工综述的页面。

每篇公开论文原则上必须回答：

1. **新的可积结构是什么？**
2. **这种结构使什么以前做不到的结果成为可能？**

两点都无法清楚回答时，通常不收录。

## 3. 已确定的政策

### 3.1 不保留个人方向优先级

DNLS、Gerdjikov--Ivanov、Fokas--Lenells、coupled NLS、特定作者或课题组都不获得额外权重。

所有候选论文使用同一套“可积结构 + 创新后果”标准。方程、作者、合作关系和编辑个人兴趣不能成为入选理由。

### 3.2 目标读者

主要读者是熟悉可积 PDE、Lax pair、谱方法、反散射和基本非线性波理论的研究者。

页面不需要从零解释基础概念；对量子可积性、可积概率等相邻方向，必须说明它们与经典谱、散射、层级、RHP 或守恒结构的桥梁。

### 3.3 新旧由论文事件决定

公开排序依据：

- 首次公开日期；
- 重大修订日期；
- 首次正式在线期刊发表日期。

本站收录日期仅属于编辑历史，不参与首页排序。

### 3.4 首页暂定最近 30 天

先试行最近 30 天窗口，再根据实际合格论文数量决定是否调整。

允许没有合格新论文的日期；不使用旧论文补数量。

### 3.5 重大修订

只有以下变化可作为新的前沿信号：

- 新定理；
- 新方法；
- 新实验；
- 主结论实质变化。

一般扩写、润色、参考文献更新、元数据修正和普通勘误不算重大修订。

### 3.6 旧预印本的新期刊版本

旧预印本首次正式在线发表期刊版本时，重新进入首页，标记为 `journal-publication`。

页面同时显示预印本首次公开日期，避免把旧结果写成刚完成的新研究。

### 3.7 核心与相邻方向比例

以统一质量门槛为前提，大致保持：

- 70--80% 核心结构前沿；
- 20--30% 可解释的相邻前沿。

这不是硬配额；不得为了比例降低标准。

### 3.8 审核状态

当前公开自动内容统一标记：

- `自动整理`

它表示元数据已核对、注释受摘要约束，但不代表编辑已经完整阅读或逐句审核。

当前阶段不自动发布假装经过人工认可的阅读链和背景说明。

### 3.9 原 W28、W29 阅读链

归档重写后，原阅读链只保留在 Git 历史：

- 不建公开 legacy 页面；
- 不搬入其他公共栏目；
- 不将其包装成人工审核材料。

### 3.10 Core topics 暂停

本轮不新增或扩写 `Core topics / 核心主题`。

以后只有在编辑准备亲自审核某个具体小主题时才继续建设，GPT 不得直接生成并发布专题正文。

### 3.11 周归档只展示最终论文

公开周归档只列最终入选论文，不公开候选总数、筛选漏斗和逐篇淘汰记录。

筛选统计保存在计划文件、PR 或内部报告中。

### 3.12 先沿用 `data/editions.yml`

试运行阶段先增加少量字段：

```yaml
- paper_id: "arxiv:xxxx.xxxxx"
  signal_date: "2026-07-19"
  signal_type: "new-preprint"
  review_status: "automated"
  frontier_class: "core"
  integrable_structure: "..."
  innovation: "..."
```

候选值：

- `signal_type`: `new-preprint`, `major-revision`, `journal-publication`;
- `review_status`: 当前只使用 `automated`;
- `frontier_class`: `core`, `adjacent`。

完成回溯改写和若干期试运行后，再决定是否拆分 `data/frontier.yml`。

## 4. 关注主题

组织原则是“可积结构 + 创新”，不是固定方程名单。

### 4.1 核心结构前沿

#### 谱问题与 Lax 结构

- 新的或实质扩展的 Lax pair、零曲率表示；
- 新条件下的 direct/inverse scattering；
- 新谱对称性、奇点、分支结构和重构机制；
- monodromy、散射数据和谱不变量带来的新定理、分类或反演结果。

只有形式 Lax pair 而没有新后果，通常不收录。

#### 可积层级、Hamiltonian 与 Poisson 结构

- 新 hierarchy、正负流和约化；
- recursion operator；
- bi-/multi-Hamiltonian structure；
- Poisson pencil 和守恒律生成；
- 具有真实结构内容的矩阵、非交换和多分量推广。

#### Riemann--Hilbert 与渐近

- 新 RHP 表述；
- nonlinear steepest descent 和 \(\bar\partial\) 方法；
- soliton resolution；
- transition/critical asymptotics；
- 非零背景、边界、谱奇点、低正则和多分量问题；
- 新 Painlevé 局部模型或普适渐近机制。

#### Tau 函数、Darboux/Bäcklund 与精确解结构

优先关注：

- 非递归、binary、vectorial 或 matrix Darboux；
- 高阶谱退化的系统处理；
- KP/Toda reduction、Gram/Wronskian/Pfaffian 和 tau-function；
- 特殊多项式控制的解几何；
- 精确解的分类、分解、渐近或新动力学机制。

标准 Darboux 套用和低阶图形展示通常排除。

#### 有限带与代数几何

- 新谱曲线、divisor 或 Baker--Akhiezer 构造；
- finite-gap degeneration 和 soliton/rogue-wave limits；
- 高 genus、连续或统计极限；
- 与 modulation、stability、soliton gas 或 RHP 的新连接。

#### Painlevé 与等单值结构

- 新 isomonodromic formulation；
- discrete Painlevé；
- Painlevé 函数作为临界渐近模型；
- rational solutions 和特殊多项式的新结构；
- 与随机矩阵、正交多项式、KPZ 或非线性波的直接连接。

#### 离散可积性与可积几何

- integrable lattice equations 和结构保持离散化；
- multidimensional consistency；
- Yang--Baxter maps；
- 离散 Lax 表示；
- discrete differential/conformal geometry；
- 有意义的连续极限和结构保持数值方法。

### 4.2 可解释的相邻前沿

#### 量子可积性

- Yang--Baxter equation 和 \(R\)-matrix；
- Bethe Ansatz、transfer matrix、quantum group 和 Yangian；
- quantum spectral curve；
- thermodynamic Bethe Ansatz；
- integrable circuits、quenches 和非平衡动力学。

#### Generalized hydrodynamics 与可积统计物理

- generalized hydrodynamics；
- soliton-gas kinetic theory；
- 热力学和流体极限；
- 非平衡输运；
- integrable turbulence 和 wave kinetics；
- 微观可积性产生的可检验宏观后果。

#### 可积概率与随机矩阵

- determinantal/Pfaffian structure；
- Fredholm determinant 和 integrable kernels；
- orthogonal-polynomial RHP；
- loop equations、Painlevé 表示和精确分布；
- 可精确求解粒子系统。

可积结构必须直接参与主结果。

#### 实验、控制、反问题与数据驱动可积性

- 散射数据测量或控制；
- nonlinear Fourier methods；
- soliton tomography 和谱传感；
- 以可积变量进行 inverse design；
- 可积理论的实验验证；
- 从数据发现 Lax pair、守恒律或隐藏可积性。

可积结构必须直接参与预测、控制、重构或实验解释。

## 5. 入选和排除规则

公开论文原则上同时满足：

1. 可积性是核心而非附带背景；
2. 有清楚的新贡献；
3. 能从 primary sources 准确解释；
4. 能向目标读者说明结构联系；
5. 提供超过直接阅读 arXiv 列表的价值。

强候选通常同时具有：

- **结构创新**：新谱问题、层级、Hamiltonian 结构、RHP、tau 结构、谱曲线、Yang--Baxter 结构等；
- **新后果**：新定理、渐近规律、普适性、分类、实验、反演、控制机制或宏观动力学。

通常排除：

- 标准变换的常规应用；
- 少量低阶显式解和参数图；
- 没有新结构结论的数值展示；
- 熟悉方法几乎无概念变化地迁移；
- 可积性只在引言或背景出现；
- 无法可靠解释；
- 因方程、作者或课题组符合个人兴趣而入选。

## 6. 网站最小调整

### 首页

- 显示最近 30 天合格研究事件；
- 按 `signal_date` 倒序；
- 直接显示主要结果、可积结构和创新类型；
- 显示 `自动整理`；
- 不要求点击详细页才能理解价值；
- 不展示旧背景 filler。

### 周归档

- 按实际研究事件日期组织；
- 只展示最终论文；
- 不再自动组织旧文阅读链；
- 明确条目为自动整理；
- W28、W29 旧版本只存在于 Git 历史。

### 其他页面

- `Core topics` 暂不改；
- `Group work` 和 `Resources` 暂不改；
- `About` 在实施阶段补充选择政策和自动整理说明。

## 7. 旧论文处理

从首页移除、从公开归档移除、从 `data/papers.yml` 删除是不同操作。

- 可靠旧论文元数据可以保留用于去重；
- 未人工审核的旧背景论文不自动进入 Core topics；
- 为凑数量、重复或关系牵强的推荐从公开 edition 删除；
- 重复、错误或无法核实的记录在确认无引用后才从 registry 删除；
- 年代久远本身不是删除 bibliographic record 的理由。

## 8. 自动化政策

每日流程从“强制生成阅读链”改为“筛选前沿信号”：

1. 按结构主题广泛检索；
2. 建立内部候选池；
3. 排除常规、弱创新和无法解释的论文；
4. 在 PR 中报告筛选漏斗；
5. 只发布强的新论文；
6. 允许空缺日期；
7. 不补旧背景论文；
8. 元数据事实与人工判断分离；
9. 当前阶段只创建 reviewable PR，不自动合并，不启用 auto-merge。

## 9. 回溯筛选结果

W28、W29 的有限候选池筛选结果为：

- 原始候选：31 篇；
- 标题初筛后：24 篇；
- 摘要筛选后：15 篇；
- 最终建议：12 篇；
- 核心结构前沿：9 篇；
- 相邻前沿：3 篇；
- W28：11 篇；
- W29：1 篇。

完整名单和原因见回溯报告。该结果仍需编辑确认，尚未写入公开网站。

## 10. 实施顺序

### Phase 0：政策和筛选报告

- [x] 建立计划文件；
- [x] 写入已确定的编辑决策；
- [x] 取消个人方向和作者优先级；
- [x] 完成 W28、W29 回溯筛选报告；
- [ ] 编辑确认 12 篇建议名单。

### Phase 1：最小数据和 renderer 调整

- [ ] 在 `data/editions.yml` 增加最少字段；
- [ ] 首页改按实际日期显示前沿论文；
- [ ] 直接展示结构、创新和 `自动整理`；
- [ ] 更新 About 和归档说明。

### Phase 2：重写 W28、W29

- [ ] 应用确认后的名单；
- [ ] 从公开前沿移除旧背景 filler；
- [ ] 保留可靠 metadata 和 Git 历史；
- [ ] 完成 renderer check、registry validation 和 `mkdocs build --strict`。

### Phase 3：30 天试运行

- [ ] 用相同协议覆盖 2026-06-20 至 2026-07-19；
- [ ] 测量最近 30 天实际入选数量；
- [ ] 判断 30 天窗口是否合适；
- [ ] 评估 `data/editions.yml` 是否仍可维护；
- [ ] 决定是否建立 `data/frontier.yml`。

## 11. 当前仍需确认

1. W28、W29 的 12 篇建议名单是否增删；
2. 最近 30 天窗口的实际数量是否适合首页；
3. 旧预印本新期刊版本是否在首页停留完整 30 天；
4. `自动整理` 是逐篇显示，还是页面顶部统一说明；
5. 试运行后是否拆分 frontier 数据文件。

在回溯名单确认前，不改首页、不重写归档、不改自动化、不新增 Core topics。
