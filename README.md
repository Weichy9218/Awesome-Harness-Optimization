<!-- Core reading list for model-external harness optimization, organized by editable surface, proposal information, and confirmation protocol. -->

# Awesome Harness Optimization

**A reading list for Harness Optimization (HarnessOpt): how run-time evidence changes the software around a frozen language model, and how a candidate becomes persistent state.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** | [中文](README_zh.md)

> **Central claim.** HarnessOpt is not defined by how many objects a system can edit. Its defining structure is an auditable update loop that separates the editable surface, proposal evidence, and state confirmation. In the works checked here, proposal mechanisms are common; candidate-level independent confirmation is still uncommon.

## Contents

- [Scope](#scope)
- [The update architecture](#the-update-architecture)
- [How to read the catalogue](#how-to-read-the-catalogue)
- [1. Why HarnessOpt needs a separate view](#1-why-harnessopt-needs-a-separate-view)
- [2. Editable surface: L0–L5](#2-editable-surface-l0l5)
- [3. Candidate generation: a ZO interface](#3-candidate-generation-a-zo-interface)
- [4. Candidate confirmation: a PAC-style boundary](#4-candidate-confirmation-a-pac-style-boundary)
- [5. Evaluation: report the trajectory](#5-evaluation-report-the-trajectory)
- [6. Future direction: governable evolution](#6-future-direction-governable-evolution)
- [Companion documents](#companion-documents)
- [Contributing](#contributing)
- [Citation](#citation)

## Scope

Fix a base model \(M\), a task distribution \(\mathcal D\), and an external evaluation boundary. Let \(s\) be model-external software state: prompts, context, memory, workflows, tools, agent code, or optimizer code. A harness executes task \(z\) as \(\tau=H_s(M,z)\).

This list includes work that meets all three conditions:

1. the base model is fixed for the update under discussion;
2. run-time evidence influences a change to an explicitly delimited state set \(\mathcal S_{\mathrm{edit}}\); and
3. the change affects later runs, either through a gate or through an unconditional write.

The list includes prompt optimization, self-evolving memory and skills, workflow search, self-modifying harness code, and optimizer/meta-harness code. L5 methods that update harness and weights together are boundary cases. Weight-only training and hand-authored harness design are listed only when they clarify the boundary.

## The update architecture

One update has four distinct objects: the editable set \(\mathcal S_{\mathrm{edit}}\), evidence collection \(Q\), proposer \(P_\phi\), and transition gate \(G\).

~~~math
\mathcal E_t=Q(s_t;D_t),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
~~~

Here \(Q\) collects traces, returns, errors, and feedback on proposal tasks \(D_t\); \(P_\phi\) creates a candidate inside \(\mathcal S_{\mathrm{edit}}\); and \(G\) accepts, rejects, or rolls back the candidate using confirmation data \(V_t\). The candidate \(\widetilde s_{t+1}\) is not the persistent state \(s_{t+1}\) until the transition rule says so.

~~~mermaid
flowchart LR
    S["s_t · editable state<br/>prompt · memory · workflow · code"] --> Q["Q · run D_t<br/>traces · returns · errors"]
    Q --> P["Pφ · form candidate<br/>ZO interface"]
    P --> G["G · confirm on V_t<br/>PAC-style boundary"]
    G -->|accept| S
    G -->|reject / rollback| S
    G -.-> B["protected boundary<br/>model · evaluator · tasks · permissions"]
~~~

The system architecture determines what can be made editable and what can be restored. The latest architecture direction in this project, summarized as **Everything Is a Plugin (EIP)**, treats tools, prompts, skills, providers, memory, verifiers, search strategies, stop conditions, UI components, and temporary resources as independently replaceable runtime components. If implemented, this expands the editable surface from files and modules to component loading, dependency resolution, live activation, and cleanup.

Unlike a restart-based plugin system, the intended runtime can activate a confirmed component in the current session and expose it to the next step. That shortens the edit–run loop, but it also makes isolation, atomic activation, and cleanup part of the confirmation problem.

For HarnessOpt, a plugin is not persistent merely because it runs. A candidate needs a contract check, isolated execution, protected evaluator and permission paths, confirmation, and two-stage atomic activation. The lifecycle must cover processes, ports, provider and tool registrations, temporary state, and memory, and must record generation through cleanup. These are architecture requirements and audit targets, not claims that current systems already satisfy them.

## How to read the catalogue

The catalogue uses three complementary axes.

| Axis | Question | Main labels |
|---|---|---|
| **Editable surface** | What object can change? | L0 prompt → L5 joint harness and weights |
| **Proposal information** | What does the proposer observe, and how is the edit structured? | ZO analogy: … |
| **Confirmation protocol** | What can prevent persistence, and how is the data related to proposal data? | Gate: … |

ZO analogy describes an information or search role. It is not a claim that an LLM editor computes a numerical gradient. held-out means a separate set can be used in selection; it is not fresh after adaptive reuse. Human review, sandboxing, and rollback are governance controls, not statistical independence.

## 1. Why HarnessOpt needs a separate view

The older self-improvement literature asks whether a system can design a better successor. HarnessOpt studies the deployable software state around a fixed model. The important distinction is the strength of the conclusion:

| Evidence level | What it can support | Typical example |
|---|---|---|
| **Formal proof** | an internal proof that the rewrite improves utility | Gödel Machine; no current HarnessOpt system establishes this generally |
| **Probabilistic confirmation** | a fixed candidate is supported on untouched data under stated assumptions | PAC-style holdout reasoning; an open target for adaptive harness evolution |
| **Empirical improvement** | a candidate scores higher on observed tasks | the dominant practice in current systems |

The gap between the second and third rows is the reason to record proposal and confirmation separately.

**Background.** [Good, *Speculations Concerning the First Ultraintelligent Machine* (1966)](https://doi.org/10.1016/S0065-2458%2808%2960418-0) introduces the self-design idea; [Schmidhuber, *Gödel Machines* (2003)](https://arxiv.org/abs/cs/0309048) makes proof-gated self-rewriting explicit; [Yudkowsky, *Recursive Self-Improvement* (2008)](https://www.lesswrong.com/posts/JBadX7rwdcRFzGuju/recursive-self-improvement) names the loop; and [Weng, *Harness Engineering for Self-Improvement* (2026)](https://lilianweng.github.io/posts/2026-07-04-harness/) places the near-term loop in the scaffolding around the model.

## 2. Editable surface: L0–L5

The level is an object range, not a capability score. Write authority, persistence, and enforcement must be recorded separately.

| Cross-cutting property | Question | Why it matters |
|---|---|---|
| **Write authority** | Does the agent write autonomously, or only after review? | Determines whether the update loop is closed. |
| **Persistence** | Is the change ephemeral, or committed to versioned state? | Determines whether errors can accumulate. |
| **Constraint enforcement** | Is the boundary stated in a prompt, or enforced by permissions, sandboxing, or static checks? | Determines whether the evaluator and protected paths remain outside the edit. |

| Level | Editable object | Typical edit unit | Representative work |
|---|---|---|---|
| **L0** | instruction prompt | prompt, instruction block, exemplar | [APE](https://arxiv.org/abs/2211.01910), [OPRO](https://arxiv.org/abs/2309.03409), [ProTeGi](https://arxiv.org/abs/2305.03495), [GEPA](https://arxiv.org/abs/2507.19457) |
| **L1** | context, memory, skill | entry, file, retrieval unit, executable skill | [Reflexion](https://arxiv.org/abs/2303.11366), [ExpeL](https://arxiv.org/abs/2308.10144), [ACE](https://arxiv.org/abs/2510.04618), [Voyager](https://arxiv.org/abs/2305.16291), [SkillOpt](https://arxiv.org/abs/2605.23904), [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) |
| **L2** | workflow, graph, architecture | node, edge, subgraph, module slot | [GPTSwarm](https://arxiv.org/abs/2402.16823), [ADAS](https://arxiv.org/abs/2408.08435), [AFlow](https://arxiv.org/abs/2410.10762), [AgentSquare](https://arxiv.org/abs/2410.06153), [MaAS](https://arxiv.org/abs/2502.04180) |
| **L3** | harness or agent code | file, module, tool, plugin | [STOP](https://arxiv.org/abs/2310.02304), [DGM](https://arxiv.org/abs/2505.22954), [SICA](https://arxiv.org/abs/2504.15228), [Self-Harness](https://arxiv.org/abs/2606.09498), [AHE](https://arxiv.org/abs/2604.25850) |
| **L4** | optimizer or meta-harness code | proposer, selector, search operator | [Meta-Harness](https://arxiv.org/abs/2603.28052), [MCE](https://arxiv.org/abs/2601.21557) |
| **L5** | harness and model adaptation | checkpoint, LoRA, prefix plus harness state | [SIA](https://arxiv.org/abs/2605.27276), [SEAL](https://arxiv.org/abs/2506.10943) |

The same work may appear on more than one axis. The level says what is edited; the next sections say how proposals are formed and what evidence can justify persistence.

### Representative entries

- **Prompt optimization (L0).** [MIPROv2](https://arxiv.org/abs/2406.11695) jointly proposes instructions and demonstrations with Bayesian optimization. [TextGrad](https://arxiv.org/abs/2406.07496) propagates textual critiques through a compound system. Both expose why “textual gradient” is useful as a proposal description but not as a numerical derivative. ZO analogy: surrogate-model search / trace-informed proposal. Gate: search-set.
- **Memory and skill evolution (L1).** [ReasoningBank](https://arxiv.org/abs/2509.25140) distills reusable strategies from successes and failures. [Trace2Skill](https://arxiv.org/abs/2603.25158) merges trajectory-local lessons into patches. Their aggregation can broaden evidence, but it does not by itself create independent confirmation. ZO analogy: batch evidence + localized edit. Gate: open or search-set, depending on the path.
- **Structured skill confirmation (L1).** [SkillOpt](https://arxiv.org/abs/2605.23904) and [SkillOpt-Lite](https://arxiv.org/abs/2607.03451) use bounded edits and a separate validation stage. They are useful reference points for connecting proposal structure to a candidate-level gate. ZO analogy: batch evidence + bounded edit. Gate: held-out.
- **Workflow and code search (L2–L4).** [AFlow](https://arxiv.org/abs/2410.10762), [AgentSquare](https://arxiv.org/abs/2410.06153), [DGM](https://arxiv.org/abs/2505.22954), and [Meta-Harness](https://arxiv.org/abs/2603.28052) make the search space more structured. Structure supports static checks, component boundaries, and replay; it also increases coupling and rollback cost. ZO analogy: population / archive or localized edit. Gate: search-set.
- **Boundary cases.** [GPTSwarm](https://arxiv.org/abs/2402.16823) and [ScoreFlow](https://arxiv.org/abs/2502.04306) use differentiable or RL-style components for part of the problem. They are included to mark where the ZO interface no longer describes the full method.

## 3. Candidate generation: a ZO interface

### 3.1 Objective interface

Fix a base model \(M\), a task distribution \(\mathcal D\), and a bounded return \(R\). For an editable state \(s\), one execution with run randomness or environment seed \(\xi\) returns

~~~math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
~~~

For text, programs, and file trees, \(\nabla_s f_M(s)\) is not defined unless the representation is embedded in an explicit continuous parameterization. HarnessOpt therefore treats execution as an objective interface: information about \(f_M\) is obtained by deploying a state and observing its result.

The proposer may receive a richer observation than a scalar return:

~~~math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
~~~

where \(\Psi\) contains traces, errors, tool calls, and verifier feedback. \(\Psi\) changes the information available to \(P_\phi\), but it is not a numerical derivative, an unbiased gradient estimator, or confirmation evidence. A trace also does not identify the causal contribution of an edit unless the state comparison and execution conditions are controlled.

Three distinctions are required:

- semantic feedback is proposal-side information, not a gradient estimator;
- compile, type, schema, and interface checks establish feasibility, not task-level performance;
- a paired parent/child score is an empirical state difference, not a central finite difference unless the required perturbation structure is explicitly constructed.

### 3.2 Three search axes

The three axes classify different parts of the proposal process. Evidence construction describes which executions are queried and how their observations are aggregated. Search geometry describes the representation-level region in which an edit may be formed. Query allocation describes how history, surrogates, or retained candidates determine the next evaluations. They are separable analytically but may be coupled in an implementation.

| Design axis | Mechanism family | Harness-native form | Correspondence to derivative-free optimization | Representative work |
|---|---|---|---|---|
| **Evidence construction** | single-state semantic proposal | Read traces, errors, and feedback from the current state and form an edit without first scoring that edited state. | Shares the objective-query interface; no numerical estimator is implied. | Reflexion, Voyager, ProTeGi, TextGrad |
|  | batch evidence aggregation | Aggregate failure patterns across tasks or seeds while holding the edited state fixed. | Repeated noisy queries or sample averaging; tasks are not perturbation directions. | SkillOpt, SkillOpt-Lite, Trace2Skill, ExpeL, SkillForge |
|  | paired state comparison | Execute the parent and edited states on the same task batch and compare task-level returns. | Two-point comparison; it is not a central difference without constructible positive and negative perturbations. | SkillCAT, selective Trace2Skill paths |
| **Search geometry** | block-local edit | Restrict one proposal to a component, file, entry, module, or graph node declared before outcome observation. | Structurally corresponds to block-coordinate search; block separability is not assumed. | SkillAdaptor, AgentSquare, DemoEvolve, AlphaEvolve |
|  | bounded local search | Limit tokens, files, diff size, operations, or an allowlist before task evaluation. | Resembles local direct search; without a behavioral distance and radius update it is not a trust region. | SkillOpt, SkillOpt-Lite, SkillForge, Self-Harness |
| **Query allocation** | history or surrogate allocation | Use score history, a response model, or a bandit rule to choose the next candidates and rollout budget. | Strict correspondence requires an explicit acquisition or allocation rule; otherwise the relation is heuristic. | ProTeGi, MIPROv2, AgentSquare, AdaEvolve |
|  | population or archive search | Retain candidate scores, differences, or Pareto relations and use them to select later candidates or lineages. | Structurally resembles evolutionary search; retention does not provide independent confirmation. | GEPA, Promptbreeder, DGM, AlphaEvolve, Meta-Harness |

The table uses three levels of correspondence. An interface correspondence only states that objective information is obtained through execution. A structural correspondence additionally requires a representation-level edit unit or retention rule. A strict correspondence requires the numerical parameterization, update rule, and sampling assumptions of the classical operator. The label alone does not imply a convergence rate, a variance reduction, a behavioral radius, or an independent confirmation set.

### 3.3 Structure and cost

The editable surface supplies the structure available to a search operator. Let \(\mathcal S_{\mathrm{feas}}\subseteq\mathcal S_{\mathrm{edit}}\) denote states satisfying compile, type, interface, and write-path contracts. A static checker can test membership in this constructive subset, but it does not estimate \(f_M\) or establish semantic correctness.

Component boundaries, allowlists, feature toggles, version snapshots, and deterministic replay can make local edits and paired comparisons executable. They do not imply that code is superior to text. Code supplies stronger structural constraints but also introduces coupling, side effects, and a larger rollback surface. A syntactic edit budget limits description space; it does not, without an additional behavioral metric, limit the change in execution behavior.

Local search is meaningful only when the editable components and the initial state are specified before evaluation. A Round-0 scaffold is therefore part of the state definition, not evidence that the update improved performance.

Harness queries have unequal cost. A useful accounting is

~~~math
C=n_{\mathrm{prop}}c_{\mathrm{prop}}+n_{\mathrm{static}}c_{\mathrm{static}}+n_{\mathrm{smoke}}c_{\mathrm{smoke}}+n_{\mathrm{task}}c_{\mathrm{task}}.
~~~

Static checks and smoke tests filter candidates before expensive task rollouts; they do not replace task-level confirmation. Search evidence and confirmation evidence must be counted separately. Paired evaluation is justified only when task, seed, and environment alignment produces sufficient covariance reduction to offset the additional execution cost; the paired label alone does not establish that reduction.

The resulting design implications are regime-dependent. When task rollouts are expensive, the budget should be allocated explicitly among proposer depth, pre-evaluation filters, and candidate count. When execution noise is high and parent and child states can be aligned, paired evaluation may improve comparison efficiency. When behavioral change can be measured more directly than token or diff size, bounded search becomes a more informative control. These are testable hypotheses, not established properties of the listed systems.

See [docs/zo-operator-map.md](docs/zo-operator-map.md) for the operator requirements and conservative labels.

## 4. Candidate confirmation: a PAC-style boundary

### 4.1 Two different statistical questions

Let \(\mathcal A\) map a proposal sample \(D_n\) to a persistent state. For a fresh evaluation task \(x\), let \(D_n^{(i\leftarrow x_i')}\) replace one proposal example with an independent draw. Proposal stability is represented by the expected replace-one sensitivity

~~~math
\beta_{\mathrm{avg}}
=
\mathbb E\!\left[
\left|
\ell(\mathcal A(D_n);x)
-
\ell(\mathcal A(D_n^{(i\leftarrow x_i')});x)
\right|
\right].
~~~

**B1, proposal stability**, asks whether this quantity is small. Batch evidence, cross-task aggregation, and bounded edits are mechanisms that may reduce sensitivity to one proposal example. The checked systems do not systematically measure \(\beta_{\mathrm{avg}}\); it is therefore a design hypothesis, not an empirical guarantee. Expected on-average stability alone also does not provide a high-probability bound.

**B2, fixed-candidate confirmation**, asks whether a candidate fixed without using a confirmation sample \(V_m\) performs well on fresh tasks. If \(V_m\sim\mathcal D^m\), the loss is bounded in \([0,1]\), and \(V_m\) does not influence candidate generation, selection, or stopping, Hoeffding's inequality gives

~~~math
\epsilon(\widetilde s)
\le
\widehat\epsilon_{V_m}(\widetilde s)
+\sqrt{\frac{\ln(1/\delta)}{2m}}
~~~

with probability at least \(1-\delta\). If a task is run with multiple seeds, the seeds are repeated observations conditional on that task; \(m\) counts independent tasks after the stated task-level aggregation. Reusing the same set adaptively does not restore independence by renaming it validation or held-out.

B1 and B2 are not substitutes. A stable proposer can overfit a reused validation set; a genuinely fresh confirmation set can evaluate a fixed candidate without proving that the proposer is stable.

Confirmation evaluations must not feed back into proposal generation, candidate ranking, or stopping decisions. Otherwise the confirmation sample becomes part of the search set. Task-level rollouts used for search and confirmation should therefore be counted separately, including rejected candidates.

### 4.2 Three state-transition protocols

The protocol is determined by where the state transition occurs and by the data that can affect it. A final-test result does not, by itself, identify a promotion gate.

| Protocol | State-transition semantics | Confirmation evidence | What the evidence supports | Representative work |
|---|---|---|---|---|
| **Write-through** | The candidate is written into memory, skill, workflow, or code without a candidate-level blocking rule. | No separate confirmation evidence. | Later tasks provide retrospective empirical evidence only. | Reflexion, Voyager, ExpeL, ACE, ReasoningBank, Trace2Skill default path |
| **Search-time selection** | Candidates or archive members are ranked on proposal/search data, and the selected object becomes the next state. | Evidence is sourced from the same search process. | Relative ordering on the observed set; a locked final test can evaluate the completed procedure, but not certify the promotion step. | APE, OPRO, GEPA, AFlow, DGM, Meta-Harness, SkillCAT |
| **Separated confirmation** | A candidate is fixed before a separate confirmation evaluation decides whether it replaces the current state. | Confirmation data are excluded from proposal and selection, subject to reuse and boundary checks. | Fixed-candidate holdout reasoning under the stated assumptions. | SkillOpt, SkillOpt-Lite, Self-Harness |

In the checked set, the descriptive counts are **11 / 19 / 3** for write-through, search-time selection, and separated confirmation. The count is limited to the systems audited in [docs/audit-table.md](docs/audit-table.md); it is not a census of the field.

Separation is a protocol property; independence also has a time scope. SkillOpt-Lite changes task allocation to enlarge the confirmation set, while Self-Harness reuses a fixed held-in/held-out split across evolution rounds. The latter supports single-round separation but not automatically fresh confirmation across rounds. A rejected candidate also consumes information about the confirmation set, even when it is not promoted.

An untouched final test used only for reporting is not a promotion gate. Human review, sandboxing, audit logs, and rollback are orthogonal controls. They govern write authority, runtime protection, and recovery; they do not establish statistical independence. A gate must be active in the implementation. A hook that is never executed is equivalent to no gate.

### 4.3 Three conditions outside B2

Write \(\epsilon(s)=\sum_{k=1}^{K}p_k\epsilon_k(s)\) for a distribution partitioned into task clusters. A degradation \(\Delta\epsilon_k\) in a cluster of mass \(p_k\) changes the aggregate risk by only \(p_k\Delta\epsilon_k\). It can remain below a confirmation slack \(\eta\) even when the cluster-level loss is materially worse. Cluster-level non-regression therefore requires stratified sampling and reporting.

1. **Criterion coverage.** The loss must include the target capability, important task clusters, safety, and policy dimensions. An aggregate score can improve while a low-mass capability deteriorates.
2. **Evaluation boundary.** Tasks, evaluators, model routing, logging, permissions, and protected paths must remain outside the editable surface or be enforced at run time.
3. **Behavioral rejection.** Rejection must restore processes, registrations, caches, external resources, and persistent memory, not only the file tree.

See [docs/pac-stability.md](docs/pac-stability.md) for the reachable-class, reuse, paired-comparison, and stability details, and [docs/audit-table.md](docs/audit-table.md) for per-system fields.

## 5. Evaluation: report the trajectory

The correct unit of evaluation is an **evolution trajectory**, not only the final version score. A trajectory report should make five groups of fields visible:

| Field group | Minimum content |
|---|---|
| **Fixed boundary** | model, evaluator, tools, environment, permissions, editable surface |
| **Data roles** | proposal, selection, confirmation, regression, and final-test sets; sample counts; reuse; proposer visibility |
| **State history** | \(s_0\), every accepted \(s_t\), rejected candidates, final \(s_T\), and old-task/OOD/fresh-task curves |
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

Benchmarks such as [SWE-bench](https://arxiv.org/abs/2310.06770), [Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak), [PaperBench](https://arxiv.org/abs/2504.01848), and long-horizon memory benchmarks can supply tasks. None supplies the full protocol automatically. Episodic benchmarks do not measure persistent state; a visible smoke test may be only a proxy; and scores across different base models, harnesses, optimizers, and evaluators are not directly additive.

## 6. Future direction: governable evolution

This section treats long-term evolution as a constrained state-transition problem. An increase in rule count is not evidence of increased capability. [Weng’s summary of harness-engineering challenges](https://lilianweng.github.io/posts/2026-07-04-harness/) identifies weak evaluators, context and memory lifecycle, negative results, diversity collapse, reward hacking, long-term success, and the role of humans. For HarnessOpt, these challenges become requirements on lifecycle, deployment boundaries, evaluators, state management, and authorization. The public discussions of DeepSeek Harness describe “Model + Harness = Agent” and “Everything Is a Plugin”; they are useful engineering cases for a pluginized runtime, but do not by themselves establish performance or self-improvement claims (see [q1](https://www.zhihu.com/question/2071331484284220938) and [q2](https://www.zhihu.com/question/2072255826778140869)).

Long-running systems should preserve four invariants: candidates cannot modify the evaluation boundary; candidates and their side effects are revocable; runtime evidence is replayable and attributable; and durable writes are auditable with explicit data roles for confirmation.

### 6.1 Plugin lifecycle, composability, and reversible state

Everything Is a Plugin requires more than additional extension points. Each component needs an auditable state machine:

`load → validate → stage → activate → observe → deactivate → cleanup → archive`

`validate` checks contracts, permissions, and dependencies; `stage` constructs a candidate in isolation; `activate` is a recorded atomic state transition; and `deactivate` plus `cleanup` must revoke side effects such as processes, ports, event listeners, provider/tool registrations, caches, and temporary files. After rejection, the file tree, runtime resources, and persistent memory should return to the same parent state. Reverting versioned files alone is not behavioral rollback.

A plugin registry should record versions, dependencies, capability declarations, permissions, state hashes, provenance, and compatibility constraints. It must address both forms of composability: whether unloading clears all temporal side effects, and whether a dependency change triggers revalidation of downstream components. Candidate writes and confirmation writes must be separate. A model-written dynamic plugin may run and be revoked inside an isolated sandbox; durable skills, memory, workflows, and Agent Notes should enter durable state only through version control, format checks, and human or independent confirmation. Agent Notes should use explicit `proposed`, `implemented`, `rejected`, and `archived` states, retaining rejection reasons, alternatives, and coverage gaps.

At runtime, a skill should be treated as replaceable, non-authoritative input. Only a recorded, versioned, and gated skill should impose persistent cross-task behavioral constraints; the model-visible catalogue and on-demand loading path should also be included in the event log.

Event logs should be append-only and cover model-visible inputs, tool calls, subagents, context injection, evaluator outcomes, state snapshots, and cleanup actions. They provide the substrate for replay and attribution and record the separation between search and confirmation data. Memory and skill stores also need compression, expiry, merge, deletion, and recovery rules. Append-only accumulation without retirement eventually creates conflicts and changes routing and behavior distributions.

### 6.2 Endpoint–edge–cloud: allocate work by confirmation cost

Endpoint–edge–cloud is a testable responsibility-allocation hypothesis, not an established deployment fact. The endpoint handles low-latency interaction and candidate generation, the edge handles runtime control and state orchestration, and the cloud handles confirmation that needs independent data or larger budgets:

| Layer | Primary responsibilities | State permissions and data boundary | Metrics to verify |
|---|---|---|---|
| **Endpoint** | Task interaction; candidate generation; contract, compile, smoke, and cheap replay; isolated execution of dynamic plugins; programmatic tool calling (PTC) programs for deterministic multi-step tool calls | Candidates and raw traces may be ephemeral; no direct writes to the evaluator, task sets, model route, or durable registry | Interaction latency, static rejection, smoke-filter benefit, endpoint rollback completeness, privacy leakage |
| **Edge/control plane** | Schedule tasks and subprocesses; maintain plugin registry, versions, dependencies, and replay metadata; enforce policy, staged activation, canaries, and conflict checks; aggregate append-only events | Owns staging state and state hashes; protects evaluator, logs, and permission paths; edge scores alone cannot promote a candidate | Activation/cleanup completeness, dependency conflicts, validation latency, cross-version failure, promotion rate |
| **Cloud/independent evaluator** | Fresh/OOD confirmation; long-horizon regression; safety and evaluation-integrity audits; cross-version statistics, lineage archival, and authorized model feedback | Confirmation data are not exposed to the proposer, selector, or stopping rule; tasks, evaluator, and model route are immutable; output returns a decision and does not activate a candidate directly | Fresh-task gain, old-task retention, confirmation cost, audit coverage, cross-tenant privacy, resource cost |

Putting a task in the cloud does not create statistical independence by itself. The system must record data-access boundaries, confirmation refresh policy, candidate-freezing points, and whether confirmation rollouts flow back into search ranking. The value of endpoint–edge–cloud is separation of duties and cost; it does not change the assumptions behind a PAC-style boundary.

### 6.3 Evaluators, long-term objectives, and failure diversity

Many real tasks lack a fast, precise, and non-manipulable verifier. A single pass rate, unit test, or judge score covers only part of the objective and can invite reward hacking. The evaluation boundary should remain outside the editable surface and use layered evidence: static contracts and permission checks for executability, task outcomes for behavior, held-out/fresh tasks for generalization, and trace audits plus human review for safety, research judgment, and qualities that are difficult to formalize. The evolution loop should not be able to modify the evaluator, task data, logs, model route, or reasoning budget.

Long-term success should include repository maintainability, ownership boundaries, migration cost, backward compatibility, and future debugging burden. A higher short-term completion rate does not replace these dimensions. For research and open-ended tasks, low-scoring branches with novelty or explanatory value should remain available under a separate budget, together with behavior descriptors, failure causes, and retry conditions; otherwise a population or archive collapses toward homogeneous solutions favored by the current evaluator.

### 6.4 Memory routing, negative results, and attribution

Failed attempts should not be silently overwritten. Each skill or Agent Note should carry its scope, evidence source, known counterexamples, alternatives, and state history; rejected candidates remain searchable but inactive. Compression and merging are valid only after all still-live contracts, reasons, and coverage gaps have been transferred to a new owner. At scale, a skill description is a routing key. Injecting the full catalogue into context will eventually fail, so semantic retrieval, hierarchical catalogues, or task-conditioned subsets are needed, with routing decisions logged.

Append-only logs provide raw material for attribution but do not determine whether a failure came from incorrect skill content, model non-compliance, environment drift, or a task that should not have used the skill. Without component-level attribution, traces cannot reliably produce local proposals or determine whether a component should be edited, downweighted, expired, or removed.

### 6.5 Model–harness co-design and human authorization

A verifiable co-design loop has five steps: traces expose recurrent failures; the harness proposes a bounded edit within the declared editable surface; independent confirmation checks gain, non-regression, and safety; stable experience enters a reusable plugin or skill, or a separately controlled model-training process; and an ablation tests whether compensatory scaffolding can be removed while fresh-task gains remain. Only reduced scaffolding with retained cross-task behavior suggests that some experience may have been internalized. More rules or a higher endpoint score alone do not support that conclusion.

The model may generate candidates autonomously, but durable write permission should be determined by independent gates and human oversight. Humans should review high-impact permissions, evaluator changes, lineage merges, semantic correctness, and long-term maintenance commitments at the appropriate abstraction level. The desired outcome is a traceable, human-gated durable state transition, not direct persistence of unverified experience.

### 6.6 Open questions

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
| [docs/glossary.md](docs/glossary.md) | Symbols and protocol terminology |

## Contributing

When adding a paper, keep three kinds of statements separate:

- **Reported fact:** the mechanism, setting, or result stated by the primary source.
- **Catalogue interpretation:** the L0–L5 level, ZO analogy, and Gate labels used here.
- **Recommendation:** a field that an experiment should report.

Use the entry form:

~~~text
- **Name** — "Title". Authors. *Venue* Year. [[paper]](link) — one line about the harness update. [ZO analogy: role] [Gate: protocol]
~~~

For held-out or fresh test, state the split, reuse count, and whether its result could block persistence. If the primary source does not establish a field, write unverified. See [CONTRIBUTING.md](CONTRIBUTING.md).

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
