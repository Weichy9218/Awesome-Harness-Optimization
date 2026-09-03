<!-- Core reading list for model-external harness optimization, organized by editable surface, proposal mechanism, and confirmation protocol. -->

# Awesome Harness Optimization

**A reading list for Harness Optimization (HarnessOpt): how run-time evidence changes the software around a frozen language model, and how a candidate becomes persistent state.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** | [中文](README_zh.md)

> **Central claim.** HarnessOpt is not defined by how many objects a system can edit. Its defining structure is an auditable update loop that records the editable surface, the proposal mechanism, and the state-transition protocol separately. In the works checked here, proposal mechanisms are common; candidate-level independent confirmation is still uncommon.

## Contents

- [Scope](#scope)
- [Motivation: why HarnessOpt needs a separate view](#motivation-why-harnessopt-needs-a-separate-view)
- [§3. HarnessOpt: state and update loop](#3-harnessopt-state-and-update-loop)
- [Catalogue schema: the three axes](#catalogue-schema-the-three-axes)
- [§4. Editable surface: L0–L5](#4-editable-surface-l0l5)
- [§5. Candidate proposal: a ZO interface](#5-candidate-proposal-a-zo-interface)
- [§6. Confirmation and persistence: transition protocols](#6-confirmation-and-persistence-transition-protocols)
- [§7. Evaluation: report the trajectory](#7-evaluation-report-the-trajectory)
- [Literature map: mainline gaps](#literature-map-mainline-gaps)
- [§8. Future direction: governable evolution](#8-future-direction-governable-evolution)
- [Companion documents](#companion-documents)
- [Contributing](#contributing)
- [Citation](#citation)

## Scope

Fix a base model $M$, a task distribution $\mathcal D$, and an external evaluation boundary. Let $s$ be the versioned, model-external state that the update is allowed to persist. A **harness** is the executable system that mediates between $M$ and a task: it may load instructions and context, route memory and skills, schedule workflow steps, call tools, enforce permissions, and run verification or replay hooks. We write $H_s$ for that execution under state $s$ and the fixed runtime boundary, so a task $z$ produces $\tau=H_s(M,z)$.

The harness is broader than a prompt file, but not every runtime artifact is persistent harness state. Temporary context, processes, caches, and generated files belong to the run unless they are explicitly versioned and reloaded later. Tasks, evaluators, model routing, permissions, and logging are protected evaluation-boundary components by default; if a candidate can change them, report an evaluation-boundary change rather than an ordinary harness edit.

This list includes work that meets all three conditions:

1. the base model is fixed for the update under discussion;
2. run-time evidence influences a change to an explicitly delimited state set $\mathcal S_{\mathrm{edit}}$; and
3. the changed state is reloaded by later runs, with an explicit accept/reject rule when one exists.

The L0–L5 table is the core catalogue. Boundary readings and literature-map anchors are labeled explicitly; they remain coverage references rather than protocol-count entries until the persistence and write path are verified.

The list includes prompt optimization, self-evolving memory and skills, workflow search, self-modifying harness code, and optimizer/meta-harness code. L5 methods that update harness and weights together are boundary cases. Weight-only training and hand-authored harness design are listed only when they clarify the boundary.

Coverage follows the update loop rather than publication chronology. This is a representative, mainline-oriented catalogue, not a field-wide census; additions should clarify an editable surface, proposal mechanism, confirmation protocol, or trajectory-evaluation issue and be checked against the primary source.

## Motivation: why HarnessOpt needs a separate view

The older self-improvement literature asks whether a system can design a better successor. HarnessOpt studies the deployable software state around a fixed model. The important distinction is the strength of the conclusion:

| Evidence level | What it can support | Typical example |
|---|---|---|
| **Formal proof** | an internal proof that the rewrite improves utility | Gödel Machine; no current HarnessOpt system establishes this generally |
| **Probabilistic confirmation** | a fixed candidate is supported on untouched data under stated assumptions | PAC-style holdout reasoning; an open target for adaptive harness evolution |
| **Empirical improvement** | a candidate scores higher on observed tasks | the dominant practice in current systems |

The gap between the second and third rows is the reason to record proposal and confirmation separately.

**Background.** [Good, *Speculations Concerning the First Ultraintelligent Machine* (1966)](https://doi.org/10.1016/S0065-2458%2808%2960418-0) introduces the self-design idea; [Schmidhuber, *Gödel Machines* (2003)](https://arxiv.org/abs/cs/0309048) makes proof-gated self-rewriting explicit; [Yudkowsky, *Recursive Self-Improvement* (2008)](https://www.lesswrong.com/posts/JBadX7rwdcRFzGuju/recursive-self-improvement) names the loop; [Weng, *Harness Engineering for Self-Improvement* (2026)](https://lilianweng.github.io/posts/2026-07-04-harness/) places the near-term loop in the scaffolding around the model; and [Code as Agent Harness (2026)](https://arxiv.org/abs/2605.18747) organizes code as an executable, verifiable, stateful substrate. The last two are scope and architecture anchors, not evidence of independent confirmation.

## §3. HarnessOpt: state and update loop

One update has four distinct objects: the editable set $\mathcal S_{\mathrm{edit}}$, evidence collection $Q$, proposer $P_\phi$, and state-transition rule $G$.

```math
\mathcal E_t=Q(s_t;D_t^{\mathrm{prop}}),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
```

Here $Q$ collects traces, returns, errors, and feedback on proposal tasks $D_t^{\mathrm{prop}}$; $P_\phi$ creates a candidate inside $\mathcal S_{\mathrm{edit}}$; and $G$ accepts, rejects, or rolls back the candidate. $V_t$ denotes data consulted by $G$ when a confirmation step exists. The candidate $\widetilde s_{t+1}$ is not the persistent state $s_{t+1}$ until the transition rule says so.

| Object | Role | Persistence |
|---|---|---:|
| $s_t$ | accepted parent state reloaded by later tasks | yes |
| $r_{t,i}$ | per-run context, processes, caches, and temporary files | no by default |
| $\mathcal E_t$ | traces, returns, errors, and diagnostics supplied to the proposer | input, not state |
| $\widetilde s_{t+1}$ | proposed patch or replacement before the transition rule runs | only after $G$ accepts |

~~~mermaid
flowchart LR
    S["s_t · editable state<br/>prompt · memory · workflow · code"] --> Q["Q · run D_t^prop<br/>traces · returns · errors"]
    Q --> P["Pφ · form candidate<br/>ZO interface"]
    P --> G["G · state transition<br/>confirmation if separated"]
    G -->|accept| S
    G -->|reject / rollback| S
    G -.-> B["protected boundary<br/>model · evaluator · tasks · permissions"]
~~~

A pluginized runtime is one possible implementation of this loop. If components can be activated live, dependency resolution, isolation, atomic activation, and cleanup become part of the rollback audit. This is an engineering target, not a fourth analysis axis and not evidence that a listed system already provides safe live replacement.

The public catalogue follows the survey's division of labour: §3 defines the harness state and update loop; §4 asks what can be edited; §5 asks how candidates are proposed; §6 asks how candidates are confirmed and persisted; §7 evaluates the complete evolution trajectory; and §8 records governance questions. The three catalogue fields therefore map to §4–§6 rather than replacing those sections.

## Catalogue schema: the three axes

The catalogue records three complementary fields. They describe different parts of one update loop; none is a synonym for another.

| Axis | Question | Required record |
|---|---|---|
| **Editable surface** | What persistent object can change? | Primary level and secondary targets (`L0`–`L5`), plus persistence, write authority, and mutation granularity |
| **Proposal mechanism** | What does the proposer observe, and what structure constrains candidate formation? | Evidence construction, search geometry, and query allocation; record a concrete label such as `Proposal: batch evidence + localized edit` |
| **Confirmation protocol** | What executable rule decides whether a candidate becomes the next state, and what data can affect that rule? | `write-through`, `search-time selection`, or `separated confirmation`, together with `open`, `search-set`, `held-out`, `fresh test`, reuse, and boundary status |

Use this table as the catalogue schema. It is the minimum record for comparing systems and keeps a sophisticated proposer separate from an independent promotion gate.

`G` is the operational state-transition rule. `PAC-style confirmation` is a conditional statistical interpretation of `separated confirmation`. It requires a candidate fixed before evaluation, confirmation data independent of proposal and selection, bounded loss, and a protected evaluation boundary. A `write-through` or `search-time selection` rule can be a gate in the operational sense, but it does not satisfy that holdout condition. Human review, sandboxing, and rollback are governance controls, not statistical independence.

## §4. Editable surface: L0–L5

The level is an object range, not a capability score. Write authority, persistence, and enforcement must be recorded separately.

| Cross-cutting property | Question | Why it matters |
|---|---|---|
| **Write authority** | Does the agent write autonomously, or only after review? | Determines whether the update loop is closed. |
| **Persistence** | Is the change ephemeral, or committed to versioned state? | Determines whether errors can accumulate. |
| **Constraint enforcement** | Is the boundary stated in a prompt, or enforced by permissions, sandboxing, or static checks? | Determines whether the evaluator and protected paths remain outside the edit. |

| Level | Editable object | Typical edit unit | Representative work |
|---|---|---|---|
| **L0** | instruction prompt | prompt, instruction block, exemplar | [APE](https://arxiv.org/abs/2211.01910), [OPRO](https://arxiv.org/abs/2309.03409), [ProTeGi](https://arxiv.org/abs/2305.03495), [GEPA](https://arxiv.org/abs/2507.19457) |
| **L1** | context, memory, skill | entry, file, retrieval unit, executable skill | [Reflexion](https://arxiv.org/abs/2303.11366), [ExpeL](https://arxiv.org/abs/2308.10144), [ACE](https://arxiv.org/abs/2510.04618), [Voyager](https://arxiv.org/abs/2305.16291), [SkillOpt](https://arxiv.org/abs/2605.23904), [SkillOpt-Lite](https://arxiv.org/abs/2607.03451), [SkillCAT](https://arxiv.org/abs/2606.13317), [SkillAdaptor](https://arxiv.org/abs/2606.01311), [SkillForge](https://arxiv.org/abs/2604.08618); [MCE](https://arxiv.org/abs/2601.21557) has a secondary L1 context-artifact target |
| **L2** | workflow, graph, architecture | node, edge, subgraph, module slot | [GPTSwarm](https://arxiv.org/abs/2402.16823), [AFlow](https://arxiv.org/abs/2410.10762), [AgentSquare](https://arxiv.org/abs/2410.06153), [MaAS](https://arxiv.org/abs/2502.04180), [MASS](https://arxiv.org/abs/2502.02533); [ADAS](https://arxiv.org/abs/2408.08435) is L3 with secondary L2 |
| **L3** | harness or agent code | file, module, tool, plugin | [ADAS](https://arxiv.org/abs/2408.08435), [DGM](https://arxiv.org/abs/2505.22954), [SICA](https://arxiv.org/abs/2504.15228), [Self-Harness](https://arxiv.org/abs/2606.09498), [AHE](https://arxiv.org/abs/2604.25850), [AutoHarness†](https://arxiv.org/abs/2603.03329), [Meta-Harness](https://arxiv.org/abs/2603.28052) |
| **L4** | improver, optimizer, or context-management mechanism | proposer, selector, search operator | [STOP](https://arxiv.org/abs/2310.02304), [MCE](https://arxiv.org/abs/2601.21557) (primary L4; secondary L1) |
| **L5** | harness and model adaptation | checkpoint, LoRA, prefix plus harness state | [SIA](https://arxiv.org/abs/2605.27276); [SEAL](https://arxiv.org/abs/2506.10943) as a model-only adjacent control |

† AutoHarness is retained as a coverage anchor; its persistence and reload path remain unverified in this audit.

The same work may appear on more than one axis. The level says what is edited; the next sections say how proposals are formed and what evidence can justify persistence.

For the L3/L4 boundary, classify the primary level by the persistent write target, not by the role of the proposer. A system that searches for harness or agent code is L3; a system that persists changes to the improver, optimizer, or context-management mechanism is L4. If both are updated, record one primary target and the other as a secondary level, with the source location that supports the choice.

### Representative entries

- **Prompt optimization (L0).** [MIPROv2](https://arxiv.org/abs/2406.11695) jointly proposes instructions and demonstrations with Bayesian optimization. [TextGrad](https://arxiv.org/abs/2406.07496) propagates textual critiques through a compound system. Both expose why “textual gradient” is useful as a proposal description but not as a numerical derivative. `[Proposal: surrogate-model search + trace-informed]` `[Confirmation: search-time selection; data: search-set]`.
- **Memory and skill evolution (L1).** [ReasoningBank](https://arxiv.org/abs/2509.25140) distills reusable strategies from successes and failures. [Trace2Skill](https://arxiv.org/abs/2603.25158) merges trajectory-local lessons into patches. Their aggregation can broaden evidence, but it does not by itself create independent confirmation. `[Proposal: batch evidence + localized edit]` `[Confirmation: write-through or search-time selection, depending on the path]`.
- **Structured skill confirmation (L1).** [SkillOpt](https://arxiv.org/abs/2605.23904) and [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) use bounded edits and a separate validation stage. They are useful reference points for connecting proposal structure to a candidate-level transition rule. `[Proposal: batch evidence + bounded edit]` `[Confirmation: separated confirmation; data: held-out]`.
- **Contrastive skill evolution (L1).** [SkillCAT](https://arxiv.org/abs/2606.13317) compares same-task success and failure trajectories, replays candidate patches on source-task clones, and then merges selected patches. This is contrastive proposal evidence plus search-time selection; it is not independent confirmation. `[Proposal: paired state comparison + localized edit]` `[Confirmation: search-time selection; data: search-set]`.
- **Workflow and code search (L2–L3).** [AFlow](https://arxiv.org/abs/2410.10762), [AgentSquare](https://arxiv.org/abs/2410.06153), [DGM](https://arxiv.org/abs/2505.22954), and [Meta-Harness](https://arxiv.org/abs/2603.28052) make the search space more structured. Structure supports static checks, component boundaries, and replay; it also increases coupling and rollback cost. `[Proposal: population/archive or localized edit]` `[Confirmation: search-time selection; data: search-set]`.
- **Meta-level context co-evolution (L4 + L1).** [MCE](https://arxiv.org/abs/2601.21557) evolves the context-engineering skill while a base-level agent optimizes context artifacts. We classify the skill as primary L4 and the artifact as secondary L1; validation-based best-so-far selection remains search-time selection, not independent confirmation.
- **Boundary cases.** [GPTSwarm](https://arxiv.org/abs/2402.16823) and [ScoreFlow](https://arxiv.org/abs/2502.04306) use differentiable or RL-style components for part of the problem. [Continual Harness](https://arxiv.org/abs/2605.09998) adapts prompts, sub-agents, skills, and memory online within a run. These works mark where the ZO interface or the cross-run persistence criterion no longer describes the full method.

## §5. Candidate proposal: a ZO interface

Here `ZO interface` names a role-level correspondence: execution supplies objective information to the proposer. It does not claim a classical ZO estimator or a convergence guarantee.

### 5.1 Objective interface

Fix a base model $M$, a task distribution $\mathcal D$, and a bounded return $R$. For an editable state $s$, one execution with run randomness or environment seed $\xi$ returns

```math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
```

For text, programs, and file trees, $\nabla_s f_M(s)$ is not defined unless the representation is embedded in an explicit continuous parameterization. HarnessOpt therefore treats execution as an objective interface: information about $f_M$ is obtained by deploying a state and observing its result.

The proposer may receive a richer observation than a scalar return:

```math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
```

where $\Psi$ contains traces, errors, tool calls, and verifier feedback. $\Psi$ changes the information available to $P_\phi$, but it is not a numerical derivative, an unbiased gradient estimator, or confirmation evidence. A trace also does not identify the causal contribution of an edit unless the state comparison and execution conditions are controlled.

Three distinctions are required:

- semantic feedback is proposal-side information, not a gradient estimator;
- compile, type, schema, and interface checks establish feasibility, not task-level performance;
- a paired parent/child score is an empirical state difference, not a central finite difference unless the required perturbation structure is explicitly constructed.

### 5.2 Three search axes

The three axes classify different parts of the proposal process. Evidence construction describes which executions are queried and how their observations are aggregated. Search geometry describes the representation-level region in which an edit may be formed. Query allocation describes how history, surrogates, or retained candidates determine the next evaluations. They are separable analytically but may be coupled in an implementation.

To make the correspondence checkable, let $\mathcal O_i(s)=\mathcal O(s,z_i;\xi_i)$, $Y_i(s)=Y(s,z_i;\xi_i)$, and $\Psi_i(s)=\Psi(s,z_i;\xi_i)$, with $\widehat f_D(s)=m^{-1}\sum_{i=1}^{m}Y_i(s)$. Let $s\oplus\delta$ denote applying a legal edit $\delta$ to state $s$, let $\mathcal H_t$ be the history of states, observations, and scores before round $t$, and let $b$ be a component block declared before outcome observation. If the system provides a behavior descriptor, write it as $d_{\mathrm{beh}}(s,s')$, and write the candidate-lineage identifier as $\lambda(s)$. In classical ZO formulas, $u$ is a random numerical direction and $d_x$ is the dimension of the continuous parameterization; Harness-native states usually have neither object.

| Design axis | Mechanism family | Harness-native form (formal) | Correspondence to derivative-free optimization (formal) | Correspondence strength | Representative work |
|---|---|---|---|---|---|
| **Evidence construction** | single-state semantic proposal | $\delta_t=P_\phi(s_t,\{\mathcal O_i(s_t)\}_{i=1}^{m})$, with candidate $s_t\oplus\delta_t$; the edited state is not queried before proposal. | Interface correspondence only. Classical one-point ZO requires $\widehat g_{1p}=(d_x/\mu)Y(x+\mu u)u$ (or a baseline-corrected variant); this family has no numerical direction $u$ or step $\mu$, so it is not that estimator. | Interface | Reflexion, Voyager, ProTeGi, TextGrad |
|  | batch evidence aggregation | $\overline{\Psi}_D(s)=\mathrm{Agg}(\{\Psi_i(s)\}_{i=1}^{m})$, with returns aggregated by $\widehat f_D(s)$. | Repeated noisy queries at one state: $\widehat f_m(s)=m^{-1}\sum_i y_i(s)$, with $\mathrm{Var}[\widehat f_m(s)]=\sigma^2/m$ under an i.i.d. assumption; tasks are not perturbation directions. | Interface | SkillOpt, SkillOpt-Lite, Trace2Skill, ExpeL, SkillForge |
|  | paired state comparison | $\widehat\Delta_D(s,\delta)=m^{-1}\sum_i[Y(s\oplus\delta,z_i;\xi_i^+)-Y(s,z_i;\xi_i^-)]$. | The comparison skeleton of the two-point ZO estimator $\widehat g_{2p}=(d_x/(2\mu))[f(x+\mu u)-f(x-\mu u)]u$; without a continuous parameterization and constructible positive/negative perturbations, it is not a central difference. | Structural | SkillCAT, selective Trace2Skill paths |
| **Search geometry** | block-local edit | $s'=s^{(b\leftarrow\delta_b)}$, where block $b$ is fixed before outcome observation. | Structurally corresponds to a block-coordinate update $x'=x+U_b d_b$; coordinates must be predefined and block separability is not assumed. | Structural | SkillAdaptor, AgentSquare, DemoEvolve, AlphaEvolve |
|  | bounded local search | $s'\in\mathcal N_L(s)\cap\mathcal S_{\mathrm{feas}}$, for example $\mathcal N_L(s)=\{s':d_{\mathrm{syn}}(s,s')\le L\}$. | Resembles local direct search or a trust-region constraint $d^\top d\le\Delta_k^2$; if $d_{\mathrm{syn}}$ is not behavioral and no radius is updated, the correct label is bounded edit. | Structural | SkillOpt, SkillOpt-Lite, SkillForge, Self-Harness |
| **Query allocation** | history or surrogate allocation | $a_{t+1}\in\arg\max_{a\in\mathcal A}\alpha_t(a\mid\mathcal H_t)$, where $a$ may denote a candidate, task, or rollout budget. | Corresponds to acquisition $x_{t+1}\in\arg\max_x\alpha_t(x\mid\mathcal H_t)$ or an explicit bandit allocation; without $\alpha_t$, it is only a history heuristic. | Strict* | ProTeGi, MIPROv2, AgentSquare, AdaEvolve |
|  | population or archive search | $A_{t+1}=\mathrm{Select}_K(A_t\cup\mathrm{Offspring}(A_t))$, with selection based on $(\widehat f,d_{\mathrm{beh}},\lambda)$ when available. | Corresponds to an evolutionary update $P_{t+1}=\mathrm{Select}(P_t\cup\mathrm{Mutate}(P_t))$ or a Pareto archive; retention does not imply convergence or independent confirmation. | Structural | GEPA, Promptbreeder, DGM, AlphaEvolve, ShinkaEvolve, ThetaEvolve, MCE, Meta-Harness |

`*Strict` is conditional: it applies only when an explicit acquisition or bandit rule and its sampling assumptions are reported. Otherwise classify the method instance as structural or heuristic.

The formulas are role-level formalizations; they do not make the discrete edit space continuous. An interface correspondence only states that objective information is obtained through execution. A structural correspondence additionally requires a representation-level edit unit, neighborhood, or retention rule. A strict correspondence requires the numerical parameterization, update rule, distance structure, and sampling assumptions of the classical operator. A classical term such as central difference, trust region, or bandit allocation is justified only when those conditions hold. No label alone implies a convergence rate, variance reduction, behavioral radius, or independent confirmation set.

### 5.3 Structure and cost

The editable surface supplies the structure available to a search operator. Let $\mathcal S_{\mathrm{feas}}\subseteq\mathcal S_{\mathrm{edit}}$ denote states satisfying compile, type, interface, and write-path contracts. A static checker can test membership in this constructive subset, but it does not estimate $f_M$ or establish semantic correctness.

Component boundaries, allowlists, feature toggles, version snapshots, and deterministic replay can make local edits and paired comparisons executable. They do not imply that code is superior to text. Code supplies stronger structural constraints but also introduces coupling, side effects, and a larger rollback surface. A syntactic edit budget limits description space; it does not, without an additional behavioral metric, limit the change in execution behavior.

Local search is meaningful only when the editable components and the initial state are specified before evaluation. A Round-0 scaffold is therefore part of the state definition, not evidence that the update improved performance.

Harness queries have unequal cost. A useful accounting is

```math
C=n_{\mathrm{prop}}c_{\mathrm{prop}}+n_{\mathrm{static}}c_{\mathrm{static}}+n_{\mathrm{smoke}}c_{\mathrm{smoke}}+n_{\mathrm{task}}c_{\mathrm{task}}.
```

Static checks and smoke tests filter candidates before expensive task rollouts; they do not replace task-level confirmation. Search evidence and confirmation evidence must be counted separately. Paired evaluation is justified only when task, seed, and environment alignment produces sufficient covariance reduction to offset the additional execution cost; the paired label alone does not establish that reduction.

The resulting design implications are regime-dependent. When task rollouts are expensive, the budget should be allocated explicitly among proposer depth, pre-evaluation filters, and candidate count. When execution noise is high and parent and child states can be aligned, paired evaluation may improve comparison efficiency. When behavioral change can be measured more directly than token or diff size, bounded search becomes a more informative control. These are testable hypotheses, not established properties of the listed systems.

See [docs/zo-operator-map.md](docs/zo-operator-map.md) for the operator requirements and conservative labels.

## §6. Confirmation and persistence: transition protocols

This section uses PAC-style holdout reasoning as an analysis lens for one protocol, not as the name of the gate itself. The operational question is where the candidate can be accepted, rejected, or rolled back; the statistical question is whether the confirmation data remain independent of proposal and selection.

### 6.1 Two different statistical questions

Let $\mathcal A$ map a proposal sample $D_n$ to a persistent state. For a fresh evaluation task $x$, let $D_n^{(i\leftarrow x_i')}$ replace one proposal example with an independent draw. Proposal stability is represented by the expected replace-one sensitivity

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

**B1, proposal stability**, asks whether this quantity is small. Batch evidence, cross-task aggregation, and bounded edits are mechanisms that may reduce sensitivity to one proposal example. The checked systems do not systematically measure $\beta_{\mathrm{avg}}$; it is therefore a design hypothesis, not an empirical guarantee. Expected on-average stability alone also does not provide a high-probability bound.

**B2, fixed-candidate confirmation**, asks whether a candidate fixed without using a confirmation sample $V_m$ performs well on fresh tasks. If $V_m\sim\mathcal D^m$, the loss is bounded in $[0,1]$, and $V_m$ does not influence candidate generation, selection, or stopping, Hoeffding's inequality gives

```math
\epsilon(\widetilde s)
\le
\widehat\epsilon_{V_m}(\widetilde s)
+\sqrt{\frac{\ln(1/\delta)}{2m}}
```

with probability at least $1-\delta$. If a task is run with multiple seeds, the seeds are repeated observations conditional on that task; $m$ counts independent tasks after the stated task-level aggregation. Reusing the same set adaptively does not restore independence by renaming it validation or held-out.

B1 and B2 are not substitutes. A stable proposer can overfit a reused validation set; a genuinely fresh confirmation set can evaluate a fixed candidate without proving that the proposer is stable.

Confirmation evaluations must not feed back into proposal generation, candidate ranking, or stopping decisions. Otherwise the confirmation sample becomes part of the search set. Task-level rollouts used for search and confirmation should therefore be counted separately, including rejected candidates.

### 6.2 Three state-transition protocols

The protocol is determined by where the state transition occurs and by the data that can affect it. A final-test result does not, by itself, identify a promotion gate.

| Protocol | State-transition semantics | Confirmation evidence | What the evidence supports | Representative work |
|---|---|---|---|---|
| **Write-through** | The candidate is written into memory, skill, workflow, or code without a candidate-level blocking rule. | No separate confirmation evidence. | Later tasks provide retrospective empirical evidence only. | Reflexion, Voyager, ExpeL, ACE, ReasoningBank, Trace2Skill default path |
| **Search-time selection** | Candidates or archive members are ranked on proposal/search data, and the selected object becomes the next state. | Evidence is sourced from the same search process. | Relative ordering on the observed set; a locked final test can evaluate the completed procedure, but not certify the promotion step. | APE, OPRO, GEPA, AFlow, DGM, Meta-Harness, SkillCAT |
| **Separated confirmation** | A candidate is fixed before a separate confirmation evaluation decides whether it replaces the current state. | Confirmation data are excluded from proposal and selection, subject to reuse and boundary checks. | Fixed-candidate holdout reasoning under the stated assumptions. | SkillOpt, SkillOpt-Lite, Self-Harness |

In the checked set, the descriptive counts are **11 / 19 / 3** for write-through, search-time selection, and separated confirmation. The count is limited to the systems audited in [docs/audit-table.md](docs/audit-table.md); it is not a census of the field.

Separation is a protocol property; independence also has a time scope. SkillOpt-Lite changes task allocation to enlarge the confirmation set, while Self-Harness reuses a fixed held-in/held-out split across evolution rounds. The latter supports single-round separation but not automatically fresh confirmation across rounds. A rejected candidate also consumes information about the confirmation set, even when it is not promoted.

An untouched final test used only for reporting is not a promotion gate. Human review, sandboxing, audit logs, and rollback are orthogonal controls. They govern write authority, runtime protection, and recovery; they do not establish statistical independence. A gate must be active in the implementation. A hook that is never executed is equivalent to no gate.

### 6.3 Three conditions outside B2

Write $\epsilon(s)=\sum_{k=1}^{K}p_k\epsilon_k(s)$ for a distribution partitioned into task clusters. A degradation $\Delta\epsilon_k$ in a cluster of mass $p_k$ changes the aggregate risk by only $p_k\Delta\epsilon_k$. It can remain below a confirmation slack $\eta$ even when the cluster-level loss is materially worse. Cluster-level non-regression therefore requires stratified sampling and reporting.

1. **Criterion coverage.** The loss must include the target capability, important task clusters, safety, and policy dimensions. An aggregate score can improve while a low-mass capability deteriorates.
2. **Evaluation boundary.** Tasks, evaluators, model routing, logging, permissions, and protected paths must remain outside the editable surface or be enforced at run time.
3. **Behavioral rejection.** Rejection must restore processes, registrations, caches, external resources, and persistent memory, not only the file tree.

See [docs/pac-stability.md](docs/pac-stability.md) for the reachable-class, reuse, paired-comparison, and stability details, and [docs/audit-table.md](docs/audit-table.md) for per-system fields.

## §7. Evaluation: report the trajectory

The correct unit of evaluation is an **evolution trajectory**, not only the final version score. A trajectory report should make five groups of fields visible:

[Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) separates the ability to produce useful persistent updates from the ability of a task-solving agent to use those updates. A trajectory report should therefore measure both update quality and downstream harness interaction.

| Field group | Minimum content |
|---|---|
| **Fixed boundary** | model, evaluator, tools, environment, permissions, editable surface |
| **Data roles** | proposal, selection, confirmation, regression, and final-test sets; sample counts; reuse; proposer visibility |
| **State history** | $s_0$, every accepted $s_t$, rejected candidates, final $s_T$, and old-task/OOD/fresh-task curves |
| **Runtime cost** | model tokens, tool calls, wall-clock, task rollouts, memory growth, human interventions, rollback cost |
| **Audit artifacts** | diffs, traces, seeds, evaluator configuration, replay command, safety checks, and rejected branches |

Evaluate the trajectory along eight dimensions:

- **Adaptivity:** does the state improve on the failure distribution that motivated the update?
- **Retention and non-regression:** are earlier tasks and important clusters preserved?
- **Generalization and transfer:** does the gain hold on OOD or fresh tasks?
- **Harness interaction:** was the new state loaded, followed, and behaviorally effective?
- **Reliability and auditability:** can runs be replayed, attributed, and recovered?
- **Efficiency and maintainability:** what are the runtime, token, dependency, and state-growth costs?
- **Safety and policy compliance:** do safety and permission outcomes remain acceptable?
- **Evaluation integrity:** can the candidate alter the evaluator, task data, logging, or model route?

Benchmarks such as [SWE-bench](https://arxiv.org/abs/2310.06770), [Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak), [PaperBench](https://arxiv.org/abs/2504.01848), and long-horizon memory benchmarks can supply tasks. [AI Agents That Matter](https://arxiv.org/abs/2407.01502) and [HAL](https://arxiv.org/abs/2510.11977) motivate standardized cost and integrity reporting, while [RE-Bench](https://arxiv.org/abs/2411.15114) and [MLE-bench](https://arxiv.org/abs/2410.07095) provide long-horizon task substrates. None supplies the full protocol automatically. Episodic benchmarks do not measure persistent state; a visible smoke test may be only a proxy; and scores across different base models, harnesses, optimizers, and evaluators are not directly additive.

## Literature map: mainline gaps

The catalogue is anchored to four literature gaps that follow the update loop. The links below are coverage anchors, not evidence that every protocol field has already been audited; see the [literature map](docs/literature-map.md) for the audit queue and the [protocol table](docs/audit-table.md) for source-level classifications.

| Mainline question | Representative anchors | What to extract from the primary source |
|---|---|---|
| **Direct harness evolution** | [Code as Agent Harness](https://arxiv.org/abs/2605.18747), [AutoHarness](https://arxiv.org/abs/2603.03329), [SkillCAT](https://arxiv.org/abs/2606.13317), [SkillAdaptor](https://arxiv.org/abs/2606.01311), [SkillForge](https://arxiv.org/abs/2604.08618), [MCE](https://arxiv.org/abs/2601.21557), [Continual Harness](https://arxiv.org/abs/2605.09998), [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) | persistent write target, reload boundary, candidate-level gate, and update-versus-benefit measurement |
| **Candidate proposal and search** | [AdaEvolve](https://arxiv.org/abs/2602.20133), [ShinkaEvolve](https://arxiv.org/abs/2509.19349), [ThetaEvolve](https://arxiv.org/abs/2511.23473), [Promptbreeder](https://arxiv.org/abs/2309.16797), [GEPA](https://arxiv.org/abs/2507.19457), [MIPROv2](https://arxiv.org/abs/2406.11695), [TextGrad](https://arxiv.org/abs/2406.07496), [DGM](https://arxiv.org/abs/2505.22954) | observed evidence, edit geometry, candidate retention, query allocation, and whether a label is interface, structural, or strict |
| **Confirmation and trajectory evaluation** | [SkillOpt](https://arxiv.org/abs/2605.23904), [SkillOpt-Lite](https://arxiv.org/abs/2607.03451), [Self-Harness](https://arxiv.org/abs/2606.09498), [AI Agents That Matter](https://arxiv.org/abs/2407.01502), [HAL](https://arxiv.org/abs/2510.11977), [RE-Bench](https://arxiv.org/abs/2411.15114), [MLE-bench](https://arxiv.org/abs/2410.07095), [PaperBench](https://arxiv.org/abs/2504.01848) | split and reuse, blocking point, cost, long-horizon retention, reproducibility, and evaluator integrity |
| **Risk and governance** | [Misevolution](https://arxiv.org/abs/2509.26354), [Defining and Characterizing Reward Hacking](https://arxiv.org/abs/2209.13085), [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760), [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) | evaluator manipulation, reward hacking, diversity collapse, permission boundaries, rollback, and human authorization |

## §8. Future direction: governable evolution

This section treats long-term evolution as a constrained state-transition problem. An increase in rule count is not evidence of increased capability. [Weng’s summary of harness-engineering challenges](https://lilianweng.github.io/posts/2026-07-04-harness/) identifies weak evaluators, context and memory lifecycle, negative results, diversity collapse, reward hacking, long-term success, and the role of humans. For HarnessOpt, these challenges become requirements on lifecycle, deployment boundaries, evaluators, state management, and authorization. The public discussions of DeepSeek Harness describe “Model + Harness = Agent” and “Everything Is a Plugin”; they are useful engineering cases for a pluginized runtime, but do not by themselves establish performance or self-improvement claims (see [q1](https://www.zhihu.com/question/2071331484284220938) and [q2](https://www.zhihu.com/question/2072255826778140869)).

Long-running systems should preserve four invariants: candidates cannot modify the evaluation boundary; candidates and their side effects are revocable; runtime evidence is replayable and attributable; and durable writes are auditable with explicit data roles for confirmation.

### 8.1 Plugin lifecycle, composability, and reversible state

Everything Is a Plugin requires an auditable lifecycle for each component:

`load → validate → stage → activate → observe → deactivate → cleanup → archive`

`validate` checks contracts, permissions, and dependencies; `stage` constructs a candidate in isolation; `activate` records an atomic state transition; and `deactivate` plus `cleanup` revoke processes, registrations, caches, and temporary files. Rejection should restore the file tree, runtime resources, and persistent memory to the same parent state. File-version rollback alone does not restore behavior.

A registry should record versions, dependencies, capabilities, permissions, state hashes, provenance, and compatibility constraints. It should revalidate downstream components after dependency changes and verify that unloading clears temporal side effects. Candidate writes and confirmation writes remain separate: dynamic plugins may be tried in an isolated sandbox, while durable skills, memory, workflows, and Agent Notes require versioning, checks, and human or independent confirmation. Agent Notes should retain explicit lifecycle states and rejection reasons.

At runtime, skills are replaceable inputs. Only a recorded, versioned, and gated skill should impose persistent cross-task constraints; catalogue visibility and on-demand loading should be logged.

Append-only logs should cover model-visible inputs, tool calls, subagents, context injection, evaluator outcomes, state snapshots, cleanup, and data roles. They support replay and attribution. Memory and skill stores also need compression, expiry, merge, deletion, and recovery rules so that accumulated entries do not silently change routing or behavior.

### 8.2 Endpoint–edge–cloud: allocate work by confirmation cost

Endpoint–edge–cloud is a testable responsibility-allocation hypothesis, not an established deployment fact. The endpoint handles low-latency interaction and candidate generation, the edge handles runtime control and state orchestration, and the cloud handles confirmation that needs independent data or larger budgets:

| Layer | Primary responsibilities | State permissions and data boundary | Metrics to verify |
|---|---|---|---|
| **Endpoint** | Task interaction; candidate generation; contract, compile, smoke, and cheap replay; isolated execution of dynamic plugins; programmatic tool calling (PTC) programs for deterministic multi-step tool calls | Candidates and raw traces may be ephemeral; no direct writes to the evaluator, task sets, model route, or durable registry | Interaction latency, static rejection, smoke-filter benefit, endpoint rollback completeness, privacy leakage |
| **Edge/control plane** | Schedule tasks and subprocesses; maintain plugin registry, versions, dependencies, and replay metadata; enforce policy, staged activation, canaries, and conflict checks; aggregate append-only events | Owns staging state and state hashes; protects evaluator, logs, and permission paths; edge scores alone cannot promote a candidate | Activation/cleanup completeness, dependency conflicts, validation latency, cross-version failure, promotion rate |
| **Cloud/independent evaluator** | Fresh/OOD confirmation; long-horizon regression; safety and evaluation-integrity audits; cross-version statistics, lineage archival, and authorized model feedback | Confirmation data are not exposed to the proposer, selector, or stopping rule; tasks, evaluator, and model route are immutable; output returns a decision and does not activate a candidate directly | Fresh-task gain, old-task retention, confirmation cost, audit coverage, cross-tenant privacy, resource cost |

Putting a task in the cloud does not create statistical independence by itself. The system must record data-access boundaries, confirmation refresh policy, candidate-freezing points, and whether confirmation rollouts flow back into search ranking. The value of endpoint–edge–cloud is separation of duties and cost; it does not change the assumptions behind a PAC-style boundary.

### 8.3 Evaluators, long-term objectives, memory, and failure diversity

Many tasks lack a fast, precise, non-manipulable verifier. Use layered evidence: static contracts and permission checks for executability, task outcomes for behavior, held-out/fresh tasks for generalization, and trace audits or human review for safety and qualities that are difficult to formalize. Keep the evaluator, task data, logs, model route, and reasoning budget outside the editable surface. Risk anchors such as [Misevolution](https://arxiv.org/abs/2509.26354), [Reward Hacking](https://arxiv.org/abs/2209.13085), [Reward Model Overoptimization](https://arxiv.org/abs/2210.10760), and [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) motivate these controls; they do not show that current HarnessOpt systems already satisfy them.

Long-term evaluation should include maintainability, ownership, migration, compatibility, and debugging cost. For open-ended tasks, retain low-scoring branches with novelty or explanatory value under a separate budget, together with behavior descriptors, failure causes, and retry conditions, to preserve diversity beyond the current evaluator.

Retain failed attempts as searchable but inactive records. Each skill or Agent Note should carry scope, evidence source, counterexamples, alternatives, and state history; compression and merging should transfer all live contracts and coverage gaps. At scale, use semantic retrieval, hierarchical catalogues, or task-conditioned subsets, and log routing decisions.

Logs support attribution but do not identify its cause automatically. Component-level attribution is needed before traces can reliably produce local proposals or decide whether a component should be edited, downweighted, expired, or removed.

### 8.4 Model–harness co-design and human authorization

A verifiable co-design loop is: traces expose recurrent failures; the harness proposes a bounded edit; independent confirmation checks gain, non-regression, and safety; stable experience enters a reusable plugin, skill, or separately controlled training process; and ablation tests whether scaffolding can be removed while fresh-task gains remain. Internalization is supported only when behavior persists after scaffolding is reduced.

The model may generate candidates autonomously, while durable write permission remains subject to independent gates and human oversight. Human review should cover high-impact permissions, evaluator changes, lineage merges, semantic correctness, and maintenance commitments. Durable state should record this authorization path.

### 8.5 Open questions

The main unresolved questions are four connected ones:

1. Under weak or fuzzy evaluators, confirmation-set reuse, and task drift, how can multi-round promotion retain auditable independence and confidence?
2. How should context, skill, and memory routing, compression, forgetting, and negative-result retention be managed over long horizons without losing verified behavior?
3. How can the trade-off among stability, plasticity, exploratory diversity, and reward-hacking risk be quantified?
4. How should high-cost confirmation, human review, and model adaptation be allocated across endpoint–edge–cloud, and how can behavior be re-confirmed after merging independently evolved plugin lineages?

## Companion documents

| Document | Purpose |
|---|---|
| [docs/zo-operator-map.md](docs/zo-operator-map.md) | Classical operator requirements and conservative HarnessOpt labels |
| [docs/pac-stability.md](docs/pac-stability.md) | Fixed-candidate bounds, multi-round reuse, stability, and non-conclusions |
| [docs/audit-table.md](docs/audit-table.md) | Per-system confirmation, evaluator-protection, and rollback fields |
| [docs/literature-map.md](docs/literature-map.md) | Mainline literature gaps and the source fields to audit next |
| [docs/glossary.md](docs/glossary.md) | Symbols and protocol terminology |

## Contributing

When adding a paper, keep three kinds of statements separate:

- **Reported fact:** the mechanism, setting, or result stated by the primary source.
- **Catalogue interpretation:** the L0–L5 level, proposal labels, and confirmation-protocol labels used here.
- **Recommendation:** a field that an experiment should report.

Use the entry form:

~~~text
- **Name** — "Title". Authors. *Venue* Year. [[paper]](link) — one line about the harness update. `[Proposal: evidence + structure]` `[Confirmation: protocol; data: relationship; reuse: scope]`
~~~

For held-out or fresh test, state the split, reuse count, and whether its result could block persistence. If the primary source does not establish a field, write `unverified`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Citation

~~~bibtex
@misc{harnessopt_zo_pac_2026,
  title        = {A Zeroth-Order and PAC View of Agent Harness Optimization},
  author       = {Wei, Chuyang and Shen, Yifei},
  year         = {2026},
  howpublished = {\url{https://github.com/Weichy9218/Awesome-Harness-Optimization}}
}
~~~

## License

[MIT](LICENSE). Paper metadata belongs to the respective authors.
