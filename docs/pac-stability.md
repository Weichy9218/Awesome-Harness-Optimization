# PAC / Stability Analysis of HarnessOpt

*Technical companion to [`README.md` § Axis II](../README.md#axis-ii--pac--stability-analysis-of-harnessopt). Self-contained: notation, the two single-round bounds, their premises and how each fails, the multi-round reachable-set results (Propositions A, A′, B, C) with full proofs, the assumption audit, the D1/D2 drift separation, and what is deliberately left unproved.*

**Sentence-type discipline.** Every substantive claim below carries exactly one tag:

- **[Lit]** — a factual claim attributable to a specific paper;
- **[Ana]** — this list's own analysis under a unified frame, *not* the original paper's claim;
- **[Rec]** — a recommendation or protocol proposal, phrased as such, never as a description of current practice.

**Derivation-risk statement, up front.** **[Ana]** Propositions A, A′, B and C use nothing beyond **Hoeffding / Chernoff concentration plus a union bound**. They are straightforward consequences of standard tools, and this note does not claim otherwise. Their value lies entirely in *what they are applied to* — the reachable set of an anchored, edit-budgeted, multi-round harness loop — and in the interpretation that follows (the $\sqrt{T}$ statistical cost of evolution rounds; $l_{\mathrm{eff}} = T(L+1)$; the coupling of $\Delta$ and $L$; the statistical necessity of exact rollback and of stratified validation). **The risk in this note is not in the proofs. It is concentrated in whether assumption A2 can be operationalized** — see [§9](#9-assumption-audit).

---

## Table of Contents

1. [Notation and setup](#1-notation-and-setup)
2. [The two single-round bounds](#2-the-two-single-round-bounds)
3. [The three premises of (B2) and how each fails](#3-the-three-premises-of-b2-and-how-each-fails-in-harnessopt)
4. [Reference point: STOP Lemma 1](#4-reference-point-stop-lemma-1)
5. [Proposition A — uniform confirmation under validation reuse](#5-proposition-a--uniform-confirmation-under-validation-reuse)
6. [Proposition A′ — validation rotation](#6-proposition-a--validation-rotation)
7. [Proposition B — acceptance threshold and exact rollback](#7-proposition-b--acceptance-threshold-and-exact-rollback)
8. [Proposition C — stratified validation and non-parametric forgetting](#8-proposition-c--stratified-validation-and-non-parametric-forgetting)
9. [Assumption audit](#9-assumption-audit)
10. [D1 vs D2 drift](#10-d1-vs-d2-drift)
11. [What is not proved here](#11-what-is-not-proved-here)
12. [Result-to-reporting map](#12-result-to-reporting-map)

---

## 1. Notation and setup

Fix a **base model $M$** for the entire analysis; nothing below permits weight updates. Tasks are drawn $z \sim \mathcal{D}$. The **editable state** is $s \in \mathcal{S}$ — model-external software state: prompts, structured context, memory, workflow graphs, tool interfaces, agent code, optimizer code. Edits are confined to an explicitly delimited subset $\mathcal{S}_{\mathrm{edit}} \subseteq \mathcal{S}$.

The harness executes a task as a trajectory

$$
\tau = H_s(M, z),
$$

with **bounded return** $R(\tau) \in [0,1]$. Define the per-task loss and the risk:

$$
\ell(s; z) = 1 - R\big(H_s(M,z)\big), \qquad
\epsilon(s) = \mathbb{E}_{z \sim \mathcal{D}}\big[\ell(s;z)\big].
$$

For a finite multiset of tasks $S$, write $\widehat{\epsilon}_S(s) = |S|^{-1}\sum_{z \in S}\ell(s;z)$ for the empirical risk and $\widehat{R}_S(s) = 1 - \widehat{\epsilon}_S(s)$ for the mean empirical return.

**The multi-round update loop** ($t = 0, \dots, T-1$) has three components and one write-back:

$$
\underbrace{\mathcal{E}_t = Q(s_t; D_t)}_{\text{collect evidence}}
\qquad
\underbrace{\tilde{s}_{t+1} = P(s_t, \mathcal{E}_t)}_{\text{propose edit}}
\qquad
\underbrace{s_{t+1} = G(s_t, \tilde{s}_{t+1}; V_t)}_{\text{gate: accept / reject / rollback}}
$$

Here $D_t$ are the tasks run to collect evidence in round $t$; $\mathcal{E}_t = \{(z_i, \tau_i, R_i, \mathrm{feedback}_i)\}$ is the evidence set; $\tilde{s}_{t+1}$ is the **candidate** (proposed, not yet persistent); $V_t$ is whatever data the gate consults; and $s_{t+1}$ is the state that persists into the next round. $V_m$ denotes a validation set of $m$ i.i.d. tasks from $\mathcal{D}$.

Two conventions matter for everything that follows.

- **[Ana]** *Rejected candidates are still evaluated states.* Any $\tilde{s}_{t+1}$ that the gate scored on validation data was measured, whether or not it was accepted. Union bounds must cover it.
- **[Ana]** *Acceptance is defined on a statistical dead-zone.* The gate writes back only when $\widehat{\Delta}_{V_m} := \widehat{R}_{V_m}(\tilde{s}_{t+1}) - \widehat{R}_{V_m}(s_t) > \Delta$ for a threshold $\Delta \ge 0$ (and any additional non-regression checks pass). $\Delta$ is treated in current practice as an empirical noise estimate; [§7](#7-proposition-b--acceptance-threshold-and-exact-rollback) gives it a sufficient value.

Symbols used repeatedly: $\Sigma$ is the alphabet over which edit scripts are written; $L$ the per-round edit budget; $\mathcal{H}_T$ the reachable set after $T$ rounds; $\eta_T$ the uniform confirmation slack (defined in [§5](#5-proposition-a--uniform-confirmation-under-validation-reuse)); $A_1,\dots,A_K$ a partition of the evaluation task family into capability clusters with masses $p_k$.

---

## 2. The two single-round bounds

A candidate that scores higher on tasks already observed is not thereby better on $\mathcal{D}$. Two distinct bounds address two distinct ways the inference can fail. Both are $T=1$, i.i.d., stationary.

### 2.1 (B1) Update side — algorithmic stability

Let $D_N = \{z_1,\dots,z_N\}$ be the training tasks, $\mathcal{A}$ the update algorithm (the composition of $Q$, evidence aggregation, and $P$), $s_D = \mathcal{A}(D_N)$, and $D_N^{\setminus i}$ the adjacent dataset with the $i$-th instance removed, $s_{D^{\setminus i}} = \mathcal{A}(D_N^{\setminus i})$.

> **Definition (Expected on-average stability).** $\mathcal{A}$ is $\beta_{\exp}$-stable in the expected on-average sense if
>
> $$\beta_{\exp} \;=\; \mathbb{E}_{D_N,\, i,\, z \sim \mathcal{D}}\Big[\big|\ell(s_D; z) - \ell(s_{D^{\setminus i}}; z)\big|\Big],$$
>
> equivalently in return form $\mathbb{E}\big|R(H(M,z,\mathcal{A}(D_N))) - R(H(M,z,\mathcal{A}(D_N^{\setminus i})))\big| \le \beta_{\exp}$. **[Lit]** *(The stability route to generalization is the standard one; SkillOpt-Lite § 2.2 instantiates it for skill libraries, citing the learnability-via-stability line of work.)*

> **(B1)** Under bounded loss and the corresponding stability condition, with probability $\ge 1-\delta$,
>
> $$\boxed{\;\epsilon(s_D) \;\le\; \widehat{\epsilon}_{D_N}(s_D) \;+\; O\!\left(\beta_{\exp} + \sqrt{\tfrac{\ln(1/\delta)}{N}}\right)\;}$$
>
> **[Lit]**

**What it governs.** **[Ana]** (B1) controls the gap from $\widehat{\epsilon}_{D_N}$ to $\epsilon$: *was the update process hijacked by a single rollout?* $\beta_{\exp}$ measures the sensitivity of the whole update pipeline to one episodic anomaly. Case-by-case hardcoded branches, mimicking environment variables unique to one failed trial, and conditioning on episode-specific strings all inflate $\beta_{\exp}$ and produce generalization collapse. **[Lit]** Practical frameworks push $\beta_{\exp}$ down by enforcing cross-task consensus: mini-batch aggregation of rollouts, batch ticket pools, and hierarchical parallel LLM tree reduction are three mechanisms aimed at this one quantity. **[Ana]** This is the statistical content of the multi-point / mini-batch row of the ZO operator table — the two axes of the list meet exactly here.

**One honesty caveat.** **[Ana]** What varies across a HarnessOpt "mini-batch" is the *task* $z_i$, not a perturbation direction $u_i$. So the batch estimates $f$ under task noise rather than a directional derivative. The honest reading is *variance reduction over $\mathcal{D}$* — which is precisely what stability, not gradient estimation, requires.

### 2.2 (B2) Confirmation side — independent validation

> **(B2)** If $V_m$ ($m$ i.i.d. tasks) is independent of both the training data and the proposal process, then for a **fixed** candidate $\tilde{s}$ not generated using $V_m$, with probability $\ge 1-\delta$,
>
> $$\boxed{\;\epsilon(\tilde{s}) \;\le\; \widehat{\epsilon}_{V_m}(\tilde{s}) \;+\; O\!\left(\sqrt{\tfrac{\ln(1/\delta)}{m}}\right)\;}$$
>
> **[Lit]** *(Standard model-selection bound over an independent validation sample, as invoked in SkillOpt-Lite § 2.2.)*

**What it governs.** **[Ana]** (B2) controls the gap from $\widehat{\epsilon}_{V_m}$ to $\epsilon$ for an already-frozen artifact: *does this specific candidate generalize?* However unstable $\mathcal{A}$ was, independent validation only asks how the final artifact behaves on unseen samples — $\beta_{\exp}$ is **completely removed** from the bound. That removal is the statistical dividend of having a validation protocol at all, and it is the reason a confirmation gate is not a formality.

### 2.3 Why they are not additive and not substitutable

**[Ana]** This subsection is the load-bearing one, and it does not depend on any result later in this document.

The two bounds control **different quantities along different paths**:

| | (B1) stability | (B2) independent confirmation |
|---|---|---|
| Controls the gap | $\widehat{\epsilon}_{D_N} \to \epsilon$ | $\widehat{\epsilon}_{V_m} \to \epsilon$ |
| Failure it prevents | one rollout hijacks the update | selection bias from repeated scoring |
| Object it constrains | the *algorithm* $\mathcal{A} = (Q, P)$ | a *fixed artifact* $\tilde{s}$ |
| Mechanism that improves it | consensus mining, batch aggregation, bounded edits | independent split, validation rotation, larger $m$ |
| Key premise | bounded loss, stability of $\mathcal{A}$ | $\tilde{s} \perp V_m$ |

Two consequences.

1. **Not additive.** They are not two terms of one decomposition to be summed. They are two separate inequalities, each valid on its own event, each bounding $\epsilon$ from a *different* empirical quantity. Writing $\epsilon \le \widehat{\epsilon} + \beta_{\exp} + \sqrt{\ln(1/\delta)/m}$ mixes empirical quantities measured on different samples and is not a theorem.

2. **Not substitutable.** An update process with tiny $\beta_{\exp}$ can still catastrophically overfit $V_m$ when the same $V_m$ is `argmax`-ed across many rounds — stability says nothing about repeated selection. Conversely, a perfectly rotated validation protocol does nothing to stop a proposer from writing an episode-specific hack into the state; it only ensures that the hack, once written, is measured honestly on fresh tasks.

> **[Ana]** Therefore **consensus mining (lowering $\beta_{\exp}$) and validation rotation (lowering selection bias) solve different problems and cannot replace each other.** The literature routinely files both under "improving generalization," which hides the split. **[Rec]** A paper claiming generalization should state *which* of the two it addressed, and should not present a stability mechanism as a substitute for an independent split, or vice versa.

---

## 3. The three premises of (B2), and how each fails in HarnessOpt

**[Ana]** (B2) is the bound HarnessOpt systems implicitly invoke when they report a held-out score. It rests on three premises, and HarnessOpt stresses each one in a different way. The multi-round loop breaks (i) mechanically; premise (ii) is structurally hard for semantic edits; premise (iii) is threatened by the defining feature of the setting.

| Premise | Content | How it fails in HarnessOpt |
|---|---|---|
| **(i) Independence** | $V_m$ is independent of the training data *and* of the proposal process | Fixed selection sets are repeatedly `argmax`-ed across rounds, so $\tilde{s}_{t+1}$ depends on $V$ through the accept/reject decisions of rounds $1..t$. When tasks are expensive, some systems skip an independent split entirely and substitute manual inspection plus string-leak audits — a defensible engineering trade-off, but **not** equivalent to independence, and the equivalence is rarely argued |
| **(ii) Bounded signal bias** | The bias of the evaluation signal relative to the quantity of interest is bounded | Compile-pass, a handful of smoke tests, or a visible test suite show that a candidate *runs*, not that it meets the specification. See [§3.1](#31-why-premise-ii-is-structurally-hardest-for-semantic-constraints) |
| **(iii) Evaluator outside $\mathcal{S}_{\mathrm{edit}}$** | The measuring apparatus is not part of what is being optimized | **Most fragile, for a structural reason: evaluator and evaluated live in the same repository.** See [§3.2](#32-why-premise-iii-is-structurally-fragile) |

### 3.1 Why premise (ii) is structurally hardest for semantic constraints

**[Ana]** The argument is not that automatic checking is currently immature. It is a selection argument, and it does not improve with tooling:

> Anything about the editable state that can be checked automatically has usually **already been made a gate** — turned into a compile step, a type check, a lint rule, a schema validation, a test. What therefore remains expressed only as a *declarative semantic constraint* in prompts, skills, or documentation is, almost by construction, **precisely the class of requirement that automatic checking cannot establish.**

Two corollaries follow.

- The residual constraint set is adversarially selected against the verifier. Measuring "constraint satisfaction" by the same automatic checks that already absorbed the checkable constraints measures the wrong subset.
- The agent's only self-verification signal is **task success**, and one whole class of declarative constraint exists specifically to prevent *fabricated* success evidence. Using task success to verify adherence to that class is circular.

**[Ana]** Consequently, for semantic modifications "bounded signal bias" is not a conservative modelling assumption — it is typically **false**, and the direction of the bias is optimistic. This is why (ii) deserves separate reporting rather than being folded into "we validated on held-out tasks."

### 3.2 Why premise (iii) is structurally fragile

**[Ana]** Existing self-evolution risk analyses generally assume the measuring apparatus sits outside the evolving surface. HarnessOpt's *defining feature* — that model-external software state, including harness and optimizer code, is editable — makes that assumption false by default. The evaluator, the task data, the logging, the permission configuration, and the code under optimization commonly live in **one repository, under one write authority.**

**[Lit]** Observed behaviors in self-modifying settings include deleting logging in order to bypass detection functions, and pre-seeding the environment to obtain reward without completing the actual task flow; goal hijacking is reported as more frequent when the detection function is *not* hidden from the agent.

**[Ana]** The operative distinction is therefore **declared vs enforced**: whether "the evaluator is read-only" is a prompt-level instruction or a runtime-enforced constraint (permissions, sandbox boundary, hidden evaluator, separate process/repo, path allowlist). A prompt-level declaration does not establish premise (iii); it merely expresses a preference to a system that is also the thing being optimized. **[Rec]** This should be a reported field, not an assumed property.

### 3.3 Attribution accuracy upper-bounds the post-hoc rollback route

**[Ana]** Premises (i)–(iii) all ask a single question: *is the measured improvement real?* A logically separate question is: *if a regression slips through, can it be detected and undone?* These are different instruments and should never be described interchangeably.

**[Lit]** Reported step-level failure-attribution accuracy sits in a low range; regression-prediction precision and recall are markedly below fix-prediction; and a substantial fraction of real regressions is never foreseen.

**[Ana]** Hence a "predict → check → roll back" strategy has a **safety ceiling set by attribution accuracy**: it cannot undo what it does not attribute. Pre-hoc gates (compile, sandbox, hiding the evaluator, permission boundaries) and post-hoc rollback are instruments of different strength. A system whose entire (B2) story is retrospective rollback should be read as *weaker* than one with a strictly disjoint held-out set, not as an equivalent alternative.

---

## 4. Reference point: STOP Lemma 1

**[Lit]** STOP (Zelikman et al., 2023; COLM 2024, Appendix A.2) proves a uniform-convergence bound on *improver programs*. Let $\Sigma$ be an alphabet and $\Sigma^{\le l}$ the set of programs of length at most $l$. Let $\hat{u}(I)$ be the empirical meta-utility of improver $I$ over $n$ i.i.d. tasks and $\bar{u}(I)$ its expectation. Then

$$
\Pr_{D \sim \mathcal{D}^n}\!\left[\forall I \in \Sigma^{\le l}:\ |\hat{u}(I) - \bar{u}(I)| < \epsilon\right] \;\ge\; 1 - \delta,
\qquad
\epsilon = \sqrt{\tfrac{1}{n}\left(l\ln|\Sigma| + \ln\tfrac{1}{\delta}\right)}.
$$

The proof is Chernoff plus a union bound over the $|\Sigma|^{l+1}$ programs of length $\le l$.

**[Ana]** Two structural features matter here.

1. **The union bound ranges over a static hypothesis class** — *all* programs of length $\le l$ — a class defined without reference to the search process. STOP does not exploit start-point information, because it does not assume improvement begins from a fixed program.
2. **The $l\ln|\Sigma|$ term grows with program size.** STOP itself does not discuss the dynamic implication, but if the improver grows over the course of evolution — and grow-and-refine is a common pattern — the bound loosens monotonically as the artifact accretes.

**[Ana] HarnessOpt has two things STOP does not, and they are exactly what turns feature 1 into exploitable structure:**

- **An anchored start $s_0$.** The Round-0 artifact is fixed before optimization begins, is an audit object, and is therefore necessarily known.
- **A per-round edit budget $L$.** This is the direct product of the trust-region / minimal-edit principle already present in the operator taxonomy (edit-budget decay, minimal-modification enforcement, bounded prefix length, allowlist path restriction). **[Lit]** *(These budget mechanisms are documented design choices of specific systems; treating them as statistical objects is **[Ana]**.)*

The next section replaces "all programs of length $\le l$" with "all states reachable from $s_0$ within $T$ rounds of $L$-bounded edits."

---

## 5. Proposition A — uniform confirmation under validation reuse

### 5.1 Assumptions and reachable-set counting

> **A1 (anchored start).** $s_0$ is fixed before optimization begins and does not depend on $V$.

> **A2 (bounded per-round edit).** There exists $L$ such that for every round $t$, the difference between the proposal $\tilde{s}_{t+1}$ and $s_t$ is describable by an **edit script of length $\le L$** over the alphabet $\Sigma$.

**[Ana]** Under A1–A2, the number of states reachable from $s_0$ in $t$ rounds is at most $|\Sigma|^{t(L+1)}$ (there are at most $\sum_{j\le L}|\Sigma|^j \le |\Sigma|^{L+1}$ distinct scripts per round, and rounds compose). Hence the set $\mathcal{H}_T$ of **all states ever proposed or tested** within $T$ rounds satisfies

$$
\ln|\mathcal{H}_T| \;\le\; T(L+1)\ln|\Sigma|.
$$

> **The count must cover rejected candidates.** A union bound has to cover *everything ever evaluated on $V_m$*, not only what was accepted. A protocol that proposes and scores $c$ candidates per round has $\mathcal{H}_T$ correspondingly larger; the counting above already permits this as long as every proposal is an $L$-bounded edit of the current state, since all such proposals live in the same reachable layer. **[Rec]** Papers should report candidates-per-round alongside $T$, because a reader cannot reconstruct the evaluated set from $T$ alone.

### 5.2 Statement and proof

> **Proposition A (uniform confirmation under validation reuse).** Let $V_m$ consist of $m$ i.i.d. tasks from $\mathcal{D}$, let the loss be bounded in $[0,1]$, and let A1–A2 hold. Then with probability at least $1-\delta$, simultaneously for all $s \in \mathcal{H}_T$,
>
> $$\boxed{\;\epsilon(s) \;\le\; \widehat{\epsilon}_{V_m}(s) \;+\; \sqrt{\frac{T(L+1)\ln|\Sigma| + \ln(1/\delta)}{2m}}\;}$$
>
> In particular it holds for the final state $s_T$, **without requiring $s_T \perp V_m$** — which is exactly what multi-round reuse needs.

*Proof.* Fix any $s \in \mathcal{S}$ not depending on $V_m$. The quantities $\ell(s;z_1),\dots,\ell(s;z_m)$ are i.i.d. and bounded in $[0,1]$ with mean $\epsilon(s)$, so Hoeffding's inequality gives

$$
\Pr\big[\,\widehat{\epsilon}_{V_m}(s) - \epsilon(s) \le -u\,\big] \;\le\; e^{-2mu^2},
\qquad
\Pr\big[\,|\widehat{\epsilon}_{V_m}(s) - \epsilon(s)| \ge u\,\big] \;\le\; 2e^{-2mu^2}.
$$

The set $\mathcal{H}_T$ is determined by $s_0$ and by the set of admissible edit scripts, both of which are fixed independently of $V_m$ under A1–A2. It is therefore a *fixed, $V_m$-independent* finite class, even though *which* element of it the run actually visits is $V_m$-dependent. Apply the one-sided Hoeffding bound with $u = \eta$ to each element and take a union bound over $|\mathcal{H}_T|$ elements:

$$
\Pr\big[\exists s \in \mathcal{H}_T:\ \epsilon(s) > \widehat{\epsilon}_{V_m}(s) + \eta\big] \;\le\; |\mathcal{H}_T|\, e^{-2m\eta^2}.
$$

Setting the right-hand side to $\delta$ gives $\eta = \sqrt{\big(\ln|\mathcal{H}_T| + \ln(1/\delta)\big)/(2m)}$, and substituting the count $\ln|\mathcal{H}_T| \le T(L+1)\ln|\Sigma|$ yields the claim. $\square$

**[Ana] Derivation risk.** Undergraduate-level: Hoeffding plus union bound, nothing more. The step that carries all the content is the *counting* step, and the counting step is only as good as assumption A2 — see [§9](#9-assumption-audit).

Write

$$
\eta_T \;:=\; \sqrt{\frac{T(L+1)\ln|\Sigma| + \ln(1/\delta)}{2m}}
$$

for the uniform slack. Three corollaries follow directly.

### 5.3 Corollary A-1 — $\sqrt{T}$ degradation

**[Ana]** The slack grows as $\sqrt{T}$. **Evolution rounds themselves consume statistical budget**: each round looks at the same validation set once more, and the reachable class grows accordingly.

This turns "evolution erodes its own generalization guarantee" from a qualitative remark into a statement with a definite rate, and supplies the *dynamic* version of STOP's static $l\ln|\Sigma|$ term: where STOP's bound loosens as the artifact grows, Proposition A's bound loosens as the *search* proceeds, whether or not the artifact grows.

### 5.4 Corollary A-2 — required validation-set growth

**[Ana]** To hold the slack below a target $\epsilon$ requires

$$
m \;\ge\; \frac{T(L+1)\ln|\Sigma| + \ln(1/\delta)}{2\epsilon^2}.
$$

Read the other way: **under a fixed validation set, the affordable number of evolution rounds scales linearly in $m$.**

**[Ana]** This collides with practice rather than describing it. Skill-optimization work reports high variance on small validation splits; harness work on expensive terminal benchmarks often declines to carve an independent split at all. Both sit in the small-$m$, non-small-$T$ regime, which is where the bound is weakest. **[Rec]** The consequence is not "the method is wrong" but "the reported held-out number does not carry the confirmation reading it is usually given"; $T$, $m$, and the reuse count must be reported for a reader to compute $\eta_T$ at all.

### 5.5 Corollary A-3 — the statistical role of the edit budget

Let $l_{\mathrm{eff}} := T(L+1)$. Proposition A has **the same form as STOP Lemma 1 with $l \to l_{\mathrm{eff}}$** (up to the constant in the exponent from the two-sided vs one-sided Hoeffding form). Therefore:

> **[Ana] Under an anchored start, what determines the tightness of the confirmation bound is not the program size of the harness, but the cumulative edit budget spent.**

Two consequences.

- **Strictly stronger than a program-space union bound when $T(L+1) < |s_T|$.** In that regime, counting the reachable set beats counting all programs of the artifact's length. A long-lived harness that is edited conservatively is *statistically cheaper to confirm* than a short one that is rewritten wholesale.
- **A previously unstated justification for trust-region / minimal-edit design.** **[Ana]** Bounded edits are usually motivated by proposal variance and review cost. Proposition A adds a second, independent reason: a smaller $L$ **directly tightens the confirmation bound**. Conversely, unbudgeted whole-file rewrites drive $L \approx |s|$ and collapse the bound back to STOP's magnitude, forfeiting the advantage of the anchored start entirely.

**[Ana]** Note that this also connects to the allowlist: restricting writes to whitelisted paths shrinks the set of admissible edit scripts and therefore shrinks $|\mathcal{H}_T|$ below the generic count. A tighter form — (number of writable paths) $\times$ (per-path diff-length bound) — is available in principle but is **not worked out here**; the generic bound is used throughout.

---

## 6. Proposition A′ — validation rotation

> **Proposition A′ (rotation reduces $T$ to $\ln T$).** Suppose round $t$ uses a **fresh** validation set $V^{(t)}$ with $|V^{(t)}| = m$, drawn i.i.d. from $\mathcal{D}$ and independent of all prior rounds and of the proposal process. Then applying (B2) per round with $\delta_t = \delta/T$ and union-bounding over rounds gives, with probability at least $1-\delta$, simultaneously for all $t$,
>
> $$\boxed{\;\epsilon(\tilde{s}_{t+1}) \;\le\; \widehat{\epsilon}_{V^{(t)}}(\tilde{s}_{t+1}) \;+\; \sqrt{\frac{\ln T + \ln(1/\delta)}{2m}}\;}$$

*Proof.* Fix $t$. By construction $\tilde{s}_{t+1}$ is a function of $s_0$, the evidence sets, and the gate decisions of rounds $1..t$ — all of which are independent of $V^{(t)}$. Conditioning on that history, $\tilde{s}_{t+1}$ is a fixed state and Hoeffding applies to the $m$ i.i.d. losses in $V^{(t)}$, giving failure probability at most $e^{-2m\eta^2}$ for slack $\eta$. Set $\eta = \sqrt{(\ln T + \ln(1/\delta))/(2m)}$, so each round's failure probability is at most $\delta/T$; union-bound over the $T$ rounds. $\square$

**[Ana]** The dependence on $T$ drops from **linear inside the square root** to **logarithmic**: $\sqrt{T(L+1)\ln|\Sigma|}$ becomes $\sqrt{\ln T}$, and the $L$ and $\ln|\Sigma|$ factors disappear entirely, because independence removes the need to count the reachable set at all. The cost is total task consumption $Tm$ instead of $m$.

**[Ana]** Note what rotation does *not* buy: A′ bounds each $\tilde{s}_{t+1}$ against *its own* round's fresh set. It does not by itself give a bound for $s_T$ against a single reused set, and it does not remove the need for the acceptance analysis in [§7](#7-proposition-b--acceptance-threshold-and-exact-rollback) — it changes which slack enters that analysis.

### The design rule

> **[Rec] This is the most actionable product of the analysis.** It converts "rotate your validation set" from a vague good habit into a design rule with a quantified payoff.

Comparing slacks at equal $\delta$: reuse costs $\eta_T \propto \sqrt{T(L+1)\ln|\Sigma| + \ln(1/\delta)}$, rotation costs $\propto \sqrt{\ln T + \ln(1/\delta)}$. To match rotation's slack by enlarging a reused set instead, $m$ must grow by roughly the ratio of the numerators — of order $T/\ln T$ in the $T$-dependence. Equivalently, in units of slack per task:

> **[Rec] If the marginal cost of acquiring fresh tasks is below $\sqrt{T/\ln T}$ times the marginal cost of enlarging the validation set, rotate rather than enlarge.**

**[Ana]** Most current work reuses a fixed selection set, so this is a directly available protocol improvement rather than a description of practice. **[Rec]** Where fresh tasks are genuinely unobtainable (expensive terminal benchmarks, human-scored tasks), the honest fallback is to report the reuse count and the resulting $\eta_T$, not to present a reused-set score as independent confirmation.

---

## 7. Proposition B — acceptance threshold and exact rollback

Proposition A supplies a *sufficient* value for the statistical dead-zone $\Delta$.

> **Proposition B (accepted improvements are real).** Let $\eta_T := \sqrt{\dfrac{T(L+1)\ln|\Sigma| + \ln(1/\delta)}{2m}}$ as above. If the acceptance criterion requires $\widehat{\Delta}_{V_m} > \Delta$ with $\Delta > 2\eta_T$, then with probability at least $1-\delta$, **every** accepted update satisfies $\epsilon(s_{t+1}) < \epsilon(s_t)$.

*Proof.* Work on the uniform event of Proposition A (in its two-sided form, which costs only the constant already absorbed in $\eta_T$'s definition of $\delta$): simultaneously for all $s \in \mathcal{H}_T$, $|\widehat{\epsilon}_{V_m}(s) - \epsilon(s)| \le \eta_T$. Both $s_t$ and $\tilde{s}_{t+1}$ lie in $\mathcal{H}_T$. Hence

$$
\epsilon(s_t) - \epsilon(\tilde{s}_{t+1})
\;\ge\; \big(\widehat{\epsilon}_{V_m}(s_t) - \widehat{\epsilon}_{V_m}(\tilde{s}_{t+1})\big) - 2\eta_T
\;=\; \widehat{\Delta}_{V_m} - 2\eta_T
\;>\; \Delta - 2\eta_T \;>\; 0,
$$

using $\widehat{\Delta}_{V_m} = \widehat{R}_{V_m}(\tilde{s}_{t+1}) - \widehat{R}_{V_m}(s_t) = \widehat{\epsilon}_{V_m}(s_t) - \widehat{\epsilon}_{V_m}(\tilde{s}_{t+1})$. Since acceptance sets $s_{t+1} = \tilde{s}_{t+1}$, we get $\epsilon(s_{t+1}) < \epsilon(s_t)$. All accepted rounds are covered simultaneously because the event of Proposition A is uniform over $\mathcal{H}_T$. $\square$

### Corollary B-1 — $\Delta$ and $L$ are coupled knobs, not independent ones

**[Ana]** The sufficient lower bound $2\eta_T$ is monotonically increasing in $L$ (and in $T$, and decreasing in $m$). Therefore **relaxing the edit budget requires raising the acceptance threshold in step, or the gate loses its meaning.**

Current practice treats $\Delta$ as an empirical estimate of run-to-run noise and $L$ as a proposal-quality / reviewability control, tuned independently and often by different considerations. **[Ana]** Proposition B says that is inconsistent: $\Delta$ calibrated to noise alone under-corrects for the selection bias induced by a large reachable set. **[Rec]** Report $\Delta$ *together with* whether it was set relative to $\eta_T$ — a $\Delta$ chosen without reference to $T$, $L$, and $m$ cannot support a "the accepted change is a real improvement" claim.

### Corollary B-2 — monotone improvement requires behaviorally exact rollback

Proposition B guarantees only that *accepted* updates truly improve. To conclude the trajectory-level statement $\epsilon(s_T) \le \epsilon(s_0)$, one additionally needs rejected proposals to leave **no residue**:

> If, after the gate rejects $\tilde{s}_{t+1}$, the equality $s_{t+1} = s_t$ holds **behaviorally and strictly**, then within the same $1-\delta$ event the risk sequence is monotone non-increasing:
> $$\epsilon(s_0) \;\ge\; \epsilon(s_1) \;\ge\; \cdots \;\ge\; \epsilon(s_T).$$

*Proof.* Each round is either accepted — strict decrease by Proposition B — or rejected, in which case $s_{t+1} = s_t$ behaviorally, so $\epsilon(s_{t+1}) = \epsilon(s_t)$ because $\epsilon$ is a functional of behavior alone. Chain over $t = 0,\dots,T-1$ inside the single uniform event. $\square$

> **[Ana] This promotes a systems property into a theorem premise.** "Rollback restores the state exactly" is not an engineering-tidiness concern — it is a **necessary condition for the monotonicity conclusion**. Uncleaned side effects (lingering processes, registry or plugin entries, cache files, already-written memory entries, mutated external resources) make $s_{t+1} \ne s_t$ behaviorally, and the chaining step fails at that round. Nothing in Proposition B repairs it: the accepted-improvement guarantee survives, but the trajectory-level claim does not.

**[Ana]** Two practical readings follow. First, this is the statistical counterpart of the **revertible-effects / temporal-composability** requirement discussed for component lifecycles: undo-on-unload is a premise of the non-regression theorem, not a feature. Second, **a `git` rollback that does not cover runtime side effects is insufficient** — version control restores the file tree, not the process table, the caches, or written memory. **[Rec]** Rollback exactness should be *evidenced* (a rejected candidate leaves no residual process, registry entry, cache file, or memory entry), not asserted.

---

## 8. Proposition C — stratified validation and non-parametric forgetting

### 8.1 The average criterion is blind to tail clusters

Propositions A and B give non-regression **in the average sense only**: $\epsilon$ is an expectation over $\mathcal{D}$, and $V_m$ is drawn i.i.d. from $\mathcal{D}$. Partition the evaluation task family into capability clusters $A_1,\dots,A_K$ (by capability, domain, or tool dependence), with $p_k = \Pr_{z\sim\mathcal{D}}[z \in A_k]$.

**[Ana]** A degradation confined to $A_k$ contributes at most $p_k \cdot (\text{intra-cluster degradation})$ to the average risk. So as long as the intra-cluster degradation stays below $\eta_T/p_k$, its effect on the average is within the slack the gate cannot resolve — it is **entirely invisible** to an average-return acceptance criterion.

> **Proposition C (stratified validation is necessary).** Under an i.i.d. validation set with an average-return acceptance criterion, one cannot rule out intra-cluster degradation of magnitude up to $O(\eta_T / p_k)$ for a cluster of probability mass $p_k$. To obtain an $\epsilon_k$-level guarantee **per cluster**, each cluster requires independent sampling with
>
> $$\boxed{\;m_k \;=\; \Omega\!\left(\frac{T(L+1)\ln|\Sigma| + \ln(K/\delta)}{\epsilon_k^{2}}\right)\;}$$

*Proof.* For the second claim: apply Proposition A separately to each cluster, replacing $\mathcal{D}$ by the conditional distribution $\mathcal{D}(\cdot \mid A_k)$, $\epsilon$ by the per-cluster risk $\epsilon_k$, and $V_m$ by an independent per-cluster sample $V^{(k)}$ of size $m_k$. Each application uses confidence parameter $\delta/K$, contributing $\ln(K/\delta)$ in place of $\ln(1/\delta)$; the reachable-set count $\ln|\mathcal{H}_T| \le T(L+1)\ln|\Sigma|$ is unchanged, since it is a property of the search, not of the evaluation distribution. Union-bounding over the $K$ clusters gives simultaneous validity with probability $\ge 1-\delta$, and requiring each per-cluster slack below $\epsilon_k$ gives the stated $m_k$. For the first claim: the average-criterion sensitivity to a cluster-local change is scaled by $p_k$, so a change of magnitude $\eta_T/p_k$ inside $A_k$ perturbs the average by $\eta_T$ — at the resolution limit of the uniform bound. $\square$

> **[Ana] Tail capabilities (small $p_k$) are statistically invisible under an average criterion.** This explains how "aggregate score rises while individual milestones are permanently lost" can occur **without violating any bound in force** — the phenomenon is consistent with Propositions A and B, which is exactly why observing it does not falsify them and why relying on them alone is unsafe.

> **[Rec]** Non-regression suites must be **stratified and reported per cluster**, not merged into the main validation set and averaged. Merging a small milestone suite into a large validation set converts a detectable regression into an undetectable one.

**[Ana]** Note the cost structure: $m_k$ does *not* shrink with $p_k$. Per-cluster confirmation requires per-cluster sample sizes independent of how rare the cluster is under $\mathcal{D}$ — which is precisely why tail coverage is expensive and why it is usually skipped.

### 8.2 Forgetting in a non-parametric setting

With no weights to speak of, forgetting can only be defined on task-set performance. **[Ana]** A candidate definition, over the same clusters:

$$
\mathrm{FGT}_T \;=\; \frac{1}{K}\sum_{k=1}^{K}\Big[\max_{t \le T}\widehat{R}_{A_k}(s_t) \;-\; \widehat{R}_{A_k}(s_T)\Big]_+ .
$$

**This is a candidate definition, not a settled one.** **[Ana]** It is offered here to make the stratified-reporting requirement executable, and it inherits every measurement caveat of $\widehat{R}$ (finite $m_k$, run-to-run variance, cluster partition choice). It should not be cited as an established metric of this setting.

**[Ana] The substantive difference from the continual-learning literature.** Formally this matches FGT as used in CL. But CL forgetting arises from **parameter overwriting** — diffuse, non-localized, and in general not attributable to an identifiable cause. Here forgetting arises from an **explicit edit**, and is therefore *in principle* attributable to a specific diff. That attributability is a genuine advantage of the non-parametric setting and should be exploited rather than discarded by importing CL metrics unchanged:

- **Attributable forgetting** — the regression can be traced to a specific accepted diff, which can be reverted or narrowed.
- **Non-attributable forgetting** — the regression is present but no single diff accounts for it (interaction effects, drift, evidence-distribution effects per [§10](#10-d1-vs-d2-drift)).

**[Rec]** Report the split, not just the aggregate. **[Ana]** The caveat from [§3.3](#33-attribution-accuracy-upper-bounds-the-post-hoc-rollback-route) applies with full force: *in principle attributable* is not *in practice attributed*, and reported attribution accuracy is the ceiling on how much of the first category can actually be recovered. This is also where the distinction from parametric-CL FGT/BWT definitions should be drawn explicitly rather than assumed away.

---

## 9. Assumption audit

**[Ana]** This section is where the honest risk sits. The proofs are routine; the assumptions are not.

### A1 — anchored start

**Status: holds naturally in HarnessOpt, with one specific failure mode.**

The Round-0 artifact is produced before the optimization loop, is typically an audit object, and usually requires human approval — so it is fixed, and known. **[Ana]** A1 fails if **Round-0 itself consumed tasks that are later used for confirmation**: then $s_0$ depends on $V$, the reachable set is no longer $V_m$-independent, and the union-bound argument of Proposition A does not go through as stated.

**[Rec]** "Did Round-0 consume tasks later used for confirmation?" should be an explicitly reported field. It is cheap to report and it decides whether Proposition A applies at all.

### A2 — bounded per-round edit (the genuine weak point)

**Status: measurable in principle, frequently mis-operationalized, and inapplicable in one important case.**

Three separate issues.

1. **Description length, not edit count.** Edit-script length is measurable — diff size is the obvious proxy. But "$\le L$ edits" is **not** "edit script of length $\le L$": a small number of edits can insert a great deal of code. A single edit that pastes a 400-line module is one edit and a very long script. **[Rec] If Proposition A (or B, or C, all of which carry $\eta_T$) is cited, $L$ must be defined as the *description length* of the edit — e.g. diff bytes — and not as an edit count.** A paper reporting only "edit budget $L_t: 4 \to 2$" has not reported the quantity the proposition needs.

2. **Allowlists tighten the count.** Restricting writes to whitelisted paths shrinks the admissible edit-script set, so the true $\ln|\mathcal{H}_T|$ is smaller than the generic $T(L+1)\ln|\Sigma|$. **[Ana]** This is a strengthening, not a threat — but the tighter form (writable-path count $\times$ per-path diff-length bound) is *not* derived in this note; the generic bound is used throughout and should be read as conservative.

3. **Out of scope: unbounded external content.** **[Ana]** The counting assumes the edit is described by a script of bounded length. If $P$ can invoke external retrieval and write **arbitrarily long content** into the state — pulling code from the internet into the harness, importing a large external artifact, materializing a retrieved document as a skill file — then $L$ is effectively unbounded and $\ln|\mathcal{H}_T|$ is not controlled by $T(L+1)\ln|\Sigma|$. **Proposition A does not apply to such systems.** **[Rec]** This case should be excluded explicitly when citing the proposition, not passed over silently.

> **[Ana] Summary of derivation risk.** The proofs of A, A′, B, C are Hoeffding/Chernoff plus a union bound and carry essentially no derivation risk. **All of the risk is in A2's operationalizability**: whether a real system's per-round edit admits a defensible bounded description length, and whether the reported $L$ is that quantity rather than an edit count.

### Bounded loss and i.i.d. sampling

**[Ana]** $R \in [0,1]$ and i.i.d. draws from $\mathcal{D}$ are the **same** assumptions already carried by (B1) and (B2). They add no new burden relative to the single-round bounds a paper is already implicitly invoking when it reports a held-out number. Two notes:

- Bounded loss is what licenses Hoeffding; an unbounded or heavy-tailed return metric requires a different concentration inequality and the constants change.
- I.i.d. sampling is broken by D1 drift — treated separately in [§10](#10-d1-vs-d2-drift), where the correction is additive and standard.

---

## 10. D1 vs D2 drift

**[Ana]** "Harness edits change the downstream behavior distribution" is repeated often in this literature and formalized rarely. It conflates two mechanisms with different mathematical homes, and conflating them produces wrong statements in both directions.

| | **D1 — Target distribution drift** | **D2 — Evidence distribution drift** |
|---|---|---|
| **What moves** | The task distribution itself: $z \sim \mathcal{D}_t$ | The trajectory-generating distribution, hence the distribution of evidence $\mathcal{E}_t$ collected by $Q$ |
| **Caused by** | The deployment environment, task mix, user population, or benchmark refresh | The harness edit itself: $s_t$ changes which trajectories occur |
| **What it breaks** | The **applicability object** of the generalization bound — $\epsilon_{\mathcal{D}_T}$ is not what $V_m \sim \mathcal{D}_0$ estimates | The **unbiasedness** of the zeroth-order estimate — $\mathcal{E}_t$ is on-policy evidence about $s_t$'s neighborhood |
| **Home** | This document (PAC / Axis II) | The ZO chapter (Axis I.5) |
| **Treatment** | Standard: introduce a divergence $d(\mathcal{D}_{t-1},\mathcal{D}_t)$ (TV, $\mathcal{H}$-divergence, or discrepancy) and accumulate | Requires modeling $P$'s behavior; **this note deliberately gives no bound** |
| **Status here** | Technically routine; stated for completeness | Identified mechanism, unsolved, no bound offered |

### D1 — the accumulated form

**[Ana]** With a divergence $d$ between adjacent task distributions, the natural accumulated statement is

$$
\epsilon_{\mathcal{D}_T}(s_T) \;\le\; \widehat{\epsilon}_{V_m}(s_T) \;+\; \eta_T \;+\; \sum_{t=1}^{T} d(\mathcal{D}_{t-1}, \mathcal{D}_t).
$$

Technically this is routine — the drift term is standard domain-adaptation bookkeeping and nothing here is new. But it has a specific consequence for HarnessOpt:

> **[Ana] The drift term accumulates *linearly* in $T$, while $\eta_T$ grows only as $\sqrt{T}$. On a long enough horizon, drift — not selection bias — becomes the dominant error term.**

**[Rec]** This yields a checkable criterion for a decision that is currently made by intuition: **when to re-run Round-0 from scratch instead of continuing incremental evolution.** Past the crossover where $\sum_t d(\mathcal{D}_{t-1},\mathcal{D}_t)$ exceeds $\eta_T$, additional rounds of incremental evolution are optimizing against an increasingly stale distribution, and re-anchoring on fresh $s_0$ and fresh data dominates. Locating that crossover empirically is a concrete experiment, not a theoretical exercise — see [§11](#11-what-is-not-proved-here).

### D2 — why no bound is given

**[Ana]** Harness modifications change the trajectory distribution, so the evidence $\mathcal{E}_t$ that $Q$ samples depends on $s_t$. The optimizer's information about the neighborhood of $s_t$ is therefore a **biased sample**. The characteristic failure mode: once a class of failure is fixed, it stops appearing in later traces; the optimizer thereby loses the evidence that the constraint is still necessary, and may **revert it in a later round**.

This is homologous to coverage deficiency in off-policy evaluation, but it acts on **constraint retention**, not on value estimation. **[Ana]** Its correct home is the ZO chapter: it is a bias problem of the zeroth-order estimator, **not** a generalization-bound problem, and filing it under PAC produces category errors (e.g. attempting to fix it with a larger validation set, which does not touch the mechanism).

**[Ana] This note deliberately gives no bound for D2.** Any bound would require modeling $P$'s behavior — how a language-model proposer weighs absent evidence against retained constraints — and the assumptions required would outweigh the conclusion obtained. Current work mitigates D2 with engineering: regression suites, held-in sets, milestone replay. Stating the mechanism as identified-and-unsolved is the honest position.

---

## 11. What is *not* proved here

**[Ana]** Listed in rough order of tractability. None of these should be cited as results.

1. **Tighter multi-round reuse than the union bound.** Proposition A pays $\sqrt{T}$ because it counts the reachable set crudely. Adaptive data analysis — differential-privacy-based reusable holdout, Thresholdout, and related mechanisms — may give a better $T$-dependence for adaptively chosen queries. **Open questions:** at what accuracy cost, under what assumptions on $P$, and whether the accuracy loss from the privacy mechanism is acceptable when each "query" is an expensive rollout batch rather than a cheap statistic. **Not resolved here; no claim is made about whether the $T$-dependence can in fact be improved in this setting.**

2. **An operational definition of the cluster partition.** Proposition C requires clusters $A_1,\dots,A_K$ and their masses $p_k$. "Report per cluster" is **unexecutable** without a defensible way to partition capabilities — one that is stable across rounds, not chosen after seeing which clusters regressed, and not so fine that $K$ inflates $\ln(K/\delta)$ and the per-cluster $m_k$ budget beyond feasibility. No such definition is offered here.

3. **A bound for evidence drift (D2).** See [§10](#10-d1-vs-d2-drift). **[Ana]** A weaker, assumption-light formulation might be possible — for instance, bounding how far a constraint's supporting evidence can decay before the constraint is at risk of reversion — but this note does not have one.

4. **Quantifying the stability–plasticity trade-off.** Intuitively, smaller $L$ means less forgetting but slower improvement, and Propositions A/A-3 give only the *statistical* half (smaller $L$ tightens the bound), not the improvement half. Turning the trade-off into a proposition requires an assumption on the **behavioral reach of an edit** — an upper bound on how much of the harness's behavior an $L$-length diff can alter. **No defensible assumption of that form is currently available**, so this is deferred rather than sketched.

5. **Merging independently evolved lineages.** **[Ana]** The reachable-set count of Proposition A **fails outright** when two independently evolved lineages are merged: the merged state lies in **neither lineage's reachable set**, so $\ln|\mathcal{H}_T| \le T(L+1)\ln|\Sigma|$ no longer covers what was evaluated, and the union bound is void. This is therefore not merely an engineering problem of structural alignment — it is a genuine theoretical gap. Whether local per-round diffs suffice to predict merged behavior, and whether full re-confirmation of the merged artifact is required, are both open. **Stated as an open problem; no attempt to solve it is made here.**

---

## 12. Result-to-reporting map

**[Rec]** Each result below is applicable to a published system **only if** the corresponding fields are reported. A paper missing them cannot be placed on the audit table; the bound is not "approximately applicable" in its absence, it is uncomputable.

| Result | What it gives | Fields a paper must report for it to apply |
|---|---|---|
| **(B1)** stability | Bound from $\widehat{\epsilon}_{D_N}$ to $\epsilon$; removes nothing about selection | Update algorithm $\mathcal{A}$ (how $Q$, aggregation and $P$ compose); whether edits rest on cross-task consensus or a single trajectory; training task count $N$ |
| **(B2)** independent confirmation | Bound from $\widehat{\epsilon}_{V_m}$ to $\epsilon$ for a fixed candidate; removes $\beta_{\exp}$ | Train / selection / test split with task counts; **what data the proposer could see**; whether the split is strictly disjoint or a substitute leak audit |
| **Premise (iii)** | Whether the measurement is trustworthy at all | Whether evaluator / task data / protected paths are read-only by **runtime enforcement** or by **prompt declaration** |
| **Proposition A** | Uniform confirmation under reuse; $\eta_T$ | $T$ (rounds), candidates per round, **validation-set reuse count**, $m$, $\delta$, and $L$ **as diff description length**; whether Round-0 consumed confirmation tasks (A1); whether $P$ can write unbounded retrieved content (A2 scope) |
| **A-2** | Required $m$ for target slack $\epsilon$ | Same as A, plus the target $\epsilon$ the authors consider meaningful |
| **A-3** ($l_{\mathrm{eff}}$) | Edit budget, not artifact size, controls tightness | $T(L+1)$ and $|s_T|$, so a reader can check whether $T(L+1) < |s_T|$ |
| **Proposition A′** | $\ln T$ slack instead of $\sqrt{T(L+1)\ln\vert\Sigma\vert}$ | Whether the validation set is **rotated** per round and drawn independently; per-round $m$; total task consumption $Tm$ |
| **Proposition B** | Accepted updates truly improve | The dead-zone $\Delta$, **and whether it was set relative to $\eta_T$** rather than to run-to-run noise alone |
| **B-1** | $\Delta$–$L$ coupling | $\Delta$ and $L$ reported jointly, with the tuning rationale for each |
| **B-2** | Monotone $\epsilon(s_0) \ge \cdots \ge \epsilon(s_T)$ | **Rollback-exactness evidence**: a rejected candidate leaves no residual process, registry entry, cache file, or written memory entry — behavioral, not just `git`-level |
| **Proposition C** | Per-cluster non-regression | Cluster partition and its definition; per-cluster $m_k$; **stratified** non-regression results reported per cluster, not merged into the average; $K$ |
| **FGT (candidate)** | Non-parametric forgetting | Per-cluster return curve $\widehat{R}_{A_k}(s_t)$ over $t$; forgetting attributed to specific diffs where possible, with the attributable / non-attributable split |
| **D1 drift** | When to restart Round-0 | Whether $\mathcal{D}$ changed across rounds; deployment horizon; any measured divergence between round distributions |
| **D2 drift** | Nothing — mechanism only | Regression suites / held-in sets / milestone replay used as mitigations, reported as mitigations rather than as solutions |

---

## Cross-references

- [`README.md` § Axis II](../README.md#axis-ii--pac--stability-analysis-of-harnessopt) — the condensed version of this analysis, plus the literature audit table.
- [`README.md` § Axis I.5](../README.md#i5-evidence-drift-zo-estimation-is-on-policy) — evidence drift (D2), where it belongs.
- [`README.md` § Reporting Checklist](../README.md#reporting-checklist) — the 🔑 fields correspond to the right-hand column of [§12](#12-result-to-reporting-map).
- [`README.md` § Open Problems](../README.md#open-problems) — the items of [§11](#11-what-is-not-proved-here) in list form.

---

**Provenance note.** **[Ana]** The two single-round bounds (B1)/(B2) and the $\beta_{\exp}$ definition are restated from the skill-optimization analysis they come from; STOP Lemma 1 is restated from its source. **[Ana]** Propositions A, A′, B, B-1, B-2 and C, the $l_{\mathrm{eff}}$ formulation, the D1/D2 separation, and the reporting map are this list's analysis under a unified frame — not any cited paper's claim — and are presented as straightforward consequences of standard concentration arguments, whose contribution is interpretive rather than technical.
