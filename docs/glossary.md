# Glossary

Only terms used by the repository's analytical framework are included here. A label describes how this list reads a system; it is not automatically a term used by the cited paper.

## Core objects

| Symbol | Meaning |
|---|---|
| $M$ | base model; fixed for the core HarnessOpt analysis |
| $z\sim\mathcal D$ | a task sampled from the target distribution |
| $s\in\mathcal S$ | model-external state: prompts, memory, workflows, tools, code, or optimizer state |
| $\mathcal S_{\mathrm{edit}}$ | the subset of state the update process may modify |
| $H_s(M,z)$ | execution of model $M$ on task $z$ under harness state $s$ |
| $\tau$ | execution trajectory or trace |
| $R(\tau)\in[0,1]$ | bounded task return used in the concentration results |
| $f_M(s)$ | expected return $\mathbb E_{z\sim\mathcal D}[R(H_s(M,z))]$ |
| $\ell(s;z)$ | per-task loss $1-R(H_s(M,z))$ |
| $\epsilon(s)$ | population risk $\mathbb E_{z\sim\mathcal D}[\ell(s;z)]$ |
| $\widehat\epsilon_V(s)$ | empirical risk on task set $V$ |
| $\widehat R_V(s)$ | mean empirical return $1-\widehat\epsilon_V(s)$ |

## Update loop

| Symbol | Meaning |
|---|---|
| $Q$ | evidence collection from runs, traces, errors, or feedback |
| $\mathcal E_t$ | evidence available in round $t$ |
| $P$ | proposer mapping current state and evidence to candidate $\widetilde s_{t+1}$ |
| $G$ | gate deciding whether and how the candidate enters persistent state |
| $D_t$ | tasks that drive proposal evidence in round $t$ |
| $V_t$ | tasks consulted by the gate in round $t$ |
| $T$ | number of update rounds |

## Zeroth-order terminology

| Term | Meaning in this repository |
|---|---|
| **zeroth-order objective interface** | objective information is obtained by executing candidate states rather than differentiating the deployed harness |
| **ZO analogy** | a proposal mechanism plays a role resembling a classical derivative-free operator; no numerical estimator or rate is implied |
| **semantic side information** | traces, errors, critiques, and verifier messages observed in addition to scalar return |
| **trace-informed proposal** | an edit proposal conditioned on traces, errors, critiques, or verifier messages |
| **history-conditioned proposal** | a proposal conditioned on earlier states, scores, or feedback; not numerical momentum |
| **feasibility filter** | compile, type, schema, lint, or static checks that can reject a candidate before task rollouts |
| **localized edit** | an edit restricted to a representation-defined step, file, module, node, or entry |
| **bounded edit** | a syntactic limit on tokens, files, diff size, or operations; not automatically a behavioral trust region |
| **population / archive** | several candidates or lineages are retained for selection or later exploration |
| **adaptive schedule** | exploration budget, candidate count, or edit radius set from the improvement history; not numerical step-size adaptation |

## Validation terminology

| Term | Meaning |
|---|---|
| **open loop** | no blocking evaluation before the proposal becomes persistent |
| **search set** | tasks whose outcomes drive proposals or candidate selection |
| **held-out gate** | a separate set can reject candidates; repeated use still creates adaptive dependence |
| **fresh confirmation** | untouched data evaluate a candidate fixed by the completed search |
| **final locked test** | a test set used once for final reporting and not used for further editing |
| **retrospective gate** | later evidence may trigger rollback after persistence |
| **human review** | a person can block a write; governance evidence, not statistical independence |
| **reuse count** | number of adaptive decisions influenced by a data set |
| **evaluator protection** | runtime enforcement preventing edits to evaluators, task data, logging, or protected paths |
| **behavioral rollback** | restoration of observable runtime state, including side effects, rather than files alone |

## Statistical symbols

| Symbol | Meaning |
|---|---|
| $m$ | number of tasks in a validation or test sample |
| $\delta$ | allowed failure probability for a concentration statement |
| $\mathcal C$ | a finite candidate class fixed independently of the validation sample |
| $\mathcal U_L$ | a finite, validation-independent set of allowed edit scripts |
| $\eta$ | a valid uniform bound on $\lvert\epsilon(s)-\widehat\epsilon_V(s)\rvert$ for the states being compared |
| $\eta_T$ | the value of $\eta$ obtained from a $T$-round reachable class $\mathcal C_T$; grows as $\sqrt{T}$ under the assumptions of `pac-stability.md` §4.1 |
| $\Delta$ | acceptance dead zone: the empirical improvement a gate requires before writing a candidate |
| $\beta_{\mathrm{avg}}$ | expected sensitivity of the update algorithm to replacing or removing one training example; not a high-probability bound by itself |

The validation note gives the exact assumptions behind these symbols: [`pac-stability.md`](pac-stability.md).

## Evaluation abbreviations

| Abbreviation | Meaning |
|---|---|
| **AULC** | area under the learning curve across update rounds |
| **BWT** | backward transfer: effect of later updates on earlier tasks |
| **FWT** | forward transfer: effect of earlier updates on later tasks |
| **FGT** | forgetting, whose exact aggregation must be stated by the experiment |
| **ASR** | attack success rate |
| **RR** | refusal rate |
| **OOD** | out-of-distribution |

Metric names do not specify a protocol. Every result should also report the task distribution, split, aggregation, reuse, and whether the metric participated in selection.
