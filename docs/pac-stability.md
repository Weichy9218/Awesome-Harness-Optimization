# Validation and Stability Notes for HarnessOpt

This note states only the guarantees used by the main list. It separates three settings that are often conflated: expected generalization from algorithmic stability, one-time evaluation of a fixed candidate, and repeated selection on a reused validation set.

## 1. Setup

Let the frozen base model be $M$, the editable harness state be $s$, and a task be $z\sim\mathcal D$. The harness produces a trajectory $H_s(M,z)$. Assume a bounded return $R\in[0,1]$, and define

```math
\ell(s;z)=1-R\!\left(H_s(M,z)\right),
\qquad
\epsilon(s)=\mathbb E_{z\sim\mathcal D}[\ell(s;z)].
```

For a sample $V_m=(z_1,\ldots,z_m)$,

```math
\widehat\epsilon_{V_m}(s)
=
\frac{1}{m}\sum_{i=1}^{m}\ell(s;z_i).
```

Write $\widehat R_{V_m}(s)=1-\widehat\epsilon_{V_m}(s)$ for the mean empirical return.

All concentration statements below require i.i.d. tasks from a stationary distribution and bounded loss. They do not cover evaluator bias, task leakage, safety properties absent from the loss, or changes to $M$.

## 2. Expected on-average stability

