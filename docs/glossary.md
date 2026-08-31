# Glossary

All symbols, terms, and metric abbreviations used in this list, in one place. Terms are defined once and used consistently — where the literature offers several synonyms, this list keeps one.

---

## Core objects

| Symbol | Name | Meaning |
|---|---|---|
| $M$ | base model | The frozen backbone LLM. Fixed within a HarnessOpt round by definition |
| $z$ | task instance | Drawn from the task distribution $\mathcal{D}$ |
| $\mathcal{D}$ | task distribution | The distribution generalization is measured against |
| $s$ | state | Model-external software state: prompt, context, memory, workflow, tool interface, agent code, optimizer code |
| $\mathcal{S}_{\mathrm{edit}}$ | editable surface | The subset of state the optimizer is permitted to modify this round |
| $H_s$ | harness | The system organizing model calls, context, tools, control flow, and run state under state $s$ |
| $\tau = H_s(M,z)$ | trajectory | The execution record of one task run |
| $R(\tau) \in [0,1]$ | return | Bounded task reward |
| $\ell(s;z) = 1 - R(H_s(M,z))$ | loss | Per-task loss |
| $\epsilon(s) = \mathbb{E}_{z\sim\mathcal{D}}[\ell(s;z)]$ | risk | True risk of a state |
| $f_M(s) = \mathbb{E}_{z\sim\mathcal{D}}[R(H_s(M,z))]$ | objective | Expected return; $f_M(s) = 1 - \epsilon(s)$ |

## The update loop

| Symbol | Name | Role |
|---|---|---|
| $Q$ | evidence collector | Runs the system on $D_t$ and returns $\mathcal{E}_t$ |
| $\mathcal{E}_t$ | evidence | $\{(z_i, \tau_i, R_i, \mathrm{feedback}_i)\}$ — the semantically rich query result |
| $P$ | proposer | Maps $(s_t, \mathcal{E}_t)$ to a candidate $\tilde{s}_{t+1}$. **Axis I** classifies $P$ |
| $G$ | gate | Maps $(s_t, \tilde{s}_{t+1}; V_t)$ to $s_{t+1}$ via accept / reject / rollback. **Axis II** classifies $G$ |
| $t$, $T$ | round index, horizon | Number of evolution rounds |
| $D_t$ | proposal tasks | Tasks driving evidence collection in round $t$ |
| $V_t$, $V_m$ | validation set | The set used for confirmation; $m = \lvert V_m \rvert$ |
| $s_0$ | seed state | The Round-0 artifact. Must be fixed independently of $V$ (assumption A1) |

## Zeroth-order (Axis I)

| Term | Meaning |
|---|---|
| **Zeroth-order (ZO)** | The optimizer obtains objective information only by querying an oracle; the gradient is inaccessible. **Not** a claim that variables are numeric |
| **ZO oracle** | Deploy candidate → run tasks → observe return. One query = one (set of) rollout(s) |
| $\mu$ | Step-size analogue in the classical operator forms. On text surfaces it has no literal realization |
| $u$, $e_i$ | Random search direction; coordinate basis vector |
| $\widehat{\nabla} f$ | ZO gradient estimator |
| $\mathcal{B}(s_k, \Delta_k)$ | Trust region: the admissible neighborhood for one edit |
| $L$, $L_t$ | **Edit budget** — the trust-region radius. For [Proposition A](pac-stability.md) it must be the *description length* of the edit (e.g. diff bytes), not the edit count |
| $c$ | Control variate |
| $\mathcal{A}_t$ | Candidate archive / population at round $t$ |
| **Feasibility oracle** | compile / type-check / static analysis: rejects candidates without consuming task rollouts. **Not** "zero cost" — it consumes compute, not rollouts |
| **On-policy evidence** | $\mathcal{E}_t$ is sampled under the current $s_t$, so information about the neighborhood of $s_t$ is biased |
| **Language-mediated program compilation** | The framing where the editable state is a program, the rollout is its execution trace, and the LLM is compiler and runtime |

## PAC / stability (Axis II)

