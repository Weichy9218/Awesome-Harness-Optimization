<!-- Moved out of README.md: governance and future-direction material. The reading
     list links here rather than restating it. -->

# Open Problems: Governable Harness Self-Evolution

This section treats long-term evolution as a constrained state-transition problem. An increase in rule count is not evidence of increased capability. [Weng’s summary of harness-engineering challenges](https://lilianweng.github.io/posts/2026-07-04-harness/) identifies weak evaluators, context and memory lifecycle, negative results, diversity collapse, reward hacking, long-term success, and the role of humans. For harness self-evolution, these challenges become requirements on lifecycle, deployment boundaries, evaluators, state management, and authorization. The public discussions of DeepSeek Harness describe “Model + Harness = Agent” and “Everything Is a Plugin”; they are useful engineering cases for a pluginized runtime, but do not by themselves establish performance or self-improvement claims (see [q1](https://www.zhihu.com/question/2071331484284220938) and [q2](https://www.zhihu.com/question/2072255826778140869)).

Long-running systems should preserve four invariants: candidates cannot modify the evaluation boundary; candidates and their side effects are revocable; runtime evidence is replayable and attributable; and durable writes are auditable with explicit data roles for confirmation.

### 8.1 Plugin lifecycle, composability, and reversible state

Everything Is a Plugin requires an auditable lifecycle for each component:

`load → validate → stage → activate → observe → deactivate → cleanup → archive`

`validate` checks contracts, permissions, and dependencies; `stage` constructs a candidate in isolation; `activate` records an atomic state transition; and `deactivate` plus `cleanup` revoke processes, registrations, caches, and temporary files. Rejection should restore the file tree, runtime resources, and persistent memory to the same parent state. File-version rollback alone does not restore behavior.

A registry should record versions, dependencies, capabilities, permissions, state hashes, provenance, and compatibility constraints. It should revalidate downstream components after dependency changes and verify that unloading clears temporal side effects. Candidate writes and confirmation writes remain separate: dynamic plugins may be tried in an isolated sandbox, while durable skills, memory, workflows, and Agent Notes require versioning, checks, and human or independent confirmation. Agent Notes should retain explicit lifecycle states and rejection reasons.

At runtime, skills are replaceable inputs. Only a recorded, versioned, and gated skill should impose persistent cross-task constraints; catalogue visibility and on-demand loading should be logged.

Append-only logs should cover model-visible inputs, tool calls, subagents, context injection, evaluator outcomes, state snapshots, cleanup, and data roles; they are the basis for replay and attribution. Memory and skill stores also need compression, expiry, merge, deletion, and recovery rules so that accumulated entries do not silently change routing or behavior.

### 8.2 Endpoint–edge–cloud: allocate work by confirmation cost

Endpoint–edge–cloud is a testable responsibility-allocation hypothesis, not an established deployment fact. The endpoint handles low-latency interaction and candidate generation, the edge handles runtime control and state orchestration, and the cloud handles confirmation that needs independent data or larger budgets:

| Layer | Primary responsibilities | State permissions and data boundary | Metrics to verify |
|---|---|---|---|
| **Endpoint** | Task interaction; candidate generation; contract, compile, smoke, and cheap replay; isolated execution of dynamic plugins; programmatic tool calling (PTC) programs for deterministic multi-step tool calls | Candidates and raw traces may be ephemeral; no direct writes to the evaluator, task sets, model route, or durable registry | Interaction latency, static rejection, smoke-filter benefit, endpoint rollback completeness, privacy leakage |
| **Edge/control plane** | Schedule tasks and subprocesses; maintain plugin registry, versions, dependencies, and replay metadata; enforce policy, staged activation, canaries, and conflict checks; aggregate append-only events | Owns staging state and state hashes; protects evaluator, logs, and permission paths; edge scores alone cannot promote a candidate | Activation/cleanup completeness, dependency conflicts, validation latency, cross-version failure, promotion rate |
| **Cloud/independent evaluator** | Fresh/OOD confirmation; long-horizon regression; safety and evaluation-integrity audits; cross-version statistics, lineage archival, and authorized model feedback | Confirmation data are not exposed to the proposer, selector, or stopping rule; tasks, evaluator, and model route are immutable; output returns a decision and does not activate a candidate directly | Fresh-task gain, old-task retention, confirmation cost, audit coverage, cross-tenant privacy, resource cost |

Putting a task in the cloud does not create statistical independence by itself. The system must record data-access boundaries, confirmation refresh policy, candidate-freezing points, and whether confirmation rollouts flow back into search ranking. The value of endpoint–edge–cloud is separation of duties and cost; it does not change the assumptions behind a PAC-style boundary.

### 8.3 Evaluators, long-term objectives, memory, and failure diversity

Many tasks lack a fast, precise, non-manipulable verifier. Use layered evidence: static contracts and permission checks for executability, task outcomes for behavior, held-out/fresh tasks for generalization, and trace audits or human review for safety and qualities that are difficult to formalize. Keep the evaluator, task data, logs, model route, and reasoning budget outside the editable surface. Risk anchors such as [Misevolution](https://arxiv.org/abs/2509.26354), [Reward Hacking](https://arxiv.org/abs/2209.13085), [Reward Model Overoptimization](https://arxiv.org/abs/2210.10760), and [Sycophancy to Subterfuge](https://arxiv.org/abs/2406.10162) motivate these controls; they do not show that current harness self-evolution systems already satisfy them.

Long-term evaluation should include maintainability, ownership, migration, compatibility, and debugging cost. For open-ended tasks, retain low-scoring branches with novelty or explanatory value under a separate budget, together with behavior descriptors, failure causes, and retry conditions, to preserve diversity beyond the current evaluator.

Retain failed attempts as searchable but inactive records. Each skill or Agent Note should carry scope, evidence source, counterexamples, alternatives, and state history; compression and merging should transfer all live contracts and coverage gaps. At scale, use semantic retrieval, hierarchical catalogues, or task-conditioned subsets, and log routing decisions.

Logs supply the material for attribution, but they do not decide on their own whether a failure came from the skill content, non-compliance by the model, environment drift, or wrong skill routing. Component-level attribution is needed before traces can reliably produce local proposals or decide whether a component should be edited, downweighted, expired, or removed.

### 8.4 Model–harness co-design and human authorization

A verifiable co-design loop is: traces expose recurrent failures; the harness proposes a bounded edit; independent confirmation checks gain, non-regression, and safety; stable experience enters a reusable plugin, skill, or separately controlled training process; and ablation tests whether scaffolding can be removed while fresh-task gains remain. Internalization is supported only when behavior persists after scaffolding is reduced.

The model may generate candidates autonomously, while durable write permission remains subject to independent gates and human oversight. Human review should cover high-impact permissions, evaluator changes, lineage merges, semantic correctness, and maintenance commitments. Durable state should record this authorization path.

### 8.5 Open questions

Four connected questions remain open:

1. Under weak or fuzzy evaluators, confirmation-set reuse, and task drift, how can multi-round promotion retain auditable independence and confidence?
2. How should context, skill, and memory routing, compression, forgetting, and negative-result retention be managed over long horizons without losing verified behavior?
3. How can the trade-off among stability, plasticity, exploratory diversity, and reward-hacking risk be quantified?
4. How should high-cost confirmation, human review, and model adaptation be allocated across endpoint–edge–cloud, and how can behavior be re-confirmed after merging independently evolved plugin lineages?
