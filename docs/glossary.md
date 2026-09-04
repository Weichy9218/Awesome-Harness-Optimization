# Glossary

Only terms used by the repository's analytical framework are included here. A label describes how this list reads a system; it is not automatically a term used by the cited paper.

## Harness definition

| Term | Meaning |
|---|---|
| **harness** | The model-external executable system that mediates between a base model and a task: it can load instructions and context, route memory and skills, schedule workflow steps, call tools, enforce permissions, and run verification or replay hooks. |
| **harness state** $s$ | The versioned subset of model-external components that an update may persist and reload on later tasks. |
| **runtime state** $r$ | Per-run context, processes, caches, generated files, and other transient state; it is not persistent harness state unless explicitly versioned and reloaded. |
| **protected evaluation boundary** | Task data, evaluator, model route, permissions, logging, and resource limits that are fixed outside $\mathcal S_{\mathrm{edit}}$ by default. A candidate that changes them is an evaluation-boundary change. |

The harness is broader than a prompt file, while the editable state is narrower than the entire runtime. This distinction prevents a temporary artifact or a modified evaluator from being counted as an ordinary harness self-evolution update.

## Core objects

| Symbol | Meaning |
|---|---|
| $M$ | base model; fixed for the core harness self-evolution analysis |
| $z\sim\mathcal D$ | a task sampled from the target distribution |
| $s\in\mathcal S$ | versioned model-external harness state: prompts, memory, workflows, tools, code, or optimizer state |
| $\mathcal S_{\mathrm{edit}}$ | the subset of state the update process may modify |
| $H_s(M,z;\xi)$ | execution of model $M$ on task $z$ under harness state $s$ with run randomness or environment seed $\xi$ |
| $\tau$ | execution trajectory or trace |
| $R(\tau)\in[0,1]$ | bounded task return used in the concentration results |
| $Y(s,z;\xi)$ | realized return $R(H_s(M,z;\xi))$ for one run |
| $f_M(s)$ | expected return $\mathbb E_{z,\xi}[Y(s,z;\xi)]$ |
| $\ell(s;z,\xi)$ | per-run loss $1-Y(s,z;\xi)$; report the task-level seed aggregation used in an experiment |
| $\epsilon(s)$ | population risk $\mathbb E_{z,\xi}[\ell(s;z,\xi)]$ |
| $\widehat\epsilon_V(s)$ | empirical risk on task set $V$ after the stated seed aggregation |
| $\widehat R_V(s)$ | mean empirical return $1-\widehat\epsilon_V(s)$ |

Plugin lifecycle is an optional runtime implementation concern. Registration, activation, deactivation, and cleanup affect behavioral rollback; they do not define the editable surface or make confirmation data independent.

For L3/L4 classification, use the primary persistent write target: harness or agent code is L3, while an improver, optimizer, or context-management mechanism is L4. A proposer that searches another object does not change that object's level.

## Update loop

| Symbol | Meaning |
|---|---|
| $Q$ | evidence collection from runs, traces, errors, or feedback |
| $\mathcal E_t$ | evidence available in round $t$ |
| $P_\phi$ | proposer mapping current state and evidence to candidate $\widetilde s_{t+1}$; $\phi$ denotes proposer parameters or policy |
| $G$ | operational state-transition rule deciding whether and how the candidate enters persistent state |
| $D_t^{\mathrm{prop}}$ | tasks that drive proposal evidence in round $t$ |
| $V_t$ | tasks consulted by $G$ in round $t$ when a confirmation step exists |
| $T$ | number of update rounds |

One update is written as

```math
\mathcal E_t=Q(s_t;D_t^{\mathrm{prop}}),\qquad
\widetilde s_{t+1}=P_\phi(s_t,\mathcal E_t),\qquad
s_{t+1}=G(s_t,\widetilde s_{t+1};V_t).
```

The observation available to a proposer may be richer than the scalar return:

```math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
```

where $\Psi$ is semantic side information such as traces, errors, tool calls, or verifier feedback. It is not a derivative and does not constitute confirmation evidence.

### Catalogue fields

| Field | Meaning |
|---|---|
| **proposal mechanism** | the evidence construction, search geometry, and query-allocation choices used by $P_\phi$ to form a candidate |
| **confirmation protocol** | the state-transition semantics implemented by $G$, together with the data relationship and reuse scope of any confirmation evaluation |

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
| **open loop** | no blocking evaluation before the proposal becomes persistent; use `write-through` as the protocol label |
| **search set** | tasks whose outcomes drive proposals or candidate selection |
| **state-transition gate** | an executable rule $G$ that can accept, reject, or roll back a candidate; this is an operational concept, not a statistical guarantee |
| **write-through** | the candidate is written into the next persistent state without a candidate-level blocking evaluation |
| **search-time selection** | candidates are ranked or retained using proposal/search data, and the selected object becomes the next state |
| **separated confirmation** | a candidate is fixed before a separate confirmation evaluation can block its promotion |
| **PAC-style confirmation** | a conditional statistical interpretation of separated confirmation when the candidate, bounded loss, independent confirmation data, and protected boundary satisfy the stated assumptions; it is not a synonym for $G$ |
| **held-out data** | a separate data split that can be used for candidate selection or confirmation; repeated adaptive use means it is not fresh |
| **fresh confirmation** | untouched data evaluate a candidate fixed by the completed search |
| **final locked test** | a test set used once for final reporting and not used for further editing |
| **retrospective gate** | later evidence may trigger rollback after persistence |
| **human review** | a person can block a write; governance evidence, not statistical independence |
| **reuse count** | number of adaptive decisions influenced by a data set |
| **evaluator protection** | runtime enforcement preventing edits to evaluators, task data, logging, or protected paths |
| **behavioral rollback** | restoration of observable runtime state, including side effects, rather than files alone |
| **two-stage atomic activation** | prepare and validate a component before swapping it into the live runtime; activation and cleanup are part of the transition |
| **plugin lifecycle** | registration, dependency resolution, activation, deactivation, and cleanup for a replaceable runtime component |
| **online adaptation** | updates applied during a continuing run; it meets the cross-run persistence criterion only when the resulting state is versioned and reloaded by later runs |
| **B1 / B2** | B1 is proposal stability; B2 is fixed-candidate confirmation on data not used by search |

## Statistical symbols

| Symbol | Meaning |
|---|---|
| $m$ | number of tasks in a validation or test sample |
| $\delta$ | allowed failure probability for a concentration statement |
| $\mathcal C$ | a finite candidate class fixed independently of the validation sample |
| $\mathcal U_L$ | a finite, validation-independent set of allowed edit scripts |
| $\eta$ | a valid uniform bound on $\lvert\epsilon(s)-\widehat\epsilon_V(s)\rvert$ for the states being compared; two-sided, so it costs $\delta\to\delta/2$ relative to a one-sided bound |
| $\eta_T$ | the value of $\eta$ obtained from a $T$-round reachable class $\mathcal C_T$; its **slack at fixed $m$** grows as $\sqrt{T}$ under the assumptions of `pac-stability.md` §4.1, and is typically vacuous at realistic $m$ and $T$ |
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
