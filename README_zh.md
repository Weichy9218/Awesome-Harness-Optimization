<!-- 面向模型外部 Harness 优化的核心阅读清单，按可编辑面、提议机制和确认协议组织。 -->

# Awesome Harness Self-Evolving

**Harness Optimization（HarnessOpt）阅读清单：运行证据如何修改冻结语言模型周围的软件，以及候选如何成为持久状态。**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | **中文**

> **核心判断。** HarnessOpt 的区别不在于系统能修改多少对象，而在于是否把可编辑面、提议机制和状态转移协议分别记录在一条可审计的更新回路中。现有工作普遍能生成候选，候选级独立确认仍然少见。

## 目录

1. [收录范围](#1-收录范围)
2. [动机：为什么需要 HarnessOpt 视角](#2-动机为什么需要-harnessopt-视角)
3. [HarnessOpt：状态与更新回路](#3-harnessopt状态与更新回路)
   - [3.1 清单字段：三条分析轴](#31-清单字段三条分析轴)
4. [可编辑面：L0–L5](#4-可编辑面l0l5)
   - [4.1 代表性条目](#41-代表性条目)
5. [候选提议：ZO interface](#5-候选提议zo-interface)
   - [5.1 目标接口与候选形式](#51-目标接口与候选形式)
   - [5.2 ZO 算子与 HarnessOpt 机制家族](#52-zo-算子与-harnessopt-机制家族)
   - [5.3 三条设计轴](#53-三条设计轴)
   - [5.4 从 SkillOpt-Lite 到 HarnessOpt](#54-从-skillopt-lite-到-harnessopt)
6. [确认与持久化：状态转移协议](#6-确认与持久化状态转移协议)
   - [6.1 两个不同的统计问题](#61-两个不同的统计问题)
   - [6.2 三类状态转移协议](#62-三类状态转移协议)
   - [6.3 B2 之外的三个条件](#63-b2-之外的三个条件)
7. [评测：报告演化轨迹](#7-评测报告演化轨迹)
- [S1. 文献地图：围绕主线补齐缺口](#s1-文献地图围绕主线补齐缺口)
8. [未来方向：可治理的演化](#8-未来方向可治理的演化)
   - [8.1 插件生命周期、组合性与可逆状态](#81-插件生命周期组合性与可逆状态)
   - [8.2 端、边、云：按确认成本分配职责](#82-端边云按确认成本分配职责)
   - [8.3 评价器、长期目标、记忆与失败多样性](#83-评价器长期目标记忆与失败多样性)
   - [8.4 Model–harness co-design 与人类授权](#84-modelharness-co-design-与人类授权)
   - [8.5 开放问题](#85-开放问题)
- [配套文档](#配套文档)
- [引用](#引用)
- [License](#license)

## 1. 收录范围

先固定基座模型 $M$、任务分布 $\mathcal D$ 和外部评价边界，并设 $s$ 为本轮更新允许持久化的模型外部版本化状态。**Harness** 是连接 $M$ 与任务的可执行系统：它可以加载 instruction 和 context，路由 memory 与 skill，调度 workflow，调用 tool，执行权限控制，并运行 verification 或 replay hook。记 $H_s$ 为状态 $s$ 与固定运行边界共同决定的执行程序，任务 $z$ 的轨迹为 $\tau=H_s(M,z)$。

Harness 的范围大于 prompt 文件，但并非每个运行时产物都算持久状态：临时 context、进程、cache 和生成文件默认只属于单次运行，除非被显式版本化并由后续运行重新加载。task、evaluator、model routing、permission 和 logging 默认属于受保护的评价边界；候选如果能改动它们，应报告为 evaluation-boundary change，而不是普通的 Harness 编辑。

本清单只收录同时满足以下条件的工作：

1. 本轮更新中基座模型保持固定；
2. 运行时证据影响对显式集合 $\mathcal S_{\mathrm{edit}}$ 的修改；
3. 修改会被后续运行重新加载；如果存在候选筛选，还要记录接受或拒绝规则。

L0–L5 表是核心清单。边界情形和文献地图中的锚点会明确标注；在持久化方式和写入路径核查完成前，它们只作为覆盖参考，不计入协议分布。

收录对象包括 prompt 优化、自演化 memory 和 skill、workflow 搜索、自修改 Harness code，以及 optimizer 或 meta-harness code。L5 的 Harness 与权重联合更新属于边界情形。纯权重训练和手工设计 Harness 只在能够说明边界时出现。

文献覆盖按更新回路组织，不按发表时间排列。当前清单是围绕主线的代表性集合，不是全领域普查；新增工作应当澄清可编辑面、提议机制、确认协议或轨迹评测中的一项，并回到一手来源核查相应字段。

## 2. 动机：为什么需要 HarnessOpt 视角

早期自我改进工作讨论系统能否设计更好的继任者。HarnessOpt 关注固定模型周围可部署、可版本化的软件状态。需要区分三种证据强度：

| 证据层级 | 能支持的结论 | 典型例子 |
|---|---|---|
| **形式证明** | 系统内部证明重写会提高效用 | Gödel Machine；现有 HarnessOpt 系统尚未普遍做到 |
| **概率性确认** | 在明确假设下，用未参与选择的数据支持固定候选 | PAC-style holdout reasoning；对自适应演化仍是开放目标 |
| **经验改进** | 候选在已观察任务上得分更高 | 当前系统的主流做法 |

概率性确认与经验改进之间的差距，是本清单把提议与确认分开的原因。

**背景文献。** [Good, *Speculations Concerning the First Ultraintelligent Machine* (1966)](https://doi.org/10.1016/S0065-2458%2808%2960418-0) 提出通过自我设计改进机器；[Schmidhuber, *Gödel Machines* (2003)](https://arxiv.org/abs/cs/0309048) 明确了以证明为条件的自我重写；[Yudkowsky, *Recursive Self-Improvement* (2008)](https://www.lesswrong.com/posts/JBadX7rwdcRFzGuju/recursive-self-improvement) 为这一回路命名；[Weng, *Harness Engineering for Self-Improvement* (2026)](https://lilianweng.github.io/posts/2026-07-04-harness/) 把近期自我改进的主要对象定位为模型周围的脚手架；[Code as Agent Harness (2026)](https://arxiv.org/abs/2605.18747) 将 code 组织为可执行、可验证、有状态的基础设施。后两者用于确定范围和架构，不提供独立确认的证据。

## 3. HarnessOpt：状态与更新回路

一次更新包含四个不同对象：可编辑集合 $\mathcal S_{\mathrm{edit}}$、证据收集 $Q$、候选提议器 $P_\phi$ 和状态转移规则 $G$。

```math
\mathcal E_t=Q(s_t;D_t^{\mathrm{prop}}),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
```

$Q$ 在提议任务 $D_t^{\mathrm{prop}}$ 上收集轨迹、回报、错误和反馈； $P_\phi$ 在 $\mathcal S_{\mathrm{edit}}$ 内形成候选； $G$ 接受、拒绝或回滚候选； $V_t$ 表示存在确认步骤时 $G$ 可以查阅的数据。候选 $\widetilde s_{t+1}$ 只有在状态转移规则允许后，才成为持久状态 $s_{t+1}$。

| 对象 | 作用 | 是否持久化 |
|---|---|---:|
| $s_t$ | 后续任务重新加载的当前已接受状态 | 是 |
| $r_{t,i}$ | 单次运行中的 context、进程、cache 和临时文件 | 默认否 |
| $\mathcal E_t$ | 提供给 proposer 的轨迹、回报、错误和诊断 | 作为输入，不是状态 |
| $\widetilde s_{t+1}$ | 状态转移规则执行前的 patch 或替换版本 | 只有 $G$ 接受后才持久化 |

~~~mermaid
flowchart LR
    S["s_t · 可编辑状态<br/>prompt · memory · workflow · code"] --> Q["Q · 运行 D_t^prop<br/>轨迹 · 回报 · 错误"]
    Q --> P["Pφ · 形成候选<br/>ZO interface"]
    P --> G["G · 状态转移<br/>分离时才做确认"]
    G -->|接受| S
    G -->|拒绝 / 回滚| S
    G -.-> B["受保护边界<br/>model · evaluator · tasks · permissions"]
~~~

插件化运行时是这条回路的一种实现方式。组件如果可以在运行中激活，依赖解析、隔离、原子激活和清理就成为 rollback 审计的一部分。这属于工程实现与审计范围，既不增加分析轴，也不能证明清单中的系统已经支持安全的 live replacement。

本清单按 survey 的章节分工组织：第 3 节定义 Harness state 与更新回路；第 4 节回答可以修改什么；第 5 节回答候选如何形成；第 6 节回答候选如何确认并持久化；第 7 节评估完整的 evolution trajectory；第 8 节记录治理问题。因此，三个清单字段对应第 4–6 节，而不是替代这些章节。

### 3.1 清单字段：三条分析轴

清单记录三个互补字段。它们对应同一更新回路的不同环节，不能互相替代。

| 分析轴 | 要回答的问题 | 必须记录的内容 |
|---|---|---|
| **可编辑面** | 哪类持久对象可以被修改？ | primary level 与 secondary targets（`L0`–`L5`），以及 persistence、write authority、mutation granularity |
| **提议机制** | proposer 观察什么，候选沿什么结构形成？ | evidence construction、search geometry、query allocation；记录具体标记，例如 `Proposal: batch evidence + localized edit` |
| **确认协议** | 哪条可执行规则决定候选能否成为下一状态，哪些数据可以影响该规则？ | `write-through`、`search-time selection` 或 `separated confirmation`，并记录 `open`、`search-set`、`held-out`、`fresh test`、reuse 和 boundary 状态 |

这张表是清单的字段规范，也是比较不同系统时的最小记录格式，作用是把候选生成过程与独立晋级门分开记录。

$G$ 是操作层面的状态转移规则。`PAC-style confirmation` 是对 `separated confirmation` 的条件性统计解释。它要求候选先固定，确认数据独立于提议与选择，损失有界，评价边界受到保护。`write-through` 与 `search-time selection` 仍可包含操作层面的 gate，但其数据关系不满足上述 holdout 前提。人工评审、sandbox 和 rollback 属于治理控制，不提供统计独立性。

## 4. 可编辑面：L0–L5

层级表示对象范围，不表示能力等级。写权限、持久性和约束执行方式需要单独记录。

| 横切属性 | 要回答的问题 | 对更新回路的影响 |
|---|---|---|
| **写权限** | agent 可以自主写入，还是必须经过评审？ | 决定更新回路是否闭合。 |
| **持久性** | 修改只在临时环境存在，还是会提交到版本化状态？ | 决定错误能否累积。 |
| **约束执行方式** | 边界只写在 prompt 中，还是由权限、sandbox 或静态检查强制？ | 决定评价器和受保护路径能否留在编辑面之外。 |

| 层级 | 可编辑对象 | 常见编辑单元 | 代表工作 |
|---|---|---|---|
| **L0** | instruction prompt | prompt、指令块、示例 | [APE](https://arxiv.org/abs/2211.01910)、[OPRO](https://arxiv.org/abs/2309.03409)、[ProTeGi](https://arxiv.org/abs/2305.03495)、[GEPA](https://arxiv.org/abs/2507.19457) |
| **L1** | context、memory、skill | 条目、文件、检索单元、可执行 skill | [Reflexion](https://arxiv.org/abs/2303.11366)、[ExpeL](https://arxiv.org/abs/2308.10144)、[ACE](https://arxiv.org/abs/2510.04618)、[Voyager](https://arxiv.org/abs/2305.16291)、[SkillOpt](https://arxiv.org/abs/2605.23904)、[SkillOpt-Lite](https://arxiv.org/abs/2607.03451)、[SkillCAT](https://arxiv.org/abs/2606.13317)、[SkillAdaptor](https://arxiv.org/abs/2606.01311)、[SkillForge](https://arxiv.org/abs/2604.08618)；[MCE](https://arxiv.org/abs/2601.21557) 具有 secondary L1 context artifact 目标 |
| **L2** | workflow、graph、architecture | 节点、边、子图、模块槽位 | [GPTSwarm](https://arxiv.org/abs/2402.16823)、[AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[MaAS](https://arxiv.org/abs/2502.04180)、[MASS](https://arxiv.org/abs/2502.02533)；[ADAS](https://arxiv.org/abs/2408.08435) 为 L3/secondary L2 |
| **L3** | Harness 或 agent code | 文件、模块、工具、插件 | [ADAS](https://arxiv.org/abs/2408.08435)、[DGM](https://arxiv.org/abs/2505.22954)、[SICA](https://arxiv.org/abs/2504.15228)、[Self-Harness](https://arxiv.org/abs/2606.09498)、[AHE](https://arxiv.org/abs/2604.25850)、[AutoHarness†](https://arxiv.org/abs/2603.03329)、[Meta-Harness](https://arxiv.org/abs/2603.28052) |
| **L4** | improver、optimizer 或 context-management mechanism | proposer、selector、搜索算子 | [STOP](https://arxiv.org/abs/2310.02304)、[MCE](https://arxiv.org/abs/2601.21557)（primary L4；secondary L1） |
| **L5** | Harness 与模型联合适配 | checkpoint、LoRA、prefix 及 Harness state | [SIA](https://arxiv.org/abs/2605.27276)；[SEAL](https://arxiv.org/abs/2506.10943) 作为纯 weight-update 邻接对照 |

† AutoHarness 保留为覆盖锚点；其持久化和 reload 路径在本次审计中仍未核实。

同一工作可以同时出现在多个分析轴上。层级只说明改了什么，后文说明候选如何产生以及哪些证据能够支持持久化。

L3/L4 的边界按实际持久写入对象判断，不按 proposer 的角色判断。搜索 Harness 或 agent code 的系统归入 L3；持久修改 improver、optimizer 或 context-management mechanism 的系统归入 L4。如果两者同时更新，应指定一个 primary target，把另一个记录为 secondary level，并给出支持该判断的原文位置。

### 4.1 代表性条目

- **Prompt 优化（L0）。** [MIPROv2](https://arxiv.org/abs/2406.11695) 用 Bayesian optimization 联合提出 instruction 和 demonstration。[TextGrad](https://arxiv.org/abs/2406.07496) 在复合系统中传播文本批评信号。两者都说明 textual gradient 可以描述提议过程，但不能当作数值导数。`[Proposal: surrogate-model search + trace-informed]` `[Confirmation: search-time selection; data: search-set]`。
- **Memory 与 skill 演化（L1）。** [ReasoningBank](https://arxiv.org/abs/2509.25140) 从成功和失败中提炼可复用策略。[Trace2Skill](https://arxiv.org/abs/2603.25158) 将轨迹中的局部经验合并为 patch。批量聚合可以扩大证据覆盖，但不会自动产生独立确认。`[Proposal: batch evidence + localized edit]` `[Confirmation: write-through or search-time selection, depending on the path]`。
- **结构化 skill 确认（L1）。** [SkillOpt](https://arxiv.org/abs/2605.23904) 和 [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) 使用有界编辑和单独的 validation 阶段，是连接提议结构与候选级状态转移规则的参考。`[Proposal: batch evidence + bounded edit]` `[Confirmation: separated confirmation; data: held-out]`。
- **对比式 skill 演化（L1）。** [SkillCAT](https://arxiv.org/abs/2606.13317) 比较同一任务的成功与失败轨迹，在 source-task clone 上重放 candidate patch，再合并筛选后的 patch。这是对比式提议证据与 search-time selection，不是独立确认。`[Proposal: paired state comparison + localized edit]` `[Confirmation: search-time selection; data: search-set]`。
- **Workflow 与代码搜索（L2–L3）。** [AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[DGM](https://arxiv.org/abs/2505.22954) 和 [Meta-Harness](https://arxiv.org/abs/2603.28052) 让搜索空间更结构化。结构支持静态检查、组件边界和回放，也会增加耦合与回滚成本。`[Proposal: population/archive or localized edit]` `[Confirmation: search-time selection; data: search-set]`。
- **元层 context 共演化（L4 + L1）。** [MCE](https://arxiv.org/abs/2601.21557) 演化 context-engineering skill，同时由 base-level agent 优化 context artifact。按 primary-write 规则，skill 是 primary L4，artifact 是 secondary L1；基于 validation 的 best-so-far 选择仍属于 search-time selection，不是独立确认。
- **边界情形。** [GPTSwarm](https://arxiv.org/abs/2402.16823) 和 [ScoreFlow](https://arxiv.org/abs/2502.04306) 对部分问题使用可微或 RL 式组件。[Continual Harness](https://arxiv.org/abs/2605.09998) 在单次运行内在线调整 prompt、sub-agent、skill 和 memory。这些工作标记了 ZO interface 或跨运行持久化标准不再覆盖完整方法的情况。

## 5. 候选提议：ZO interface

本节只把 SkillOpt-Lite 的 ZO 对照扩展到 HarnessOpt：把可编辑状态从单个 skill 文件扩展为持久化 harness 状态。ZO 在这里描述目标信息如何通过运行获得，不表示现有方法使用了数值梯度或具有收敛保证。

同一论文可以出现在多个行中，因为这些行记录的是不同字段，不是互斥的论文集合。SkillOpt 和 SkillOpt-Lite 同时出现在 L1、bounded edit 和 separated confirmation 位置，不能把这些出现次数相加为系统数量。

### 5.1 目标接口与候选形式

固定基座模型 $M$、任务分布 $\mathcal D$ 和回报函数 $R$。对状态 $s$，一次运行返回

```math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
```

运行还可以返回轨迹、错误和 verifier feedback：

```math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr).
```

对离散文本、程序和文件树， $\nabla_s f_M(s)$ 通常没有定义。用 $\mathsf E(s,\delta)$ 表示合法编辑，候选的最小形式是 $\delta_t=P_\phi(s_t,\mathcal O_t)$、$\widetilde s_{t+1}=\mathsf E(s_t,\delta_t)$；候选是否写回交给第 6 节。

### 5.2 ZO 算子与 HarnessOpt 机制家族

下表沿用 SkillOpt-Lite 的直接机制映射。Harness-native 公式只描述离散编辑如何扮演相应角色；只有满足列出的条件时，才可以使用经典算子的名称。

| ZO 机制家族 | Harness-native 形式 | 经典 ZO 参照 | 对应关系与边界 | 代表工作 |
|---|---|---|---|---|
| ZO oracle | $Y(s,z;\xi)$，$f_M(s)=\mathbb E[Y]$ | 黑盒目标 $f(x)$ | 运行提供目标信息；这是接口对应 | 所有通过任务运行获得回报的纳入条目 |
| 1-point / single-trace proposal | $\delta_t=P_\phi(s_t,\mathcal O(s_t,z_t;\xi_t))$ | $\widehat g_{1p}=\frac{d_x}{\mu}Y(x+\mu u)u$ | 没有数值方向 $u$ 和步长 $\mu$，不是 one-point estimator | Reflexion、Voyager、ProTeGi、TextGrad |
| multi-point / mini-batch | $\widehat f_D(s)=m^{-1}\sum_iY(s,z_i;\xi_i)$，并聚合 $\Psi_i$ | $\widehat g_{\mathrm{mb}}=b^{-1}\sum_i[Y(x+\mu u_i)-Y(x)]u_i$ | 任务或 seed 是同一点上的重复取样，不是扰动方向 | SkillOpt、SkillOpt-Lite、Trace2Skill、ExpeL、SkillForge |
| central difference / paired comparison | $\widehat\Delta_D=m^{-1}\sum_i[Y(s^+,z_i;\xi_i^+)-Y(s^-,z_i;\xi_i^-)]$ | $\frac{f(x+\mu u)-f(x-\mu u)}{2\mu}u$ | parent/child 只是比较骨架；需可逆、对称的正负扰动才是 central difference | SkillCAT、Trace2Skill selective path |
| coordinate descent / block-local edit | $s'=s^{(b\leftarrow\delta_b)}$，块 $b$ 预先固定 | $\frac{f(x+\mu e_i)-f(x)}{\mu}e_i$ | 一次只改一个预定义坐标或组件；通常是结构对应 | SkillAdaptor、AgentSquare、DemoEvolve、AlphaEvolve |
| trust region / bounded edit | $\widetilde s\in\mathcal N_L(s)\cap\mathcal S_{\mathrm{feas}}$ | $x_{k+1}\in B(x_k,\Delta_k)$ | diff、token 或路径上限只是 bounded edit；还需行为距离、半径更新和接受规则才是 trust region | SkillOpt、SkillOpt-Lite、SkillForge、Self-Harness |
| control variate / historical baseline | $\widehat f^{\mathrm{cv}}_t=\widehat f_t-c_t+\mathbb E[c_t]$（需有明确 baseline） | $\widehat g^{\mathrm{cv}}_t=\widehat g_t-c_t+\mathbb E[c_t]$ | rejected buffer 不是自动的 control variate；需报告相关量和实测方差下降 | SkillOpt（条件性；算子证据未核查） |

`history/surrogate allocation` 和 `population/archive search` 不属于上面的直接 ZO 算子表。rejected buffer 只有满足表中 control-variate 的估计条件时才可这样标注，否则就是负例证据。三者都应报告明确的 acquisition、选择规则或方差测量。

### 5.3 三条设计轴

设计轴是记录 schema，不是新的 ZO 算子分类：

| 设计轴 | 记录什么 | 机制家族 |
|---|---|---|
| 证据构造 | 查询哪些运行、如何聚合观测 | 1-point、multi-point、paired comparison |
| 搜索几何 | 编辑在哪个结构中形成、规模如何受限 | block-local、bounded edit |
| 查询分配 | 如何安排候选、任务和 rollout 预算 | history/surrogate、population/archive |

使用 rich trace 不代表比较 parent 与 child；保留 archive 不代表有候选级 reject gate；限制 diff 大小不代表定义了行为半径。

### 5.4 从 SkillOpt-Lite 到 HarnessOpt

扩展只改变三处：

1. 可编辑域从单个 skill 文件变为显式的 $\mathcal S_{\mathrm{edit}}$，可包含 prompt、memory、workflow、tool 和 harness code；
2. 文件 patch 变为受组件边界、allowlist、接口契约和版本快照约束的合法编辑 $\mathsf E(s,\delta)$；
3. 轨迹探索和候选提议保持不变，compile、smoke、full rollout 的持久化决定仍由第 6 节处理。

因此 HarnessOpt 是同一 query-based proposal loop 在更宽状态域上的实例。代码带来更多结构，也带来更大的耦合和回滚面；它改变实施成本，不改变 ZO 接口。

## 6. 确认与持久化：状态转移协议

本节把 PAC-style holdout reasoning 作为一种分析视角，而不是门控本身的名称。操作问题是候选在哪里被接受、拒绝或回滚；统计问题是确认数据是否仍独立于提议和选择。

### 6.1 两个不同的统计问题

令 $\mathcal A$ 把提议样本 $D_n$ 映射为持久状态， $x$ 为独立评测任务， $D_n^{(i\leftarrow x_i')}$ 表示用独立样本替换第 $i$ 个提议样本后的集合。提议稳定性由 expected replace-one sensitivity 刻画：

```math
\beta_{\mathrm{avg}}
=
\mathbb E\!\left[
\left|
\ell(\mathcal A(D_n);x)
-
\ell(\mathcal A(D_n^{(i\leftarrow x_i')});x)
\right|
\right].
```

**B1，提议稳定性**，关注这一敏感性是否足够小。batch evidence、跨任务聚合和有界编辑可能降低单个提议样本对状态的影响。本清单核查的系统都没有系统性测量 $\beta_{\mathrm{avg}}$，因此它属于设计假设，不是实证保证。expected on-average stability 本身也不能推出高概率界。

**B2，固定候选确认**，关注一个在没有使用确认样本 $V_m$ 的情况下被固定的候选，是否在新任务上表现良好。若 $V_m\sim\mathcal D^m$，损失取值在 $[0,1]$ 内，且 $V_m$ 没有参与候选生成、选择或停止决策，则 Hoeffding 不等式给出：

```math
\epsilon(\widetilde s)
\le
\widehat\epsilon_{V_m}(\widetilde s)
+\sqrt{\frac{\ln(1/\delta)}{2m}}
```

以至少 $1-\delta$ 的概率成立。如果一个任务使用多个 seed，seed 是给定任务条件下的重复观测；在完成任务级聚合后， $m$ 才表示独立任务数。对同一集合进行自适应复用后，改名为 validation 或 held-out 也不会恢复独立性。

B1 与 B2 不能互相替代。即使提议过程稳定，也可能在复用的验证集上过拟合；真正独立的确认集可以评估固定候选，但不能证明 proposer 稳定。

确认评测的结果不能回流到候选提议、候选排序或停止决策。否则确认集已经成为搜索集的一部分。用于搜索和确认的任务级 rollout 应分别统计，并计入被拒候选。

### 6.2 三类状态转移协议

协议由状态转移发生的位置和能够影响该转移的数据共同决定。仅报告 final-test 结果，不能据此判定系统存在 promotion gate。

| 协议 | 状态转移语义 | 确认证据 | 能支持的结论 | 代表工作 |
|---|---|---|---|---|
| **Write-through** | 候选直接写入 memory、skill、workflow 或 code，没有候选级阻断规则。 | 没有独立确认数据。 | 后续任务只能提供回溯式经验表现。 | Reflexion、Voyager、ExpeL、ACE、ReasoningBank、Trace2Skill 默认路径 |
| **Search-time selection** | 在 proposal/search 数据上对候选或 archive 成员排序，选中对象成为下一状态。 | 与搜索过程同源。 | 支持已观察集合上的相对排序；锁定的 final test 可以评估完整流程，但不能证明晋级步骤有效。 | APE、OPRO、GEPA、AFlow、DGM、Meta-Harness、SkillCAT |
| **Separated confirmation** | 先固定候选，再由独立确认评测决定是否替换当前状态。 | 确认数据未参与提议和选择，但仍需检查跨轮复用和评价边界。 | 在假设成立时，支持固定候选层面的 holdout 推理。 | SkillOpt、SkillOpt-Lite、Self-Harness |

在本清单核查的集合中，三类协议的描述性数量为 **11 / 19 / 3**。统计范围仅限于 [docs/audit-table.md](docs/audit-table.md) 中审计的系统，不代表整个领域的普查。

分离是协议结构层面的属性，独立性还要注明时间范围。SkillOpt-Lite 通过调整任务分配扩大确认集；Self-Harness 在多个演化轮次中复用固定的 held-in/held-out 划分。后者满足单轮分离，但不能自动提供跨轮 fresh confirmation。被拒候选同样会消耗确认集所包含的信息，即使它最终没有晋级。

只用于最终报告、没有参与状态转移的 untouched final test 不是 promotion gate。人工评审、sandbox、审计日志和 rollback 是正交控制，分别作用于写入权限、运行时保护和失败恢复，不建立统计独立性。门控必须在实现中实际执行；从未触发的 hook 与不存在门控等价。

### 6.3 B2 之外的三个条件

若任务分布划分为 $K$ 个任务簇，可写为 $\epsilon(s)=\sum_{k=1}^{K}p_k\epsilon_k(s)$。概率质量为 $p_k$ 的任务簇发生幅度为 $\Delta\epsilon_k$ 的退化时，总体风险只变化 $p_k\Delta\epsilon_k$。即使该簇的损失显著恶化，变化仍可能小于确认半径 $\eta$。因此，任务簇级 non-regression 需要分层采样和分别报告。

1. **判据覆盖。** 损失必须覆盖目标能力、重要任务簇、安全和策略维度。总体分数提高时，低概率能力仍可能退化。
2. **评价边界。** 任务、评价器、模型路由、日志、权限和受保护路径必须位于可编辑面之外，或由运行时强制保护。
3. **行为级拒绝。** 拒绝候选时要恢复进程、注册项、缓存、外部资源和持久 memory，不能只恢复文件树。

可达集、复用、成对比较和稳定性的细节见 [docs/pac-stability.md](docs/pac-stability.md)；逐系统字段见 [docs/audit-table.md](docs/audit-table.md)。

## 7. 评测：报告演化轨迹

评测的基本单位是 **evolution trajectory**，不是最终版本的单点分数。[Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) 区分了“能否产生有用的持久更新”和“任务求解 agent 能否从更新中获益”，因此轨迹报告应同时测量更新质量和后续 Harness 使用这些更新的效果。

每次报告至少要公开以下五组字段：

| 字段组 | 最少内容 |
|---|---|
| **固定边界** | model、evaluator、tools、environment、permissions、editable surface |
| **数据角色** | proposal、selection、confirmation、regression、final-test 集合；样本量；复用次数；proposer 可见范围 |
| **状态历史** | $s_0$、每个接受的 $s_t$、被拒候选、最终 $s_T$，以及 old-task/OOD/fresh-task 曲线 |
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

[SWE-bench](https://arxiv.org/abs/2310.06770)、[Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak)、[PaperBench](https://arxiv.org/abs/2504.01848) 和长跨度 memory benchmark 可以提供任务。[AI Agents That Matter](https://arxiv.org/abs/2407.01502) 与 [HAL](https://arxiv.org/abs/2510.11977) 提供成本和评价器完整性的规范化视角，[RE-Bench](https://arxiv.org/abs/2411.15114) 与 [MLE-bench](https://arxiv.org/abs/2410.07095) 提供长程任务基座，但都不会自动提供完整协议。按 episode 重置 state 的 benchmark 无法测量持久状态；可见 smoke test 可能只是 proxy；不同 model、harness、optimizer 和 evaluator 的分数也不能直接相加。

## S1. 文献地图：围绕主线补齐缺口

清单按更新回路的四个缺口组织文献。下面的链接是覆盖锚点，不代表每个协议字段都已逐篇核查；核查队列见[文献地图](docs/literature-map.md)，已完成的协议归类见[审计表](docs/audit-table.md)。

| 主线问题 | 代表性锚点 | 一手来源需要提取的字段 |
|---|---|---|
| **直接 Harness 演化** | [Code as Agent Harness](https://arxiv.org/abs/2605.18747)、[AutoHarness](https://arxiv.org/abs/2603.03329)、[SkillCAT](https://arxiv.org/abs/2606.13317)、[SkillAdaptor](https://arxiv.org/abs/2606.01311)、[SkillForge](https://arxiv.org/abs/2604.08618)、[MCE](https://arxiv.org/abs/2601.21557)、[Continual Harness](https://arxiv.org/abs/2605.09998)、[AutoAgent](https://arxiv.org/abs/2603.09716)、[Evo-Memory](https://arxiv.org/abs/2511.20857)、[Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) | 持久写入对象、reload 边界、候选级 gate，以及 update 与 benefit 的区分 |
| **候选提议与搜索** | [AdaEvolve](https://arxiv.org/abs/2602.20133)、[ShinkaEvolve](https://arxiv.org/abs/2509.19349)、[ThetaEvolve](https://arxiv.org/abs/2511.23473)、[Promptbreeder](https://arxiv.org/abs/2309.16797)、[GEPA](https://arxiv.org/abs/2507.19457)、[MIPROv2](https://arxiv.org/abs/2406.11695)、[TextGrad](https://arxiv.org/abs/2406.07496)、[DGM](https://arxiv.org/abs/2505.22954) | proposer 观察的证据、编辑几何、候选保留、查询分配，以及对应属于 interface、structural 还是 strict |
| **确认与轨迹评测** | [SkillOpt](https://arxiv.org/abs/2605.23904)、[SkillOpt-Lite](https://arxiv.org/abs/2607.03451)、[Self-Harness](https://arxiv.org/abs/2606.09498)、[AI Agents That Matter](https://arxiv.org/abs/2407.01502)、[HAL](https://arxiv.org/abs/2510.11977)、[RE-Bench](https://arxiv.org/abs/2411.15114)、[MLE-bench](https://arxiv.org/abs/2410.07095)、[PaperBench](https://arxiv.org/abs/2504.01848) | split 与 reuse、阻断持久化的位置、成本、长期保留、可复现性和 evaluator integrity |
| **Harness 架构与评测基座** | [SWE-agent](https://arxiv.org/abs/2405.15793)、[OpenHands](https://arxiv.org/abs/2407.16741)、[OpenHands SDK](https://arxiv.org/abs/2511.03690)、[BrowserGym ecosystem](https://arxiv.org/abs/2412.05467)、[ToolSandbox](https://arxiv.org/abs/2408.04682)、[$\tau$-bench](https://arxiv.org/abs/2406.12045)、[AgentDojo](https://arxiv.org/abs/2406.13352)、[WorkArena](https://arxiv.org/abs/2403.07718) | interface、tool/state 边界、评价器设计和可复现性；未完成独立审计前不计入持久更新协议数量 |
| **风险与治理** | [Misevolution](https://arxiv.org/abs/2509.26354)、[Defining and Characterizing Reward Hacking](https://arxiv.org/abs/2209.13085)、[Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760)、[Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) | evaluator 操纵、reward hacking、多样性坍缩、权限边界、rollback 和人类授权 |

## 8. 未来方向：可治理的演化

本节把长期演化定义为受约束的状态转移问题，不把规则数量的增加视为能力增长。[Weng 对 Harness Engineering 的总结](https://lilianweng.github.io/posts/2026-07-04-harness/) 将弱评价器、上下文与记忆生命周期、负结果、多样性坍缩、奖励投机、长期成功和人类监督列为主要瓶颈。对 HarnessOpt 而言，这些瓶颈分别落在生命周期、部署边界、评价器、状态记忆和人类授权上。DeepSeek Harness 的公开讨论概括出 “Model + Harness = Agent” 与 “Everything Is a Plugin”，可作为插件化运行时的工程案例参考，但不足以单独支撑任何性能或自我进化结论（见 [q1](https://www.zhihu.com/question/2071331484284220938) 和 [q2](https://www.zhihu.com/question/2072255826778140869)）。

长期运行至少需要维持四个不变量：评价边界不可由候选修改，候选及其副作用可撤回，运行证据可回放和归因，持久写入可审计并能说明确认数据的角色。

### 8.1 插件生命周期、组合性与可逆状态

Everything Is a Plugin 要求每个组件都有可审计的生命周期：

`load → validate → stage → activate → observe → deactivate → cleanup → archive`

`validate` 检查契约、权限和依赖，`stage` 在隔离环境中构造候选，`activate` 记录原子状态转移，`deactivate` 停止进程，`cleanup` 撤销注册项并清理缓存和临时文件。拒绝候选后，文件树、运行时资源和持久 memory 都应恢复到同一个 parent 状态；只回滚文件版本并不能恢复行为。

插件注册表应记录版本、依赖、能力、权限、状态哈希、来源和兼容性约束。依赖变化要触发下游组件重新验证，卸载要确认临时副作用已清理。候选写入与确认写入必须分开：动态 plugin 可在隔离 sandbox 中试运行，持久 skill、memory、workflow 和 Agent Note 需要版本控制、检查以及人工或独立确认。Agent Note 应保留明确的生命周期状态和拒绝理由。

运行时的 skill 是可替换输入。只有经过记录、版本化和 gate 确认的 skill，才可以承担跨任务的持久行为约束；目录可见性和按需加载路径应写入日志。

append-only 日志应覆盖模型可见输入、工具调用、子任务、上下文注入、评价器结果、状态快照、清理动作和数据角色，作为回放与归因的基础。memory 与 skill store 还需要压缩、过期、合并、删除和恢复规则，避免积累条目静默改变路由和行为。

### 8.2 端、边、云：按确认成本分配职责

端、边、云不是部署事实，而是一个可检验的职责划分假设。端侧承担低延迟交互和候选生成，边侧承担运行时控制与状态编排，云侧承担需要独立数据和更大计算预算的确认。一个最小分工如下：

| 层级 | 主要职责 | 状态权限与数据边界 | 需要验证的指标 |
|---|---|---|---|
| **端（endpoint）** | 任务交互；候选生成；contract、compile、smoke 和低成本 replay；在隔离环境中运行动态 plugin；用 PTC（programmatic tool calling）类方式把确定性的多步工具调用交给程序执行 | 候选和原始轨迹可以是易失状态；不得直接写入 evaluator、任务集、model route 或 durable registry | 交互延迟、静态拒绝率、smoke 过滤收益、端侧回滚完整性、隐私泄露 |
| **边（edge/control plane）** | 调度任务和子进程；维护 plugin registry、版本、依赖和 replay metadata；执行策略、分阶段激活、canary 和冲突检查；汇总 append-only 事件 | 维护 staging 状态和状态哈希；强制保护评价器、日志和权限路径；边侧分数不能单独触发晋级 | activation/cleanup 完整性、依赖冲突、验证延迟、跨版本失效率、晋级率 |
| **云（cloud/independent evaluator）** | fresh/OOD confirmation；长期 regression；安全与 evaluation-integrity audit；跨版本统计、谱系归档和经过授权的模型反馈 | confirmation 集不能暴露给 proposer、selector 或停止规则；任务、评价器和模型路由保持不可写；输出只返回确认结果，不直接激活候选 | fresh-task 收益、old-task 保留、确认成本、审计覆盖、跨租户隐私和资源成本 |

把任务放到 cloud 不会自动产生统计独立性。必须记录数据访问边界、确认集刷新策略、候选是否固定，以及 confirmation rollout 是否回流到搜索排序。端、边、云的价值在于隔离职责和成本，不在于改变 PAC-style boundary 的前提。

### 8.3 评价器、长期目标、记忆与失败多样性

许多任务没有快速、精确且不可操纵的 verifier。应采用分层证据：静态契约和权限检查用于可执行性，任务级结果用于行为性能，held-out/fresh task 用于泛化，trace audit 或人工评审用于安全和难以形式化的质量。评价器、任务数据、日志、模型路由和 reasoning budget 应位于可编辑面之外。[Misevolution](https://arxiv.org/abs/2509.26354)、[Reward Hacking](https://arxiv.org/abs/2209.13085)、[Reward Model Overoptimization](https://arxiv.org/abs/2210.10760) 和 [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) 提供风险锚点，用来说明这些控制为什么必要，但不证明现有 HarnessOpt 系统已经满足它们。

长期评测还应包含可维护性、所有权、迁移、兼容和调试成本。研究或开放式任务应在单独预算下保留低分但有新颖性或解释价值的分支，并记录行为描述、失败原因和重试条件，以维持超出当前评价器的多样性。

失败尝试应保留为可检索但不激活的记录。每条 skill 或 Agent Note 应携带适用范围、证据来源、反例、替代方案和状态历史；压缩与合并必须转移仍然有效的契约和覆盖缺口。规模增大后，应使用语义检索、分层目录或按任务生成子集，并记录路由决策。

日志提供归因材料，但不能自动判定失败源于 skill 内容、模型未遵循、环境漂移，还是错误的 skill 路由。只有具备组件级归因，轨迹才足以支持局部提议以及编辑、降权、过期或删除决策。

### 8.4 Model–harness co-design 与人类授权

可验证的共同演化回路是：轨迹暴露重复失败，Harness 提出有界修改，独立确认检查收益、non-regression 和安全，稳定经验进入 plugin、skill 或独立训练流程，再通过 ablation 检查减少脚手架后是否仍保持 fresh-task 收益。只有行为在脚手架减少后仍保持，才支持“经验被内化”的判断。

模型可以自主生成候选，但持久状态的写权限仍需经过独立门控和人工监督。人工应审查高影响权限、评价器变更、谱系合并、语义正确性和维护承诺；持久状态应记录这条授权路径。

### 8.5 开放问题

四组相互关联的问题仍然开放：

1. 在弱或模糊评价器、确认集复用和任务漂移下，如何给多轮晋级提供可审计的独立性与置信度？
2. 如何在长程任务中联合管理上下文、skill 和 memory 的路由、压缩、遗忘与负结果保留，并保持已确认行为？
3. 如何定量描述稳定性、可塑性、探索多样性与 reward-hacking 风险之间的权衡？
4. 如何在端、边、云之间分配高成本确认、人工复核和模型适配，并在合并独立演化谱系后重新确认行为对齐？

## 配套文档

| 文档 | 用途 |
|---|---|
| [docs/zo-operator-map.md](docs/zo-operator-map.md) | 经典算子要求和 HarnessOpt 的保守标记 |
| [docs/pac-stability.md](docs/pac-stability.md) | 固定候选界、多轮复用、稳定性和不能推出的结论 |
| [docs/audit-table.md](docs/audit-table.md) | 各系统的确认、评价器保护和回滚字段 |
| [docs/literature-map.md](docs/literature-map.md) | 围绕主线的文献缺口和下一轮一手来源核查字段 |
| [docs/glossary.md](docs/glossary.md) | 符号和协议术语 |

## 引用

~~~bibtex
@misc{harnessopt_zo_pac_2026,
  title        = {A Zeroth-Order and PAC View of Agent Harness Optimization},
  author       = {Wei, Chuyang and Shen, Yifei},
  year         = {2026},
  howpublished = {\url{https://github.com/Weichy9218/Awesome-Harness-Self-Evolving}}
}
~~~

## License

[MIT](LICENSE)。论文元数据版权归各自作者所有。
