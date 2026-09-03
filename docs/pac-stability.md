# Validation and Stability Notes for HarnessOpt

This note states only the guarantees used by the main list. It separates three settings that are often conflated: expected generalization from algorithmic stability, one-time evaluation of a fixed candidate, and repeated selection on a reused validation set.

It is the technical appendix for README Section 4. The README names the two boundaries as B1 (proposal stability) and B2 (fixed-candidate confirmation); this note supplies the assumptions, bounds, and failure modes. The companion [audit table](audit-table.md) records which state-transition protocol and runtime controls a cited system actually exposes. EIP/plugin lifecycle controls belong to that runtime boundary: they affect activation and behavioral rollback, not statistical independence.

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

All concentration statements below require i.i.d. tasks from a stationary distribution and bounded loss. The formulas suppress run randomness $\xi$; when a task is run with multiple seeds, aggregate at the task level before counting $m$ as the number of tasks. These statements do not cover evaluator bias, task leakage, safety properties absent from the loss, or changes to $M$.

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

The statement above is one-sided. A two-sided statement, needed for the comparison in §5, replaces $\ln(1/\delta)$ with $\ln(2/\delta)$:

```math
\left|\epsilon(s)-\widehat\epsilon_{V_m}(s)\right|
\le
\sqrt{\frac{\ln(2/\delta)}{2m}}
\qquad\text{with probability at least }1-\delta.
```

Every bound below is stated one-sided; each requires the same $\delta\to\delta/2$ adjustment when used as a two-sided $\eta$.

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

**This count is usually too large to be useful, and the arithmetic should be checked before the bound is invoked.** The slack is $O(\sqrt{T\ln|\mathcal U_L|/m})$, and $\ln|\mathcal U_L|$ scales with the *description length* of an edit, not the number of edits. Encoding an edit as a bounded script over an alphabet $\Sigma$ with length at most $L$ gives $\ln|\mathcal U_L|\approx (L+1)\ln|\Sigma|$, so with $|\Sigma|=128$ and a very tight $L=20$ bytes, $\ln|\mathcal U_L|\approx 102$. At $m=500$ and $\delta=0.05$ the slack reaches $0.32$ at $T=1$ and exceeds $1$ — vacuous, since $\ell\in[0,1]$ — by $T=10$. Holding the slack at $0.1$ under those settings would need $m\approx 5\times10^4$.

The practical consequence is that §4.1 should be read as a statement about *what the reuse regime costs*, not as a usable certificate for multi-round reuse. Its role in this repository is to make the cost visible and to motivate §4.2, not to license reusing one validation set across rounds.

### 4.2 Fresh data at every round

If round $t$'s candidate is fixed before a fresh set $V_t\sim\mathcal D^m$ is drawn, and the sets are independent across $T$ rounds, a union bound over rounds gives simultaneous one-sided error at most

```math
\sqrt{\frac{\ln(T/\delta)}{2m}}.
```

This statement concerns fresh samples. Rotating among a small pool of previously observed sets is reuse, not fresh confirmation.

Comparing the two regimes at equal slack $\eta$ is the useful form, because the two regimes spend tasks differently: reuse consumes $m$ tasks in total, rotation consumes $m$ per round, or $Tm$ in total. Setting each slack to $\eta$ and solving for the total task cost gives

```math
m_{\text{reuse}}
=
\frac{T\ln|\mathcal U_L|+\ln(1/\delta)}{2\eta^{2}},
\qquad
T\,m_{\text{rotate}}
=
\frac{T\ln(T/\delta)}{2\eta^{2}}.
```

The reuse requirement is $O(T)$ in total tasks for a fixed edit-script class, whereas rotation is $O(T\ln T)$ because it pays a $\ln T$ term for the across-round union bound. Their ratio is

```math
\frac{T\,m_{\text{rotate}}}{m_{\text{reuse}}}
\approx
\frac{\ln(T/\delta)}{\ln|\mathcal U_L|}.
```

