# 可积系统研究雷达调整计划

**状态：** 已确认主要编辑政策；等待回溯筛选结果审核后实施  
**最后更新：** 2026-07-19

## 1. 调整的原因

当前网站把几种性质不同的内容混在了一起：

1. 最近公开的研究成果；
2. 自动化流程发现的论文；
3. 为了组成阅读链而补入的旧论文；
4. GPT 根据摘要生成的背景说明；
5. 编辑本人真正读过并认可的内容。

这种混合会产生两个直接后果：

- 一篇多年以前的论文因为今天被推荐而排到首页前面，看起来像“最新研究”；
- 一段自动生成的阅读建议容易被理解为编辑本人已经审核和认可的判断。

调整的目标不是扩大网站规模，而是让每条内容的时间含义和编辑权威程度清楚。

## 2. 网站定位

公开网站定位为：

> 面向熟悉可积 PDE 和谱方法的研究者，有选择地追踪新的可积结构，以及这些结构带来的新数学或物理结果。

网站不应成为：

- arXiv 最新列表的中文镜像；
- 整个可积系统领域的百科全书；
- 必须每天完成固定篇数的推荐器；
- 未经人工审核的个人阅读笔记集合；
- 把自动生成的背景链包装成人工综述的页面。

每篇进入公开前沿流的论文原则上必须回答：

1. **论文引入、揭示、扩展或使用了什么新的可积结构？**
2. **这种结构使以前做不到的什么结果成为可能？**

两点都无法清楚回答时，通常不应公开收录。

## 3. 已确定的编辑政策

### 3.1 不保留任何个人方向优先级

DNLS、Gerdjikov--Ivanov、Fokas--Lenells、coupled NLS、特定作者或课题组都不再获得额外优先级。

方程、作者、合作关系和编辑个人兴趣不能成为入选理由。所有候选论文使用同一套“可积结构 + 创新后果”标准。

### 3.2 目标读者

主要读者是已经熟悉可积 PDE、Lax pair、谱方法、反散射和基本非线性波理论的研究者。

因此页面不需要从零解释每个基础概念，但对量子可积性、可积概率等相邻方向，必须清楚说明其与经典可积结构的桥梁。

### 3.3 新旧由论文事件决定

公开排序依据实际研究事件日期：

- 首次公开日期；
- 重大修订日期；
- 首次正式在线期刊发表日期。

本站何时发现或推荐论文只属于编辑历史，不参与首页排序。

### 3.4 首页暂定覆盖最近 30 天

首页先试行最近 30 天时间窗口，再根据实际合格论文数量决定是否缩短或延长。

时间窗口内没有达到标准的论文时允许不更新；不使用旧论文补数量。

### 3.5 重大修订的定义

只有下列变化可以作为新的前沿信号：

- 新定理；
- 新方法；
- 新实验；
- 主结论发生实质变化。

一般扩写、文字润色、参考文献更新、元数据修正和普通勘误不算重大修订。

### 3.6 旧预印本的新期刊版本

旧预印本首次正式在线发表期刊版本时，重新进入首页，标记为 `journal-publication`。

这表示“正式发表”本身是一个新的研究事件，但页面必须同时显示原预印本日期，避免把旧结果误写成刚完成的新研究。

### 3.7 核心与相邻方向的比例

以质量门槛为前提，公开流大致保持：

- 70--80% 核心结构前沿；
- 20--30% 可解释的相邻前沿。

这不是硬配额。某一时段没有足够强的相邻论文时，不为满足比例而降低标准。

### 3.8 内容状态

自动化生成并经过元数据核对、摘要约束的条目公开标记为：

- `自动整理`

该标签表示内容可以作为发现线索，但不等于编辑已经逐句审核或完整阅读论文。

人工审校状态以后再增加；当前阶段不自动发布任何假装经过人工认可的阅读链或背景说明。

### 3.9 原始 W28、W29 阅读链

回溯改写后，原来的阅读链只保留在 Git 历史中：

- 不建立 legacy 公共页面；
- 不搬到新的公开栏目；
- 不将其包装为人工审核材料。

### 3.10 Core topics 暂停建设

本轮不新增或扩写 `Core topics / 核心主题`。

以后只有在编辑准备亲自审核某个具体小主题时才继续建设，GPT 不得直接生成并发布专题正文。

### 3.11 周归档只展示最终结果

公开周归档只列最终入选论文，不公开候选总数、筛选漏斗和逐篇淘汰记录。

筛选统计保存在计划、PR 或内部报告中，作为编辑审计材料。

### 3.12 先沿用 `data/editions.yml`

试运行阶段不立即新增 `data/frontier.yml`。先在现有 edition entry 中增加最少字段：

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

完成一次回溯改写和若干期日常试运行后，再决定是否拆分独立的 `data/frontier.yml`。

## 4. 关注主题

组织原则是“可积结构 + 创新”，而不是固定方程名单。

### 4.1 核心结构前沿

#### 谱问题与 Lax 结构

- 新的或实质扩展的 Lax pair、零曲率表示；
- 新条件下的 direct/inverse scattering；
- 新的谱对称性、奇点、分支结构和重构机制；
- monodromy、散射数据和谱不变量带来的新定理、分类或反演结果。

只有形式 Lax pair 而没有新后果，通常不收录。

#### 可积层级、Hamiltonian 与 Poisson 结构

- 新 hierarchy、正负流和约化；
- recursion operator；
- bi-/multi-Hamiltonian structure；
- Poisson pencil 和系统守恒律生成；
- 具有真实结构内容的矩阵、非交换和多分量推广。

#### Riemann--Hilbert 与渐近分析