Let an update algorithm $\mathcal A$ map a training sample $D_N$ to a state $s_D$. Let $D_N^{(i\leftarrow z_i')}$ replace example $i$ with an independent draw $z_i'\sim\mathcal D$. One expected replace-one sensitivity is

```math
\beta_{\mathrm{avg}}
=
\mathbb E_{D_N,z_i',i,z}
\left[
\left|
\ell(\mathcal A(D_N);z)
-
\ell(\mathcal A(D_N^{(i\leftarrow z_i')});z)
\right|
\right].
```

Appropriate average-stability conditions support an **expectation-level** relationship between empirical and population risk, namely $\mathbb E[\epsilon(\mathcal A(D_N))-\widehat\epsilon_{D_N}(\mathcal A(D_N))]\le\beta_{\mathrm{avg}}$. No high-probability bound follows from this definition alone; that requires a stronger stability notion, such as uniform stability, or additional assumptions.

For HarnessOpt, batching evidence, aggregating across tasks, or limiting edit scope may reduce sensitivity to one task. That is a mechanism hypothesis, not a measured stability coefficient unless the paper estimates the replace-one quantity.

Primary references: [Bousquet and Elisseeff, 2002](https://www.jmlr.org/papers/v2/bousquet02a.html); [Shalev-Shwartz et al., 2010](https://jmlr.org/papers/v11/shalev-shwartz10a.html).

## 3. A fixed candidate on fresh data

Suppose $s$ is fixed without using $V_m$, and $V_m\sim\mathcal D^m$. Hoeffding's inequality gives, with probability at least $1-\delta$,

```math
\epsilon(s)
\le
\widehat\epsilon_{V_m}(s)
+
\sqrt{\frac{\ln(1/\delta)}{2m}}.
```

This is the cleanest meaning of independent confirmation in this repository. A set is not fresh merely because it was initially called `validation` or `held-out`: if its scores changed the search trajectory, the final candidate depends on it.

## 4. Reusing one validation set

Let $\mathcal C$ be a finite candidate class chosen independently of $V_m$. A union bound yields, with probability at least $1-\delta$, simultaneously for every $s\in\mathcal C$,

```math
\epsilon(s)
\le
\widehat\epsilon_{V_m}(s)
+
\sqrt{
\frac{\ln|\mathcal C|+\ln(1/\delta)}{2m}
}.
```

Because the event is uniform over $\mathcal C$, an adaptive procedure may select an element of this class after observing validation scores. The important requirement is that the whole class, not merely the realized list of candidates, was fixed independently of $V_m$.

### 4.1 A conditional reachable-class count

Assume:

1. $s_0$ is fixed before $V_m$ is observed;
2. every round applies one script from a finite set $\mathcal U_L$;
3. $\mathcal U_L$ is also fixed independently of $V_m$; and
4. the script encoding includes every behavior-affecting choice, including file paths, inserted content, external retrieval, tool calls, and side effects.

Then the states reachable within $T$ edits lie in a class satisfying

```math
|\mathcal C_T|
\le
\sum_{t=0}^{T}|\mathcal U_L|^t.
```

Substituting this count into the finite-class bound is valid under these assumptions. Diff size or the number of candidates actually evaluated is not, by itself, a complete class description. Natural-language edits drawn from an unrestricted generator do not automatically define a finite validation-independent class.

### 4.2 Fresh data at every round

If round $t$'s candidate is fixed before a fresh set $V_t\sim\mathcal D^m$ is drawn, and the sets are independent across $T$ rounds, a union bound over rounds gives simultaneous one-sided error at most

```math
\sqrt{\frac{\ln(T/\delta)}{2m}}.
```

This statement concerns fresh samples. Rotating among a small pool of previously observed sets is reuse, not fresh confirmation.

Comparing the two regimes: reusing one set costs slack $O(\sqrt{T\ln|\mathcal U_L|/m})$ from §4.1, while rotating costs $O(\sqrt{\ln(T/\delta)/m})$ — logarithmic rather than square-root in $T$ — at a task cost of $Tm$ instead of $m$. Rotation is therefore preferable when the price of fresh tasks is below roughly $\sqrt{T/\ln T}$ times the price of enlarging the single set. This is an order-of-magnitude comparison under the stated assumptions, not a proof that rotation dominates: the constants and the per-task cost are setting-specific.

For more general adaptive reuse, mechanisms such as [reusable holdout](https://www.science.org/doi/10.1126/science.aaa9375) or [adaptive data analysis](https://arxiv.org/abs/1411.2664) may be relevant, but this repository does not claim that existing HarnessOpt systems satisfy their mechanisms.

### 4.3 Aggregate risk hides cluster-level degradation

$\epsilon$ is an expectation over $\mathcal D$. If the task distribution decomposes into $K$ clusters with masses $p_k$ and per-cluster risks $\epsilon_k$, degradation confined to cluster $k$ shifts $\epsilon$ by only $p_k\,\Delta\epsilon_k$, so it stays inside the slack $\eta$ whenever $\Delta\epsilon_k<\eta/p_k$. A guarantee at the cluster level is a separate statement and needs separate sampling: applying the finite-class bound within each cluster and a union bound across clusters requires

```math
m_k
=
\Omega\!\left(
\frac{\ln|\mathcal C_T|+\ln(K/\delta)}{\epsilon_k^{2}}
\right).
```

This is the mechanism by which an aggregate score can rise while a specific capability is lost, with no bound violated. It is an argument for stratified non-regression reporting; it does not by itself supply a defensible cluster partition, which remains an open problem.

## 5. Comparing a current state and a candidate

Suppose one valid event guarantees, for both $s_t$ and $\widetilde s_{t+1}$,

```math
|\epsilon(s)-\widehat\epsilon_{V_m}(s)|\le\eta.
```

Then an empirical return improvement greater than $2\eta$,

```math
\widehat R_{V_m}(\widetilde s_{t+1})
-
\widehat R_{V_m}(s_t)
>
2\eta,
```

is sufficient to conclude lower true risk for the candidate on the measured distribution. This is a conditional comparison, not a universal acceptance rule. It says nothing about unmeasured safety constraints, non-i.i.d. tasks, evaluator tampering, or side effects left by a rejected candidate.

## 6. What a gate should report

A statistically interpretable experiment should report:

1. the proposal, selection, validation, and final-test splits, with sample counts;
2. which split can block persistence;
3. how many times each split is reused and what feedback is revealed;
4. the number of rounds and candidate evaluations;
5. any finite candidate class and its validation-independent encoding;
6. whether the evaluator and task data are protected at runtime;
7. whether rejection restores behavior, not merely files; and
8. a fresh final test when the selection data were reused.

These fields separate a statistical claim from governance evidence such as code review, sandboxing, logging, or rollback. Both matter, but they establish different properties.

## 7. Non-conclusions

The results above do **not** establish that:

- a smaller textual diff causes proportionally smaller behavioral change;
- repeated validation reuse costs exactly $\sqrt T$;
- a particular edit budget is optimal;
- validation rotation dominates a larger validation set;
- exact file rollback restores all runtime state; or
- any listed system satisfies a PAC guarantee.

Those questions require system-specific assumptions and measurements. They remain research problems rather than consequences of Hoeffding's inequality.
