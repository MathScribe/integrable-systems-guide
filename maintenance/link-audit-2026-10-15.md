# 2026-10-15 链接与书目体检

本次只维护已有内容，不新增推荐，不改变公开事件日期、方向或阅读笔记。记录以下核查范围、已确认修正与未确认事项；HTTP 成功不等于页面内容和论文身份已逐项人工确认。

## 覆盖与结果

- 428 条书目完成身份去重检查；DOI、arXiv ID、规范化标题均无重复，近似标题阈值 0.94 也未产生待合并项。
- 410 条 arXiv 记录均通过官方 API 取得版本记录。已标记的两篇撤稿记录仍保留书目身份，且未出现在公开推荐中。
- 864 个源文件中的独立外链完成请求：841 个 HTTP 200、18 个 403、4 个 202、1 个 TLS 验证失败。没有确认的 404/410，因此本次没有删除或猜测替换链接。
- 已有 DOI 的 98 条记录查询 Crossref：96 条成功、2 条 429；其中 APS 论文的元数据另外通过出版社页面确认。
- 没有 DOI 的 330 条记录查询出版信息：282 条成功响应、48 条 429。查询无精确匹配不等于确认“尚未发表”。
- 17 个新增期刊 DOI 均另外访问了解析目标：13 个 HTTP 200、4 个 403；其书目由出版社登记的 Crossref 记录确认，作者名单与题名已比对。
- 110 条已有记录有实质字段更正：补 32 条投稿日期及对应 UTC 时间戳、64 条缺失版本号、更新 13 条已有版本号；补 17 个正式期刊 DOI、16 条原有期刊记录的缺失年份，并补充可确认的卷期页码等。字段计数彼此重叠。
- 首页仍为 293 条公开记录。本书目补丁不改公开事件日期；前置日期补丁已将 RST-PINN 条目的首次上线日修正为 2026-10-12。

## 日期与出版类型的处理

