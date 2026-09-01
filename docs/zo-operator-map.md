# Zeroth-Order Operator Map

This companion explains what the repository means by a “ZO analogy.” It is an interpretation layer for comparing proposal mechanisms, not a claim that text-editing systems estimate numerical gradients.

## 1. Two information channels

For a frozen model $M$, define expected return

```math
f_M(s)
=
\mathbb E_{z\sim\mathcal D}
\left[R\!\left(H_s(M,z)\right)\right].
```

When $s$ is discrete text, code, or a file tree, $\nabla_s f_M(s)$ is undefined unless a continuous parameterization or relaxation is introduced. The objective is nevertheless queried through executions of $H_s$, which motivates a zeroth-order view of the **objective interface**.

Harness optimization usually observes more than a scalar value. A rollout may expose traces, exceptions, verifier messages, and natural-language critiques. These are proposal-side information:

```math
Y(s,z)
=
\bigl(R,\tau,\text{error},\text{feedback}\bigr).
```

Therefore the setting is not a strict classical function-value oracle. “ZO” describes the absence of a usable derivative of the deployed objective; it does not require the proposer to ignore semantic side information.

## 2. Classical operators and repository labels

| Repository label | Classical requirement | HarnessOpt role | Where the analogy stops |
|---|---|---|---|
| `one-point` | evaluate one perturbed numeric point | revise from one scored rollout or one candidate | no random direction or gradient estimate is implied |
| `batch evidence` | average several noisy observations | aggregate failures or critiques across tasks | tasks are noise samples, not perturbation directions |
| `contrastive diagnosis` | compare paired evaluations | compare success/failure traces or alternatives | no $s+\mu u$ and $s-\mu u$ symmetry is implied |
| `trace-informed proposal` | use observation details beyond a scalar | let traces, errors, or critiques guide an edit | semantic feedback is not a derivative or unbiased estimator |
| `history-conditioned proposal` | adapt from previous observations | condition a proposal on earlier states, scores, or feedback | history dependence is not numerical momentum |
| `localized edit` | change one coordinate or block | patch a named step, module, file, or skill | the block must be defined by the representation, not inferred after the fact |
| `bounded edit` | optimize within a trust region | constrain diff size, token count, files, or edit operations | syntactic size need not bound behavioral distance |
| `adaptive schedule` | set step size or radius from progress history | schedule exploration budget or candidate count by improvement | the improvement signal is itself high-variance at small $m$, so a schedule can lock onto noise |
| `surrogate-model search` | fit a model of the objective | use Bayesian optimization or another response model | ordinary LLM critique is not automatically a surrogate model |
| `population / archive` | retain and select several candidates | evolutionary selection, Pareto archive, tree search | retaining candidates alone supplies no convergence result; archive scores are usually same-set scores |
| `control-variate role` | use correlated information to reduce estimator variance | reuse rejected edits, paired replay, or baselines | variance reduction must be measured before using the classical term literally |
| `boundary — …` | — | the method leaves this axis: a real gradient, an RL objective, or a trained policy | not a ZO analogy at all; the suffix names what it is instead (`first-order`, `RL`, `trained policy`, `mixed`) |

Use the left-column labels in entries. Use a classical name literally only when the implementation meets its mathematical requirements.

## 3. Surface structure determines implementability

| Editable surface | Structure available before evaluation | Defensible operation |
|---|---|---|
| prompt text | token spans, sections, exemplars | bounded or localized textual edit |
| memory / skill store | entries, files, retrieval keys | entry-level addition, replacement, deletion |
| workflow graph | nodes, edges, module slots | coordinate or block search over declared components |
| executable code | files, symbols, types, tests, feature flags | static filtering, module-level edits, paired replay when toggles are valid |
| optimizer code | same as code, while changing the proposal loop itself | meta-level code search with additional evaluator-integrity risk |

A compiler, type checker, schema validator, or static analyzer is a **feasibility filter**: it can reject some candidates without task rollouts. It does not establish semantic correctness or generalization.

### 3.1 Requirements for stronger labels

- `central difference` requires paired evaluations around a defined center along a constructible positive and negative direction.
- `coordinate descent` requires coordinates fixed by the representation before observing the outcome.
- `trust region` requires a distance or neighborhood with some justified connection to behavior; edit count alone is only a budget.
- `control variate` requires a specified correlated quantity and an estimator whose variance reduction can be checked.
- `(1+1)-ES` requires an explicit parent, one offspring, comparison, and replacement rule; “propose one edit” is insufficient by itself.

## 4. How to annotate a paper

For each entry, record four facts before assigning an analogy:

1. what data the proposer observes: scalar scores, traces, errors, critiques, or a batch;
2. what edit unit is fixed before evaluation;
3. how many candidates are generated and retained; and
4. what feasibility checks run before task evaluation.

Then label the **role**, for example:

```text
[ZO analogy: batch evidence + localized edit]
```

Do not infer a convergence rate, variance reduction, or behavioral radius from the label. Those require a separate theorem or measurement.

## 5. Representative readings

These are repository interpretations, not the papers' own mathematical claims.

| Work | Reported mechanism | Conservative label |
|---|---|---|
| OPRO | prior solution–score pairs condition new proposals | `one-point / history-conditioned` |
| ProTeGi | critiques drive prompt edits | `trace-informed proposal` |
| MIPROv2 | Bayesian optimization over instructions and demonstrations | `surrogate-model search` |
| GEPA | trace-informed genetic/Pareto search | `population + trace-informed proposal` |
| Trace2Skill | trajectory-local lessons merged into patches | `batch evidence + localized edit` |
| SkillCAT | contrasts trajectories at an action-divergence point | `contrastive diagnosis` |
| AFlow | MCTS over workflow candidates | `population / tree search` |
| AlphaEvolve | edits declared code blocks in an evolutionary loop | `localized edit + population` |
| ELM | diff model used inside MAP-Elites | `bounded edit + archive` |

The main README contains a broader list. This table is intentionally small: its purpose is to calibrate labels, not duplicate the catalogue.

## 6. Sources for classical terminology

- [Liu et al., *A Primer on Zeroth-Order Optimization*, 2020](https://arxiv.org/abs/2006.06224)
- [Duchi et al., *Optimal Rates for Zero-Order Convex Optimization*, 2015](https://arxiv.org/abs/1312.2139)
- [Nesterov and Spokoiny, *Random Gradient-Free Minimization of Convex Functions*, 2017](https://link.springer.com/article/10.1007/s10208-015-9296-2)
- [Conn, Scheinberg, and Vicente, *Introduction to Derivative-Free Optimization*, 2009](https://epubs.siam.org/doi/book/10.1137/1.9780898718768)

These sources define numerical derivative-free methods. They do not analyze language-agent harnesses, and their rates do not transfer through analogy alone.
