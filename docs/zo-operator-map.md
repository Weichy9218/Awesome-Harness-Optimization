# Zeroth-Order Operator Map

This note defines how the repository uses ZO language to compare HarnessOpt proposal mechanisms. It is an interpretation layer, not a claim that text-editing systems estimate numerical gradients.

## 1. Objective interface and side information

For a frozen base model \(M\), task \(z\sim\mathcal D\), and editable state \(s\), define

~~~math
Y(s,z;\xi)=R\!\left(H_s(M,z;\xi)\right),\qquad
f_M(s)=\mathbb E_{z,\xi}[Y(s,z;\xi)].
~~~

For text, code, and file trees, \(\nabla_s f_M(s)\) is not defined without an explicit continuous parameterization. The deployed objective is still observable through execution, which motivates a zeroth-order view of the objective interface.

A proposer may receive more than a scalar:

~~~math
\mathcal O(s,z;\xi)=\bigl(Y(s,z;\xi),\Psi(s,z;\xi)\bigr),
~~~

where \(\Psi\) contains traces, errors, tool calls, and verifier feedback. This side information can improve proposal quality, but it is not a numerical derivative, an unbiased estimator, or candidate confirmation.

The repository therefore separates:

- objective information obtained by running a deployed state;
- semantic side information used to form an edit; and
- confirmation evidence used to decide persistence.

## 2. Labels and their limits

| Repository label | Classical requirement | HarnessOpt role | Where the analogy stops |
|---|---|---|---|
| one-point | evaluate one perturbed numeric point | revise from one scored rollout or one candidate | no random direction or gradient estimate is implied |
| batch evidence | average several noisy observations | aggregate failures or critiques across tasks | tasks are samples, not perturbation directions |
| contrastive diagnosis | compare paired evaluations | compare success/failure traces or alternatives | no \(s+\mu u\) and \(s-\mu u\) symmetry is implied |
| trace-informed proposal | use observation details beyond a scalar | condition an edit on traces, errors, or critiques | semantic feedback is not a derivative |
| history-conditioned proposal | adapt from previous observations | condition on earlier states, scores, or feedback | history dependence is not numerical momentum |
| localized edit | change one coordinate or block | patch a named entry, file, module, node, or skill | the block must be defined before outcome observation |
| bounded edit | optimize within a trust region | constrain tokens, files, diff size, or operations | syntactic size need not bound behavioral distance |
| adaptive schedule | set step size or radius from progress | schedule candidate count, budget, or edit scope | the progress signal can be noisy and selection-biased |
| surrogate-model search | fit a model of the objective | Bayesian optimization or another response model | ordinary LLM critique is not automatically a surrogate |
| population / archive | retain and select several candidates | evolutionary selection, Pareto archive, or tree search | retention alone gives no convergence or confirmation result |
| control-variate role | use correlated information to reduce estimator variance | rejected edits, baselines, or paired replay | variance reduction must be specified and measured |
| boundary — first-order / RL / trained policy | the method changes representation or objective | real gradient, RL, or trained-policy component | not a ZO analogy for the complete method |

Use a classical term literally only when the implementation meets its mathematical requirements. Otherwise use the repository label as a conservative role description.

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
[ZO analogy: batch evidence + localized edit]
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