- [RST-PINN / Wave Motion 103858](https://www.sciencedirect.com/science/article/pii/S0165212526001605)：本机 Zotero 保存的 ScienceDirect 页面明确显示 “Available online 12 October 2026”，citation_online_date 与 citation_publication_date 均为 2026/10/12；已采用 2026-10-12。Crossref 仅提供卷期月份，但本地出版社快照补齐了首次上线证据，不再列为未确认事项。
- [Taxonomy of integrable and ground-state solvable models](https://journals.aps.org/prb/abstract/10.1103/g7hk-tlq1)：Crossref 429，APS 页面 citation 元数据确认 2026-06-24、113(23)、235151，已据此补齐。
- [DNLS: Global Well-Posedness and Soliton Resolution](https://doi.org/10.1090/qam/1553)：保留 Crossref 首次在线日 2019-09-16；卷 78(1) 的书目年份使用 2020，见 [AMS 期刊目标](https://pubs.ams.org/journals/qam/2020-78-01/S0033-569X-2019-01553-2) 和[作者机构记录](https://scholars.uky.edu/es/publications/the-derivative-nonlinear-schrodinger-equation-global-well-posedne/)。
- OCNMP 的 Crossref 卷号为截断的 “Special Issue in honour of...”；未把该字符串当卷号写入。JSIAM 的 issue=0 未作为有效期号展示。
- Crossref 的 posted-content（包括 SSRN、Preprints、Optica Open）未写作期刊 DOI。
- [Singularity Interactions for Lattice Equations: Introducing the Taishi](https://doi.org/10.1007/978-981-95-4526-1_16) 确认匹配书章而非期刊文章；现有模型缺少书名／章节字段，本次未强行填入 journal。需要后续明确非期刊书目模型。
- arXiv:2411.18685 的预印本标题与 SciPost 正式标题不同，但 arXiv DOI 与作者身份一致；保持现有预印本标题，不当作错链。

## 已确认修正

| 条目 | 本次更正字段（省略核验日期） | 主要证据 |
| --- | --- | --- |
| [arxiv:2607.04756](<https://arxiv.org/abs/2607.04756>) | submitted, submitted_at, updated, version, published | [arXiv](https://arxiv.org/abs/2607.04756) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/1751-8121/aea3c6>) |
| [arxiv:2607.01348](<https://arxiv.org/abs/2607.01348>) | submitted, submitted_at, updated, version, doi, journal, volume, issue, year, published, article_number | [arXiv](https://arxiv.org/abs/2607.01348) · [出版社登记元数据](<https://api.crossref.org/works/10.1111/sapm.70307>) |
| [arxiv:2605.28856](<https://arxiv.org/abs/2605.28856>) | submitted, submitted_at, updated, version, journal, volume, issue, year, published, pages | [arXiv](https://arxiv.org/abs/2605.28856) · [出版社登记元数据](<https://api.crossref.org/works/10.58997/ejde.2026.37>) |
| [arxiv:2602.13589](<https://doi.org/10.1007/s00208-026-03322-x>) | volume, issue, published, article_number | [arXiv](https://arxiv.org/abs/2602.13589) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s00208-026-03322-x>) |
| [doi:10.1111/j.1467-9590.2012.00568.x](<https://doi.org/10.1111/j.1467-9590.2012.00568.x>) | submitted, submitted_at, updated, version, issue, published | [arXiv](https://arxiv.org/abs/1205.4369) · [出版社登记元数据](<https://api.crossref.org/works/10.1111/j.1467-9590.2012.00568.x>) |
| [doi:10.1016/j.cnsns.2015.08.023](<https://doi.org/10.1016/j.cnsns.2015.08.023>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/1407.5194) |
| [arxiv:0808.1534](<https://arxiv.org/abs/0808.1534>) | doi, journal, volume, issue, year, pages | [arXiv](https://arxiv.org/abs/0808.1534) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.physd.2008.07.005>) |
| [doi:10.1088/1361-6544/accfdf](<https://doi.org/10.1088/1361-6544/accfdf>) | volume, issue, published, pages | [arXiv](https://arxiv.org/abs/2210.01350) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/1361-6544/accfdf>) |
| [arxiv:2304.06541](<https://arxiv.org/abs/2304.06541>) | doi, journal, volume, issue, year, published, article_number | [arXiv](https://arxiv.org/abs/2304.06541) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/physreve.109.061001>) |
| [doi:10.1088/1361-6544/abcc4b](<https://doi.org/10.1088/1361-6544/abcc4b>) | issue, published | [arXiv](https://arxiv.org/abs/2104.00154) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/1361-6544/abcc4b>) |
| [arxiv:1905.02866](<https://arxiv.org/abs/1905.02866>) | doi, journal, volume, issue, year, published, pages | [arXiv](https://arxiv.org/abs/1905.02866) · [出版社登记元数据](<https://api.crossref.org/works/10.1090/qam/1553>) |
| [doi:10.1088/1751-8113/43/43/434023](<https://doi.org/10.1088/1751-8113/43/43/434023>) | issue, published | [arXiv](https://arxiv.org/abs/0911.4802) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/1751-8113/43/43/434023>) |
| [arxiv:2606.10037](<https://arxiv.org/abs/2606.10037>) | doi, journal, year, article_number | [arXiv](https://arxiv.org/abs/2606.10037) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.geomphys.2026.106019>) |
| [arxiv:2507.21660](<https://arxiv.org/abs/2507.21660>) | doi, journal, volume, year, article_number | [arXiv](https://arxiv.org/abs/2507.21660) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.physd.2026.135119>) |
| [doi:10.1111/sapm.12287](<https://doi.org/10.1111/sapm.12287>) | volume, issue, published, pages | [arXiv](https://arxiv.org/abs/1812.04212) · [出版社登记元数据](<https://api.crossref.org/works/10.1111/sapm.12287>) |
| [doi:10.1088/0305-4470/35/36/310](<https://doi.org/10.1088/0305-4470/35/36/310>) | issue, published | [arXiv](https://arxiv.org/abs/nlin/0105053) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/0305-4470/35/36/310>) |
| [arxiv:2607.09333](<https://arxiv.org/abs/2607.09333>) | updated, version | [arXiv](https://arxiv.org/abs/2607.09333) |
| [arxiv:2105.08412](<https://arxiv.org/abs/2105.08412>) | doi, journal, volume, issue, year, published, pages | [arXiv](https://arxiv.org/abs/2105.08412) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s10255-024-1109-4>) |
| [doi:10.1080/14029251.2015.996438](<https://doi.org/10.1080/14029251.2015.996438>) | published | [arXiv](https://arxiv.org/abs/1501.07634) · [出版社登记元数据](<https://api.crossref.org/works/10.1080/14029251.2015.996438>) |
| [arxiv:2211.07014](<https://arxiv.org/abs/2211.07014>) | doi, journal, volume, issue, year, published, pages | [arXiv](https://arxiv.org/abs/2211.07014) · [出版社登记元数据](<https://api.crossref.org/works/10.1111/sapm.12558>) |
| [doi:10.1016/j.physleta.2021.127793](<https://doi.org/10.1016/j.physleta.2021.127793>) | volume | [arXiv](https://arxiv.org/abs/2106.14252) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.physleta.2021.127793>) |
| [arxiv:2110.01047](<https://arxiv.org/abs/2110.01047>) | doi, journal, volume, year, article_number | [arXiv](https://arxiv.org/abs/2110.01047) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.padiff.2022.100292>) |
| [arxiv:1510.00480](<https://arxiv.org/abs/1510.00480>) | doi, journal, volume, issue, year, published, article_number | [arXiv](https://arxiv.org/abs/1510.00480) · [出版社登记元数据](<https://api.crossref.org/works/10.1063/1.4974018>) |
| [doi:10.1103/PhysRevLett.134.193804](<https://doi.org/10.1103/PhysRevLett.134.193804>) | issue | [arXiv](https://arxiv.org/abs/2409.16090) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/PhysRevLett.134.193804>) |
| [arxiv:2508.17534](<https://arxiv.org/abs/2508.17534>) | updated, version | [arXiv](https://arxiv.org/abs/2508.17534) |
| [doi:10.1016/j.physd.2025.134706](<https://doi.org/10.1016/j.physd.2025.134706>) | volume | [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.physd.2025.134706>) |
| [doi:10.1016/j.physd.2024.134111](<https://doi.org/10.1016/j.physd.2024.134111>) | updated | [arXiv](https://arxiv.org/abs/2307.02008) |
| [doi:10.1007/JHEP07(2026)120](<https://doi.org/10.1007/JHEP07(2026)120>) | issue | [arXiv](https://arxiv.org/abs/2510.10519) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/JHEP07(2026)120>) |
| [doi:10.1007/JHEP07(2026)123](<https://doi.org/10.1007/JHEP07(2026)123>) | issue | [arXiv](https://arxiv.org/abs/2604.26452) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/JHEP07(2026)123>) |
| [doi:10.1007/s10955-026-03663-6](<https://doi.org/10.1007/s10955-026-03663-6>) | issue | [arXiv](https://arxiv.org/abs/2510.22120) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s10955-026-03663-6>) |
| [arxiv:2606.22438](<https://arxiv.org/abs/2606.22438>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.22438) |
| [arxiv:2606.24925](<https://arxiv.org/abs/2606.24925>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.24925) |
| [arxiv:2606.23167](<https://arxiv.org/abs/2606.23167>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.23167) |
| [arxiv:2606.24662](<https://arxiv.org/abs/2606.24662>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.24662) |
| [arxiv:2606.24273](<https://arxiv.org/abs/2606.24273>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.24273) |
| [doi:10.1103/hvzz-8zmt](<https://doi.org/10.1103/hvzz-8zmt>) | version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2511.03947) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/hvzz-8zmt>) |
| [arxiv:2606.25846](<https://arxiv.org/abs/2606.25846>) | version | [arXiv](https://arxiv.org/abs/2606.25846) |
| [arxiv:2606.25802](<https://arxiv.org/abs/2606.25802>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.25802) |
| [doi:10.1103/g7hk-tlq1](<https://doi.org/10.1103/g7hk-tlq1>) | updated, version, year, volume, issue, article_number | [arXiv](https://arxiv.org/abs/2602.22315) · [APS](https://journals.aps.org/prb/abstract/10.1103/g7hk-tlq1) |
| [arxiv:2606.27125](<https://arxiv.org/abs/2606.27125>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.27125) |
| [arxiv:2606.26526](<https://arxiv.org/abs/2606.26526>) | version | [arXiv](https://arxiv.org/abs/2606.26526) |
| [arxiv:2606.28579](<https://arxiv.org/abs/2606.28579>) | version | [arXiv](https://arxiv.org/abs/2606.28579) |
| [arxiv:2606.28250](<https://arxiv.org/abs/2606.28250>) | submitted, submitted_at, updated, version, doi, journal, volume, issue, year, published, article_number | [arXiv](https://arxiv.org/abs/2606.28250) · [出版社登记元数据](<https://api.crossref.org/works/10.1111/sapm.70302>) |
| [arxiv:2606.29103](<https://arxiv.org/abs/2606.29103>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.29103) |
| [arxiv:2606.29263](<https://arxiv.org/abs/2606.29263>) | updated, version, doi, journal, year, published, article_number | [arXiv](https://arxiv.org/abs/2606.29263) · [出版社登记元数据](<https://api.crossref.org/works/10.46298/ocnmp.18664>) |
| [arxiv:2606.29156](<https://arxiv.org/abs/2606.29156>) | version | [arXiv](https://arxiv.org/abs/2606.29156) |
| [arxiv:2606.30717](<https://arxiv.org/abs/2606.30717>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2606.30717) |
| [arxiv:2607.01493](<https://arxiv.org/abs/2607.01493>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.01493) |
| [arxiv:2607.01545](<https://arxiv.org/abs/2607.01545>) | version | [arXiv](https://arxiv.org/abs/2607.01545) |
| [arxiv:2607.02093](<https://arxiv.org/abs/2607.02093>) | version | [arXiv](https://arxiv.org/abs/2607.02093) |
| [arxiv:2607.03555](<https://arxiv.org/abs/2607.03555>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.03555) |
| [doi:10.1103/n2hm-lk94](<https://doi.org/10.1103/n2hm-lk94>) | version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2504.20292) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/n2hm-lk94>) |
| [arxiv:2607.05681](<https://arxiv.org/abs/2607.05681>) | version | [arXiv](https://arxiv.org/abs/2607.05681) |
| [arxiv:2607.06119](<https://arxiv.org/abs/2607.06119>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.06119) |
| [arxiv:2504.05200](<https://doi.org/10.1112/jlms.70618>) | version, volume | [arXiv](https://arxiv.org/abs/2504.05200) · [出版社登记元数据](<https://api.crossref.org/works/10.1112/jlms.70618>) |
| [arxiv:2607.06942](<https://arxiv.org/abs/2607.06942>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.06942) |
| [arxiv:2607.06980](<https://arxiv.org/abs/2607.06980>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.06980) |
| [arxiv:2607.07345](<https://arxiv.org/abs/2607.07345>) | version, doi, journal, volume, year, article_number | [arXiv](https://arxiv.org/abs/2607.07345) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.chaos.2026.119252>) |
| [arxiv:2607.07617](<https://arxiv.org/abs/2607.07617>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.07617) |
| [doi:10.1103/y66t-t8zw](<https://doi.org/10.1103/y66t-t8zw>) | updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2508.20713) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/y66t-t8zw>) |
| [arxiv:2607.08901](<https://arxiv.org/abs/2607.08901>) | version | [arXiv](https://arxiv.org/abs/2607.08901) |
| [arxiv:2607.09180](<https://arxiv.org/abs/2607.09180>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2607.09180) |
| [arxiv:2607.15132](<https://arxiv.org/abs/2607.15132>) | updated, version | [arXiv](https://arxiv.org/abs/2607.15132) |
| [arxiv:2607.15013](<https://arxiv.org/abs/2607.15013>) | version | [arXiv](https://arxiv.org/abs/2607.15013) |
| [arxiv:2607.12142](<https://arxiv.org/abs/2607.12142>) | version | [arXiv](https://arxiv.org/abs/2607.12142) |
| [arxiv:2607.08536](<https://arxiv.org/abs/2607.08536>) | version | [arXiv](https://arxiv.org/abs/2607.08536) |
| [arxiv:2607.04075](<https://arxiv.org/abs/2607.04075>) | version | [arXiv](https://arxiv.org/abs/2607.04075) |
| [arxiv:2607.02359](<https://arxiv.org/abs/2607.02359>) | version | [arXiv](https://arxiv.org/abs/2607.02359) |
| [arxiv:2607.00594](<https://doi.org/10.1007/s00220-026-05724-z>) | version, issue | [arXiv](https://arxiv.org/abs/2607.00594) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s00220-026-05724-z>) |
| [arxiv:2607.00231](<https://arxiv.org/abs/2607.00231>) | version | [arXiv](https://arxiv.org/abs/2607.00231) |
| [arxiv:2606.27261](<https://arxiv.org/abs/2606.27261>) | version | [arXiv](https://arxiv.org/abs/2606.27261) |
| [arxiv:2606.27186](<https://arxiv.org/abs/2606.27186>) | version | [arXiv](https://arxiv.org/abs/2606.27186) |
| [arxiv:2606.23803](<https://arxiv.org/abs/2606.23803>) | version | [arXiv](https://arxiv.org/abs/2606.23803) |
| [arxiv:2606.22004](<https://arxiv.org/abs/2606.22004>) | version | [arXiv](https://arxiv.org/abs/2606.22004) |
| [arxiv:2607.13673](<https://arxiv.org/abs/2607.13673>) | updated, version | [arXiv](https://arxiv.org/abs/2607.13673) |
| [arxiv:2606.18701](<https://arxiv.org/abs/2606.18701>) | updated, version | [arXiv](https://arxiv.org/abs/2606.18701) |
| [arxiv:2606.17238](<https://arxiv.org/abs/2606.17238>) | volume | [arXiv](https://arxiv.org/abs/2606.17238) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.cnsns.2026.110892>) |
| [arxiv:2606.16789](<https://arxiv.org/abs/2606.16789>) | updated, version, doi, journal, year, published, article_number | [arXiv](https://arxiv.org/abs/2606.16789) · [出版社登记元数据](<https://api.crossref.org/works/10.46298/ocnmp.18568>) |
| [doi:10.1007/s10955-026-03637-8](<https://doi.org/10.1007/s10955-026-03637-8>) | submitted, submitted_at, updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2511.07212) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s10955-026-03637-8>) |
| [doi:10.1007/jhep06(2026)173](<https://doi.org/10.1007/JHEP06(2026)173>) | submitted, submitted_at, updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2601.20960) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/JHEP06(2026)173>) |
| [doi:10.21468/scipostphys.20.6.164](<https://doi.org/10.21468/SciPostPhys.20.6.164>) | submitted, submitted_at, updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2512.07742) · [出版社登记元数据](<https://api.crossref.org/works/10.21468/SciPostPhys.20.6.164>) |
| [doi:10.1088/1751-8121/ae767e](<https://doi.org/10.1088/1751-8121/ae767e>) | volume, issue, year, pages | [出版社登记元数据](<https://api.crossref.org/works/10.1088/1751-8121/ae767e>) |
| [doi:10.46298/ocnmp.18125](<https://doi.org/10.46298/ocnmp.18125>) | submitted, submitted_at, updated, version, year, article_number | [arXiv](https://arxiv.org/abs/2604.01743) · [出版社登记元数据](<https://api.crossref.org/works/10.46298/ocnmp.18125>) |
| [doi:10.1209/0295-5075/ae7152](<https://doi.org/10.1209/0295-5075/ae7152>) | volume, issue, year, pages | [出版社登记元数据](<https://api.crossref.org/works/10.1209/0295-5075/ae7152>) |
| [doi:10.46298/ocnmp.18295](<https://doi.org/10.46298/ocnmp.18295>) | submitted, submitted_at, updated, version, year, article_number | [arXiv](https://arxiv.org/abs/2605.22565) · [出版社登记元数据](<https://api.crossref.org/works/10.46298/ocnmp.18295>) |
| [doi:10.1137/25m1764062](<https://doi.org/10.1137/25M1764062>) | volume, issue, year, pages | [出版社登记元数据](<https://api.crossref.org/works/10.1137/25M1764062>) |
| [doi:10.1007/s11005-026-02119-y](<https://doi.org/10.1007/s11005-026-02119-y>) | submitted, submitted_at, updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2601.15841) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s11005-026-02119-y>) |
| [doi:10.1103/99hb-q8bd](<https://doi.org/10.1103/99hb-q8bd>) | submitted, submitted_at, updated, version | [arXiv](https://arxiv.org/abs/2602.11288) |
| [doi:10.1088/1361-6544/ae7fe7](<https://doi.org/10.1088/1361-6544/ae7fe7>) | submitted, submitted_at, updated, version, volume, issue, year, pages | [arXiv](https://arxiv.org/abs/2507.12051) · [出版社登记元数据](<https://api.crossref.org/works/10.1088/1361-6544/ae7fe7>) |
| [doi:10.1007/s10231-026-01703-2](<https://doi.org/10.1007/s10231-026-01703-2>) | submitted, submitted_at, updated, version, year | [arXiv](https://arxiv.org/abs/2504.21678) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/s10231-026-01703-2>) |
| [doi:10.1103/vbsx-xyjm](<https://doi.org/10.1103/vbsx-xyjm>) | submitted, submitted_at, updated, version, volume, issue, year, article_number | [arXiv](https://arxiv.org/abs/2603.24832) · [出版社登记元数据](<https://api.crossref.org/works/10.1103/vbsx-xyjm>) |
| [arxiv:2607.15670](<https://arxiv.org/abs/2607.15670>) | version | [arXiv](https://arxiv.org/abs/2607.15670) |
| [arxiv:2607.15237](<https://arxiv.org/abs/2607.15237>) | version | [arXiv](https://arxiv.org/abs/2607.15237) |
| [arxiv:2607.17749](<https://arxiv.org/abs/2607.17749>) | updated, version | [arXiv](https://arxiv.org/abs/2607.17749) |
| [arxiv:2607.17613](<https://arxiv.org/abs/2607.17613>) | updated, version | [arXiv](https://arxiv.org/abs/2607.17613) |
| [doi:10.1515/zna-2026-0116](<https://doi.org/10.1515/zna-2026-0116>) | volume, issue, pages | [出版社登记元数据](<https://api.crossref.org/works/10.1515/zna-2026-0116>) |
| [arxiv:2607.29373](<https://arxiv.org/abs/2607.29373>) | updated, version | [arXiv](https://arxiv.org/abs/2607.29373) |
| [arxiv:2608.01878](<https://arxiv.org/abs/2608.01878>) | updated, version | [arXiv](https://arxiv.org/abs/2608.01878) |
| [arxiv:2608.04850](<https://arxiv.org/abs/2608.04850>) | updated, version | [arXiv](https://arxiv.org/abs/2608.04850) |
| [arxiv:2607.24920](<https://arxiv.org/abs/2607.24920>) | updated, version | [arXiv](https://arxiv.org/abs/2607.24920) |
| [doi:10.1007/JHEP08(2026)081](<https://doi.org/10.1007/JHEP08(2026)081>) | issue | [arXiv](https://arxiv.org/abs/2512.14059) · [出版社登记元数据](<https://api.crossref.org/works/10.1007/JHEP08(2026)081>) |
| [arxiv:2608.17837](<https://arxiv.org/abs/2608.17837>) | updated, version | [arXiv](https://arxiv.org/abs/2608.17837) |
| [arxiv:2608.31080](<https://arxiv.org/abs/2608.31080>) | updated, version | [arXiv](https://arxiv.org/abs/2608.31080) |
| [arxiv:2609.00517](<https://arxiv.org/abs/2609.00517>) | updated, version | [arXiv](https://arxiv.org/abs/2609.00517) |
| [arxiv:2609.02765](<https://arxiv.org/abs/2609.02765>) | updated, version | [arXiv](https://arxiv.org/abs/2609.02765) |
| [arxiv:2606.14541](<https://doi.org/10.1140/epjc/s10052-026-16262-2>) | issue | [arXiv](https://arxiv.org/abs/2606.14541) · [出版社登记元数据](<https://api.crossref.org/works/10.1140/epjc/s10052-026-16262-2>) |
| [arxiv:2609.04595](<https://arxiv.org/abs/2609.04595>) | doi, journal, volume, year, pages | [arXiv](https://arxiv.org/abs/2609.04595) · [出版社登记元数据](<https://api.crossref.org/works/10.14495/jsiaml.18.89>) |
| [arxiv:2609.06217](<https://arxiv.org/abs/2609.06217>) | doi, journal, volume, issue, year, published, pages | [arXiv](https://arxiv.org/abs/2609.06217) · [出版社登记元数据](<https://api.crossref.org/works/10.1134/s1995080223050517>) |
| [arxiv:2609.07588](<https://arxiv.org/abs/2609.07588>) | updated, version | [arXiv](https://arxiv.org/abs/2609.07588) |
| [arxiv:2609.31475](<https://arxiv.org/abs/2609.31475>) | doi, journal, volume, year, article_number | [arXiv](https://arxiv.org/abs/2609.31475) · [出版社登记元数据](<https://api.crossref.org/works/10.1016/j.optlastec.2026.116587>) |

## 外链访问仍待确认

以下链接全部保留。403 是访问限制；202 未提供可确认的完整页面；TLS 错误可能与本机信任链有关，不足以证明站点失效。下一步可用正常浏览器或校园网络核对；不关闭 TLS 验证，也不改网络配置。

| 链接 | 结果 |
| --- | --- |
| [访问原链接](<https://doi.org/10.1002/lpor.71994>) — `https://doi.org/10.1002/lpor.71994` | 403 |
| [访问原链接](<https://doi.org/10.1063/5.0331826>) — `https://doi.org/10.1063/5.0331826` | 403 |
| [访问原链接](<https://doi.org/10.1063/5.0336825>) — `https://doi.org/10.1063/5.0336825` | 403 |
| [访问原链接](<https://doi.org/10.1098/rspa.2018.0806>) — `https://doi.org/10.1098/rspa.2018.0806` | 403 |
| [访问原链接](<https://doi.org/10.1111/j.1467-9590.2012.00568.x>) — `https://doi.org/10.1111/j.1467-9590.2012.00568.x` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.12287>) — `https://doi.org/10.1111/sapm.12287` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.70263>) — `https://doi.org/10.1111/sapm.70263` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.70314>) — `https://doi.org/10.1111/sapm.70314` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.70318>) — `https://doi.org/10.1111/sapm.70318` | 403 |
| [访问原链接](<https://doi.org/10.1112/jlms.70618>) — `https://doi.org/10.1112/jlms.70618` | 403 |
| [访问原链接](<https://doi.org/10.1112/jlms.70728>) — `https://doi.org/10.1112/jlms.70728` | 403 |
| [访问原链接](<https://doi.org/10.1137/25M1764062>) — `https://doi.org/10.1137/25M1764062` | 403 |
| [访问原链接](<https://doi.org/10.1515/forum-2025-0485>) — `https://doi.org/10.1515/forum-2025-0485` | 202 |
| [访问原链接](<https://doi.org/10.1515/jiip-2026-0048>) — `https://doi.org/10.1515/jiip-2026-0048` | 202 |
| [访问原链接](<https://doi.org/10.1515/zna-2026-0116>) — `https://doi.org/10.1515/zna-2026-0116` | 202 |
| [访问原链接](<https://websites.umich.edu/~millerpd/>) — `https://websites.umich.edu/~millerpd/` | 403 |
| [访问原链接](<https://websites.umich.edu/~millerpd/CurrentCourses/651_Winter18.html>) — `https://websites.umich.edu/~millerpd/CurrentCourses/651_Winter18.html` | 403 |
| [访问原链接](<https://websites.umich.edu/~millerpd/Teaching.html>) — `https://websites.umich.edu/~millerpd/Teaching.html` | 403 |
| [访问原链接](<https://www-users.cse.umn.edu/~olver/>) — `https://www-users.cse.umn.edu/~olver/` | TLS certificate verification failed |
| [访问原链接](<https://www.sciencedirect.com/science/article/pii/S0022039626006960>) — `https://www.sciencedirect.com/science/article/pii/S0022039626006960` | 403 |
| [访问原链接](<https://www.sciencedirect.com/science/article/pii/S0022039626007102>) — `https://www.sciencedirect.com/science/article/pii/S0022039626007102` | 403 |
| [访问原链接](<https://www.semanticscholar.org/search?q=Liming%20Ling&sort=relevance>) — `https://www.semanticscholar.org/search?q=Liming%20Ling&sort=relevance` | 202 |
| [访问原链接](<https://zbmath.org/>) — `https://zbmath.org/` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.70307>) — `https://doi.org/10.1111/sapm.70307` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.12558>) — `https://doi.org/10.1111/sapm.12558` | 403 |
| [访问原链接](<https://doi.org/10.1063/1.4974018>) — `https://doi.org/10.1063/1.4974018` | 403 |
| [访问原链接](<https://doi.org/10.1111/sapm.70302>) — `https://doi.org/10.1111/sapm.70302` | 403 |

## 正式发表匹配仍待确认

以下仅为相似题名线索，未据此添加 DOI。需要出版社页面或原文确认同一作品与完整作者名单；题名相近不足以匹配。

| 已有条目 | 候选 DOI | 尚需核对 |
| --- | --- | --- |
| [arxiv:2606.27125](<https://arxiv.org/abs/2606.27125>) — The Ising Model Coupled to 2D Gravity: Critical Partition Function | [10.3842/sigma.2025.079](<https://doi.org/10.3842/sigma.2025.079>) | 题名不同，尚未确认同一作品 |
| [arxiv:2608.26054](<https://arxiv.org/abs/2608.26054>) — Numerical Direct Scattering Transform for Dark Solitons | [10.1098/rspa.2023.0529](<https://doi.org/10.1098/rspa.2023.0529>) | 题名不同，尚未确认同一作品 |
| [arxiv:2608.31080](<https://arxiv.org/abs/2608.31080>) — Boundary Quantum Knizhnik-Zamolodchikov Equations and Integrability of Quantum Field Theories with Time-Dependent Bulk and Boundary Coupling Strengths | [10.1103/cr3y-71lr](<https://doi.org/10.1103/cr3y-71lr>) | 题名不同，尚未确认同一作品 |
| [arxiv:2609.23628](<https://arxiv.org/abs/2609.23628>) — On inverse scattering for the one-dimensional nonlinear Dirac equation | [10.1016/j.jde.2024.04.020](<https://doi.org/10.1016/j.jde.2024.04.020>) | 题名不同，尚未确认同一作品 |
| [arxiv:2609.28975](<https://arxiv.org/abs/2609.28975>) — Well-Posedness for KdV-Type Equations with Second-Order Derivative Nonlinearities | [10.1002/mma.70448](<https://doi.org/10.1002/mma.70448>) | 第三作者不同：现有 Zhong Wang，候选 Long Xiao；未合并 |
| [arxiv:2609.14996](<https://arxiv.org/abs/2609.14996>) — Multivariable Painlevé-II equation: connection formulas for arbitrary system size | [10.1088/1751-8121/aeab1a](<https://doi.org/10.1088/1751-8121/aeab1a>) | 题名不同，尚未确认同一作品 |
| [arxiv:2609.30858](<https://arxiv.org/abs/2609.30858>) — On the Cauchy problem for the Tzitzéica equation: Soliton resolution conjecture and asymptotic analysis | [10.1007/s00220-025-05551-8](<https://doi.org/10.1007/s00220-025-05551-8>) | 题名不同，尚未确认同一作品 |
| [arxiv:2609.30668](<https://arxiv.org/abs/2609.30668>) — Long-time Korteweg-de Vries approximation for the Fermi-Pasta-Ulam-Tsingou system | [10.1007/s00205-021-01629-4](<https://doi.org/10.1007/s00205-021-01629-4>) | 题名不同，尚未确认同一作品 |
| [arxiv:2610.02541](<https://arxiv.org/abs/2610.02541>) — Persistence of kinks in the NLS equation with competing nonlinearities | [10.1090/proc/17955](<https://doi.org/10.1090/proc/17955>) | 题名不同，尚未确认同一作品 |
| [arxiv:2610.06403](<https://arxiv.org/abs/2610.06403>) — Whitham modulation theory for the Davey-Stewartson system and stability analysis of its periodic traveling wave solutions | [10.1111/sapm.12651](<https://doi.org/10.1111/sapm.12651>) | 题名不同，尚未确认同一作品 |
| [arxiv:2511.13382](<https://arxiv.org/abs/2511.13382>) — Long-time asymptotics of the good Boussinesq equation and its modified version: Painlevé region | [10.1063/5.0118374](<https://doi.org/10.1063/5.0118374>) | 题名不同，尚未确认同一作品 |

## 元数据服务未覆盖的条目

以下 48 条无 DOI 记录的 Crossref 查询返回 429，保留原数据；下一次维护按此清单补查，不重做整库扫描。

| 条目 | 标题 |
| --- | --- |
| [arxiv:2504.21315](<https://arxiv.org/abs/2504.21315v3>) | Long-time asymptotics of the coupled nonlinear Schrödinger equation in a weighted Sobolev space |
| [arxiv:2210.08417](<https://arxiv.org/abs/2210.08417>) | The Fokas-Lenells equation on the line: Global well-posedness with solitons |
| [arxiv:2607.13773](<https://arxiv.org/abs/2607.13773>) | Multihump-Multivalley Soliton Families on a Plane Wave Background in Birefringent Optical Fibers |
| [arxiv:2606.28579](<https://arxiv.org/abs/2606.28579>) | Transition asymptotics for the real solutions of the sinh-Gordon Painlevé III equation |
| [arxiv:2606.27186](<https://arxiv.org/abs/2606.27186>) | An integrable approach to macroscopic fluctuation theory for the multispecies SSEP |
| [arxiv:2607.29373](<https://arxiv.org/abs/2607.29373>) | Haantjes torsion and integrability: a proof of Bolsinov-Konyaev-Matveev's conjecture |
| [arxiv:2608.00117](<https://arxiv.org/abs/2608.00117>) | A bijective topological recursion for maps |
| [arxiv:2608.01293](<https://arxiv.org/abs/2608.01293>) | Deformations of (2+1)-dimensional integrable systems and isotropic and anisotropic Harry Dym variants |
| [arxiv:2608.02179](<https://arxiv.org/abs/2608.02179>) | $q$-Deformed Topological Recursion: Quantum Curves and Non-perturbative Analysis |
| [arxiv:2608.05952](<https://arxiv.org/abs/2608.05952>) | Integrable curl-force Hamiltonians: bi-Hamiltonian structure, separability, and periodic orbits |
| [arxiv:2607.22202](<https://arxiv.org/abs/2607.22202>) | Mersenne Representation, the Conolly Sequence, and Soliton Profiles over Finite Fields |
| [arxiv:2607.23151](<https://arxiv.org/abs/2607.23151>) | Explicit higher order rational rogue waves of the nonlinear Schrödinger equation |
| [arxiv:2607.26223](<https://arxiv.org/abs/2607.26223>) | The pair correlation function of the Sine_6 process |
| [arxiv:2608.06889](<https://arxiv.org/abs/2608.06889>) | The direct scattering problem for the defocusing nonlinear Schrödinger equation with step-like periodic background |
| [arxiv:2608.08397](<https://arxiv.org/abs/2608.08397>) | A Riemann--Hilbert representation for Sobolev orthogonal polynomials |
| [arxiv:2608.09081](<https://arxiv.org/abs/2608.09081>) | Scalene Yang--Baxter triples as a source of hidden symmetries beyond the ordinary Yang--Baxter equation |
| [arxiv:2608.15756](<https://arxiv.org/abs/2608.15756>) | Bootstrapping bilinear relations of discrete Painlevé systems from 5d gauge theories |
| [arxiv:2608.16865](<https://arxiv.org/abs/2608.16865>) | Unitary Yang--Baxter Operators: Towards a Classification |
| [arxiv:2608.20721](<https://arxiv.org/abs/2608.20721>) | A Parameterization of Small Amplitude KP Finite Gap Solutions via Classical Schottky Uniformization and Persistence of One and Two Gap Solutions |
| [arxiv:2608.24538](<https://arxiv.org/abs/2608.24538>) | Direct linearization, Cauchy matrix and Sato Grassmannian |
| [arxiv:2608.25283](<https://arxiv.org/abs/2608.25283>) | Almost periodic solutions of the defocusing mKdV equation |
| [arxiv:2608.28942](<https://arxiv.org/abs/2608.28942>) | Action-angle variables and phase space formulation of Hermitian matrix models |
| [arxiv:2609.05103](<https://arxiv.org/abs/2609.05103>) | From quadratic integrals to Nijenhuis operators: two-dimensional dictionary |
| [arxiv:2609.06821](<https://arxiv.org/abs/2609.06821>) | Mirror Counts of Spectral Curves |
| [arxiv:2609.08987](<https://arxiv.org/abs/2609.08987>) | Exact Phase-Space Rotation in the Trapped Quantum Calogero Model |
| [arxiv:2609.09273](<https://arxiv.org/abs/2609.09273>) | Constant Maps and Exponentially Small Sectors in ABJM Bethe Observables |
| [arxiv:2609.23795](<https://arxiv.org/abs/2609.23795>) | Equations of state of hydrodynamic type and particle statistics of a Dyson gas in an analytic confining potential |
| [arxiv:2609.29353](<https://arxiv.org/abs/2609.29353>) | Lie and point symmetries of Nyzhnyk models |
| [arxiv:2609.12970](<https://arxiv.org/abs/2609.12970>) | Matrix Dressing Beyond Pfaff-Toda |
| [arxiv:2609.14372](<https://arxiv.org/abs/2609.14372>) | A Classification of Hirota-Integrable Supersymmetric Bilinear KdV-Type Equations |
| [arxiv:2609.15316](<https://arxiv.org/abs/2609.15316>) | On the commuting charges and the Bethe ansatz for the quantised Kadomtsev-Petviashvili equation |
| [arxiv:2609.19508](<https://arxiv.org/abs/2609.19508>) | Radial dam breaks in a two-dimensional droplet bearing environment |
| [arxiv:2609.12518](<https://arxiv.org/abs/2609.12518>) | Large-data modified wave operators for the defocusing nonlinear Schrödinger equation in one space dimension with subcritical long-range nonlinearity |
| [arxiv:2609.14423](<https://arxiv.org/abs/2609.14423>) | Caterpillar Degenerations of Spectral Curves and Double Gelfand-Zeitlin Geometry |
| [arxiv:2609.14786](<https://arxiv.org/abs/2609.14786>) | Fast dynamical control of quantum droplets via Feshbach resonances |
| [arxiv:2605.23229](<https://arxiv.org/abs/2605.23229>) | Strichartz estimates for Schrödinger equations with nonlinear boundary interactions |
| [arxiv:2609.37573](<https://arxiv.org/abs/2609.37573>) | Asymptotic behavior analysis of solutions to the Heisenberg ferromagnet equation with the Schwartz initial data |
| [arxiv:2609.34909](<https://arxiv.org/abs/2609.34909>) | Holography for integrable field theories |
| [arxiv:2609.37785](<https://arxiv.org/abs/2609.37785>) | Global theory for NLS in the weighted spaces II: final data problem |
| [arxiv:2610.02358](<https://arxiv.org/abs/2610.02358>) | Blow-up for the integrable defocusing Ablowitz-Ladik equation |
| [arxiv:2610.04492](<https://arxiv.org/abs/2610.04492>) | Quasi-solitons of the 1D Bose gas at arbitrary-strength contact repulsion |
| [arxiv:2610.11536](<https://arxiv.org/abs/2610.11536>) | Nonlinearity management of matter-wave vector solitons of Bose-Einstein condensates in two dimensions |
| [arxiv:2610.10458](<https://arxiv.org/abs/2610.10458>) | Asymptotic Stability of Domain Walls for One Dimensional Schrödinger Map with Dzyaloshinskii-Moriya Interaction |
| [arxiv:2610.11968](<https://arxiv.org/abs/2610.11968>) | Nonlinear Schrödinger equation in an exterior domain |
| [arxiv:2610.13629](<https://arxiv.org/abs/2610.13629>) | An inverse spectral problem for the wave equation with a varying Robin parameter at the boundary |
| [arxiv:2603.05211](<https://arxiv.org/abs/2603.05211>) | Lagrangian formulation of the Darboux system |
| [arxiv:2610.16378](<https://arxiv.org/abs/2610.16378>) | Spectral stability of resonant Y-solitons for the KP-II equation |
| [arxiv:2505.23403](<https://arxiv.org/abs/2505.23403>) | Transverse dependence and asymptotic dimensional reduction of ground states for the logarithmic Schrödinger equation on a waveguide manifold |

已有 DOI 的 [10.1016/j.physd.2024.134111](https://doi.org/10.1016/j.physd.2024.134111) 的 Crossref 查询在一次有限重试后仍为 429；链接本身返回 200，保留现有书目，不推断更新。

## 验证与复核方式

数据修改后重新运行渲染器和完整项目检查，校验身份、日期、生成页一致性、浏览器过滤行为及严格 MkDocs 构建。书目与工程补丁分开提交。原始 HTTP/API 响应保存在本地忽略目录 `.radar-audit/2026-10-15/`；本报告提供可重复访问的来源，避免将数百份响应正文加入仓库。