Rotation is cheaper exactly when $\ln(T/\delta)<\ln|\mathcal U_L|$, that is, when the number of rounds is small relative to the size of the edit-script class. Under the illustrative numbers of §4.1 ($\ln|\mathcal U_L|\approx102$, $\delta=0.05$) this holds for any $T$ below roughly $10^{42}$, so rotation is cheaper in every realistic regime covered by that illustration. Its ratio grows with $\ln T$, however; this is not an asymptotic cost advantage. Rotation's defensible advantage is keeping the *slack at fixed per-round $m$* logarithmic in $T$, not reducing total sampling cost.

Two caveats. First, the comparison assumes fresh tasks and reused tasks cost the same; when fresh tasks are strictly more expensive to obtain, the relevant comparison is between their prices, and this note does not fix those. Second, the $\sqrt{T}$-versus-$\ln T$ contrast concerns the *slack at fixed $m$*, which is the quantity that determines whether a bound is vacuous — not the total task budget. Both readings are correct about different quantities, and conflating them is a common error: rotation's advantage is that it keeps the slack non-vacuous as $T$ grows, not that it reduces total sampling cost by an order of magnitude.

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

Suppose one valid event guarantees, for both $s_t$ and $\widetilde s_{t+1}$ **simultaneously**,

```math
|\epsilon(s)-\widehat\epsilon_{V_m}(s)|\le\eta.
```

Obtaining such an $\eta$ requires the two-sided form of §3 and a class covering both states — for two states fixed independently of $V_m$, $\eta=\sqrt{\ln(4/\delta)/(2m)}$; under §4.1's assumptions, $\eta=\eta_T$ from the finite-class bound with $\delta\to\delta/2$. Then an empirical return improvement greater than $2\eta$,

```math
\widehat R_{V_m}(\widetilde s_{t+1})
-
\widehat R_{V_m}(s_t)
>
2\eta,
```

is sufficient to conclude lower true risk for the candidate on the measured distribution. This is a conditional comparison, not a universal acceptance rule. It says nothing about unmeasured safety constraints, non-i.i.d. tasks, evaluator tampering, or side effects left by a rejected candidate.

Because $\eta$ depends on the candidate class, the dead zone $\Delta$ and the edit budget $L$ are not independent knobs: widening $L$ enlarges $\ln|\mathcal U_L|$, which raises $\eta_T$, which raises the improvement a gate must require. A system that relaxes its edit budget while holding $\Delta$ fixed has weakened its acceptance rule without recording that it did so. Paired evaluation — same tasks, same seeds, comparing per-task differences — is the standard way to reduce the $\eta$ actually needed, and is cheaper than enlarging $m$; this note does not state a bound for it, since the variance reduction is setting-specific.

## 6. What a gate should report

A statistically interpretable experiment should report:

1. the proposal, selection, validation, and final-test splits, with sample counts **and split ratios**;
2. which split can block persistence;
3. how many times each split is reused and what feedback is revealed;
4. the number of rounds and candidate evaluations, **counting rejected candidates**;
5. any finite candidate class and its validation-independent encoding;
6. whether the evaluator and task data are protected at runtime;
7. whether rejection restores behavior, not merely files; and
8. for pluginized runtimes, the component version, dependency, activation, deactivation, and cleanup records; and
9. a fresh final test when the selection data were reused.

Items 1 and 2 are separate properties and a system may satisfy one without the other: a clean top-level split says nothing about whether any gate can reject a candidate. Item 4 counts every state that was scored on the validation set, since selection pressure comes from evaluation rather than acceptance.

These fields separate a statistical claim from governance evidence such as code review, sandboxing, logging, or rollback. Both matter, but they establish different properties.

## 7. Non-conclusions

The results above do **not** establish that:

- a smaller textual diff causes proportionally smaller behavioral change;
- repeated validation reuse costs exactly $\sqrt T$;
- rotation reduces the total task budget by an order of magnitude (§4.2: it bounds the slack, and the total-cost ratio is a constant set by $\ln|\mathcal U_L|$);
- the finite-class bound of §4.1 is non-vacuous at realistic $m$, $L$, and $T$;
- a particular edit budget is optimal;
- validation rotation dominates a larger validation set;
- exact file rollback restores all runtime state; or
- any listed system satisfies a PAC guarantee.

Those questions require system-specific assumptions and measurements. They remain research problems rather than consequences of Hoeffding's inequality.