- 新 RHP 表述；
- nonlinear steepest descent 和 \(\bar\partial\) 方法；
- soliton resolution；
- transition/critical asymptotics；
- 非零背景、边界、谱奇点、低正则和多分量问题；
- 新的 Painlevé 局部模型或普适渐近机制。

#### Tau 函数、Darboux/Bäcklund 与精确解结构

优先关注：

- 非递归、binary、vectorial 或 matrix Darboux 结构；
- 高阶谱退化的系统处理；
- KP/Toda reduction、Gram/Wronskian/Pfaffian 和 tau-function 结构；
- 特殊多项式控制的解几何；
- 精确解的分类、分解、渐近或新动力学机制。

把标准 Darboux 套到相似方程并主要展示低阶图形，通常排除。

#### 有限带与代数几何结构

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

- integrable lattice equations 和保持结构的离散化；
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

必须说明这些对象与经典谱、散射和守恒结构的对应或区别。

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

仅仅属于随机矩阵或 KPZ 主题并不自动入选；可积结构必须直接参与主结果。

#### 实验、控制、反问题与数据驱动可积性

- 散射数据的测量或控制；
- nonlinear Fourier methods；
- soliton tomography 和谱传感；
- 以可积变量进行 inverse design；
- 可积理论的实验验证；
- 从数据发现 Lax pair、守恒律或隐藏可积性。

可积结构必须直接参与预测、控制、重构或实验解释。

## 5. 入选和排除标准

公开论文原则上同时满足：

1. 可积性是论文核心而非附带背景；
2. 有清楚的新贡献；
3. 能从当前 primary sources 准确解释；
4. 能向目标读者说明结构联系；
5. 提供超过直接阅读 arXiv 列表的编辑价值。

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
- 主要因为方程、作者或课题组与编辑兴趣相符而入选。

## 6. 网站最小调整方向

### 6.1 首页

首页应成为真正的最新前沿：

- 只显示最近 30 天内合格的研究事件；
- 按 `signal_date` 倒序；
- 直接显示主要结果、可积结构和创新类型；
- 显示 `自动整理`；
- 不要求点击详细页才能理解论文价值；
- 不展示为补数量而加入的旧背景论文。

### 6.2 周归档

周归档记录最终公开前沿流：

- 按实际研究事件日期组织；
- 只展示最终入选论文；
- 不再组织自动生成的旧文阅读链；
- 明确说明条目为自动整理而非逐篇人工审校；
- W28、W29 重写后，旧版本只存在于 Git 历史。

### 6.3 其他页面

- `Core topics` 暂不改动；
- `Group work` 和 `Resources` 暂不改动；
- `About` 在实施阶段补充选择政策、元数据政策和自动整理说明。

## 7. 旧论文处理

从首页移除、从公开归档移除、从 `data/papers.yml` 删除是三种不同操作。

- 可靠的旧论文元数据可以保留用于去重；
- 未经人工审核的旧背景论文不自动进入 Core topics；
- 为凑数量、重复或关系牵强的推荐从公开 edition 中删除；
- 重复、错误或无法核实的记录在确认无引用后才从 registry 删除；
- 年代久远本身不是删除 bibliographic record 的理由。

## 8. 自动化政策

每日流程应从“强制生成阅读链”改为“筛选前沿信号”：

1. 按约定结构主题广泛检索；
2. 建立内部候选池；
3. 排除常规、弱创新和无法解释的论文；
4. 在 PR 中报告筛选漏斗；
5. 只发布强的新论文；
6. 允许空缺日期；
7. 不补旧背景论文；
8. 元数据事实与人工判断分离；
9. 当前阶段只创建 reviewable PR，不自动合并，不启用 auto-merge。

## 9. 实施顺序

### Phase 0：政策文件

- [x] 建立计划文件；
- [x] 写入已确定的编辑决策；
- [x] 取消个人方向和作者优先级。

### Phase 1：W28、W29 回溯筛选报告

- [x] 按扩展范围重新建立候选池；
- [x] 报告原始候选、标题初筛、摘要筛选和最终建议数量；
- [x] 列出最终建议与淘汰原因；
- [ ] 由编辑确认最终名单。

这一阶段不修改公开网站。

### Phase 2：最小数据和 renderer 调整

- [ ] 在 `data/editions.yml` 增加最少字段；
- [ ] 首页改按实际日期显示前沿论文；
- [ ] 直接展示结构、创新和 `自动整理`；
- [ ] 更新 About 和归档说明。

### Phase 3：重写 W28、W29

- [ ] 应用确认后的名单；
- [ ] 从公开前沿页移除旧背景 filler；
- [ ] 保留可靠 metadata 和 Git 历史；
- [ ] 完成 renderer check、registry validation 和 `mkdocs build --strict`。

### Phase 4：试运行后评估

- [ ] 观察最近 30 天最终入选数量；
- [ ] 决定 30 天窗口是否合适；
- [ ] 评估 `data/editions.yml` 是否仍可维护；
- [ ] 再决定是否建立 `data/frontier.yml`。

## 10. 当前仍需确认的问题

回溯报告完成后只剩以下问题需要决定：

1. W28、W29 的 11 篇建议名单是否需要增删；
2. 最近 30 天窗口产生的实际论文数量是否适合首页；
3. 旧预印本新期刊版本是否需要在首页停留完整 30 天，还是使用较短展示期；
4. `自动整理` 应显示在每篇条目，还是页面顶部统一说明并仅对例外状态加标签；
5. 试运行后是否需要把 frontier events 从 `data/editions.yml` 分离。

## 11. 当前下一步

在编辑确认回溯筛选报告前：

- 不改首页；
- 不重写 W28、W29；
- 不改自动化；
- 不新增 Core topics；
- 不合并任何实施性改动。