| Symbol | Name | Meaning |
|---|---|---|
| $\beta_{\exp}$ | expected on-average stability | Sensitivity of the update algorithm's output to removing one training task; controls bound **(B1)** |
| $N$ | training task count | Sample size in (B1) |
| $m$ | validation task count | Sample size in (B2) and in $\eta_T$ |
| $\delta$ | failure probability | Bounds hold with probability $\ge 1-\delta$ |
| $\widehat{\epsilon}_{D_N}$, $\widehat{\epsilon}_{V_m}$ | empirical risk | On training and validation sets respectively |
| $\widehat{\Delta}_{V_m}$ | empirical gain | $\widehat{R}_{V_m}(\tilde{s}) - \widehat{R}_{V_m}(s_t)$ |
| $\Delta$ | statistical dead-zone | Acceptance threshold. [Proposition B](pac-stability.md): $\Delta > 2\eta_T$ suffices |
| $\Sigma$ | alphabet | For edit scripts |
| $\mathcal{H}_T$ | reachable set | All states ever proposed **or tested** within $T$ rounds — including rejected ones |
| $l_{\mathrm{eff}} = T(L+1)$ | effective length | The cumulative edit budget; replaces program length in the STOP-style bound |
| $\eta_T$ | uniform slack | $\sqrt{\dfrac{T(L+1)\ln\lvert\Sigma\rvert + \ln(1/\delta)}{2m}}$ |
| $p_k$, $A_k$, $K$ | cluster mass, cluster, cluster count | For stratified validation ([Proposition C](pac-stability.md)) |
| $d(\mathcal{D}_{t-1},\mathcal{D}_t)$ | drift divergence | TV, $\mathcal{H}$-divergence, or discrepancy between consecutive task distributions |

### Protocol classes

| Class | Definition |
|---|---|
| **Open loop** | Experience is written straight into later state; no candidate test can stop it, no failure recovery |
| **Same-set scoring** | Candidates are scored, ranked, and retained on the *search* tasks; a test set is reported separately at the end |
| **Independent confirmation** | Candidates are tested on tasks that did not participate in proposal, and can be rejected or rolled back |

> The decisive distinction is **not** whether tests were run. It is whether a test result can stop a candidate from entering persistent state, and whether the set used for that decision is reused across rounds.

### The three premises of (B2)

| Premise | Content |
|---|---|
| **(i) Independence** | $V_m$ is independent of the training data and the proposal process |
| **(ii) Bounded signal bias** | The evaluation signal's bias is bounded |
| **(iii) External evaluator** | The evaluator lies outside $\mathcal{S}_{\mathrm{edit}}$ |

### The three discriminating sub-axes

| Sub-axis | Question |
|---|---|
| **Write authority** | Agent writes autonomously, or only after human review? |
| **Persistence** | Ephemeral sandbox run, or committed to versioned state? |
| **Constraint enforcement** | Declared in the prompt, or enforced by permissions / sandbox / hidden evaluator / static checks? |

---

## Metric abbreviations

| Abbrev. | Expansion | What it measures |
|---|---|---|
| **AULC** | Area Under the Learning Curve | Cumulative gain across evolution rounds, not just the endpoint |
| **FGT** | Forgetting | $\frac{1}{K}\sum_k [\max_{t\le T}\widehat{R}_{A_k}(s_t) - \widehat{R}_{A_k}(s_T)]_+$ — peak-to-final drop, averaged over clusters |
| **BWT** | Backward Transfer | Effect of later updates on earlier tasks |
| **FWT** | Forward Transfer | Effect of earlier updates on later tasks |
| **SLR** | Skill Load Rate | Was the optimized artifact loaded at all? |
| **HFR** | Harness Follow Rate | Once loaded, was it followed? |
| **LPR** | Loaded-Plan Rate | Was the loaded plan actually used in the trajectory? |
| **ASR** | Attack Success Rate | Safety probe; must be a gate input, not a final-table column |
| **RR** | Refusal Rate | Safety probe; can fall sharply while task performance rises |
| **OOD** | Out-of-Distribution | Transfer to tasks outside the evolution distribution |

> **SLR / HFR / LPR exist to decompose an end-task failure** into "not loaded", "loaded but not followed", and "followed but still failed". Reporting only the end-task score conflates all three.

---

## Terms deliberately avoided

These appear in adjacent literature but are not used in this list without a directly supporting citation, because they carry no operational content here:

- **"zero-cost oracle"** — the feasibility check consumes compute; it consumes no *task rollouts*. Say the latter.
- **"the harness has a gradient"** — textual feedback is semantic side-information on a zeroth-order query, not a verifiable derivative.
- **"higher level ⇒ stronger optimizer"** — operator implementability depends on surface *structure*, not on level number.
- **"validated"** as a synonym for "tested" — reserve it for independent confirmation that can reject a candidate.
- **"all existing work" / "an unsolved gap to date"** — not used without systematic search evidence.
