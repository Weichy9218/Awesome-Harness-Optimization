# The Zeroth-Order Operator Map of HarnessOpt

*Companion to [Axis I](../README.md#axis-i--the-zeroth-order-view-of-harnessopt) of Awesome Harness Optimization.*

This document is the long form of the ZO axis. The README states the taxonomy; this document states **why each operator exists in classical zeroth-order optimization, which mechanism plays its role in HarnessOpt, and — for every row — the exact point at which the analogy breaks.** The break points are the load-bearing content. A mapping table without them is an aesthetic exercise.

**Claim marking is a hard requirement in this list.** Every substantive sentence carries one of:

| Marker | Meaning |
|---|---|
| **[Lit]** | Attributable to a specific paper — its stated mechanism, setting, or reported result. |
| **[Ana]** | This document's reading under a unified frame. Not the original paper's conclusion. |
| **[Rec]** | A recommendation for practice or reporting. Never a description of current practice. |

**[Ana] A standing rule for this entire document.** Every correspondence below is an **analogy at the level of information structure**. No text-space method in this list *is* a continuous zeroth-order estimator. Where a mechanism "plays the role of" an operator, that phrase is doing real work: it means the mechanism occupies the same position in the query→proposal→acceptance loop, not that it inherits the operator's estimator properties, bias, variance, or convergence guarantees.

---

## Table of contents

1. [Why zeroth-order, precisely](#1-why-zeroth-order-precisely)
2. [The one substantive departure: language-mediated program compilation](#2-the-one-substantive-departure-language-mediated-program-compilation)
3. [The operator map](#3-the-operator-map)
4. [Implementability depends on surface structure](#4-implementability-depends-on-surface-structure)
5. [The honest restatement of SkillOpt](#5-the-honest-restatement-of-skillopt)
6. [The extra oracle tier: feasibility checks](#6-the-extra-oracle-tier-feasibility-checks)
7. [Evidence drift (D2): zeroth-order estimation is on-policy](#7-evidence-drift-d2-zeroth-order-estimation-is-on-policy)
8. [Cross-reference: which PAC quantity each operator moves](#8-cross-reference-which-pac-quantity-each-operator-moves)

---

## 1. Why zeroth-order, precisely

### 1.1 The defining property is gradient inaccessibility, not numeric variables

**[Ana]** The most common misreading of the ZO framing is that it requires numeric decision variables, and therefore cannot apply to text. That is backwards. What makes a method zeroth-order is a statement about **information availability**, not about the type of the decision variable:

> **The optimizer cannot access $\nabla_s f$. It can only obtain objective information by querying an oracle at a chosen point.**

Random numeric perturbation is one common *implementation* of such querying. It is not the definition. **[Lit]** The classical ZO literature is organized around exactly this information setting — the objective is available only through (possibly noisy) function evaluations (Liu et al., *IEEE SPM* 2020).

In HarnessOpt the optimizer's action set is: **deploy a candidate state → let the agent run tasks → observe scores and traces → decide how to edit.** There is no path from a return value back to a derivative with respect to the editable state. That is the whole argument. **[Ana]**

### 1.2 The objective

Fix the base model $M$ and the external evaluation boundary. Let $s \in \mathcal{S}_{\mathrm{edit}}$ be the editable state (prompt text, memory entries, skill files, workflow graph, harness code — see [Axis 0](../README.md#axis-0--the-editable-surface-l0l5)), let $z \sim \mathcal{D}$ be a task instance, let $H_s(M,z)$ denote the trajectory produced by running the harness instantiated at $s$, and let $R$ be a bounded return. The objective is

$$
f_M(s) \;=\; \mathbb{E}_{z \sim \mathcal{D}}\big[R\big(H_s(M, z)\big)\big].
$$

**[Lit]** This is the formalization given in SkillOpt-Lite §2.1 for skill optimization; the HarnessOpt reading generalizes $s$ from a text skill artifact to the full editable surface. **[Ana]**

$\nabla_s f_M$ is unavailable for two independent reasons, and it is worth keeping them separate because they fail differently:

1. **Discreteness.** $\mathcal{S}_{\mathrm{edit}}$ consists of discrete text, programs, and file structures. There is no ambient vector space in which $s + \mu u$ is defined for arbitrary $u$. **[Ana]**
2. **Non-differentiable composition.** Even if the state were relaxed into a continuous object, the composition $H_s \circ M$ — tool calls, control flow, environment side effects, sampling, external process exit codes — is not a differentiable map. **[Ana]**

**[Ana]** Reason (2) is the more fundamental one, and it is what rules out the tempting escape route of "just embed the text." A continuous relaxation of the *state* does not produce a differentiable *objective*, because the harness execution in between is not differentiable regardless of how the state is encoded. This is also why methods that do achieve a genuine gradient — GPTSwarm's edge-level REINFORCE over topology, ScoreFlow's Score-DPO relaxation, SEAL's RL loop — are boundary cases on this axis rather than instances of it. **[Lit]** for their mechanisms; **[Ana]** for the boundary classification.

### 1.3 One run is one stochastic observation

A single execution does not return $f_M(s)$. It returns one draw:

$$
Y(s,z) \;=\; R\big(H_s(M,z)\big), \qquad \mathbb{E}_{z\sim\mathcal{D}}\big[Y(s,z)\big] \;=\; f_M(s).
$$

The optimizer estimates $f_M(s)$ by the empirical mean over $n$ runs,

$$
\widehat{f}_n(s) \;=\; \frac{1}{n}\sum_{i=1}^{n} Y(s, z_i), \qquad z_i \overset{\text{i.i.d.}}{\sim} \mathcal{D}.
$$

**[Ana]** Three distinct randomness sources feed $Y(s,z)$, and conflating them is a recurring reporting failure:

| Source | What varies | Controllable by | Consequence if ignored |
|---|---|---|---|
| **Task sampling** | which $z$ is drawn from $\mathcal{D}$ | the evaluation split | The dominant variance term on small validation sets; drives the $\sqrt{\ln(1/\delta)/m}$ slack in [bound B2](../README.md#ii1-two-single-round-bounds-and-their-division-of-labor) |
| **Model sampling** | decoding stochasticity of $M$ within one $z$ | temperature, seed (partially) | Two runs of the *same* candidate on the *same* task differ; a single-run A/B comparison measures decoding noise, not the edit |
| **Environment execution** | tool latency, network state, non-determinism of the sandbox, external service responses | rarely controllable | Makes exact paired replay unavailable in many settings — which is precisely the structure the [control-variate row](#37-control-variate) needs |

**[Rec]** A HarnessOpt result should state which of these three were held fixed and which were resampled between the base and the candidate. "We reran the benchmark" does not determine this, and the three have different implications for whether an observed $\widehat{\Delta}$ is attributable to the edit.

**[Ana]** Note what is *not* required by this setup: the optimizer is never obliged to construct an explicit perturbation direction $u$. It only has to be able to name a candidate and pay for a query. This is exactly why the ZO frame transfers to LLM-proposed edits, and exactly why most of the operator analogies below are one-sided — the *query* side transfers cleanly; the *estimator* side usually does not.

---

## 2. The one substantive departure: language-mediated program compilation

### 2.1 The query returns semantics, not just a scalar

**[Lit]** In classical ZO, the oracle is a strict black box: it returns $f(s)$ and nothing else. Intermediate state transitions and the internal causal chain are latent and unobservable (Liu et al., 2020; SkillOpt-Lite §2.1.2 for the contrast).

In HarnessOpt the query returns

$$
\mathcal{E}_t \;=\; \big\{(z_i,\ \tau_i,\ R_i,\ \mathrm{feedback}_i)\big\}_{i=1}^{n_t},
$$

where $\tau_i$ is the full trajectory, $R_i$ the scalar return, and $\mathrm{feedback}_i$ collects error logs, stack traces, test output, and tool responses. **[Lit]** These trajectories carry the causal chain of success or failure and can localize *where* a run went wrong and *what kind* of edit might address it (SkillOpt-Lite §2.1.2).

**[Lit]** SkillOpt-Lite names the resulting view **language-mediated program compilation**:

| Program-execution concept | HarnessOpt counterpart |
|---|---|
| Source program | the editable state $s$ — a program written in natural language or code |
| Compiler / runtime | the LLM $M$ together with the harness $H$ |
| Execution trace / debug log | the rollout trajectory $\tau$ and its feedback |
| Patch | the proposed edit $\tilde{s}_{t+1}$ |

> **Insight 1 (Conceptual divergence).** **[Lit]** Classical ZO optimization relies on blind numerical perturbation because it cannot inspect the function. Agentic skill / harness optimization functions as language-mediated program compilation, where rollout trajectories serve as interpretable debugging feedback. **[Ana]** The gain is in **proposal quality**, not in oracle access.

### 2.2 Two caveats, stated forcefully

**[Ana]** Insight 1 is the single most quotable line in this framing, and therefore the single most over-quotable. Two caveats must travel with it, or it becomes an overclaim.

**Caveat 1 — semantic side-information does not lift the query-only constraint.**

The trace tells the optimizer *what happened at $s_t$*. It does not tell the optimizer $f_M(\tilde{s})$ for any $\tilde{s} \neq s_t$. Every candidate still costs a deployment and a set of rollouts before its value is known. **[Ana]** Consequently:

- The query-budget analysis of ZO applies unchanged. Reading a trace is free; *knowing whether the edit derived from it helps* is not.
- A method that reads richer traces is not thereby sample-efficient. **[Lit]** GEPA reports up to $35\times$ fewer rollouts than RL by reflecting over full traces — this is evidence that trace-informed proposals reduce the *number of queries needed*, which is a proposal-quality claim, not a claim that any query was avoided in the accounting sense. **[Ana]**
- Rich feedback changes the proposal distribution $P_\phi$. It does not change the oracle.

**Caveat 2 — a readable trace is not correct attribution, and correct attribution is not statistical acceptance evidence.**

This is a two-link chain, and both links are weak:

$$
\underbrace{\text{trace is readable}}_{\text{observation}}
\;\not\Rightarrow\;
\underbrace{\text{failure correctly attributed}}_{\text{causal claim}}
\;\not\Rightarrow\;
\underbrace{\text{the derived edit should be accepted}}_{\text{statistical claim}}
$$

- **First link.** **[Lit]** Reported step-level attribution accuracy in agent-trace analysis sits in a low range, and regression prediction has markedly lower precision and recall than fix prediction. A trace that reads fluently as a causal story can still assign blame to the wrong step. **[Ana]** The LLM optimizer's confidence in its own attribution is not a calibrated quantity and should not be treated as one.
- **Second link.** Even a correctly attributed root cause says nothing about whether the *specific edit* generalizes over $\mathcal{D}$. Attribution is about one episode; acceptance is a statement about the task distribution. **[Ana]** That gap is the entire subject of [Axis II](../README.md#axis-ii--pac--stability-analysis-of-harnessopt), and it is why the ZO axis cannot be the whole analysis.

**[Ana] The practical form of the error this prevents.** "The trace clearly shows the agent failed because the skill file lacked a retry rule; we added one; the fix is justified" is a chain of three claims presented as one observation. The first is an observation, the second is an unverified causal attribution, and the third is an unverified statistical claim. **[Rec]** Papers should not use trace readability as evidence for acceptance. It is evidence for *proposal plausibility*, which is a different and much weaker thing.

---

## 3. The operator map

**[Ana]** Starting from the SkillOpt-Lite operator table and extended with two rows this list adds — adaptive step / momentum, and population & archive — so that evolutionary-search methods have a home on this axis. Without those rows, methods like AdaEvolve (which explicitly schedules exploration from improvement history) and the whole FunSearch/AlphaEvolve/DGM family have no cell to occupy, and the table silently misclassifies them as one-point or coordinate methods.

**Read the third column as a role assignment, not an implementation claim.**

| ZO operator | Classical form | Mechanism playing the same role in HarnessOpt | Representative work |
|---|---|---|---|
| **Zeroth-order oracle** | $f(s + \mu u)$ | Sandbox / environment feedback; a scalar task metric returned by running a deployed candidate | all of the below |
| **One-point estimate** | $\widehat{\nabla} f(s) \propto f(s+\mu u)\, u$ | A single trajectory or a single exception directly drives one edit | Reflexion, Voyager, Dynamic Cheatsheet, OPRO, Gödel Agent |
| **Multi-point / mini-batch** | $\frac{1}{b}\sum_{i=1}^{b}\big[f(s+\mu u_i) - f(s)\big]u_i$ | Batch rollouts aggregated before proposing; **consensus mining** requires the edit to rest on a cross-task reproducible pattern rather than a single anomaly | SkillOpt ($B_m{=}8$), SkillOpt-Lite (consensus mining), Trace2Skill (map-reduce patch merge), SkillForge (batch ticket pool), ExpeL, Self-Harness |
| **Central difference** | $\dfrac{f(s+\mu u) - f(s-\mu u)}{2\mu}$ | Success/failure trace contrast localized at the action-divergence point; or an on/off A-B run of the same candidate | SkillCAT (CCE operator at divergence point $w_i$), ProTeGi, TextGrad, DemoEvolve, ReasoningBank, Agent Symbolic Learning; feature-toggle implementations |
| **ZO coordinate descent** | $\dfrac{f(s+\mu e_i) - f(s)}{\mu}\, e_i$ | Fault-isolated atomic modification: one module / file / entry changed, all else held fixed | SkillAdaptor (faulty step $t^*$ as axis, candidate skill $s_j$ as basis), Trace2Skill, SkillForge, SkillWeaver, AgentSquare, MASS, AlphaEvolve (`EVOLVE-BLOCK`), Meta-Harness, AHE, Ouroboros |
| **Trust region** | $s_{k+1} \in \mathcal{B}(s_k, \Delta_k)$ | Edit budget, minimal-modification principle, allowlist path restriction, interface-signature invariance, bounded prefix length | SkillOpt (budget decay $L_t: 4 \to 2$), SkillOpt-Lite, SkillForge (minimal modification), SoftSkill (prefix bounded at $m{=}32$ tokens), ACE (delta updates), Self-Harness, HarnessOpt allowlist $+\ \Delta$ |
| **Control variate** | $\hat{g}_{\mathrm{cv}} = \hat{g} - c + \mathbb{E}[c]$ | Rejected-edit buffer steering later proposals away from known-dead directions; novelty rejection sampling; paired replay cancelling common randomness | SkillOpt rejected buffer, ShinkaEvolve (novelty rejection sampling), GEPA, Meta-Harness |
| **Adaptive step / momentum** *(row added by this list)* | step size / smoothing radius scheduled from improvement history | Exploration budget, candidate count, and parent sampling scheduled by the fitness-improvement trajectory | AdaEvolve, ShinkaEvolve, AlphaEvolve, ThetaEvolve, AFlow (MCTS schedule) |
| **Population & archive** *(row added by this list)* | $\tilde{s} \in \operatorname{Select}(\mathcal{A}_t; R)$ | Elitism, island models, novelty rejection sampling, Pareto selection over an archive of scored candidates | Promptbreeder, EvoPrompt, ADAS, AFlow, AgentSquare, MaAS, ELM (MAP-Elites), FunSearch, AlphaEvolve, ShinkaEvolve, DGM, GEPA, CORAL, AIDE |
| **Confirmation gate** | one-shot evaluation on independent samples | compile → smoke → full staged confirmation; held-out selection; statistical dead-zone $\Delta$; exact rollback | SkillOpt, SkillOpt-Lite, Self-Harness, SkillForge, GEPA, CORAL |

**[Ana]** Two structural remarks on the table itself:

- **The rows are not mutually exclusive.** Most serious systems occupy three or four cells at once — SkillOpt is multi-point *and* trust region *and* control variate *and* confirmation gate. The taxonomy classifies mechanisms, not papers.
- **The last row is not a ZO operator in the classical sense.** Classical ZO has no acceptance step: the iterate moves wherever the estimator points. The confirmation gate exists because HarnessOpt writes to persistent state, and it is included here so that the handoff to [Axis II](../README.md#axis-ii--pac--stability-analysis-of-harnessopt) is explicit rather than implied.

The subsections below give, for each row: **(a)** what the classical operator does and why it exists; **(b)** per-work notes on how each representative system realizes the role; **(c)** where the analogy breaks.

---

### 3.1 Zeroth-order oracle

**(a) Classical role.** **[Lit]** The oracle is the *only* interface to the objective: submit a point, receive $f(s)$ or a noisy $f(s) + \xi$. Everything else in the ZO toolbox is built to economize on calls to it, because query count is the resource that convergence rates are stated in (Liu et al., 2020; Nesterov & Spokoiny, 2017).

**(b) Realization in HarnessOpt.** **[Lit]** The oracle is the sandbox: deploy the candidate state, run tasks, collect returns. Every system in this list has one; what differs is what counts as a query and what it costs.

- **[Ana]** On cheap benchmarks with fast automatable verifiers (KernelBench's `fast_p`, unit-test-scored program search), the oracle is close to the classical idealization: many queries, low per-query cost, low-variance scoring.
- **[Ana]** On terminal and long-horizon benchmarks (Terminal-Bench, SWE-bench-scale tasks), one query is an expensive multi-minute agent run. **[Lit]** Meta-Harness reports declining to carve an independent split on expensive terminal tasks — a direct consequence of oracle cost, not of methodological carelessness.

**(c) Where the analogy breaks.**

- **[Ana]** **The classical oracle is stateless; the HarnessOpt oracle is not.** Running a candidate can leave side effects — files written, processes lingering, registry or cache entries, memory entries already appended. If the environment is not reset exactly, the second query at the same $s$ is not a second draw from the same distribution. This is the same property that [B-2](../README.md#ii3-acceptance-thresholds-and-exact-rollback) turns into a premise for monotone improvement.
- **[Ana]** **The classical oracle returns a scalar; here the return is a design choice.** Whether $R$ is task pass rate, a rubric score, a Pareto vector, or an LLM judgment materially changes what is being optimized, and none of these is the "true" $f$. When the scorer is itself an LLM inside the same repository, premise (iii) of (B2) is at risk — see [II.1](../README.md#ii1-two-single-round-bounds-and-their-division-of-labor).
- **[Ana]** **Query cost is not uniform across candidates.** A candidate that fails to compile costs nearly nothing to reject; a candidate that runs for twenty minutes and then fails costs a full budget slot. Classical query-complexity accounting assumes fungible queries. See [§6](#6-the-extra-oracle-tier-feasibility-checks).

---

### 3.2 One-point estimate

**(a) Classical role.** The one-point estimator

$$
\widehat{\nabla} f(s) \;=\; \frac{d}{\mu}\, f(s + \mu u)\, u, \qquad u \sim \mathrm{Unif}(\mathbb{S}^{d-1}),
$$

is the cheapest possible gradient surrogate: **one query per step**. **[Lit]** It is an unbiased estimator of the gradient of the *smoothed* objective $f_\mu$, but its variance scales badly — it retains an $f(s)/\mu$ term that does not cancel, so the variance blows up as $\mu \to 0$. This is why the classical literature treats it as a fallback and prefers two-point estimators when a second query is affordable (Duchi, Jordan, Wainwright & Wibisono, 2015). **[Ana]** The relevant intuition to carry forward: *one-point estimation is high-variance by construction, and no amount of cleverness in the proposal fixes that.*

**(b) Per-work notes.**

- **Reflexion.** **[Lit]** Converts feedback from a single episode into a verbal self-reflection stored in episodic memory. **[Ana]** The archetypal one-point design: one trace in, one edit out, no cross-episode aggregation, and — per the [audit table](../README.md#ii6-stability--confirmation-audit-of-the-literature) — no candidate test. The highest-$\beta_{\exp}$ design in the list.
- **Voyager.** **[Lit]** A single error signal triggers a local overwrite of the skill program. **[Ana]** One-point estimation on an *executable* surface: the same estimator structure as Reflexion, but with a compiler-checkable artifact, which changes the feasibility tier ([§6](#6-the-extra-oracle-tier-feasibility-checks)) without changing the estimator.
- **Dynamic Cheatsheet.** **[Lit]** Persistent self-curated memory of strategies updated at inference time. **[Ana]** One-point at the memory layer; the persistence is what makes the variance consequential rather than transient.
- **OPRO.** **[Lit]** Generates new candidates from a meta-prompt containing prior (solution, score) pairs. **[Ana]** A hybrid: the *proposal* conditions on an archive, but each new candidate is scored from what is effectively a scalar-return-only history — one-point in the information it uses per direction, archive-driven in how it selects a base.
- **Gödel Agent.** **[Lit]** Monkey-patches its own logic at runtime. **[Ana]** One-point on the harness code surface, with the additional property that in-place runtime patching makes exact rollback hard — so the high variance is compounded by irreversibility.

**(c) Where the analogy breaks.**

- **[Ana]** **There is no $u$, and therefore no direction to multiply by.** In the classical form, the estimator returns $f(s+\mu u)\,u$ — a *vector* pointing along the sampled direction, scaled by the observed value. In a text method, the "direction" is whatever the LLM wrote; it is not drawn from a known distribution, its density is not known, and it cannot be multiplied by a scalar. What survives is only the shape "one observation, one move."
- **[Ana]** **The bias is of a different kind.** Classical one-point estimation is unbiased for $\nabla f_\mu$ and merely high-variance. The text analogue has no unbiasedness property at all: the proposal is generated by an LLM conditioned on the trace, so its expectation is not characterized with respect to anything. Calling it "high-variance" is an analogy about *sensitivity to a single sample*, which is real and is exactly what $\beta_{\exp}$ measures — it is not a variance statement about an estimator.
- **[Ana]** **The step is not scaled by the observed value.** Classical one-point scales the move by $f(s+\mu u)$. In text methods a failure trace typically triggers an edit of roughly constant "size" regardless of how bad the failure was. The magnitude channel is simply absent.

---

### 3.3 Multi-point / mini-batch

**(a) Classical role.** Averaging $b$ independent directional estimates,

$$
\widehat{\nabla} f(s) \;=\; \frac{1}{b}\sum_{i=1}^{b}\Big[f(s+\mu u_i) - f(s)\Big] u_i,
$$

reduces the variance of the gradient estimate by roughly $1/b$ and improves the dimension dependence of the resulting rate. **[Lit]** The point of the operator is **variance reduction over the sampled directions $u_i$** — it is a statement about the geometry of the estimate, not about the data distribution (Liu et al., 2020; Duchi et al., 2015).

**(b) Per-work notes.**

- **SkillOpt.** **[Lit]** Iterative reflection with mini-batching at size $B_m = 8$: reflection is performed over a batch of rollouts rather than a single trace, with hierarchical parallel LLM tree reduction for merging. **[Ana]** The most explicit realization of the role in the skill literature.
- **SkillOpt-Lite.** **[Lit]** Consensus mining: an edit is admitted only when it rests on a pattern reproduced across tasks, not on a single anomaly. **[Ana]** This is the cleanest statement of the *statistical intent* behind the row — it targets $\beta_{\exp}$ directly.
- **Trace2Skill.** **[Lit]** Map-reduce patch merging across trajectories, described by its authors as ZO-SGD. **[Ana]** Strong on the (B1) side, compromised on (B2) — its gates run on sub-sampled training subsets.
- **SkillForge.** **[Lit]** Phase-2 batch ticket aggregation for trajectory denoising. **[Ana]** "Denoising" is the right word for what the operator actually does here, and a better description than "gradient estimation."
- **ExpeL.** **[Lit]** Extracts natural-language insights across a pool of experiences into a growing store. **[Ana]** A $\beta_{\exp}$-reducing mechanism even though it has no formal gate — the aggregation is real; the confirmation is absent.
- **Self-Harness.** **[Lit]** Weakness mining over accumulated runs before proposing a bounded harness change. **[Ana]** Multi-point at the harness-code layer.

**(c) Where the analogy breaks — the most important break point in this document.**

> **[Ana] What varies across the batch is the task $z_i$, not the perturbation $u_i$.**

In the classical operator, $s$ is fixed and $b$ *different directions* $u_1,\dots,u_b$ are probed, each with its own query. In every text/code system above, the batch consists of $b$ *different tasks* evaluated at (essentially) the same state, and the aggregation happens over the resulting traces. Formally, the text methods compute something in the family

$$
\frac{1}{b}\sum_{i=1}^{b} Y(s, z_i) \quad\text{and aggregate } \{\tau_i\}, \qquad\text{not}\qquad \frac{1}{b}\sum_{i=1}^{b}\big[f(s+\mu u_i)-f(s)\big]u_i .
$$

**[Ana]** Consequences, stated precisely:

1. **This estimates $f$ under task noise. It does not estimate a directional derivative.** There is no direction being averaged, so there is nothing being made less noisy in the geometric sense the classical operator is about.
2. **The honest reading is *variance reduction over $\mathcal{D}$*.** That is a real and valuable property — but it is a property about robustness to which tasks were sampled, not about gradient estimation.
3. **That property is exactly what stability needs.** Reducing sensitivity to any single $z_i$ is the definition of lowering $\beta_{\exp}$ in [bound B1](../README.md#ii1-two-single-round-bounds-and-their-division-of-labor). So the row is not empty — it just belongs to Axis II's quantity, not to Axis I's estimator theory. **This is the single place where the two axes touch most directly.**
4. **Batch size therefore has a different meaning.** In classical ZO, larger $b$ buys a better-conditioned direction. Here, larger $B_m$ buys lower single-sample sensitivity. **[Rec]** Papers should justify batch size on the second ground, not the first, and should not cite ZO variance-reduction rates as support for a mini-batch choice.

- **[Ana]** A secondary break: the aggregation is performed by an LLM merging traces or patches, not by arithmetic averaging. Averaging is linear and commutes with expectation; LLM merging does neither. Two batches with the same per-task returns can produce different merged patches.

---

### 3.4 Central difference

**(a) Classical role.** The two-point / central-difference estimator

$$
\widehat{\nabla}_u f(s) \;=\; \frac{f(s+\mu u) - f(s-\mu u)}{2\mu}\, u
$$

exists for two reasons. **[Lit]** First, subtracting the two evaluations **cancels the $f(s)$ term** that dominates one-point variance, giving an estimator whose variance no longer blows up as $\mu \to 0$. Second, the symmetric difference cancels the leading even-order term in the Taylor expansion, so the bias is $O(\mu^2)$ rather than $O(\mu)$. **[Lit]** Duchi et al. (2015) is the formal statement that two function evaluations suffice to recover near-optimal rates — the reason two-point estimators dominate one-point ones whenever the second query is affordable.

**(b) Per-work notes.**

- **SkillCAT.** **[Lit]** A custom contrastive operator (CCE) that aligns a successful and a failed trajectory and analyses the behavior at the **action-divergence point $w_i$** — the first step after the common prefix where the two runs differ. **[Ana]** The closest thing in the skill literature to a genuine central difference: it does have two runs and it does subtract them, at a well-defined location.
- **ProTeGi.** **[Lit]** Coined "textual gradients"; forms a critique from failure cases and edits the prompt in the indicated direction, with beam search. **[Ana]** Structurally a success/failure contrast — the central-difference *role* without a constructible $s - \mu u$.
- **TextGrad.** **[Lit]** Backpropagates textual feedback through a compound AI system. **[Ana]** The "gradient" is semantic side-information attached to a zeroth-order query, not a verifiable derivative; the chain rule it mimics has no correctness guarantee at any node.
- **DemoEvolve.** **[Lit]** Human demonstrations supply the contrast signal that sparse rewards do not. **[Ana]** The contrast partner comes from outside the search rather than from a perturbation — a *substitute* for $s - \mu u$, obtained by importing a reference trajectory.
- **ReasoningBank.** **[Lit]** Distills strategies from successes *and* failures. **[Ana]** The central-difference role at the memory layer.
- **Agent Symbolic Learning.** **[Lit]** Language "loss / gradient / backprop" over prompts, tools, and pipeline jointly. **[Ana]** Same classification and same caveat as TextGrad.
- **Feature-toggle implementations.** **[Ana]** On a versioned code surface, running the same harness with a capability toggled on and off, on the same task batch, is the one case where both evaluation points genuinely exist and are genuinely deployable.

**(c) Where the analogy breaks.**

> **[Ana] $s - \mu u$ is not constructible on a text surface.**

- **[Ana]** The estimator requires evaluating the objective at a point *symmetrically opposite* the perturbation. Given a text edit ("add a retry rule"), there is no defined operation producing the anti-edit. "Remove the retry rule" is not $s - \mu u$: it is $s$ itself if the rule was newly added, and it is a different, unrelated state if the rule already existed in some form. The group structure that makes negation meaningful does not exist.
- **[Ana]** **Success/failure trace contrast is not the same comparison.** SkillCAT-style contrast compares two runs *of the same state $s$* on different tasks or with different sampling outcomes. Central difference compares two *different states* on the same task. These are orthogonal comparisons: one isolates run-level divergence at fixed state, the other isolates state-level difference at fixed task. **[Ana]** Calling both "central difference" hides the fact that the first cannot, even in principle, tell you the effect of an edit.
- **[Ana]** **Nothing cancels.** The entire reason central difference exists is the cancellation of the $f(s)$ term and the even-order bias term. In the trace-contrast analogue there is no subtraction of two evaluations of a common quantity, so neither cancellation occurs, and none of the variance or bias advantages transfer.
- **[Ana]** **The divergence point is a heuristic localization, not a derivative.** $w_i$ marks where behavior differed. It does not measure by how much the objective changes per unit of state change, and its identification is subject to the attribution-accuracy ceiling of [Caveat 2](#22-two-caveats-stated-forcefully).
- **[Ana]** **The one case where it survives:** feature toggles on versioned executable code. There, on and off are both real deployable states, both are evaluated on the same batch, and the subtraction is a genuine paired comparison. This is the strongest example of [§4](#4-implementability-depends-on-surface-structure)'s thesis.

---

### 3.5 ZO coordinate descent

**(a) Classical role.** The coordinate-wise estimator

$$
\widehat{\nabla}_i f(s) \;=\; \frac{f(s + \mu e_i) - f(s)}{\mu}\, e_i
$$

probes one basis direction at a time. **[Lit]** It exists because it makes each query **attributable**: the observed change is caused by exactly one coordinate, so the credit assignment problem disappears. It also allows per-coordinate step sizes and exploits separable structure. Its cost is dimension dependence — a full sweep costs $d$ queries — which is why it is preferred when $d$ is modest or when coordinates are known to be nearly separable (Liu et al., 2020). **[Ana]** The property to carry forward is **attribution by construction**, and its precondition is **an orthogonal basis**.

**(b) Per-work notes.**

- **SkillAdaptor.** **[Lit]** Coordinate descent with the faulty step $t^*$ of the trajectory as the axis and a candidate skill $s_j$ as the basis vector — one localized repair at a time. **[Ana]** The most literal instantiation of the row in the skill literature.
- **Trace2Skill / SkillForge.** **[Lit]** Patch-level and ticket-level edits keep the rest of the skill library fixed. **[Ana]** Coordinate descent at entry granularity.
- **SkillWeaver.** **[Lit]** Synthesizes and debugs individual reusable API skills into the harness. **[Ana]** Each skill is a separately addressable unit — closer to a real coordinate than a paragraph is.
- **AgentSquare.** **[Lit]** Evolution and recombination over Planning / Reasoning / ToolUse / Memory module slots. **[Ana]** The cleanest objective coordinate basis in the list: the slots are declared by the design space, not inferred from text.
- **MASS.** **[Lit]** Interleaved multi-stage search over prompts and topologies. **[Ana]** Block coordinate descent with blocks defined by pipeline stage.
- **AlphaEvolve.** **[Lit]** LLM ensemble editing regions marked `EVOLVE-BLOCK` within an otherwise fixed program. **[Ana]** The cleanest example in the entire list of a surface *engineered* to make coordinate descent implementable: the basis is human-declared and machine-enforced, and edits outside the blocks are not possible.
- **Meta-Harness / AHE / Ouroboros.** **[Lit]** File-level and commit-level edits over harness code. **[Ana]** The import graph and interface signatures supply block boundaries that are statically decidable, so "one coordinate" has an objective meaning.

**(c) Where the analogy breaks.**

> **[Ana] Text "coordinates" are not orthogonal, and paragraph splits are arbitrary.**

- **[Ana]** **Non-orthogonality.** Editing one bullet in a skill file changes how the model reads the surrounding bullets. The effect of coordinate $i$ depends on the current value of coordinate $j$ — precisely the condition under which coordinate descent loses its attribution property. In a genuinely non-separable objective, coordinate descent is still a valid algorithm, but the single-query attribution claim that motivates it here does not hold.
- **[Ana]** **The basis is chosen, not given.** In $\mathbb{R}^d$ the standard basis is canonical. In a text artifact, "one coordinate" might be a line, a bullet, a paragraph, a section, or a file — and the choice is made by whoever wrote the prompt for the optimizer. It is **block coordinate descent with no objective definition of a block.** Different block choices give different search behavior with no principled way to compare them.
- **[Ana]** **Dimension is undefined.** Classical query complexity for coordinate methods is stated in $d$. A text artifact has no $d$: adding a paragraph adds coordinates. So the dimension-dependence results — the main quantitative content of the classical row — have nothing to attach to. **[Ana]** Nesterov & Spokoiny's dimension dependence is nevertheless a useful *qualitative* warning: larger edit surfaces are statistically more expensive to search, independent of the PAC argument.
- **[Ana]** **Where it stops breaking.** With an import graph, interface signatures, module slots, or explicit `EVOLVE-BLOCK` markers, the blocks become objective and statically checkable, intra-block versus inter-block effects become decidable, and the attribution property is partially recovered. **[Ana]** This is why [Axis 0 §4 (L2)](../README.md#4-l2--agentic-workflow--architecture-search) is described as the first level where this operator is more than an analogy.

---

### 3.6 Trust region

**(a) Classical role.** Trust-region and model-based derivative-free methods restrict each step to a ball $\mathcal{B}(s_k, \Delta_k)$ within which the local model is trusted, and adapt $\Delta_k$ based on the agreement between predicted and actual improvement. **[Lit]** The operator exists because a derivative-free local model is only reliable near the current iterate; the radius is the formal expression of "how far the current evidence licenses moving" (Conn, Scheinberg & Vicente, 2009). **[Ana]** Two properties are essential and are the ones to check in any analogue: **(i)** the radius is a *distance in the space the objective is sensitive to*; **(ii)** the radius is *adapted from observed agreement*, not fixed by fiat.

**(b) Per-work notes.**

- **SkillOpt.** **[Lit]** An explicit edit budget with decay $L_t: 4 \to 2$ — fewer permitted edits as optimization proceeds. **[Ana]** The decay schedule is the closest thing in the literature to radius adaptation, though it is a fixed schedule rather than a feedback rule.
- **SkillForge.** **[Lit]** An enforced minimal-modification principle. **[Ana]** A qualitative radius: "change as little as possible," with no metric attached.
- **SoftSkill.** **[Lit]** A soft prefix bounded at $m = 32$ tokens. **[Ana]** A rare case where the trust region is a **hard dimensional constraint** rather than an edit-count heuristic — the reachable set is genuinely bounded by construction, not by instruction.
- **ACE.** **[Lit]** Incremental delta updates to the evolving context, which the paper credits with avoiding "context collapse." **[Ana]** A trust region on a text surface; the collapse it prevents is a concrete instance of high $\beta_{\exp}$.
- **SkillOpt-Lite / Self-Harness.** **[Lit]** Bounded proposals combined with staged confirmation. **[Ana]** Radius and gate designed together rather than independently.
- **HarnessOpt allowlists.** **[Ana]** An allowlist is a **static trust region** — it constrains *which paths* may be written, before any return is observed. The dead-zone $\Delta$ is a **return-side trust region** — it constrains *which observed improvements* count. They are different objects and should not be described interchangeably.

**(c) Where the analogy breaks.**

> **[Ana] Edit count is not a semantic distance.**

- **[Ana]** Changing one word can change behavior drastically ("always" → "never"; a single changed default in a config). Adding ten lines of explanatory commentary can change nothing at all. A radius measured in edits, tokens, or diff bytes is therefore **not monotone in behavioral effect**, which is the one property a trust-region radius must have for the operator to mean anything.
- **[Ana]** **No agreement-based adaptation.** Classical trust-region methods expand or shrink $\Delta_k$ by comparing predicted improvement to actual improvement. No text-space system in this list computes a predicted improvement to compare against, so the adaptation half of the operator is simply absent. SkillOpt's $L_t: 4 \to 2$ is a *schedule*, not a feedback loop. **[Rec]** An actual feedback rule — shrink the edit budget after a rejected candidate, expand after a confirmed gain — is implementable and, to our knowledge, unreported.
- **[Ana]** **The radius is on the wrong space.** Edit budget measures distance in *description space*; the operator needs distance in *behavior space*. These come apart in both directions, as above.
- **[Ana]** **But the wrong-space radius is still doing real statistical work.** Even a description-space budget bounds the reachable set $\mathcal{H}_T$, and therefore tightens the confirmation bound through $l_{\mathrm{eff}} = T(L+1)$ in [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound). **[Ana]** So this row has the unusual property that the analogy fails on the ZO side while the mechanism succeeds on the PAC side — for a completely different reason than the one usually given for it.
- **[Rec]** If citing Proposition A, $L$ must be the **description length** of the edit (e.g. diff bytes), not the edit count: "at most $L$ edits" does not bound how much code a single edit inserts.

---

### 3.7 Control variate

**(a) Classical role.** Given an estimator $\hat{g}$ and an auxiliary variate $c$ correlated with it whose mean $\mathbb{E}[c]$ is **known**, the corrected estimator

$$
\hat{g}_{\mathrm{cv}} \;=\; \hat{g} - c + \mathbb{E}[c]
$$

is **unbiased for the same quantity** and has lower variance whenever $\mathrm{Cov}(\hat{g}, c)$ is sufficiently positive. **[Lit]** The three requirements are non-negotiable: an explicit random variate $c$, a known $\mathbb{E}[c]$, and the additive correction that restores unbiasedness. Common-random-numbers / paired replay is the same idea applied to comparisons: evaluate two candidates under identical randomness so that the shared noise cancels in the difference.

**(b) Per-work notes.**

- **SkillOpt.** **[Lit]** Rejected edits are passed into a buffer that conditions later proposals, described as a negative control variate. **[Ana]** Functionally: it prevents the proposer from re-exploring directions already known to fail.
- **ShinkaEvolve.** **[Lit]** Novelty rejection sampling filters proposals too similar to already-evaluated ones. **[Ana]** The same role from the opposite side — steering away from already-covered directions rather than from known-failed ones.
- **GEPA.** **[Lit]** Reflective evolution reading full traces with a Pareto archive. **[Ana]** Trace-conditioned proposal reuse plays a partial control-variate role by reducing redundant exploration.
- **Meta-Harness.** **[Lit]** Searches over harness code via the file system with a scored archive. **[Ana]** On a versioned code surface with fixed seeds, paired replay is genuinely available — this is the branch of the row that can be made real.

**(c) Where the analogy breaks.**

> **[Ana] The rejected buffer has no explicit random variate $c$, no known $\mathbb{E}[c]$, and no unbiased correction. Its variance reduction is therefore unverifiable — not small, not unproven, but undefined.**

- **[Ana]** **No $c$.** A buffer of rejected edit texts is not a random variable that is jointly distributed with an estimator. There is nothing to subtract.
- **[Ana]** **No $\mathbb{E}[c]$.** Even granting some notional $c$, its mean is unknown, so the additive correction that makes the classical estimator unbiased cannot be applied. Without that term the construction is not a control variate at all; it is a filter.
- **[Ana]** **The effect is on the proposal distribution, not on an estimator.** What the buffer actually does is **negative conditioning of $P_\phi$**: it changes which candidates get proposed. That is a search-efficiency mechanism. It is a legitimate and probably useful one. It is not variance reduction in any sense that has a definition.
- **[Ana]** **It can also introduce bias.** A direction rejected once may have been rejected due to run noise, or because it was premature given the state at the time. Permanently excluding it biases the search. Classical control variates cannot do this — they are unbiased by construction. **[Rec]** Rejection buffers should carry an expiry or a retry policy; permanent exclusion should be reported as a design decision, not left implicit.
- **[Ana]** **Where it stops breaking.** Deterministic seeds plus version control make paired replay real: the same task, the same seed, two states, and the difference genuinely cancels the common randomness. **[Ana]** Note that this recovers the *common-random-numbers* branch of the row, not the $\hat{g} - c + \mathbb{E}[c]$ branch — the rejected buffer remains an analogy even on a code surface.

---

### 3.8 Adaptive step / momentum *(row added by this list)*

**(a) Classical role.** Adaptive step-size rules and momentum use the *history* of observed improvements to set the current step. **[Lit]** In ZO specifically, the smoothing radius $\mu$ and the step size interact with the estimator's variance, so scheduling them from observed progress is a standard way to trade exploration against precision. **[Ana]** The row is added here because without it, the family of systems that explicitly schedule exploration from fitness history has no cell in the table and gets misfiled under population or one-point.

**(b) Per-work notes.**

- **AdaEvolve.** **[Lit]** Explicitly casts LLM-driven search as zeroth-order optimization with an adaptive schedule. **[Ana]** The nearest neighbor to this axis in the literature, and the direct reason this row exists.
- **ShinkaEvolve.** **[Lit]** Parent sampling, novelty rejection sampling, and bandit-based LLM selection. **[Ana]** The bandit over proposer models is an adaptive allocation rule over *which proposer to query*, a dimension classical ZO does not have.
- **AlphaEvolve.** **[Lit]** An LLM ensemble over marked evolve blocks. **[Ana]** Ensemble weighting plays the adaptive-allocation role.
- **ThetaEvolve.** **[Lit]** Evolutionary search combined with RL and in-context learning at test time. **[Ana]** Mixed-mechanism; the adaptive component is the schedule over search modes.
- **AFlow.** **[Lit]** MCTS over code-represented workflow graphs. **[Ana]** MCTS makes the exploration/exploitation schedule explicit and principled — the most structurally justified member of this row.

**(c) Where the analogy breaks.**

- **[Ana]** **There is no step size to adapt.** Classical adaptation modulates a scalar multiplying a direction. Here what is modulated is the *number of candidates*, *which proposer model is called*, or *which parent is sampled* — allocation decisions, not magnitudes. The analogy is to adaptive *budget allocation*, which is closer to bandit theory than to step-size control.
- **[Ana]** **Momentum has no accumulator.** Momentum requires adding scaled past directions to the current one. Text edits do not admit addition or scaling, so "momentum" in this setting means, at most, "the proposer is shown a history and tends to continue in a similar direction" — a conditioning effect with no accumulation semantics and no decay parameter with a defined meaning.
- **[Ana]** **Adaptation from a noisy signal is unguarded.** Classical adaptive rules assume the improvement signal is a reasonable estimate of actual improvement. Under the small-$m$ validation regimes common here, the improvement signal is itself high-variance, so an adaptive schedule can lock onto noise. **[Rec]** Adaptive schedules should be driven by the same statistically-defensible quantity as the gate ($\widehat{\Delta}$ against a dead-zone), not by raw score movement.

---

### 3.9 Population & archive *(row added by this list)*

**(a) Classical role.** Population-based derivative-free search maintains a set of scored candidates and selects the next parent from it: $\tilde{s} \in \operatorname{Select}(\mathcal{A}_t; R)$. **[Lit]** Evolution strategies, elitism, island models, and quality-diversity archives (MAP-Elites) are the standard machinery; CMA-ES is the reference point for adapting a proposal distribution from a population without gradients (Hansen & Ostermeier, 2001). **[Ana]** The role exists to hold multiple hypotheses simultaneously and to avoid committing to a single trajectory through the search space.

**(b) Per-work notes.**

- **FunSearch.** **[Lit]** LLM proposer plus evaluator in an evolutionary loop. **[Ana]** The template the rest of this row descends from.
- **AlphaEvolve / ShinkaEvolve / ThetaEvolve.** **[Lit]** Archive-based program evolution with varying selection machinery. **[Ana]** These sit in this row and the adaptive-step row simultaneously.
- **ELM.** **[Lit]** An LLM diff model as the mutation operator inside MAP-Elites. **[Ana]** A *diff* model is a literal bounded-edit-script proposer — the concrete realization of assumption A2 of [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound).
- **ADAS, AFlow, AgentSquare, MaAS, Promptbreeder, EvoPrompt, DSPy, AIDE.** **[Lit]** Archive- or population-driven search over prompts, workflows, and module compositions. **[Ana]** All classified `[PAC: same-set]` in the audit table — the population machinery is real; the confirmation is not independent.
- **DGM.** **[Lit]** A coding agent rewrites its own codebase over an open-ended archive. **[Ana]** Large per-round $L$ — the regime where the confirmation slack $\eta_T$ grows fastest.
- **GEPA.** **[Lit]** Genetic-Pareto reflective optimizer. **[Ana]** One of the few in this row with independent confirmation.
- **CORAL.** **[Lit]** Coding agents in isolated worktrees around an external grader, retaining scored attempts. **[Ana]** Worktree isolation is a concrete implementation of the exact-rollback premise of [B-2](../README.md#ii3-acceptance-thresholds-and-exact-rollback).

**(c) Where the analogy breaks.**

- **[Ana]** **The mutation operator is not a known distribution.** In ES, the proposal distribution is explicit and its parameters are adapted from observed fitness — that is what makes convergence analysis possible. Here the mutation operator is an LLM conditioned on a prompt, an archive, and possibly traces. Its distribution is unknown, non-stationary (it changes when the prompt or the archive changes), and not characterized by any parameter the algorithm controls.
- **[Ana]** **Archive scores are usually same-set scores.** The selection signal comes from the same tasks that drive proposals. Classical ES assumes the fitness evaluation is an unbiased sample of the objective; repeated `argmax` over a fixed set is not. This is structurally identical to repeated leaderboard querying (Blum & Hardt, 2015), and the same defense applies — only act on significant improvements.
- **[Ana]** **The archive is a hypothesis class that must be counted.** Every candidate ever *evaluated* on the validation set enters the union bound of [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound), including rejected ones. A large population is therefore not statistically free: it purchases search coverage with confirmation slack. **[Ana]** This is a cost that the evolutionary-search literature does not usually account for.

---

### 3.10 Confirmation gate

**(a) Classical role — and its absence.** **[Ana]** Classical ZO has **no** acceptance step. The iterate moves wherever the estimator points; there is no notion of "rejecting" a step, because there is no persistent state to protect and no distinction between a trial and a commitment. The gate appears in HarnessOpt because **candidates are written to persistent state that affects all later rounds.** The nearest classical relatives are model-selection procedures and trust-region acceptance ratios, not ZO estimators.

**(b) Per-work notes.**

- **SkillOpt.** **[Lit]** A three-way disjoint split with the test set locked before final reporting; strict-improvement acceptance on held-out.
- **SkillOpt-Lite.** **[Lit]** Held-out selection with staged compile → smoke → full confirmation.
- **Self-Harness.** **[Lit]** Bidirectional held-in / held-out non-regression validation. **[Ana]** The closest published approximation to the four acceptance checks in [II.6](../README.md#ii6-stability--confirmation-audit-of-the-literature).
- **SkillForge.** **[Lit]** Candidate confirmation with rejection on failure.
- **CORAL.** **[Lit]** An external grader outside the agents' worktrees. **[Ana]** Structurally the correct placement for premise (iii): the measuring apparatus sits outside the editable surface.
- **[Lit]** By contrast, SkillCAT, SkillAdaptor, and Trace2Skill run gates on direct clones of the source training-failure instances or on sub-sampled training subsets — compromising the (B2) bound rather than satisfying it.

**(c) Where the analogy breaks.**

- **[Ana]** **It is not a ZO operator.** It is included in the table for completeness of the loop and to make the handoff to Axis II explicit. Treating it as "just another operator" invites the error of thinking a stronger gate is a *search* improvement; it is a *confirmation* improvement, and the two are not interchangeable.
- **[Ana]** **A gate that reuses its set across rounds is not the one-shot evaluation the classical form assumes.** The independence premise that makes a single held-out evaluation valid fails by round two. What remains valid is the reachable-set bound of [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound), which is weaker and $T$-dependent.
- **[Ana]** **The gate can be inside the search space.** In L3–L4 systems the evaluator and the evaluated live in the same repository. No classical model-selection procedure contemplates the candidate being able to edit the selector. **[Lit]** Observed behaviors in comparable settings include deleting logging to bypass detection functions and pre-seeding the environment to obtain reward without completing the actual flow.

---

## 4. Implementability depends on surface structure

**[Ana]** Section 3 established that most rows are analogies on a plain-text surface. This section states the condition under which each stops being an analogy. **This is the real dependency between [Axis 0](../README.md#axis-0--the-editable-surface-l0l5) and Axis I**, and the single most useful practical output of the ZO framing.

The pattern is uniform: **each operator requires one specific structural property from the editable surface.** When the surface supplies it, the operator becomes an implementable mechanism with the properties the classical analysis attributes to it. When it does not, the operator survives only as a role assignment.

| Operator | Requires the surface to provide | Structure absent (typical: plain-text artifact) | Structure present (typical: versioned executable code) |
|---|---|---|---|
| **Central difference** | **A constructible negative direction** | Only heuristic contrast at trace divergence points; $s - \mu u$ cannot actually be built, so neither the $f(s)$ cancellation nor the $O(\mu^2)$ bias reduction transfers | Feature toggles make on/off versions of one harness co-runnable in the same batch — $s - \mu u$ is a genuinely deployable state and the subtraction is a real paired comparison |
| **Coordinate descent** | **Objective block boundaries** | Text "coordinates" are not orthogonal; paragraph splits are arbitrary — it is block-coordinate descent with no objective definition of a block, and dimension $d$ is undefined | Import graph, interface signatures, module slots, and declared evolve regions give objective boundaries; intra-block edits and inter-block dependencies are statically decidable |
| **Control variate** | **Pairable replay** | The rejected buffer has no explicit random variate $c$, no known $\mathbb{E}[c]$, and no unbiased correction — variance reduction is unverifiable, and permanent rejection can itself introduce bias | Deterministic seeds plus version control make paired comparison real; common randomness genuinely cancels in the difference of two states on the same task |
| **Multi-point / mini-batch** | **Perturbations, not just resampled tasks** | What varies across the batch is the task $z_i$, not the perturbation $u_i$ — this estimates $f$ under task noise, not a directional derivative | **The same caveat holds.** Executable structure does not fix this one. The honest reading remains *variance reduction over $\mathcal{D}$* — which is what stability actually needs |
| **Trust region** | **A measurable behavioral distance** | Edit count is not a reliable semantic distance: one word can change behavior drastically; ten lines of commentary may change nothing. No agreement-based radius adaptation exists | Radius can use harder quantities: files touched, cross-module reach, interface-signature change, smoke pass rate. Allowlist = static trust region; dead-zone $\Delta$ = return-side trust region |

### 4.1 The conclusion that matters: this is not monotone in level

> **[Ana] It is not that "higher levels get stronger operators." It is that specific operators require specific structure from the editable surface.**

The distinction is not pedantic, and getting it wrong produces two concrete errors:

- **[Ana]** **Error 1 — inferring operator strength from level number.** An L3 harness-code system whose edits are unstructured whole-file rewrites, with no version control and no deterministic replay, supports *fewer* real operators than an L2 workflow system with declared module slots. Level says what can be changed; it does not say what structure the change surface exposes.
- **[Ana]** **Error 2 — assuming the property comes for free with code.** Executable code makes central difference and control variates *possible*; it does not make them *present*. Feature toggles must be built. Seeds must be fixed. Without those, a code surface has the same operator inventory as a text one, plus a compiler.
- **[Ana]** **The mini-batch row is the counterexample that proves the pattern.** It is the one row where executable structure does *not* repair the analogy, because the break is about what is being varied (tasks, not directions), which no amount of surface structure changes. It is worth keeping in the table precisely because it shows the diagnosis is per-operator, not a general "code is better" claim.

> **[Ana] This is why allowlists, feature toggles, and versioned rollback are not bolt-on safety measures.** They are the preconditions that make the corresponding operators implementable at all. And per [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound), they simultaneously tighten the confirmation bound — the same three mechanisms serve the search side and the statistical side, for independent reasons.

### 4.2 What a real text-space trust region should measure

> **[Rec]** A trust region that actually approximates behavioral distance should jointly account for, at minimum:
>
> | Quantity | What it captures |
> |---|---|
> | **Files changed** | Breadth of the edit across the artifact |
> | **Lines changed** | Volume of the edit — the description-length proxy that [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound) actually needs for $L$ |
> | **Modules crossed** | Whether the edit stayed within one block or spans dependencies |
> | **Behavioral-test diff** | Which tests changed outcome — the most direct behavioral measurement available |
> | **Tool-call distribution shift** | Whether the agent's action distribution moved, even where outcomes did not |
> | **Output distribution shift** | Whether responses changed character on tasks whose scores were unaffected |
>
> **[Rec]** Not merely a token cap or an edit-count cap. The last three are the ones that make the radius a *behavioral* distance rather than a *description* distance, and they are the ones current practice omits.

**[Ana]** Note that the last two quantities are measurable without any additional labels: both are computable from traces the system already collects. Their absence from current practice is not a data-availability problem.

---

## 5. The honest restatement of SkillOpt

**[Lit]** SkillOpt describes its mechanism with first-order vocabulary: learning rate, momentum, mini-batch. It reports mini-batch reflection at $B_m = 8$, a decaying edit budget $L_t: 4 \to 2$, a rejected-edit buffer, a slow cross-epoch update, and a three-way disjoint split with the test set locked before final reporting.

**[Ana]** Structurally, the algorithm is not stochastic gradient descent. It is closer to **a $(1{+}1)$-evolution strategy — a stochastic hill-climber — with a structured proposal operator.** The correspondence is exact enough to state term by term:

| SkillOpt's vocabulary | What the mechanism structurally is |
|---|---|
| Edit budget $L_t$ ("learning rate", decaying $4 \to 2$) | **Proposal radius** of the mutation operator, on a fixed decay schedule |
| Rejected-edit buffer ("negative control variate") | **Negative conditioning of the proposal distribution** — a filter on where the mutation operator may propose, not a variance-reducing correction ([§3.7](#37-control-variate)) |
| Slow update ("momentum") | A **low-frequency component across epochs** — a second, slower update channel, not an accumulated direction ([§3.8](#38-adaptive-step--momentum-row-added-by-this-list)) |
| Mini-batch $B_m = 8$ | **Variance reduction over $\mathcal{D}$**, i.e. $\beta_{\exp}$ control — not a multi-directional gradient estimate ([§3.3](#33-multi-point--mini-batch)) |
| Acceptance rule | **Strict-improvement-on-held-out** — the $(1{+}1)$ selection step: keep the offspring only if it beats the parent on the confirmation set |

**[Ana]** Under this reading, the loop is: propose one mutation within radius $L_t$, conditioned away from the rejected set; evaluate on held-out; keep if strictly better; otherwise revert and record the rejection. That is a $(1{+}1)$-ES with an LLM as the mutation operator and a statistical acceptance test as the selection operator. **[Lit]** CMA-ES (Hansen & Ostermeier, 2001) is the reference point for reading this family of methods as evolution strategies rather than as SGD.

### 5.1 Why this restatement does not weaken the method

**[Ana]** Three points, in order of importance:

1. **The mechanisms are unaffected by what they are called.** Mini-batch aggregation genuinely reduces single-sample sensitivity. A decaying edit budget genuinely bounds the reachable set. Held-out strict improvement is genuinely the strongest acceptance rule in the skill-optimization literature. None of that depends on the vocabulary.
2. **$(1{+}1)$-ES is a respectable algorithm with real theory.** Reclassifying a method from "SGD-like" to "ES-like" is not a demotion; it changes which body of analysis applies. **[Ana]** In particular, ES theory is where the useful questions live for this design: what is the success-probability target that should drive radius adaptation, and is a fixed $4 \to 2$ schedule the right answer to it? That question is invisible under the SGD reading.
3. **The correct classification predicts the correct failure modes.** Under the SGD reading, one expects the method to converge given enough steps and a small enough learning rate. Under the $(1{+}1)$-ES reading, one expects the known ES failure modes — premature convergence when the radius shrinks too fast, stagnation when the acceptance test is too noisy to distinguish offspring from parent — and both are checkable against reported behavior.

> **[Ana] The general point.** The ZO map's value is that it **organizes information structure**: what is queried, what is returned, what conditions the next proposal, what decides acceptance. Its value is *not* that it licenses treating these mechanisms as gradient-descent equivalents. When a paper's own vocabulary and its structure disagree, the structure is what determines which theory applies.

**[Rec]** This is a general reporting recommendation, not a criticism of one system: methods should state their selection rule (how many candidates are generated, how many survive) explicitly, since that single fact distinguishes $(1{+}1)$, $(\mu{+}\lambda)$, and population-based designs, and it determines the size of the reachable set $\mathcal{H}_T$ that [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound) must union-bound over.

---

## 6. The extra oracle tier: feasibility checks

**[Ana]** Classical ZO models exactly one oracle: submit a candidate, receive a (noisy) objective value. HarnessOpt has a **staged oracle whose tiers differ in cost by orders of magnitude**:

$$
\underbrace{\text{compile / type-check / static analysis}}_{\text{feasibility oracle: no task rollout; returns feasible / infeasible}}
\;\longrightarrow\;
\underbrace{\text{smoke test } (N \text{ small})}_{\text{cheap, high-variance estimate of } f_M}
\;\longrightarrow\;
\underbrace{\text{full validation}}_{\text{expensive, low-variance}}
$$

**[Lit]** SkillOpt-Lite implements exactly this staging as compile → smoke → full confirmation.

### 6.1 Consequence 1 — query allocation is not uniform across candidates

**[Ana]** Classical query-complexity accounting assumes fungible queries: $n$ queries cost $n$ units regardless of where they are spent. Here they do not. A candidate that fails to compile is eliminated for a cost that does not appear in the rollout budget at all; a candidate that runs and then fails consumes a full slot.

**[Ana]** Therefore the optimal allocation is **not** "split the rollout budget evenly across candidates." It is: generate a larger candidate set than the rollout budget could support, filter with the cheap tier, and spend rollouts only on survivors. This changes the shape of the search — it makes *proposing more candidates* cheaper than it appears under a flat query model, provided the cheap tier has real discriminating power.

**[Ana]** The corresponding hazard: the feasibility oracle filters on a *different criterion* than the objective. A candidate that compiles is not a candidate that helps. Over-reliance on the cheap tier biases the surviving set toward syntactic conservatism.

### 6.2 Consequence 2 — the form of the editable surface determines feasibility-oracle strength

> **[Ana] Executable code is checkable by a compiler and a type system. A natural-language artifact has no comparable pre-run feasibility criterion.**

**[Ana]** This is a structural search-efficiency advantage of code-level HarnessOpt over text-level skill optimization, and it is the actual reason for the compile → smoke → full ordering — not merely engineering caution. It also explains an empirical regularity: **[Lit]** evolutionary harnesses favor targets with fast automatable verifiers (KernelBench's `fast_p`, unit-test-scored program search), because those targets supply a strong cheap tier.

**[Ana]** What a text artifact can offer in place of a compiler is strictly weaker and should not be described as equivalent: schema validation, length limits, string-leak audits, and LLM-based self-review. The first three check form, not feasibility. The fourth is another rollout of the same model whose reliability is the thing in question — it is a *cheap noisy estimate*, belonging in the smoke tier, not a feasibility check.

**[Ana]** Note the interaction with [§4](#4-implementability-depends-on-surface-structure): this is a *second*, independent axis on which surface structure determines what the optimizer can do. Section 4 is about which search operators are implementable; this section is about which candidates can be rejected before paying for them. A surface can be strong on one and weak on the other.

### 6.3 A terminological prohibition

> **[Rec] Do not call this a "zero-cost oracle."** It is a **pre-run feasibility check**. It consumes compute — compilation, type inference, and static analysis are not free, and on large repositories they are not even cheap in wall-clock terms. What it does not consume is **task rollouts**.

**[Ana]** The distinction is not cosmetic. It matters in three places:

- **Budget reporting.** A system that reports "200 rollouts" while running 10,000 compilations has a compute cost that the rollout count does not represent. **[Rec]** Both should be reported.
- **Comparability.** Two systems with the same rollout budget are not comparably cheap if one spends a large multiple of the other's compute on filtering.
- **Transferability of the claim.** "Free filtering" would imply the advantage scales without limit. It does not: the filter tier has its own cost curve, and on large codebases it can become the bottleneck.

**[Ana]** Compatible with [Axis II](../README.md#ii6-stability--confirmation-audit-of-the-literature): safety probes can live in the smoke tier, far cheaper than full validation, which is what makes a joint (performance, safety) acceptance condition affordable rather than aspirational.

---

## 7. Evidence drift (D2): zeroth-order estimation is on-policy

### 7.1 The mechanism

**[Ana]** The evidence distribution sampled by $Q$ depends on the current state. Running the harness at $s_t$ produces trajectories generated *by* $s_t$; the failures that appear in $\mathcal{E}_t$ are the failures that $s_t$ still makes. Therefore:

> **[Ana] $\mathcal{E}_t$ is on-policy evidence, and the optimizer's information about the neighborhood of $s_t$ is a biased sample.**

Formally, the trajectory-generating distribution is $\tau \sim H_{s_t}(M, \cdot)$, so the evidence law $\mathcal{L}(\mathcal{E}_t)$ is indexed by $s_t$ and moves whenever $s_t$ moves. Nothing in the loop resamples evidence from states the optimizer has left behind.

### 7.2 The concrete failure mode

**[Ana]** The failure is specific and it is a failure of *retention*, not of *acquisition*:

1. At round $t$, a class of failures $F$ appears in $\mathcal{E}_t$. The optimizer adds a constraint $c_F$ to $s$ that prevents it.
2. At rounds $t+1, t+2, \dots$, $F$ no longer occurs — precisely because $c_F$ is working.
3. $F$ therefore stops appearing in the traces. The evidence that $c_F$ is necessary **disappears from the observable record as a direct consequence of $c_F$ succeeding.**
4. At some later round, $c_F$ looks like unmotivated clutter: it costs context, it constrains behavior, and nothing in the current evidence supports it. A compression pass, a simplification pass, or a proposer optimizing for brevity removes it.
5. $F$ returns.

**[Ana]** The structure of this failure is that **a successful constraint destroys its own justification**. This is not a bug in any particular proposer; it is a property of on-policy evidence collection. Any optimizer that proposes from current traces alone is exposed to it.

**[Ana]** It also interacts badly with the compression pressure that context and skill-library systems are under: the artifacts most likely to be deleted are exactly those whose value is invisible in current traces.

### 7.3 Homology and its limit

**[Ana]** This is **homologous to coverage deficiency in off-policy evaluation**: in both cases, the data-collecting policy determines which regions of the space are observed, and estimates about unobserved regions are unreliable no matter how much data is collected.

**[Ana]** But the homology has a precise limit, and stating it is the point:

| | Off-policy evaluation | Evidence drift in HarnessOpt |
|---|---|---|
| What is being estimated | The **value** of an alternative policy | Whether an existing **constraint is still needed** |
| What coverage deficiency breaks | The unbiasedness of the value estimate | The evidential basis for **retention** decisions |
| Standard remedy | Importance weighting, behavior-policy modelling, pessimism under uncertainty | No standard remedy; engineering mitigations only |

**[Ana]** Off-policy methods correct coverage deficiency by reweighting toward the target distribution, which requires knowing the behavior policy's density. Here there is no density and no reweighting; the affected decision is a discrete keep/delete choice about a constraint, not a numeric estimate that can be reweighted.

### 7.4 This is an estimator-bias problem, not a generalization-bound problem

**[Ana]** The classification matters and is frequently muddled. Two drifts are routinely conflated under "harness edits change the downstream distribution":

| | **D1 — Target distribution drift** | **D2 — Evidence distribution drift** *(this section)* |
|---|---|---|
| **What moves** | The task distribution itself, $z \sim \mathcal{D}_t$ | The trajectory-generating distribution, hence the law of $\mathcal{E}_t$ sampled by $Q$ |
| **What it breaks** | The *applicability object* of the generalization bound | The *unbiasedness* of the zeroth-order evidence |
| **Home** | [Axis II](../README.md#ii5-two-drifts-that-must-not-be-conflated) | Axis I (here) |
| **Treatment** | Standard: introduce a divergence $d(\mathcal{D}_{t-1}, \mathcal{D}_t)$ and accumulate it | Requires modelling $P$'s behavior; **no bound given** |

**[Ana]** D2 does not invalidate [bound B2](../README.md#ii1-two-single-round-bounds-and-their-division-of-labor) or [Proposition A](../README.md#ii2-multi-round-reuse-the-reachable-set-confirmation-bound). Those bounds are statements about a fixed validation set and a bounded reachable class; they hold whatever the proposer's evidence looks like. What D2 corrupts is the **input to the proposal step** — which candidates get generated at all, and specifically which existing constraints survive into the next candidate. A gate can only choose among the candidates it is offered; if the reverting candidate is the only one proposed and it happens to score acceptably on the validation set (because the validation set does not cover $F$ densely either), the gate will pass it.

**[Ana]** That last clause is the sharp version of the problem: **D2 and stratified-validation blindness ([Proposition C](../README.md#ii4-stratified-validation-average-non-regression-hides-tail-collapse)) compound.** The failure class whose evidence disappeared from traces is often a low-mass cluster whose regression is also invisible to an average-return gate.

### 7.5 Mitigations and the deliberate absence of a bound

**[Lit]** Current work mitigates D2 with engineering instruments: regression test suites, held-in sets retained across rounds, and milestone replay. **[Ana]** These work by making a slice of evidence collection *off-policy by construction* — the regression suite keeps running tasks that the current state no longer fails, which is exactly the coverage the on-policy loop loses. **[Rec]** Framed this way, the design rule is explicit: a regression suite should be populated by the failure classes that past constraints were introduced to fix, and each retained constraint should be linked to the test that justifies it.

> **[Ana] This document states D2 as an identified but unsolved mechanism and deliberately gives no bound.**

**[Ana]** The reason is specific, not a hedge. A bound on the retention failure would have to quantify the probability that the proposer $P$ removes a constraint whose supporting evidence is absent. That requires **modelling $P$'s behavior** — its sensitivity to evidence absence, its compression pressure, its conditioning on the current artifact. Any such model would rest on assumptions about an LLM proposer that are neither verifiable nor stable across models and prompts. **The assumptions would outweigh the conclusion**: the resulting bound would be a restatement of its own premises, and would give the appearance of a guarantee where the guarantee lives entirely in an unvalidated behavioral model. Stating the mechanism precisely and leaving it unbounded is the more honest position, and it is what this list does.

---

## 8. Cross-reference: which PAC quantity each operator moves

**[Ana]** This table is the bridge between the two axes. Axis I explains **how candidates are produced**; Axis II explains **under what conditions a candidate may be promoted to persistent state**. The operators are not neutral with respect to the second question: each one moves a specific quantity in a specific bound, and several move quantities in *opposite* directions.

| ZO operator | PAC quantity it moves | Direction and mechanism |
|---|---|---|
| **One-point estimate** | $\beta_{\exp}$ in **(B1)** | **Increases it.** One trace determines one edit, so removing a single training instance can change the output artifact substantially. **[Ana]** The archetypal high-$\beta_{\exp}$ design. |
| **Multi-point / mini-batch, consensus mining** | $\beta_{\exp}$ in **(B1)** | **Decreases it.** Requiring cross-task reproducibility means no single $z_i$ can determine the edit. **[Ana]** This is the statistical content of the mini-batch row and the reason [§3.3](#33-multi-point--mini-batch)'s broken analogy is nevertheless a good mechanism — it is variance reduction over $\mathcal{D}$, which is exactly what stability requires. |
| **Central difference** | $\beta_{\exp}$ in **(B1)**, weakly | **Ambiguous.** A single success/failure pair is still two episodes, so the contrast does not by itself aggregate over $\mathcal{D}$. **[Ana]** Contrast improves proposal *targeting*, not single-sample insensitivity; it should not be counted as a stability mechanism. |
| **Coordinate descent** | $L$, hence $l_{\mathrm{eff}} = T(L+1)$ in **Proposition A** | **Decreases it.** One block per round bounds the per-round edit description length, which is assumption A2. **[Ana]** Attribution and bound-tightness are served by the same restriction. |
| **Trust region** | **Two quantities at once:** (i) proposal variance; (ii) $l_{\mathrm{eff}} = T(L+1)$ in **Proposition A**; and via B-1, the required dead-zone $\Delta$ | **Decreases both.** Bounding the edit reduces how far one round can move the artifact, *and* it directly shrinks the reachable set $\mathcal{H}_T$ that the union bound ranges over. **[Ana]** This is the operator with the strongest dual role, and the justification via Proposition A is one that the trust-region literature in this space has not stated. **[Rec]** $L$ must be a description length (diff bytes), not an edit count. Note also B-1: relaxing $L$ requires raising $\Delta$ in step. |
| **Control variate (rejected buffer)** | Nothing in either bound, directly | **Neutral, with a caveat.** It changes the proposal distribution, not the estimator and not the hypothesis-class count. **[Ana]** Indirectly it can *reduce* $|\mathcal{H}_T|$ by preventing re-proposal of already-tested candidates — but only if rejected candidates are genuinely never re-evaluated. |
| **Control variate (paired replay)** | The variance of $\widehat{\Delta}_{V_m}$ | **Decreases it.** Common randomness cancels in the difference, so the same $m$ resolves a smaller true gap. **[Ana]** Only available where the surface supports deterministic replay ([§4](#4-implementability-depends-on-surface-structure)) — the one branch of this row with a real statistical payoff. |
| **Adaptive step / momentum** | $T$ and the candidate count per round, hence $\mathcal{H}_T$ | **Ambiguous.** Efficient scheduling can reach a good state in fewer rounds (smaller $T$, tighter $\eta_T$); aggressive exploration inflates the candidate count. **[Rec]** Schedule from the gated quantity $\widehat{\Delta}$ against a dead-zone, not from raw score movement, or the schedule adapts to noise. |
| **Population & archive** | $|\mathcal{H}_T|$ in **Proposition A** | **Increases it — this is the cost the evolutionary literature does not account for.** The union bound must cover **every candidate ever evaluated on $V_m$**, including rejected ones. A population of size $\lambda$ multiplies the per-round count. **[Ana]** Population buys search coverage and pays in confirmation slack. |
| **Confirmation gate** | **(B2)**, and the applicability of Proposition A / A′ | **This is the quantity.** An independent, unreused $V_m$ gives (B2) with $\beta_{\exp}$ removed entirely. Reuse across rounds voids premise (i) and demotes the reading to Proposition A with $\eta_T$ growing in $T$ and $L$; **[Lit]** rotation per round recovers a $\ln T$ dependence via Proposition A′. |
| **Feasibility oracle** ([§6](#6-the-extra-oracle-tier-feasibility-checks)) | Neither bound — it filters *before* the statistical budget is spent | **Strictly favorable, and structurally interesting.** Candidates eliminated at the compile tier are never evaluated on $V_m$, so they **do not enter $\mathcal{H}_T$** and do not consume confirmation budget. **[Ana]** This is the only mechanism in the list that increases search throughput without loosening any bound. |
| **Evidence drift D2** ([§7](#7-evidence-drift-d2-zeroth-order-estimation-is-on-policy)) | The *input* to the proposal step; interacts with **Proposition C** | **Not a bound quantity.** It corrupts which candidates are generated. **[Ana]** It compounds with stratified-validation blindness: the failure class whose evidence vanished is typically a low-mass cluster whose regression an average-return gate cannot see. |

### 8.1 Three readings of the table

**[Ana]** **(1) The two axes meet at the mini-batch row and the trust-region row, for different reasons.** Mini-batch's broken ZO analogy resolves into a clean Axis II mechanism ($\beta_{\exp}$). Trust region's broken ZO analogy resolves into *two* Axis II mechanisms (proposal variance and $l_{\mathrm{eff}}$). In both cases the operator is worth keeping despite the failed analogy — but the justification has to be restated in Axis II's terms, not asserted in Axis I's.

**[Ana]** **(2) Search strength and confirmation strength trade off, and the trade is usually invisible.** Population, larger candidate counts, and relaxed edit budgets all improve search and all loosen the confirmation bound. Systems that report only the search-side gain are reporting half a ledger. **[Rec]** The reportable pair is $(T, L, m, \text{candidates evaluated on } V_m)$ — the four numbers that determine $\eta_T$.

**[Ana]** **(3) The feasibility oracle is the only free lunch, and it is available only to some surfaces.** It filters candidates without touching either bound. Everything else in the table costs something somewhere. That asymmetry is the strongest structural argument for executable, checkable editable surfaces — stronger than the operator-implementability argument of [§4](#4-implementability-depends-on-surface-structure), because it requires no additional engineering beyond having a compiler.

---

## Related documents

| Document | Contents |
|---|---|
| [`../README.md`](../README.md) | The list itself; [Axis I](../README.md#axis-i--the-zeroth-order-view-of-harnessopt) is the condensed form of this document |
| [`pac-stability.md`](pac-stability.md) | Full statements and proofs of Propositions A, A′, B, B-1, B-2, C, with the assumption audit |
| [`audit-table.md`](audit-table.md) | Per-system stability/confirmation audit |
| [`glossary.md`](glossary.md) | All symbols and metric abbreviations |

**[Ana] A closing note on how to use this document.** The operator names are useful for organizing a literature that otherwise looks like a pile of unrelated heuristics. They are not a license to import the classical operators' guarantees. Every time a paper — including this list — writes "this is the trust-region role" or "this plays the control-variate role," the accompanying question should be: *which structure does the surface supply, and which property of the classical operator therefore actually transfers?* Section 4 is the checklist for answering it, and §8 is where the answer becomes a statement about a bound rather than a statement about an analogy.
