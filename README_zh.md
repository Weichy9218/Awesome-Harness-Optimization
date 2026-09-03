<!-- 面向模型外部 Harness 优化的核心阅读清单，按可编辑面、提议信息和确认协议组织。 -->

# Awesome Harness Optimization

**Harness Optimization（HarnessOpt）阅读清单：运行证据如何修改冻结语言模型周围的软件，以及候选如何成为持久状态。**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#贡献)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | **中文**

> **核心判断。** HarnessOpt 的区别不在于系统能修改多少对象，而在于是否把可编辑面、提议证据和状态确认放进一条可审计的更新回路。现有工作普遍能生成候选，候选级的独立确认仍然少见。

## 目录

- [收录范围](#收录范围)
- [更新架构](#更新架构)
- [如何阅读清单](#如何阅读清单)
- [1. 为什么需要 HarnessOpt 视角](#1-为什么需要-harnessopt-视角)
- [2. 可编辑面：L0–L5](#2-可编辑面l0l5)
- [3. 候选生成：ZO interface](#3-候选生成zo-interface)
- [4. 候选确认：PAC-style boundary](#4-候选确认pac-style-boundary)
- [5. 评测：报告演化轨迹](#5-评测报告演化轨迹)
- [6. 未来方向：可治理的演化](#6-未来方向可治理的演化)
- [配套文档](#配套文档)
- [贡献](#贡献)
- [引用](#引用)

## 收录范围

固定基座模型 \(M\)、任务分布 \(\mathcal D\) 和外部评价边界。设 \(s\) 为模型外部的软件状态，包括 prompt、context、memory、workflow、tool、agent code 和 optimizer code。Harness 在状态 \(s\) 下执行任务 \(z\)，得到 \(\tau=H_s(M,z)\)。

本文只收录同时满足以下条件的工作：

1. 本轮更新中基座模型保持固定；
2. 运行时证据影响对显式集合 \(\mathcal S_{\mathrm{edit}}\) 的修改；
3. 修改会影响后续运行，可以通过确认门进入，也可以无条件写入。

收录对象包括 prompt 优化、自演化 memory 和 skill、workflow 搜索、自修改 Harness code，以及 optimizer 或 meta-harness code。L5 的 Harness 与权重联合更新属于边界情形。纯权重训练和手工设计 Harness 只在能够说明边界时出现。

## 更新架构

一次更新包含四个不同对象：可编辑集合 \(\mathcal S_{\mathrm{edit}}\)、证据收集 \(Q\)、候选提议器 \(P_\phi\) 和状态转移门 \(G\)。

~~~math
\mathcal E_t=Q(s_t;D_t),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
~~~

\(Q\) 在提议任务 \(D_t\) 上收集轨迹、回报、错误和反馈；\(P_\phi\) 在 \(\mathcal S_{\mathrm{edit}}\) 内形成候选；\(G\) 使用确认数据 \(V_t\) 接受、拒绝或回滚候选。候选 \(\widetilde s_{t+1}\) 只有在状态转移规则允许后，才是持久状态 \(s_{t+1}\)。

~~~mermaid
flowchart LR
    S["s_t · 可编辑状态<br/>prompt · memory · workflow · code"] --> Q["Q · 运行 D_t<br/>轨迹 · 回报 · 错误"]
    Q --> P["Pφ · 形成候选<br/>ZO interface"]
    P --> G["G · 在 V_t 上确认<br/>PAC-style boundary"]
    G -->|接受| S
    G -->|拒绝 / 回滚| S
    G -.-> B["受保护边界<br/>model · evaluator · tasks · permissions"]
~~~

系统架构决定哪些对象能够被编辑，也决定拒绝后能否恢复。本项目最新的架构方向可以概括为 **Everything Is a Plugin（EIP）**：将 tool、prompt、skill、provider、memory、verifier、search strategy、stop condition、UI 和 temporary resource 建模为可替换的运行时组件。若这一方向被实现，可编辑面就会从文件和模块扩展到组件加载、依赖解析、实时激活和清理。

与需要重启 agent 的传统插件系统不同，这一运行时设想允许经过确认的组件在当前 session 中激活，并由下一步直接调用。这样可以缩短编辑到运行的回路，也让隔离、原子激活和清理成为确认协议的一部分。

对 HarnessOpt 来说，插件能运行不等于插件可以持久化。候选至少需要经过 contract 检查、隔离执行、评价器与权限路径保护、确认和两阶段原子激活。生命周期还要覆盖进程、端口、provider 与 tool 注册、临时状态和 memory，并记录从生成到清理的完整轨迹。这些是架构要求和审计目标，不是对现有系统的普遍判断。

## 如何阅读清单

清单使用三条互补的分析轴：

| 分析轴 | 要回答的问题 | 主要标记 |
|---|---|---|
| **可编辑面** | 哪类对象可以被修改？ | L0 prompt → L5 Harness 与权重联合更新 |
| **提议信息** | proposer 观察什么，编辑沿什么结构产生？ | ZO analogy: … |
| **确认协议** | 什么可以阻止持久化，确认数据与提议数据是什么关系？ | Gate: … |

ZO analogy 只表示信息或搜索角色，不表示 LLM 编辑器计算了数值梯度。held-out 表示可以使用独立划分参与选择；数据被自适应复用后，它不再是 fresh。人工评审、sandbox 和 rollback 属于治理控制，不提供统计独立性。

## 1. 为什么需要 HarnessOpt 视角

早期自我改进工作讨论系统能否设计更好的继任者。HarnessOpt 关注固定模型周围可部署、可版本化的软件状态。需要区分三种证据强度：

| 证据层级 | 能支持的结论 | 典型例子 |
|---|---|---|
| **形式证明** | 系统内部证明重写会提高效用 | Gödel Machine；现有 HarnessOpt 系统尚未普遍做到 |
| **概率确认** | 在明确假设下，用未参与选择的数据支持固定候选 | PAC-style holdout reasoning；对自适应演化仍是开放目标 |
| **经验改进** | 候选在已观察任务上得分更高 | 当前系统的主流做法 |

第二行与第三行之间的差距，是本清单把提议与确认分开的原因。

**背景文献。** [Good，*Speculations Concerning the First Ultraintelligent Machine*（1966）](https://doi.org/10.1016/S0065-2458%2808%2960418-0) 提出通过自我设计改进机器；[Schmidhuber，*Gödel Machines*（2003）](https://arxiv.org/abs/cs/0309048) 明确了以证明为条件的自我重写；[Yudkowsky，*Recursive Self-Improvement*（2008）](https://www.lesswrong.com/posts/JBadX7rwdcRFzGuju/recursive-self-improvement) 为这一回路命名；[Weng，*Harness Engineering for Self-Improvement*（2026）](https://lilianweng.github.io/posts/2026-07-04-harness/) 将近期自我改进的主要对象定位为模型周围的脚手架。

## 2. 可编辑面：L0–L5

层级表示对象范围，不表示能力等级。写权限、持久性和约束执行方式需要单独记录。

| 横切属性 | 要回答的问题 | 对更新回路的影响 |
|---|---|---|
| **写权限** | agent 可以自主写入，还是必须经过评审？ | 决定更新回路是否闭合。 |
| **持久性** | 修改只在临时环境存在，还是会提交到版本化状态？ | 决定错误能否累积。 |
| **约束执行方式** | 边界只写在 prompt 中，还是由权限、sandbox 或静态检查强制？ | 决定评价器和受保护路径能否留在编辑面之外。 |

| 层级 | 可编辑对象 | 常见编辑单元 | 代表工作 |
|---|---|---|---|
| **L0** | instruction prompt | prompt、指令块、示例 | [APE](https://arxiv.org/abs/2211.01910)、[OPRO](https://arxiv.org/abs/2309.03409)、[ProTeGi](https://arxiv.org/abs/2305.03495)、[GEPA](https://arxiv.org/abs/2507.19457) |
| **L1** | context、memory、skill | 条目、文件、检索单元、可执行 skill | [Reflexion](https://arxiv.org/abs/2303.11366)、[ExpeL](https://arxiv.org/abs/2308.10144)、[ACE](https://arxiv.org/abs/2510.04618)、[Voyager](https://arxiv.org/abs/2305.16291)、[SkillOpt](https://arxiv.org/abs/2605.23904)、[SkillOpt-Lite](https://arxiv.org/abs/2607.03451) |
| **L2** | workflow、graph、architecture | 节点、边、子图、模块槽位 | [GPTSwarm](https://arxiv.org/abs/2402.16823)、[ADAS](https://arxiv.org/abs/2408.08435)、[AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[MaAS](https://arxiv.org/abs/2502.04180) |
| **L3** | Harness 或 agent code | 文件、模块、工具、插件 | [STOP](https://arxiv.org/abs/2310.02304)、[DGM](https://arxiv.org/abs/2505.22954)、[SICA](https://arxiv.org/abs/2504.15228)、[Self-Harness](https://arxiv.org/abs/2606.09498)、[AHE](https://arxiv.org/abs/2604.25850) |
| **L4** | optimizer 或 meta-harness code | proposer、selector、搜索算子 | [Meta-Harness](https://arxiv.org/abs/2603.28052)、[MCE](https://arxiv.org/abs/2601.21557) |
| **L5** | Harness 与模型联合适配 | checkpoint、LoRA、prefix 及 Harness state | [SIA](https://arxiv.org/abs/2605.27276)、[SEAL](https://arxiv.org/abs/2506.10943) |

一项工作可以同时出现在多个分析轴上。层级只说明改了什么，后文说明候选如何产生以及哪些证据能够支持持久化。

### 代表性条目

- **Prompt 优化（L0）。** [MIPROv2](https://arxiv.org/abs/2406.11695) 用 Bayesian optimization 联合提出 instruction 和 demonstration。[TextGrad](https://arxiv.org/abs/2406.07496) 在复合系统中传播文本批评。两者都说明 textual gradient 可以描述提议过程，但不能当作数值导数。ZO analogy：surrogate-model search / trace-informed proposal。Gate：search-set。
- **Memory 与 skill 演化（L1）。** [ReasoningBank](https://arxiv.org/abs/2509.25140) 从成功和失败中提炼可复用策略。[Trace2Skill](https://arxiv.org/abs/2603.25158) 将轨迹局部经验合并为 patch。批量聚合可以扩大证据覆盖，但不会自动产生独立确认。ZO analogy：batch evidence + localized edit。Gate：open 或 search-set，取决于具体路径。
- **结构化 skill 确认（L1）。** [SkillOpt](https://arxiv.org/abs/2605.23904) 和 [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) 使用有界编辑和独立的 validation 阶段，是连接提议结构与候选级确认门的参考。ZO analogy：batch evidence + bounded edit。Gate：held-out。
- **Workflow 与代码搜索（L2–L4）。** [AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[DGM](https://arxiv.org/abs/2505.22954) 和 [Meta-Harness](https://arxiv.org/abs/2603.28052) 让搜索空间更结构化。结构支持静态检查、组件边界和回放，也会增加耦合与回滚成本。ZO analogy：population / archive 或 localized edit。Gate：search-set。
- **边界情形。** [GPTSwarm](https://arxiv.org/abs/2402.16823) 和 [ScoreFlow](https://arxiv.org/abs/2502.04306) 对部分问题使用可微或 RL 式组件，用来标记 ZO interface 不再覆盖完整方法的情况。

## 3. 候选生成：ZO interface

### 3.1 目标接口

固定模型和任务分布后，一次运行产生：

~~~math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
~~~

部署后的目标只能通过运行状态观察。proposer 还可以得到更丰富的观测：

~~~math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
~~~

其中 \(\Psi\) 包括轨迹、错误、工具调用和 verifier feedback。这些信息可以让提议更有针对性，但不提供 \(\nabla_s f_M\)，可读轨迹也不能证明编辑级因果归因。

需要固定三条边界：

- semantic feedback 不等于 gradient estimator；
- compile、type、schema 或 interface 检查是 feasibility filter，不是性能 oracle；
- parent 与 child 的成对分数是状态间经验差，不自动构成 central finite difference。

### 3.2 三条搜索轴

| 设计轴 | 机制家族 | HarnessOpt 问题 | 代表工作 |
|---|---|---|---|
| **证据构造** | single-state proposal | 一条轨迹、错误或批评能否提示局部编辑？ | Reflexion、Voyager、ProTeGi、TextGrad |
|  | batch evidence | 哪些失败模式跨任务或 seed 重复出现？ | ExpeL、SkillOpt、SkillOpt-Lite、Trace2Skill、SkillForge |
|  | paired state comparison | parent 与 edited state 在同一任务批上有何差异？ | SkillCAT、Trace2Skill 的 selective path |
| **搜索几何** | block-local edit | 哪个声明过的组件、文件、条目或模块可以修改？ | SkillAdaptor、AgentSquare、DemoEvolve、AlphaEvolve |
|  | bounded local search | 如何在评测前限制描述空间中的编辑范围？ | SkillOpt、SkillOpt-Lite、SkillForge、Self-Harness |
| **查询分配** | history 或 surrogate | 如何用历史、surrogate 或 bandit 分配 rollout 预算？ | ProTeGi、MIPROv2、AgentSquare、AdaEvolve |
|  | population 或 archive | 哪些候选或谱系继续保留以供探索？ | GEPA、Promptbreeder、DGM、AlphaEvolve、Meta-Harness |

这些机制可以组合，但不能互相替代。batch 不是扰动方向集合；有组件边界不等于各块可以独立评价；archive 提高搜索多样性，不等于独立确认。

### 3.3 结构与成本

可编辑面提供搜索算子能够使用的结构。组件边界、allowlist、feature toggle、版本快照和确定性 replay 可以让局部编辑及成对比较真正可实施。它们不意味着代码天然优于文本：代码同时带来更强的耦合、副作用和回归路径。

Harness 查询的成本不相同，可用下面的分解式记账：

~~~math
C=n_{\mathrm{prop}}c_{\mathrm{prop}}+n_{\mathrm{static}}c_{\mathrm{static}}+n_{\mathrm{smoke}}c_{\mathrm{smoke}}+n_{\mathrm{task}}c_{\mathrm{task}}.
~~~

静态检查和 smoke test 在完整 rollout 前过滤候选，但不能替代任务级确认。search evidence 和 confirmation evidence 必须分开统计。只有当任务、seed 和环境能够降低噪声，且收益足以抵消额外运行成本时，成对评估才值得使用。

算子要求和保守标记见 [docs/zo-operator-map.md](docs/zo-operator-map.md)。

## 4. 候选确认：PAC-style boundary

### 4.1 两个不同的统计问题

**B1，提议稳定性**，关注替换一个提议样本是否会显著改变最终状态。batch evidence、跨任务聚合和有界编辑可能降低这种敏感性。本文核查的系统没有系统测量 replace-one 系数，因此这里只能把它写成设计假设。

**B2，固定候选确认**，关注一个在没有使用 \(V_m\) 的情况下被固定的候选，是否在新任务上表现良好。对有界损失 \(\ell\)，Hoeffding 给出：

~~~math
\epsilon(\widetilde s)
\le
\widehat\epsilon_{V_m}(\widetilde s)
+\sqrt{\frac{\ln(1/\delta)}{2m}}
~~~

以至少 \(1-\delta\) 的概率成立，前提是 \(V_m\) 没有参与候选生成、选择或停止决策。反复自适应使用同一集合后，改名为 validation 或 held-out 也不会恢复独立性。

B1 与 B2 不能互相替代。提议过程稳定，仍可能在复用的验证集上过拟合；真正独立的确认集可以评估固定候选，但不能证明 proposer 稳定。

### 4.2 三类状态转移协议

| 协议 | 什么可以阻止持久化？ | 确认证据能支持什么？ | 代表工作 |
|---|---|---|---|
| **Write-through** | 没有候选级阻断 | 只能报告后续任务上的经验表现 | Reflexion、Voyager、ExpeL、ACE、ReasoningBank、Trace2Skill 默认路径 |
| **Search-time selection** | 在提议或搜索数据上排序、选择 | 支持已观察集合上的经验排序；锁定的 final test 可以评估完整流程 | APE、OPRO、GEPA、AFlow、DGM、Meta-Harness、SkillCAT |
| **Separated confirmation** | 使用未参与提议和选择的数据执行候选级 gate | 在边界条件成立时，支持固定候选的 holdout 推理 | SkillOpt、SkillOpt-Lite、Self-Harness |

在本文核查集合中，三类协议的描述性数量为 **11 / 19 / 3**。统计范围限于 [docs/audit-table.md](docs/audit-table.md) 审计的系统，不代表整个领域的普查。

只用于最终报告、没有参与状态转移的 untouched final test 不是 promotion gate。人工评审、sandbox、审计日志和 rollback 是正交叠加层，决定谁能写入以及失败后如何恢复，不决定分数是否统计独立。门控代码如果没有实际触发，状态转移效果与不存在门控相同。

### 4.3 B2 之外的三个条件

1. **判据覆盖。** 损失必须覆盖目标能力、重要任务簇、安全和策略维度。总体分数上升时，低概率能力仍可能塌陷。
2. **评价边界。** 任务、评价器、模型路由、日志、权限和受保护路径必须位于可编辑面之外，或由运行时强制保护。
3. **行为级拒绝。** 拒绝候选时要恢复进程、注册项、缓存、外部资源和持久 memory，不能只恢复文件树。

可达集、复用、成对比较和稳定性的细节见 [docs/pac-stability.md](docs/pac-stability.md)；逐系统字段见 [docs/audit-table.md](docs/audit-table.md)。

## 5. 评测：报告演化轨迹

合适的评测单位是 **evolution trajectory**，不是最终版本的单点分数。每次报告至少要公开以下五组字段：

| 字段组 | 最少内容 |
|---|---|
| **固定边界** | model、evaluator、tools、environment、permissions、editable surface |
| **数据角色** | proposal、selection、confirmation、regression、final-test 集合；样本量；复用次数；proposer 可见范围 |
| **状态历史** | \(s_0\)、每个接受的 \(s_t\)、被拒候选、最终 \(s_T\)，以及 old-task/OOD/fresh-task 曲线 |
| **运行成本** | token、tool call、wall-clock、task rollout、memory 增长、人工介入和 rollback 成本 |
| **审计产物** | diff、trace、seed、evaluator 配置、replay 命令、安全检查和 rejected branch |

轨迹应从八个维度评估：

- **Adaptivity：** 状态是否改善了触发本轮更新的失败分布？
- **Retention / non-regression：** 旧任务和重要任务簇是否保持？
- **Generalization / transfer：** 收益是否出现在 OOD 或 fresh task？
- **Harness interaction：** 新状态是否被加载、遵循并实际影响行为？
- **Reliability / auditability：** 运行能否回放、归因和恢复？
- **Efficiency / maintainability：** 运行、token、依赖和状态增长成本是多少？
- **Safety / policy compliance：** 安全与权限结果是否保持在要求内？
- **Evaluation integrity：** 候选能否修改评价器、任务数据、日志或模型路由？

[SWE-bench](https://arxiv.org/abs/2310.06770)、[Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak)、[PaperBench](https://arxiv.org/abs/2504.01848) 和长跨度 memory benchmark 可以提供任务，但不会自动提供完整协议。按 episode 重置 state 的 benchmark 无法测量持久状态；可见 smoke test 可能只是 proxy；不同 model、harness、optimizer 和 evaluator 的分数也不能直接相加。

## 6. 未来方向：可治理的演化

### 6.1 Plugin 化 Harness 的生命周期契约

Everything Is a Plugin 只有在每个组件都有明确生命周期时才有用：load、validate、activate、observe、deactivate、cleanup 和 archive。关键测试是拒绝候选后能否在行为上恢复。Plugin registry 应记录依赖和版本；运行时隔离应覆盖进程、端口、注册项、缓存和临时资源；memory 与 skill store 除了追加，还需要删除和压缩策略。

### 6.2 按确认成本分配职责

候选生成和候选确认需要不同资源。一个可检验的部署假设是：

- local sandbox 生成候选，并执行 contract、compile、smoke 和低成本 replay 检查；
- edge service 维护组件 registry、依赖、版本和 replay metadata；
- independent evaluator 处理 fresh-task confirmation、长期 regression 和 safety audit。

这不是“放到 cloud 就自动独立”的结论。应测量 promotion rate、validation latency、rollback cost、privacy exposure、dependency conflict 和 cross-version failure rate。

### 6.3 Model–harness co-design

一个可观察的共同演化回路包含四步：轨迹暴露重复失败；Harness 提出局部修改，或把轨迹转为训练数据；fresh task 确认收益；稳定经验沉淀为可复用组件或模型能力。关键 ablation 是模型变强后能否删除补偿性脚手架，同时保持 fresh-task 收益。规则数量增加或最终分数提高，都不足以证明能力已经内化。

### 6.4 开放问题

当前主线留下四个问题：

1. 什么行为量可以替代 diff size，作为编辑范围的约束？
2. 在验证集复用和任务漂移下，如何维持多轮确认的有效性？
3. 如何压缩、遗忘和回滚非参数状态，同时保留已经确认的行为？
4. 如何合并独立演化的 plugin 谱系，并重新确认合并后的状态？

## 配套文档

| 文档 | 用途 |
|---|---|
| [docs/zo-operator-map.md](docs/zo-operator-map.md) | 经典算子要求和 HarnessOpt 的保守标记 |
| [docs/pac-stability.md](docs/pac-stability.md) | 固定候选界、多轮复用、稳定性和不能推出的结论 |
| [docs/audit-table.md](docs/audit-table.md) | 各系统的确认、评价器保护和回滚字段 |
| [docs/glossary.md](docs/glossary.md) | 符号和协议术语 |

## 贡献

新增论文时，保持三类陈述分开：

- **原文事实：** 一手来源报告的机制、设置或结果；
- **清单解释：** 本清单使用的 L0–L5、ZO analogy 和 Gate 标记；
- **建议：** 实验应报告的字段或协议。

条目格式：

~~~text
- **Name** — "Title". Authors. *Venue* Year. [[paper]](link) — 一句话说明 Harness 如何更新。 [ZO analogy: role] [Gate: protocol]
~~~

使用 held-out 或 fresh test 时，要说明划分、复用次数，以及结果是否能够阻止持久化。如果一手来源没有说明某字段，写 unverified。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 引用

~~~bibtex
@misc{harnessopt_zo_pac_2026,
  title        = {A Zeroth-Order and PAC View of Agent Harness Optimization},
  author       = {Wei, Chuyang and Shen, Yifei},
  year         = {2026},
  howpublished = {\url{https://github.com/Weichy9218/Awesome-Harness-Optimization}}
}
~~~

## License

[MIT](LICENSE)。论文元数据版权归各自作者所有。
