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

固定基座模型 $`M`$、任务分布 $`\mathcal D`$ 和外部评价边界。设 $`s`$ 为模型外部的软件状态，包括 prompt、context、memory、workflow、tool、agent code 和 optimizer code。Harness 在状态 $`s`$ 下执行任务 $`z`$，得到 $`\tau=H_s(M,z)`$。

本文只收录同时满足以下条件的工作：

1. 本轮更新中基座模型保持固定；
2. 运行时证据影响对显式集合 $`\mathcal S_{\mathrm{edit}}`$ 的修改；
3. 修改会影响后续运行，可以通过确认门进入，也可以无条件写入。

收录对象包括 prompt 优化、自演化 memory 和 skill、workflow 搜索、自修改 Harness code，以及 optimizer 或 meta-harness code。L5 的 Harness 与权重联合更新属于边界情形。纯权重训练和手工设计 Harness 只在能够说明边界时出现。

## 更新架构

一次更新包含四个不同对象：可编辑集合 $`\mathcal S_{\mathrm{edit}}`$、证据收集 $`Q`$、候选提议器 $`P_\phi`$ 和状态转移门 $`G`$。

```math
\mathcal E_t=Q(s_t;D_t),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
```

$`Q`$ 在提议任务 $`D_t`$ 上收集轨迹、回报、错误和反馈；$`P_\phi`$ 在 $`\mathcal S_{\mathrm{edit}}`$ 内形成候选；$`G`$ 使用确认数据 $`V_t`$ 接受、拒绝或回滚候选。候选 $`\widetilde s_{t+1}`$ 只有在状态转移规则允许后，才是持久状态 $`s_{t+1}`$。

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
| **L2** | workflow、graph、architecture | 节点、边、子图、模块槽位 | [GPTSwarm](https://arxiv.org/abs/2402.16823)、[AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[MASS](https://arxiv.org/abs/2502.02533)；[ADAS](https://arxiv.org/abs/2408.08435) 为 L3/secondary L2 |
| **L3** | Harness 或 agent code | 文件、模块、工具、插件 | [ADAS](https://arxiv.org/abs/2408.08435)、[DGM](https://arxiv.org/abs/2505.22954)、[SICA](https://arxiv.org/abs/2504.15228)、[Self-Harness](https://arxiv.org/abs/2606.09498)、[AHE](https://arxiv.org/abs/2604.25850)、[AutoHarness](https://arxiv.org/abs/2603.03329)、[Meta-Harness](https://arxiv.org/abs/2603.28052) |
| **L4** | optimizer 或 context-management mechanism | proposer、selector、搜索算子 | [STOP](https://arxiv.org/abs/2310.02304)、[MCE](https://arxiv.org/abs/2601.21557) |
| **L5** | Harness 与模型联合适配 | checkpoint、LoRA、prefix 及 Harness state | [SIA](https://arxiv.org/abs/2605.27276)；[SEAL](https://arxiv.org/abs/2506.10943) 作为纯 weight-update 邻接对照 |

一项工作可以同时出现在多个分析轴上。层级只说明改了什么，后文说明候选如何产生以及哪些证据能够支持持久化。

### 代表性条目

- **Prompt 优化（L0）。** [MIPROv2](https://arxiv.org/abs/2406.11695) 用 Bayesian optimization 联合提出 instruction 和 demonstration。[TextGrad](https://arxiv.org/abs/2406.07496) 在复合系统中传播文本批评。两者都说明 textual gradient 可以描述提议过程，但不能当作数值导数。ZO analogy：surrogate-model search / trace-informed proposal。Gate：search-set。
- **Memory 与 skill 演化（L1）。** [ReasoningBank](https://arxiv.org/abs/2509.25140) 从成功和失败中提炼可复用策略。[Trace2Skill](https://arxiv.org/abs/2603.25158) 将轨迹局部经验合并为 patch。批量聚合可以扩大证据覆盖，但不会自动产生独立确认。ZO analogy：batch evidence + localized edit。Gate：open 或 search-set，取决于具体路径。
- **结构化 skill 确认（L1）。** [SkillOpt](https://arxiv.org/abs/2605.23904) 和 [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) 使用有界编辑和独立的 validation 阶段，是连接提议结构与候选级确认门的参考。ZO analogy：batch evidence + bounded edit。Gate：held-out。
- **Workflow 与代码搜索（L2–L3）。** [AFlow](https://arxiv.org/abs/2410.10762)、[AgentSquare](https://arxiv.org/abs/2410.06153)、[DGM](https://arxiv.org/abs/2505.22954) 和 [Meta-Harness](https://arxiv.org/abs/2603.28052) 让搜索空间更结构化。结构支持静态检查、组件边界和回放，也会增加耦合与回滚成本。ZO analogy：population / archive 或 localized edit。Gate：search-set。
- **边界情形。** [GPTSwarm](https://arxiv.org/abs/2402.16823) 和 [ScoreFlow](https://arxiv.org/abs/2502.04306) 对部分问题使用可微或 RL 式组件，用来标记 ZO interface 不再覆盖完整方法的情况。

## 3. 候选生成：ZO interface

### 3.1 目标接口

固定模型和任务分布后，一次运行产生：

```math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
```

对于文本、程序和文件树，除非先给出显式的连续参数化，否则 $`\nabla_s f_M(s)`$ 没有定义。因此，HarnessOpt 将运行过程视为目标接口：关于 $`f_M`$ 的信息只能通过部署状态并观察其结果获得。

proposer 还可以得到比标量回报更丰富的观测：

```math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
```

其中 $`\Psi`$ 包括轨迹、错误、工具调用和 verifier feedback。它改变了 $`P_\phi`$ 可用的信息，但不是数值导数、无偏梯度估计器或确认数据。除非状态比较和执行条件受到控制，轨迹本身不能识别某次编辑的因果贡献。

需要区分三件事：

- semantic feedback 是提议侧信息，不是 gradient estimator；
- compile、type、schema 和 interface 检查只能建立可执行性，不能证明任务性能；
- parent 与 child 的成对分数是状态间经验差。只有显式构造出所需的扰动结构时，才能讨论 central finite difference。

### 3.2 三条搜索轴

三条搜索轴对应提议过程的不同环节。证据构造说明查询哪些运行以及如何聚合观测；搜索几何说明编辑可以在表示空间的哪一部分形成；查询分配说明如何依据历史、surrogate 或保留候选决定下一次评测。三条轴在分析上可分解，在实现中可能相互耦合。

为使对应关系可以核查，令 $`\mathcal O_i(s)=\mathcal O(s,z_i;\xi_i)`$、$`Y_i(s)=Y(s,z_i;\xi_i)`$ 和 $`\Psi_i(s)=\Psi(s,z_i;\xi_i)`$，并令 $`\widehat f_D(s)=m^{-1}\sum_{i=1}^{m}Y_i(s)`$。$`s\oplus\delta`$ 表示对状态 $`s`$ 应用合法编辑 $`\delta`$，$`\mathcal H_t`$ 表示第 $`t`$ 轮以前的状态、观测和分数历史，$`b`$ 表示在结果观测前已经声明的组件块；若系统提供行为描述子，记为 $`d_{\mathrm{beh}}(s,s')`$，候选谱系标识记为 $`\lambda(s)`$。经典 ZO 公式中的 $`u`$ 是随机数值方向，$`d_x`$ 是连续参数维度；Harness-native 状态通常没有这两个对象。

| 设计轴 | 机制家族 | Harness-native 形式（形式化） | 与经典 derivative-free 方法的对应关系（形式化） | 代表工作 |
|---|---|---|---|---|
| **证据构造** | single-state semantic proposal | $`\delta_t=P_\phi(s_t,\{\mathcal O_i(s_t)\}_{i=1}^{m})`$，候选为 $`s_t\oplus\delta_t`$，提议前不查询编辑状态。 | 只有目标接口对应。经典 one-point ZO 需要 $`\widehat g_{1p}=(d_x/\mu)Y(x+\mu u)u`$（或带基线修正的变体）；本类方法没有数值方向 $`u`$ 和步长 $`\mu`$，不构成该估计器。 | Reflexion、Voyager、ProTeGi、TextGrad |
|  | batch evidence aggregation | $`\overline{\Psi}_D(s)=\mathrm{Agg}(\{\Psi_i(s)\}_{i=1}^{m})`$，并以 $`\widehat f_D(s)`$ 聚合回报。 | 对应同一点上的重复噪声查询：$`\widehat f_m(s)=m^{-1}\sum_i y_i(s)`$，在独立同分布假设下 $`\mathrm{Var}[\widehat f_m(s)]=\sigma^2/m`$；任务不是扰动方向。 | SkillOpt、SkillOpt-Lite、Trace2Skill、ExpeL、SkillForge |
|  | paired state comparison | $`\widehat\Delta_D(s,\delta)=m^{-1}\sum_i[Y(s\oplus\delta,z_i;\xi_i^+)-Y(s,z_i;\xi_i^-)]`$。 | 对应 two-point ZO $`\widehat g_{2p}=(d_x/(2\mu))[f(x+\mu u)-f(x-\mu u)]u`$ 的比较骨架；没有连续参数化和可构造的正负扰动时，不是 central difference。 | SkillCAT、Trace2Skill 的 selective path |
| **搜索几何** | block-local edit | $`s'=s^{(b\leftarrow\delta_b)}`$，其中块 $`b`$ 在结果观测前固定。 | 对应 block-coordinate 更新 $`x'=x+U_b d_b`$；需要预定义坐标，且不假定块间可分离。 | SkillAdaptor、AgentSquare、DemoEvolve、AlphaEvolve |
|  | bounded local search | $`s'\in\mathcal N_L(s)\cap\mathcal S_{\mathrm{feas}}`$，例如 $`\mathcal N_L(s)=\{s':d_{\mathrm{syn}}(s,s')\le L\}`$。 | 与局部直接搜索或 trust-region 约束 $`d^\top d\le\Delta_k^2`$ 具有形式相似性；若 $`d_{\mathrm{syn}}`$ 不是行为距离且没有半径更新规则，只能称 bounded edit。 | SkillOpt、SkillOpt-Lite、SkillForge、Self-Harness |
| **查询分配** | history 或 surrogate allocation | $`a_{t+1}\in\arg\max_{a\in\mathcal A}\alpha_t(a\mid\mathcal H_t)`$，其中 $`a`$ 可表示候选、任务或 rollout 预算。 | 对应 acquisition 选择 $`x_{t+1}\in\arg\max_x\alpha_t(x\mid\mathcal H_t)`$ 或显式 bandit allocation；缺少 $`\alpha_t`$ 时只是历史启发式。 | ProTeGi、MIPROv2、AgentSquare、AdaEvolve |
|  | population 或 archive search | $`A_{t+1}=\mathrm{Select}_K(A_t\cup\mathrm{Offspring}(A_t))`$，选择可依赖 $`(\widehat f,d_{\mathrm{beh}},\lambda)`$。 | 对应 evolutionary update $`P_{t+1}=\mathrm{Select}(P_t\cup\mathrm{Mutate}(P_t))`$ 或 Pareto archive；保留候选不等于收敛，也不提供独立确认。 | GEPA、Promptbreeder、DGM、AlphaEvolve、Meta-Harness |

表中的公式是角色级形式化，不把离散编辑空间连续化。interface correspondence 只要求目标信息通过运行获得；structural correspondence 还要求存在预先定义的编辑单元、邻域或保留规则；strict correspondence 则要求满足经典算子的数值参数化、更新规则、距离结构和抽样假设。只有在这些条件同时成立时，才可以使用 central difference、trust region、bandit allocation 等经典术语。任何一个标签都不能单独推出收敛率、方差下降、行为半径或独立确认。

### 3.3 结构与成本

可编辑面决定搜索算子能够使用的结构。令 $`\mathcal S_{\mathrm{feas}}\subseteq\mathcal S_{\mathrm{edit}}`$ 表示满足 compile、type、interface 和写入路径契约的状态集合。静态检查可以判定候选是否属于这一构造性子集，但不能估计 $`f_M`$，也不能证明语义正确。

组件边界、allowlist、feature toggle、版本快照和确定性 replay 可以使局部编辑及成对比较具备可执行条件。这些结构不意味着代码优于文本。代码提供更强的结构约束，同时引入耦合、副作用和更大的回滚面。syntactic edit budget 只限制描述空间；如果没有额外的行为度量，它不能限制执行行为的变化幅度。

局部搜索只有在评测前已经确定可编辑组件和初始状态时才有明确含义。因此，Round-0 scaffold 属于状态定义，不构成性能改进证据。

Harness 查询的成本不相同，可用下面的分解式记账：

```math
C=n_{\mathrm{prop}}c_{\mathrm{prop}}+n_{\mathrm{static}}c_{\mathrm{static}}+n_{\mathrm{smoke}}c_{\mathrm{smoke}}+n_{\mathrm{task}}c_{\mathrm{task}}.
```

静态检查和 smoke test 在完整 task rollout 前过滤候选，但不能替代任务级确认。search evidence 和 confirmation evidence 必须分开统计。只有当任务、seed 和环境对齐后产生的协方差下降足以抵消额外执行成本时，成对评估才有统计上的理由；paired 标签本身不能证明这种下降。

由此得到的设计含义取决于运行条件。task rollout 成本较高时，应明确分配 proposer 深度、评测前过滤和候选数量的预算。执行噪声较高且 parent 与 child 可以对齐时，成对评估可能提高比较效率。如果能够直接度量行为变化，bounded search 比 token 数或 diff size 更有解释力。这些都是可检验的设计假设，不是本文核查系统的已证属性。

算子要求和保守标记见 [docs/zo-operator-map.md](docs/zo-operator-map.md)。

## 4. 候选确认：PAC-style boundary

### 4.1 两个不同的统计问题

令 $`\mathcal A`$ 将提议样本 $`D_n`$ 映射为持久状态，令 $`x`$ 为独立评测任务，令 $`D_n^{(i\leftarrow x_i')}`$ 表示用独立样本替换第 $`i`$ 个提议样本。提议稳定性可用 expected replace-one sensitivity 表示：

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

**B1，提议稳定性**，关注这一敏感性是否足够小。batch evidence、跨任务聚合和有界编辑可能降低单个提议样本对状态的影响。本文核查的系统没有系统测量 $`\beta_{\mathrm{avg}}`$，因此它属于设计假设，不是实证保证。expected on-average stability 本身也不能推出高概率界。

**B2，固定候选确认**，关注一个在没有使用确认样本 $`V_m`$ 的情况下被固定的候选，是否在新任务上表现良好。若 $`V_m\sim\mathcal D^m`$，损失取值在 $`[0,1]`$ 内，且 $`V_m`$ 没有参与候选生成、选择或停止决策，则 Hoeffding 不等式给出：

```math
\epsilon(\widetilde s)
\le
\widehat\epsilon_{V_m}(\widetilde s)
+\sqrt{\frac{\ln(1/\delta)}{2m}}
```

以至少 $`1-\delta`$ 的概率成立。如果一个任务使用多个 seed，seed 是给定任务条件下的重复观测；在完成任务级聚合后，$`m`$ 才表示独立任务数。对同一集合进行自适应复用后，改名为 validation 或 held-out 也不会恢复独立性。

B1 与 B2 不能互相替代。提议过程稳定，仍可能在复用的验证集上过拟合；真正独立的确认集可以评估固定候选，但不能证明 proposer 稳定。

确认评测的结果不能回流到候选提议、候选排序或停止决策。否则确认集已经成为搜索集的一部分。用于搜索和确认的任务级 rollout 应分别统计，并计入被拒候选。

### 4.2 三类状态转移协议

协议由状态转移发生的位置，以及能够影响该转移的数据共同决定。仅报告 final-test 结果，不能据此判定系统存在 promotion gate。

| 协议 | 状态转移语义 | 确认证据 | 能支持的结论 | 代表工作 |
|---|---|---|---|---|
| **Write-through** | 候选直接写入 memory、skill、workflow 或 code，没有候选级阻断规则。 | 没有独立确认数据。 | 后续任务只能提供回溯式经验表现。 | Reflexion、Voyager、ExpeL、ACE、ReasoningBank、Trace2Skill 默认路径 |
| **Search-time selection** | 在 proposal/search 数据上对候选或 archive 成员排序，选中对象成为下一状态。 | 与搜索过程同源。 | 支持已观察集合上的相对排序；锁定的 final test 可以评估完整流程，但不能证明晋级步骤有效。 | APE、OPRO、GEPA、AFlow、DGM、Meta-Harness、SkillCAT |
| **Separated confirmation** | 先固定候选，再由独立确认评测决定是否替换当前状态。 | 确认数据未参与提议和选择，但仍需检查跨轮复用和评价边界。 | 在假设成立时，支持固定候选层面的 holdout 推理。 | SkillOpt、SkillOpt-Lite、Self-Harness |

在本文核查集合中，三类协议的描述性数量为 **11 / 19 / 3**。统计范围限于 [docs/audit-table.md](docs/audit-table.md) 审计的系统，不代表整个领域的普查。

分离是协议属性，独立性还具有时间范围。SkillOpt-Lite 通过调整任务分配扩大确认集；Self-Harness 在多个演化轮次中复用固定的 held-in/held-out 划分。后者满足单轮分离，但不能自动提供跨轮 fresh confirmation。被拒候选同样会消耗确认集所包含的信息，即使它最终没有晋级。

只用于最终报告、没有参与状态转移的 untouched final test 不是 promotion gate。人工评审、sandbox、审计日志和 rollback 是正交控制，分别作用于写入权限、运行时保护和失败恢复，不建立统计独立性。门控必须在实现中实际执行；从未触发的 hook 与不存在门控等价。

### 4.3 B2 之外的三个条件

若任务分布划分为 $`K`$ 个任务簇，可写为 $`\epsilon(s)=\sum_{k=1}^{K}p_k\epsilon_k(s)`$。概率质量为 $`p_k`$ 的任务簇发生幅度为 $`\Delta\epsilon_k`$ 的退化时，总体风险只变化 $`p_k\Delta\epsilon_k`$。即使该簇的损失显著恶化，变化仍可能小于确认半径 $`\eta`$。因此，任务簇级 non-regression 需要分层采样和分别报告。

1. **判据覆盖。** 损失必须覆盖目标能力、重要任务簇、安全和策略维度。总体分数提高时，低概率能力仍可能退化。
2. **评价边界。** 任务、评价器、模型路由、日志、权限和受保护路径必须位于可编辑面之外，或由运行时强制保护。
3. **行为级拒绝。** 拒绝候选时要恢复进程、注册项、缓存、外部资源和持久 memory，不能只恢复文件树。

可达集、复用、成对比较和稳定性的细节见 [docs/pac-stability.md](docs/pac-stability.md)；逐系统字段见 [docs/audit-table.md](docs/audit-table.md)。

## 5. 评测：报告演化轨迹

合适的评测单位是 **evolution trajectory**，不是最终版本的单点分数。每次报告至少要公开以下五组字段：

| 字段组 | 最少内容 |
|---|---|
| **固定边界** | model、evaluator、tools、environment、permissions、editable surface |
| **数据角色** | proposal、selection、confirmation、regression、final-test 集合；样本量；复用次数；proposer 可见范围 |
| **状态历史** | $`s_0`$、每个接受的 $`s_t`$、被拒候选、最终 $`s_T`$，以及 old-task/OOD/fresh-task 曲线 |
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

本节把长期演化定义为受约束的状态转移问题，不把规则数量的增加视为能力增长。[Weng 对 Harness Engineering 的总结](https://lilianweng.github.io/posts/2026-07-04-harness/) 将弱评价器、上下文与记忆生命周期、负结果、多样性坍缩、奖励投机、长期成功和人类监督列为主要瓶颈。对 HarnessOpt 而言，这些瓶颈分别落在生命周期、部署边界、评价器、状态记忆和人类授权上。DeepSeek Harness 的公开讨论所概括的 “Model + Harness = Agent” 与 “Everything Is a Plugin”，可以作为插件化运行时的工程案例参考，但不能单独证明任何性能或自我进化结论（见 [q1](https://www.zhihu.com/question/2071331484284220938) 和 [q2](https://www.zhihu.com/question/2072255826778140869)）。

长期运行至少需要维持四个不变量：评价边界不可由候选修改，候选及其副作用可撤回，运行证据可回放和归因，持久写入可审计并能说明确认数据的角色。

### 6.1 插件生命周期、组合性与可逆状态

Everything Is a Plugin 要求的不是更多扩展点，而是每个组件都有可审计的状态机：

`load → validate → stage → activate → observe → deactivate → cleanup → archive`

其中 `validate` 负责契约、权限和依赖检查，`stage` 负责在隔离环境中构造候选，`activate` 必须是可记录的原子状态转移，`deactivate` 和 `cleanup` 必须撤销进程、端口、事件监听、provider/tool 注册、缓存和临时文件等副作用。拒绝候选后，文件树、运行时资源和持久 memory 都应恢复到同一个 parent 状态；只回退版本文件不构成行为级 rollback。

插件注册表至少需要记录版本、依赖、能力声明、权限、状态哈希、来源和兼容性约束。它还要处理两类组合性：时间上的卸载是否清理全部副作用，空间上的依赖变化是否触发下游组件重新验证。候选写入与确认写入必须分开。运行期由模型生成的动态 plugin 可以在隔离 sandbox 中试运行并撤回；持久的 skill、memory、workflow 和 Agent Note 应通过版本控制、格式检查和人工或独立确认后才能进入 durable state。建议为 Agent Note 固定 `proposed`、`implemented`、`rejected` 和 `archived` 状态，并保留拒绝理由、替代方案和覆盖缺口。

Skill 在运行时应被视为可替换的非权威输入。只有经过记录、版本化和 gate 确认的 skill，才可以承担跨任务的持久行为约束；模型可见的目录和按需加载路径也应纳入事件日志。

事件日志应采用 append-only 形式，至少覆盖模型可见输入、工具调用、子任务、上下文注入、评价器结果、状态快照和清理动作。日志既是回放和归因的基础，也是确认集与搜索集分离的审计记录。memory 与 skill store 还需要压缩、过期、合并、删除和恢复规则；只追加不淘汰会积累冲突，最终改变检索路由和行为分布。

### 6.2 端—边—云：按确认成本分配职责

端边云不是部署事实，而是一个可检验的职责划分假设。端侧承担低延迟交互和候选生成，边侧承担运行时控制与状态编排，云侧承担需要独立数据和更大计算预算的确认。一个最小分工如下：

| 层级 | 主要职责 | 状态权限与数据边界 | 需要验证的指标 |
|---|---|---|---|
| **端（endpoint）** | 任务交互；候选生成；contract、compile、smoke 和低成本 replay；在隔离环境中运行动态 plugin；用 PTC（programmatic tool calling）类方式把确定性的多步工具调用交给程序执行 | 候选和原始轨迹可以是易失状态；不得直接写入 evaluator、任务集、model route 或 durable registry | 交互延迟、静态拒绝率、smoke 过滤收益、端侧回滚完整性、隐私泄露 |
| **边（edge/control plane）** | 调度任务和子进程；维护 plugin registry、版本、依赖和 replay metadata；执行策略、分阶段激活、canary 和冲突检查；汇总 append-only 事件 | 维护 staging 状态和状态哈希；强制保护评价器、日志和权限路径；边侧分数不能单独触发晋级 | activation/cleanup 完整性、依赖冲突、验证延迟、跨版本失效率、晋级率 |
| **云（cloud/independent evaluator）** | fresh/OOD confirmation；长期 regression；安全与 evaluation-integrity audit；跨版本统计、谱系归档和经过授权的模型反馈 | confirmation 集不能暴露给 proposer、selector 或停止规则；任务、评价器和模型路由保持不可写；输出只返回确认结果，不直接激活候选 | fresh-task 收益、old-task 保留、确认成本、审计覆盖、跨租户隐私和资源成本 |

把任务放到 cloud 不会自动产生统计独立性。必须记录数据访问边界、确认集刷新策略、候选是否固定、以及 confirmation rollout 是否回流到搜索排序。端边云的价值在于隔离职责和成本，不在于改变 PAC-style boundary 的前提。

### 6.3 评价器、长期目标与失败多样性

许多真实任务没有快速、精确且不可操纵的 verifier。单一 pass rate、unit test 或 judge score 只能覆盖目标的一部分，还可能诱发 reward hacking。评价边界应位于可编辑面之外，并采用分层证据：静态契约和权限检查用于可执行性，任务级结果用于行为性能，held-out/fresh task 用于泛化，trace audit 和人工评审用于安全、研究判断和难以形式化的质量。评价器、任务数据、日志、模型路由和 reasoning budget 不应由演化回路修改。

长期成功还应包含仓库可维护性、所有权边界、迁移成本、向后兼容和后续调试负担。短期任务完成率提高，不能替代这些维度。对于研究或开放式任务，需要保留低分但有新颖性或解释价值的分支，并记录它们的行为描述、失败原因和未来重试条件；否则 population/archive 会收敛到当前评价器偏好的同质解。

### 6.4 记忆路由、负结果与归因

失败尝试不应被静默覆盖。每条 skill 或 Agent Note 都应携带适用范围、证据来源、已知反例、替代方案和状态变更历史；被拒候选保留在可检索但不激活的档案中。记忆压缩和合并只能在所有仍然有效的契约、理由和覆盖缺口都转移到新 owner 后执行。对大规模 skill 库，description 是路由键，单纯把完整目录注入上下文会随着规模增长而失效，需要语义检索、分层目录或按任务动态生成子集，并记录路由决策。

append-only 日志提供了归因所需的原始材料，但不能自动回答失败来自 skill 内容、模型未遵循、环境漂移，还是任务本身不适合该 skill。没有组件级归因，就无法把轨迹稳定地转化为下一轮的局部提议，也无法判断应当修改、降权、过期还是删除某个组件。

### 6.5 Model–harness co-design 与人类授权

可验证的共同演化回路应包含五步：轨迹暴露可重复失败；Harness 在声明的 editable surface 内提出有界修改；独立确认检查收益、non-regression 和安全；稳定经验进入可复用 plugin、skill 或经过单独训练流程的模型；随后通过 ablation 检查原先的补偿性脚手架能否删除，同时保持 fresh-task 收益。只有“脚手架减少且跨任务行为保持”才说明部分经验可能已经被模型或更底层机制吸收，规则数量增加或终点分数提高都不足以支持这一判断。

模型可以自主生成候选，但持久状态的写权限应由独立门控和人类监督共同决定。人工应介入高影响权限、评价器变更、谱系合并、语义正确性和长期维护承诺等节点，并在更高的抽象层审查目标、约束和证据，而不是只审核最终文本。这样保留的是可追溯的 human-gated durable state transition，而不是把未验证经验直接写入下一轮运行时。

### 6.6 开放问题

当前主线留下四组相互关联的问题：

1. 在弱或模糊评价器、确认集复用和任务漂移下，如何给多轮晋级提供可审计的独立性与置信度？
2. 如何在长程任务中联合管理上下文、skill 和 memory 的路由、压缩、遗忘与负结果保留，并保持已确认行为？
3. 如何定量描述稳定性、可塑性、探索多样性与 reward-hacking 风险之间的权衡？
4. 如何在端边云之间分配高成本确认、人工复核和模型适配，并在合并独立演化谱系后重新确认行为对齐？

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
