<!-- harness 自演化阅读清单，按编辑面、提出机制、确认协议组织。BEGIN/END 标记之间由
     scripts/build_readme.py 从 data/papers.json 生成——请改数据，不要改标记内的markup。
     其余部分为手写。 -->

# Awesome Harness Self-Evolving

**harness 自演化阅读清单：运行时证据如何改变冻结模型周围的软件，以及一个候选要满足什么条件才能成为持久状态。**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | **中文**

> **核心论断.** 自演化 harness 的定义不在于它能编辑多少种对象，而在于一个可审计的更新循环——**编辑面**、**提出机制**、**状态转移协议**三者分开记录。在本清单核查过的工作里，提出机制很常见；候选级的独立确认仍然罕见。

## 目录

- [什么算 harness 自演化](#什么算-harness-自演化)
- [如何阅读本清单](#如何阅读本清单)
- [完整目录](#完整目录)
- [按编辑面浏览](#按编辑面浏览)
- [评测基准与运行基底](#评测基准与运行基底)
- [综述与相关清单](#综述与相关清单)
- [配套文档](#配套文档)
- [贡献](#贡献)
- [引用](#引用) · [许可](#许可)

## 什么算 harness 自演化

**harness** 是模型与任务之间的可执行系统：它加载指令与上下文、路由 memory 与 skill、调度 workflow、调用工具、执行权限、跑验证或 replay hook。记 $H_s$ 为在版本化的模型外部状态 $s$ 下的这次执行，任务 $z$ 产生 $\tau = H_s(M, z)$。

同时满足三条才收录：

1. 讨论的这次更新中，**基座模型是冻结的**；
2. **运行时证据**影响了一个明确划定的状态集合 $\mathcal S_{\mathrm{edit}}$ 的改动；
3. **改动后的状态被后续运行重新加载**，并在存在接受/拒绝规则时把该规则写明。

临时上下文、进程、缓存和生成文件属于单次运行，不属于 $s$，除非被显式版本化并重新加载。任务、评测器、模型路由、权限和日志默认是受保护的边界组件：候选若能改动它们，那是评测边界变更，不是普通的 harness 编辑。

收录范围：prompt optimization、自演化 memory 与 skill、workflow search、自修改 harness 代码、optimizer/meta-harness 代码。同时更新 harness 与权重的方法属于边界情形，会显式标记。纯权重训练与手工 harness 设计只在澄清边界时出现。

## 如何阅读本清单

每个条目记录三个字段，它们描述**同一个更新循环的不同部分**，互不等价。

| 字段 | 回答什么问题 | 取值 |
|---|---|---|
| **编辑面** | 什么持久对象可以改变？ | `L0`–`L5`，见下表 |
| **提出机制** | 谁形成候选，依据什么证据？ | `proposer`、`search`、`co-learning`、`runtime policy`、`self-modifier` |
| **确认协议** | 什么规则裁定候选成为下一个状态，哪些数据能影响该规则？ | `直写`、`搜索期选择`、`分离确认` |

层级是**对象范围，不是能力评分**。层级更高不等于系统更好。

| 层级 | 可编辑对象 | 典型编辑单元 |
|---|---|---|
| **L0** | 指令 prompt | prompt、指令块、示例 |
| **L1** | 上下文、memory、skill | 条目、文件、检索单元、可执行 skill |
| **L2** | workflow、图、架构 | 节点、边、子图、模块槽位 |
| **L3** | harness 或 agent 代码 | 文件、模块、工具、插件 |
| **L4** | improver、optimizer、上下文机制 | proposer、selector、搜索算子 |
| **L5** | harness **与**模型联合适配 | checkpoint、LoRA、prefix 加 harness 状态 |

标记：`†` 边界条目（模型–harness 联合、仅运行时、或自修改） · `‡` 邻接的程序演化样本 · `ᴮ` 冻结计数快照之外的覆盖条目 · `—` 刻意留空。

`ᴮ` 说的是**计数**，不是论文本身。配套 survey 撰写期间快照冻结，因此新条目即使字段已核过也留在快照之外；这类条目在大表中带 `audit` 链接，指向 [docs/audit-table.md](docs/audit-table.md)。

<!-- BEGIN:STATS -->
Ledger revision `2026-09-04.v6.2-working` 的计数快照：**33** 条填满六个审计字段并计入下表；另有 **19** 条覆盖条目位于冻结快照之外，不计入任何协议——其中部分已有逐字段记录，在大表中以 `audit` 链接标出。

| 状态转移协议 | 含义 | 条目数 |
|---|---|---:|
| ✍️ 直写 | 候选进入持久状态，没有候选级的阻断性评估 | 11 |
| 🔍 搜索期选择 | 用提出候选的同一批数据对候选排序或保留 | 19 |
| ✅ 分离确认 | 候选先固定，再由一次可阻断晋级的独立评估裁决 | 3 |
| — 不计入 | 冻结快照之外的覆盖条目；不计入任何协议 | 19 |

> ✅ 的稀缺正是本清单要说明的事。提出机制很常见，候选级的独立确认并不常见。协议字段只在 primary source 能确立时才填写——绝不从层级、benchmark 或论文里出现"validation" 一词反推。
<!-- END:STATS -->

为什么提出与确认必须分开记录：在产生候选的同一批任务上观察到的提升，支持的是一个排序，而不是关于新任务的保证。只有 `分离确认` 才允许固定候选的 holdout 推理，且必须满足独立性、有界损失与受保护边界假设——见 [docs/pac-stability.md](docs/pac-stability.md)。人工复核、沙箱、审计日志与回滚是治理控制，不产生统计独立性。永远不被执行的 hook 等价于没有 gate。

提出侧见 [docs/zo-operator-map.md](docs/zo-operator-map.md)：它把每种机制映射到对应的零阶算子，并说明类比在哪里失效——文本批评不是数值梯度，parent/child 配对不是中心差分，被拒候选缓冲区不是 control variate。

## 完整目录

<!-- BEGIN:CATALOGUE -->
| 论文 | 出处 | 编辑面 | 提出机制 | 协议 | 链接 |
|---|---|---|---|---|---|
| **APE** · [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910) | arXiv'22 | L0 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2211.01910) |
| **OPRO** · [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409) | arXiv'23 | L0 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2309.03409) [code](https://github.com/google-deepmind/opro) [audit](docs/audit-table.md#representative-systems) |
| **Promptbreeder** · [Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution](https://arxiv.org/abs/2309.16797) | arXiv'23 | L0 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2309.16797) |
| **MIPROv2** · [Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs](https://arxiv.org/abs/2406.11695) | arXiv'24 | L0 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2406.11695) [audit](docs/audit-table.md#representative-systems) |
| **GEPA** · [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) | arXiv'25 | L0 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2507.19457) [code](https://github.com/gepa-ai/gepa) [audit](docs/audit-table.md#representative-systems) |
| **ProTeGi** ᴮ · [Automatic Prompt Optimization with “Gradient Descent” and Beam Search](https://arxiv.org/abs/2305.03495) | arXiv'23 | L0 | — | — | [abs](https://arxiv.org/abs/2305.03495) |
| **TextGrad** ᴮ · [TextGrad: Automatic “Differentiation” via Text](https://arxiv.org/abs/2406.07496) | arXiv'24 | L0 | — | — | [abs](https://arxiv.org/abs/2406.07496) |
| **Reflexion** · [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) | arXiv'23 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2303.11366) [audit](docs/audit-table.md#representative-systems) |
| **Voyager** · [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) | arXiv'23 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2305.16291) [audit](docs/audit-table.md#representative-systems) |
| **ExpeL** · [ExpeL: LLM Agents Are Experiential Learners](https://arxiv.org/abs/2308.10144) | arXiv'23 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2308.10144) |
| **Dynamic Cheatsheet** · [Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory](https://arxiv.org/abs/2504.07952) | arXiv'25 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2504.07952) |
| **ReasoningBank** · [ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory](https://arxiv.org/abs/2509.25140) | arXiv'25 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2509.25140) [code](https://github.com/google-research/reasoning-bank) |
| **Memp** · [Memp: Exploring Agent Procedural Memory](https://arxiv.org/abs/2508.06433) | arXiv'25 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2508.06433) [code](https://github.com/zjunlp/MemP) |
| **ACE** · [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2510.04618) | arXiv'25 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2510.04618) |
| **AWM** · [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) | arXiv'24 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2409.07429) |
| **MemAct** · [Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks](https://arxiv.org/abs/2510.12635) | arXiv'25 | L1 | runtime policy | ✍️ 直写 | [abs](https://arxiv.org/abs/2510.12635) |
| **Trace2Skill** · [Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills](https://arxiv.org/abs/2603.25158) | arXiv'26 | L1 | proposer | ✍️ 直写 | [abs](https://arxiv.org/abs/2603.25158) [audit](docs/audit-table.md#representative-systems) |
| **SkillCAT** · [SkillCAT: Contrastive, Assessment-Augmented and Topology-Aware Skill Self-Evolution for LLM Agents](https://arxiv.org/abs/2606.13317) | arXiv'26 | L1 | proposer | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2606.13317) [audit](docs/audit-table.md#representative-systems) |
| **SkillAdaptor** · [SkillAdaptor: Self-Adapting Skills for LLM Agents from Trajectories](https://arxiv.org/abs/2606.01311) | arXiv'26 | L1 | proposer | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2606.01311) [code](https://github.com/zjunlp/SkillAdaptor) [audit](docs/audit-table.md#representative-systems) |
| **SkillOpt** · [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904) | arXiv'26 | L1 | proposer | ✅ 分离确认 | [abs](https://arxiv.org/abs/2605.23904) [audit](docs/audit-table.md#representative-systems) |
| **SkillOpt-Lite** · [SkillOpt-Lite: Better and Faster Agent Self-evolution via One Line of Vibe](https://arxiv.org/abs/2607.03451) | arXiv'26 | L1 | proposer | ✅ 分离确认 | [abs](https://arxiv.org/abs/2607.03451) [code](https://github.com/EvolvingLMMs-Lab/SkillOpt-Lite) [audit](docs/audit-table.md#representative-systems) |
| **Evo-Memory** ᴮ · [Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory](https://arxiv.org/abs/2511.20857) | arXiv'25 | L1 | — | — | [abs](https://arxiv.org/abs/2511.20857) |
| **SkillForge** ᴮ · [SkillForge: Forging Domain-Specific, Self-Evolving Agent Skills in Cloud Technical Support](https://arxiv.org/abs/2604.08618) | arXiv'26 | L1 | — | — | [abs](https://arxiv.org/abs/2604.08618) [audit](docs/audit-table.md#representative-systems) |
| **AFlow** · [AFlow: Automating Agentic Workflow Generation](https://arxiv.org/abs/2410.10762) | arXiv'24 | L2 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2410.10762) [code](https://github.com/FoundationAgents/AFlow) |
| **MaAS** · [Multi-agent Architecture Search via Agentic Supernet](https://arxiv.org/abs/2502.04180) | arXiv'25 | L2 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2502.04180) |
| **AgentSquare** · [AgentSquare: Automatic LLM Agent Search in Modular Design Space](https://arxiv.org/abs/2410.06153) | arXiv'24 | L2 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2410.06153) [code](https://github.com/tsinghua-fib-lab/AgentSquare) |
| **GPTSwarm** ᴮ · [GPTSwarm: Language Agents as Optimizable Graphs](https://arxiv.org/abs/2402.16823) | arXiv'24 | L2 | — | — | [abs](https://arxiv.org/abs/2402.16823) [code](https://github.com/metauto-ai/gptswarm) |
| **MASS** ᴮ · [Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies](https://arxiv.org/abs/2502.02533) | arXiv'25 | L2 | — | — | [abs](https://arxiv.org/abs/2502.02533) |
| **ScoreFlow** ᴮ · [ScoreFlow: Mastering LLM Agent Workflows via Score-based Preference Optimization](https://arxiv.org/abs/2502.04306) | arXiv'25 | L2 | — | — | [abs](https://arxiv.org/abs/2502.04306) [code](https://github.com/Gen-Verse/ScoreFlow) |
| **Continual Harness** · [Continual Harness: Online Adaptation for Self-Improving Foundation Agents](https://arxiv.org/abs/2605.09998) | arXiv'26 | L3 | co-learning | ✍️ 直写 | [abs](https://arxiv.org/abs/2605.09998) |
| **ADAS** · [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435) | arXiv'24 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2408.08435) |
| **ELM** · [Evolution through Large Models](https://arxiv.org/abs/2206.08896) | arXiv'22 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2206.08896) |
| **ThetaEvolve** · [ThetaEvolve: Test-time Learning on Open Problems](https://arxiv.org/abs/2511.23473) | arXiv'25 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2511.23473) [code](https://github.com/ypwang61/ThetaEvolve) |
| **AlphaEvolve** · [AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery](https://arxiv.org/abs/2506.13131) | arXiv'25 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2506.13131) |
| **ShinkaEvolve** · [ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution](https://arxiv.org/abs/2509.19349) | arXiv'25 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2509.19349) |
| **DGM** · [Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) | arXiv'25 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2505.22954) |
| **SICA** · [A Self-Improving Coding Agent](https://arxiv.org/abs/2504.15228) | arXiv'25 | L3 | search | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2504.15228) |
| **DemoEvolve** · [DemoEvolve: Overcoming Sparse Feedback in Agentic Harness Evolution with Demonstrations](https://arxiv.org/abs/2605.24539) | arXiv'26 | L3 | proposer | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2605.24539) |
| **Self-Harness** · [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498) | arXiv'26 | L3 | proposer | ✅ 分离确认 | [abs](https://arxiv.org/abs/2606.09498) [audit](docs/audit-table.md#representative-systems) |
| **AutoHarness** ᴮ · [AutoHarness: improving LLM agents by automatically synthesizing a code harness](https://arxiv.org/abs/2603.03329) | arXiv'26 | L3 | — | — | [abs](https://arxiv.org/abs/2603.03329) [audit](docs/audit-table.md#representative-systems) |
| **Meta-Harness** ᴮ · [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/abs/2603.28052) | arXiv'26 | L3 | — | — | [abs](https://arxiv.org/abs/2603.28052) [code](https://yoonholee.com/meta-harness/) [audit](docs/audit-table.md#representative-systems) |
| **Agentic Harness Engineering** ᴮ · [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850) | arXiv'26 | L3 | — | — | [abs](https://arxiv.org/abs/2604.25850) [audit](docs/audit-table.md#representative-systems) |
| **Gödel Agent** · [Gödel Agent: A Self-Referential Agent Framework for Recursively Self-Improvement](https://arxiv.org/abs/2410.04444) | arXiv'24 | L4 | self-modifier | 🔍 搜索期选择 | [abs](https://arxiv.org/abs/2410.04444) |
| **STOP** ᴮ · [Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation](https://arxiv.org/abs/2310.02304) | COLM'24 | L4 | — | — | [abs](https://arxiv.org/abs/2310.02304) [audit](docs/audit-table.md#representative-systems) |
| **MCE** ᴮ · [Meta Context Engineering via Agentic Skill Evolution](https://arxiv.org/abs/2601.21557) | arXiv'26 | L4 | — | — | [abs](https://arxiv.org/abs/2601.21557) [audit](docs/audit-table.md#representative-systems) |
| **SEAL** ᴮ · [Self-Adapting Language Models](https://arxiv.org/abs/2506.10943) | arXiv'25 | L5‡ | — | — | [abs](https://arxiv.org/abs/2506.10943) |
| **SIA** ᴮ · [SIA: Self Improving AI with Harness & Weight Updates](https://arxiv.org/abs/2605.27276) | arXiv'26 | L5† | — | — | [abs](https://arxiv.org/abs/2605.27276) |
| **AdaEvolve** ᴮ · [AdaEvolve: Adaptive LLM Driven Zeroth-Order Optimization](https://arxiv.org/abs/2602.20133) | arXiv'26 | — | — | — | [abs](https://arxiv.org/abs/2602.20133) |
| **AutoAgent** ᴮ · [AutoAgent: Evolving Cognition and Elastic Memory Orchestration for Adaptive Agents](https://arxiv.org/abs/2603.09716) | arXiv'26 | — | — | — | [abs](https://arxiv.org/abs/2603.09716) |
| **Code as Agent Harness** ᴮ · [Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems](https://arxiv.org/abs/2605.18747) | arXiv'26 | — | — | — | [abs](https://arxiv.org/abs/2605.18747) |
| **Harness Updating Is Not Harness Benefit** ᴮ · [Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents](https://arxiv.org/abs/2605.30621) | arXiv'26 | — | — | — | [abs](https://arxiv.org/abs/2605.30621) [code](https://github.com/A-EVO-Lab/a-evolve/tree/release/harness-evolution) |
| **Ouroboros** ᴮ · [Ouroboros: A Self-Developing Frontier Coding Agent with Reviewed Core Evolution](https://arxiv.org/abs/2608.08311) | arXiv'26 | — | — | — | [abs](https://arxiv.org/abs/2608.08311) [audit](docs/audit-table.md#representative-systems) |
<!-- END:CATALOGUE -->

## 按编辑面浏览

<!-- BEGIN:BY-SURFACE -->
### L0 · 指令与 prompt

- **APE** · [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910) `arXiv'22` `🔍 搜索期选择`<br>  持久化 candidate prompts/search rounds；automated search controller 以 prompt 粒度写入；协议为 search-time selection。
- **OPRO** · [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409) `arXiv'23` `🔍 搜索期选择` · [code](https://github.com/google-deepmind/opro)<br>  持久化 search rounds；automated search controller 以 prompt 粒度写入；协议为 search-time selection。
- **Promptbreeder** · [Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution](https://arxiv.org/abs/2309.16797) `arXiv'23` `🔍 搜索期选择`<br>  持久化 population/archive；automated search controller 以 prompt 粒度写入；协议为 search-time selection。
- **MIPROv2** · [Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs](https://arxiv.org/abs/2406.11695) `arXiv'24` `🔍 搜索期选择`<br>  持久化 optimization rounds；automated search controller 以 prompt/demo set 粒度写入；协议为 search-time selection。
- **GEPA** · [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) `arXiv'25` `🔍 搜索期选择` · [code](https://github.com/gepa-ai/gepa)<br>  持久化 Pareto archive；automated search controller 以 prompt/field 粒度写入；协议为 search-time selection。
- **ProTeGi** ᴮ · [Automatic Prompt Optimization with “Gradient Descent” and Beam Search](https://arxiv.org/abs/2305.03495) `arXiv'23`<br>  textual feedback 加 beam search；`gradient` 措辞边界的参照点。
- **TextGrad** ᴮ · [TextGrad: Automatic “Differentiation” via Text](https://arxiv.org/abs/2406.07496) `arXiv'24`<br>  在 compound system 上反向传播文本批评；textual-gradient 措辞审查的核心对象。

### L1 · 上下文、记忆与 skill

- **Reflexion** · [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) `arXiv'23` `✍️ 直写`<br>  持久化 cross-trial/task memory；automated proposer 以 entry 粒度写入；协议为 write-through。
- **Voyager** · [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) `arXiv'23` `✍️ 直写`<br>  持久化 cross-task skill library；automated proposer 以 file/module 粒度写入；协议为 write-through。
- **ExpeL** · [ExpeL: LLM Agents Are Experiential Learners](https://arxiv.org/abs/2308.10144) `arXiv'23` `✍️ 直写`<br>  持久化 cross-task retrieval；automated proposer 以 entry 粒度写入；协议为 write-through。
- **Dynamic Cheatsheet** · [Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory](https://arxiv.org/abs/2504.07952) `arXiv'25` `✍️ 直写`<br>  持久化 cross-task memory；automated proposer 以 entry/file 粒度写入；协议为 write-through。
- **ReasoningBank** · [ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory](https://arxiv.org/abs/2509.25140) `arXiv'25` `✍️ 直写` · [code](https://github.com/google-research/reasoning-bank)<br>  持久化 cross-task memory；automated proposer 以 entry 粒度写入；协议为 write-through。
- **Memp** · [Memp: Exploring Agent Procedural Memory](https://arxiv.org/abs/2508.06433) `arXiv'25` `✍️ 直写` · [code](https://github.com/zjunlp/MemP)<br>  持久化 cross-task library；automated proposer 以 entry 粒度写入；协议为 write-through。
- **ACE** · [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2510.04618) `arXiv'25` `✍️ 直写`<br>  持久化 cross-round/task；automated proposer 以 entry/file 粒度写入；协议为 write-through。
- **AWM** · [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) `arXiv'24` `✍️ 直写`<br>  持久化 cross-task；automated proposer 以 entry/file 粒度写入；协议为 write-through。
- **MemAct** · [Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks](https://arxiv.org/abs/2510.12635) `arXiv'25` `✍️ 直写`<br>  持久化 within one long-horizon task; no cross-task persistence guarantee；learned runtime policy 以 in-place context segment 粒度写入；协议为 write-through。
- **Trace2Skill** · [Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills](https://arxiv.org/abs/2603.25158) `arXiv'26` `✍️ 直写`<br>  持久化 cross-round/task；automated proposer 以 patch/file 粒度写入；协议为 write-through。
- **SkillCAT** · [SkillCAT: Contrastive, Assessment-Augmented and Topology-Aware Skill Self-Evolution for LLM Agents](https://arxiv.org/abs/2606.13317) `arXiv'26` `🔍 搜索期选择`<br>  持久化 skill collection across tasks；automated proposer 以 patch/entry 粒度写入；协议为 search-time selection。
- **SkillAdaptor** · [SkillAdaptor: Self-Adapting Skills for LLM Agents from Trajectories](https://arxiv.org/abs/2606.01311) `arXiv'26` `🔍 搜索期选择` · [code](https://github.com/zjunlp/SkillAdaptor)<br>  持久化 cross-task skill collection；automated proposer 以 targeted patch 粒度写入；协议为 search-time selection。
- **SkillOpt** · [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904) `arXiv'26` `✅ 分离确认`<br>  持久化 cross-round；automated proposer 以 file/patch 粒度写入；协议为 separated confirmation。
- **SkillOpt-Lite** · [SkillOpt-Lite: Better and Faster Agent Self-evolution via One Line of Vibe](https://arxiv.org/abs/2607.03451) `arXiv'26` `✅ 分离确认` · [code](https://github.com/EvolvingLMMs-Lab/SkillOpt-Lite)<br>  持久化 cross-round；automated proposer 以 single file/patch 粒度写入；协议为 separated confirmation。
- **Evo-Memory** ᴮ · [Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory](https://arxiv.org/abs/2511.20857) `arXiv'25`<br>  self-evolving memory 的 test-time learning；需核查任务复用与 held-out 角色。
- **SkillForge** ᴮ · [SkillForge: Forging Domain-Specific, Self-Evolving Agent Skills in Cloud Technical Support](https://arxiv.org/abs/2604.08618) `arXiv'26`<br>  领域自进化 skills；L1 skill 家族的覆盖补强。

### L2 · workflow、图与架构

- **AFlow** · [AFlow: Automating Agentic Workflow Generation](https://arxiv.org/abs/2410.10762) `arXiv'24` `🔍 搜索期选择` · [code](https://github.com/FoundationAgents/AFlow)<br>  持久化 search rounds；automated search controller 以 graph/module 粒度写入；协议为 search-time selection。
- **MaAS** · [Multi-agent Architecture Search via Agentic Supernet](https://arxiv.org/abs/2502.04180) `arXiv'25` `🔍 搜索期选择`<br>  持久化 search rounds；automated search controller 以 block/graph 粒度写入；协议为 search-time selection。
- **AgentSquare** · [AgentSquare: Automatic LLM Agent Search in Modular Design Space](https://arxiv.org/abs/2410.06153) `arXiv'24` `🔍 搜索期选择` · [code](https://github.com/tsinghua-fib-lab/AgentSquare)<br>  持久化 search rounds；automated search controller 以 module/graph 粒度写入；协议为 search-time selection。
- **GPTSwarm** ᴮ · [GPTSwarm: Language Agents as Optimizable Graphs](https://arxiv.org/abs/2402.16823) `arXiv'24` · [code](https://github.com/metauto-ai/gptswarm)<br>  多 agent graph 与可微/RL 组件的混合边界。
- **MASS** ᴮ · [Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies](https://arxiv.org/abs/2502.02533) `arXiv'25`<br>  多阶段 prompt/topology 优化；不要与 Tier A 的 MaAS (2502.04180) 合并。
- **ScoreFlow** ᴮ · [ScoreFlow: Mastering LLM Agent Workflows via Score-based Preference Optimization](https://arxiv.org/abs/2502.04306) `arXiv'25` · [code](https://github.com/Gen-Verse/ScoreFlow)<br>  Score-DPO 连续化 workflow 优化；ZO 接口不覆盖的梯度型对照。

### L3 · harness 与 agent 代码

- **Continual Harness** · [Continual Harness: Online Adaptation for Self-Improving Foundation Agents](https://arxiv.org/abs/2605.09998) `arXiv'26` `✍️ 直写`<br>  持久化 online cross-round; joint branch；automated co-learning loop 以 module/script 粒度写入；协议为 write-through。
- **ADAS** · [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435) `arXiv'24` `🔍 搜索期选择`<br>  持久化 candidate agent programs；automated search controller 以 file/codebase 粒度写入；协议为 search-time selection。
- **ELM** · [Evolution through Large Models](https://arxiv.org/abs/2206.08896) `arXiv'22` `🔍 搜索期选择`<br>  持久化 population/archive；automated search controller 以 file/program 粒度写入；协议为 search-time selection。
- **ThetaEvolve** · [ThetaEvolve: Test-time Learning on Open Problems](https://arxiv.org/abs/2511.23473) `arXiv'25` `🔍 搜索期选择` · [code](https://github.com/ypwang61/ThetaEvolve)<br>  持久化 test-time rounds；automated search controller 以 program/file 粒度写入；协议为 search-time selection。
- **AlphaEvolve** · [AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery](https://arxiv.org/abs/2506.13131) `arXiv'25` `🔍 搜索期选择`<br>  持久化 population/archive；automated search controller 以 file/program 粒度写入；协议为 search-time selection。
- **ShinkaEvolve** · [ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution](https://arxiv.org/abs/2509.19349) `arXiv'25` `🔍 搜索期选择`<br>  持久化 population/archive；automated search controller 以 file/program 粒度写入；协议为 search-time selection。
- **DGM** · [Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) `arXiv'25` `🔍 搜索期选择`<br>  持久化 cross-round lineage；automated search controller 以 codebase/module 粒度写入；协议为 search-time selection。
- **SICA** · [A Self-Improving Coding Agent](https://arxiv.org/abs/2504.15228) `arXiv'25` `🔍 搜索期选择`<br>  持久化 cross-round candidates；automated search controller 以 codebase/module 粒度写入；协议为 search-time selection。
- **DemoEvolve** · [DemoEvolve: Overcoming Sparse Feedback in Agentic Harness Evolution with Demonstrations](https://arxiv.org/abs/2605.24539) `arXiv'26` `🔍 搜索期选择`<br>  持久化 archive/cross-round；automated proposer 以 file/patch 粒度写入；协议为 search-time selection。
- **Self-Harness** · [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498) `arXiv'26` `✅ 分离确认`<br>  持久化 cross-round lineage；automated proposer 以 single declarative file 粒度写入；协议为 separated confirmation。
- **AutoHarness** ᴮ · [AutoHarness: improving LLM agents by automatically synthesizing a code harness](https://arxiv.org/abs/2603.03329) `arXiv'26`<br>  自动合成 code harness，补足工程化覆盖；persistence 与 reload 路径在本轮审计中未核实。
- **Meta-Harness** ᴮ · [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/abs/2603.28052) `arXiv'26` · [code](https://yoonholee.com/meta-harness/)<br>  outer-loop 与 task-specific harness 的边界。
- **Agentic Harness Engineering** ᴮ · [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850) `arXiv'26`<br>  component/experience/decision observability；不自动等同于 confirmation gate。

### L4 · improver、optimizer 与上下文机制

- **Gödel Agent** · [Gödel Agent: A Self-Referential Agent Framework for Recursively Self-Improvement](https://arxiv.org/abs/2410.04444) `arXiv'24` `🔍 搜索期选择`<br>  持久化 runtime/cross-round；recursive self-modifier 以 module/runtime 粒度写入；协议为 search-time selection。
- **STOP** ᴮ · [Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation](https://arxiv.org/abs/2310.02304) `COLM'24`<br>  改写 improver/scaffolding 的递归自改。
- **MCE** ᴮ · [Meta Context Engineering via Agentic Skill Evolution](https://arxiv.org/abs/2601.21557) `arXiv'26`<br>  skill 与 context artifact 的双层演化；secondary L1。

### L5 · harness 与模型联合适配

- **SEAL** ᴮ · [Self-Adapting Language Models](https://arxiv.org/abs/2506.10943)‡ `arXiv'25`<br>  模型自生成微调数据（weight-only）；作为固定基座之外的邻接对照。
- **SIA** ᴮ · [SIA: Self Improving AI with Harness & Weight Updates](https://arxiv.org/abs/2605.27276)† `arXiv'26`<br>  权重与 harness 联合更新的范围对照；不占当前 L5 计数。

### 未定级 · 分析与范围锚点

- **AdaEvolve** ᴮ · [AdaEvolve: Adaptive LLM Driven Zeroth-Order Optimization](https://arxiv.org/abs/2602.20133) `arXiv'26`<br>  LLM-driven zeroth-order optimization；的正面 ZO 对照。持久写入对象待核，未定层级。
- **AutoAgent** ᴮ · [AutoAgent: Evolving Cognition and Elastic Memory Orchestration for Adaptive Agents](https://arxiv.org/abs/2603.09716) `arXiv'26`<br>  literature map 归入 direct harness evolution；本地无 primary source，层级未核实。
- **Code as Agent Harness** ᴮ · [Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems](https://arxiv.org/abs/2605.18747) `arXiv'26`<br>  把 code 组织为可执行、可验证、有状态的基底；scope/architecture 锚点，非单系统机制证据。
- **Harness Updating Is Not Harness Benefit** ᴮ · [Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents](https://arxiv.org/abs/2605.30621) `arXiv'26` · [code](https://github.com/A-EVO-Lab/a-evolve/tree/release/harness-evolution)<br>  解耦"能更新"与"受益于更新"；分析类工作，直接关系 / 的归因边界。
- **Ouroboros** ᴮ · [Ouroboros: A Self-Developing Frontier Coding Agent with Reviewed Core Evolution](https://arxiv.org/abs/2608.08311) `arXiv'26`<br>  reviewed core evolution、治理与恢复层；L3 或 L4 随变体而定，不在此处择一。
<!-- END:BY-SURFACE -->

## 评测基准与运行基底

以下都不能单独提供一套自演化协议。episodic benchmark 不度量持久状态；不同基座模型、harness、optimizer、评测器之间的分数不能直接相加。正确的评测单元是**演化轨迹**而非最终版本分数——报告 schema 见 [docs/evaluation-protocol.md](docs/evaluation-protocol.md)。

**任务基底**

- [SWE-bench](https://arxiv.org/abs/2310.06770) —— 仓库级 issue 求解，标准 coding 靶。
- [MLE-bench](https://arxiv.org/abs/2410.07095) —— 75 个 Kaggle 式机器学习工程任务。
- [RE-Bench](https://arxiv.org/abs/2411.15114) —— ML 研发任务，与人类专家对比。
- [PaperBench](https://arxiv.org/abs/2504.01848) —— 从零复现 20 篇 ICML 论文。
- [Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak) —— 终端原生的长程任务。

**harness 与环境基底**

- [SWE-agent](https://arxiv.org/abs/2405.15793) —— 面向仓库任务的 agent–computer 接口设计。
- [OpenHands](https://arxiv.org/abs/2407.16741) · [OpenHands SDK](https://arxiv.org/abs/2511.03690) —— 开源 agent 平台及其可编程 harness 层。
- [BrowserGym ecosystem](https://arxiv.org/abs/2412.05467) —— 统一的 web agent 环境与评测。
- [ToolSandbox](https://arxiv.org/abs/2408.04682) —— 有状态、对话式的工具使用评测。
- [$\tau$-bench](https://arxiv.org/abs/2406.12045) —— 领域策略约束下的 tool–agent–user 交互。
- [AgentDojo](https://arxiv.org/abs/2406.13352) —— 面向工具调用 agent 的对抗性 prompt injection 评测。
- [WorkArena](https://arxiv.org/abs/2403.07718) —— 真实 web 平台上的企业知识工作任务。

**测量完整性**

- [AI Agents That Matter](https://arxiv.org/abs/2407.01502) —— 只看 accuracy 的榜单掩盖了成本与 holdout 纪律。
- [HAL](https://arxiv.org/abs/2510.11977) —— 成本感知的第三方 agent leaderboard。

**促使引入 gate 的失败模式**

- [Misevolution](https://arxiv.org/abs/2509.26354) —— 自演化 agent 特有的涌现风险。
- [Defining and Characterizing Reward Hacking](https://arxiv.org/abs/2209.13085) · [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760) · [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) —— 代理分数上升为什么不等于系统变好。

## 综述与相关清单

**综述**

- [A Survey of Self-Evolving Agents](https://arxiv.org/abs/2507.21046) —— 按 what/when/how 与 model/memory/tools/architecture 组织自演化。
- [Comprehensive Survey of Self-Evolving AI Agents](https://arxiv.org/abs/2508.07407)
- [Survey on Self-Evolution of LLMs](https://arxiv.org/abs/2404.14387)
- [Survey of Context Engineering](https://arxiv.org/abs/2507.13334) —— 1400+ 篇，harness 的上下文一侧。
- [Rethinking Memory Mechanisms of Foundation Agents](https://arxiv.org/abs/2602.06052)
- [Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering](https://arxiv.org/abs/2604.08224) —— 与本清单对象最接近的综述。

**历史锚点**

- Good, *Speculations Concerning the First Ultraintelligent Machine* (1966) —— [DOI](https://doi.org/10.1016/S0065-2458%2808%2960418-0)
- Schmidhuber, [*Gödel Machines* (2003)](https://arxiv.org/abs/cs/0309048) —— proof-gated 自改写。
- Yudkowsky, [*Recursive Self-Improvement* (2008)](https://www.lesswrong.com/posts/JBadX7rwdcRFzGuju/recursive-self-improvement)
- Weng, [*Harness Engineering for Self-Improvement* (2026)](https://lilianweng.github.io/posts/2026-07-04-harness/) —— 把近期的循环定位在模型周围的 scaffolding。

**相关清单**

- [leezythu/Awesome-Harness-Self-Improvement](https://github.com/leezythu/Awesome-Harness-Self-Improvement)
- [Gloriaameng/Awesome-Agent-Harness](https://github.com/Gloriaameng/Awesome-Agent-Harness)

## 配套文档

| 文档 | 内容 |
|---|---|
| [docs/audit-table.md](docs/audit-table.md) | 逐系统的确认协议字段，以及读取这些字段所用的控制词 |
| [docs/pac-stability.md](docs/pac-stability.md) | 为什么只有 `分离确认` 允许 holdout 推理，以及在哪些假设下成立 |
| [docs/zo-operator-map.md](docs/zo-operator-map.md) | 提出机制到零阶算子的映射，以及类比失效的位置 |
| [docs/evaluation-protocol.md](docs/evaluation-protocol.md) | 轨迹报告 schema 与八个评测维度 |
| [docs/literature-map.md](docs/literature-map.md) | 主线缺口与审计队列 |
| [docs/open-problems.md](docs/open-problems.md) | 插件生命周期、部署分层、评测器、协同设计与治理 |
| [docs/glossary.md](docs/glossary.md) | 符号与协议术语 |

## 贡献

目录是**生成的**，所以 PR 改的是数据而非 markup。完整规则见 [CONTRIBUTING.md](CONTRIBUTING.md)，简版如下：

| 改动 | 位置 | 审核 |
|---|---|---|
| 补充或修正标题、出处、代码链接、一句话摘要 | [`data/paper-meta.md`](data/paper-meta.md) | 核实后合并 |
| 新增论文 | 开 issue；以覆盖条目（`ᴮ`）进入，位于计数快照之外 | 门槛低 |
| 指定或修改编辑面、提出机制、**确认协议** | 不接受 PR | 需上游完成 primary-source 审计 |

最后一行是刻意的。协议字段只在 primary source 能确立时才填写。请不要从系统的层级、benchmark 分数，或论文中出现 "validation" 一词反推——当原文没有说明时，留空就是正确答案。

数据改动后重新生成：

```bash
python3 scripts/build_readme.py
python3 scripts/check_consistency.py
```

## 引用

~~~bibtex
@misc{harness_self_evolving_list_2026,
  title        = {Awesome Harness Self-Evolving: A Reading List Organized by
                  Editable Surface, Proposal Mechanism, and Confirmation Protocol},
  author       = {Wei, Chuyang and Shen, Yifei},
  year         = {2026},
  howpublished = {\url{https://github.com/Weichy9218/Awesome-Harness-Self-Evolving}}
}
~~~

配套综述正在撰写中；本清单是其公开配套。

## 许可

[MIT](LICENSE)。论文元数据版权归各自作者所有。
