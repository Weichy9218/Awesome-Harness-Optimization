# Zeroth-Order Operator Map

This note defines how the repository uses ZO language to compare harness self-evolution proposal mechanisms. It is an interpretation layer, not a claim that text-editing systems estimate numerical gradients.

## 1. Objective interface and side information

For a frozen base model $M$, task $z\sim\mathcal D$, and editable state $s$, define

```math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
```

For text, code, and file trees, $\nabla_s f_M(s)$ is not defined without an explicit continuous parameterization. The deployed objective is still observable through execution, which motivates a zeroth-order view of the objective interface.

A proposer may receive more than a scalar:

```math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
```

where $\Psi$ contains traces, errors, tool calls, and verifier feedback. This side information can improve proposal quality, but it is not a numerical derivative, an unbiased estimator, or candidate confirmation.

The repository therefore separates:

- objective information obtained by running a deployed state;
- semantic side information used to form an edit; and
- confirmation evidence used to decide persistence.

## 2. Direct operator map

The main comparison follows the mechanism families in SkillOpt-Lite. Extending from SkillOpt to harness self-evolution changes the editable domain from one skill file to an explicit harness state; it does not create a new ZO algorithm.

| ZO mechanism family | Harness-native role | Classical requirement | Safe repository label |
|---|---|---|---|
| ZO oracle | execute $s$ and observe $Y(s,z;\xi)$ and $\Psi(s,z;\xi)$ | query a black-box objective $f(x)$ | `ZO interface` |
| 1-point estimate | propose an edit from one scored trace | evaluate a numerical perturbation $x+\mu u$ and form a direction-scaled estimator | `single-trace proposal`; not an estimator without $u$ and $\mu$ |
| multi-point / mini-batch | aggregate tasks or seeds at the same state | evaluate several perturbation directions $u_i$ | `batch evidence`; sample averaging unless perturbations are constructed |
| central difference | compare two deployed states on aligned tasks | evaluate reversible symmetric perturbations $x+\mu u$ and $x-\mu u$ | `paired comparison`; central difference only when symmetry exists |
| coordinate descent | edit one declared component or block | choose a coordinate before evaluation and update only that coordinate | `block-local edit` |
| trust region | constrain a candidate by diff, token, file, or path budget | define a behavior-linked distance, update the radius, and use an acceptance rule | `bounded edit`; trust region only when all requirements hold |
| control variate / historical baseline | use $\widehat q_t^{\mathrm{cv}}=\widehat q_t-c_t+\mathbb E[c_t]$ with a named correlated baseline | require a valid baseline and measured variance reduction; a rejected buffer alone is not sufficient | `control-variate baseline`; otherwise `negative evidence` |

Two mechanisms are reported separately because they are not direct ZO operators in this mapping:

- `history/surrogate allocation` schedules the next candidate, task, or rollout budget;
- `population/archive search` retains and selects multiple candidates.

Rejected buffers and historical failures enter the control-variate row only when a correlated baseline and measured variance reduction are reported; otherwise they are negative evidence.

The formulas in the README are role-level comparisons. They do not transfer a convergence rate, a variance-reduction result, a behavioral radius, or an independent confirmation set to a harness self-evolution system.
## 3. Surface structure determines implementability

| Editable surface | Structure available before evaluation | Defensible operation |
|---|---|---|
| prompt text | token spans, sections, exemplars | bounded or localized textual edit |
| memory or skill store | entries, files, retrieval keys | entry-level addition, replacement, deletion |
| workflow graph | nodes, edges, module slots | coordinate or block search over declared components |
| executable code | files, symbols, types, tests, feature flags | static filtering, module edits, paired replay when toggles are valid |
| optimizer code | the same code structure while changing the proposal loop | meta-level code search with evaluator-integrity risk |
| pluginized runtime | registry entries, dependencies, lifecycle hooks, resources | component-level activation, deactivation, and cleanup |

A compiler, type checker, schema validator, or static analyzer is a feasibility filter. It can reject some candidates before task rollouts; it does not establish semantic correctness or generalization.

Version snapshots, feature flags, deterministic replay, and explicit allowlists can make local edits and paired comparisons executable. They do not make code intrinsically better than text. Code also introduces stronger coupling, more side effects, and a larger rollback surface.

### 3.1 Requirements for stronger labels

- **Central difference** requires paired evaluations around a defined center with constructible positive and negative directions.
- **Coordinate or block search** requires coordinates fixed by the representation before observing outcomes.
- **Trust region** requires a distance or neighborhood with a justified connection to behavior. Edit count alone is an edit budget.
- **Control variate** requires a named correlated quantity and a measured reduction in estimator variance.
- **(1+1)-ES** requires an explicit parent, one offspring, comparison, and replacement rule. “Propose one edit” is not enough.

## 4. How to annotate a paper

Record these facts before assigning a label:

1. what the proposer observes: scalar scores, traces, errors, critiques, or a batch;
2. what edit unit is fixed before evaluation;
3. how many candidates are generated and retained; and
4. which feasibility checks run before task evaluation.

Then annotate the proposal role, for example:

~~~text
[Proposal: batch evidence + localized edit]
~~~

Do not infer a convergence rate, variance reduction, behavioral radius, or independent confirmation from a label. Those require a theorem, a measurement, or an explicit protocol.

## 5. Representative readings

These are repository interpretations, not the cited papers’ own mathematical claims.

| Work | Reported mechanism | Conservative label |
|---|---|---|
| OPRO | prior solution–score pairs condition new proposals | one-point + history-conditioned proposal |
| ProTeGi | critiques drive prompt edits | trace-informed proposal |
| MIPROv2 | Bayesian optimization over instructions and demonstrations | surrogate-model search |
| GEPA | trace-informed genetic and Pareto search | population / archive + trace-informed proposal |
| Trace2Skill | trajectory-local lessons merged into patches | batch evidence + localized edit |
| SkillCAT | trajectories contrasted at an action-divergence point | contrastive diagnosis |
| AFlow | MCTS over workflow candidates | population / tree search |
| AlphaEvolve | edits declared code blocks in an evolutionary loop | localized edit + population / archive |
| ELM | diff model used inside MAP-Elites | bounded edit + archive |

The main README contains the catalogue. This table calibrates labels and does not duplicate the full list.

## 6. Sources

- [Liu et al., *A Primer on Zeroth-Order Optimization*, 2020](https://arxiv.org/abs/2006.06224)
- [Duchi et al., *Optimal Rates for Zero-Order Convex Optimization*, 2015](https://arxiv.org/abs/1312.2139)
- [Nesterov and Spokoiny, *Random Gradient-Free Minimization of Convex Functions*, 2017](https://link.springer.com/article/10.1007/s10208-015-9296-2)
- [Conn, Scheinberg, and Vicente, *Introduction to Derivative-Free Optimization*, 2009](https://epubs.siam.org/doi/book/10.1137/1.9780898718768)

These sources define numerical derivative-free methods. Their rates and assumptions do not transfer to language-agent harnesses by analogy alone.
