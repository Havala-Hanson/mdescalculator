# MDES engine formulas

This document collects the analytic formulas used by the MDES engine, organized by concept and reused across designs.

---

## 1. Notation and common quantities

- **Treatment indicator:**
  
  \[
  T_i =
  \begin{cases}
  1 & \text{if unit } i \text{ is assigned to treatment} \\
  0 & \text{otherwise}
  \end{cases}
  \]

- **Standardized impact (MDES target):**
  
  \[
  \delta = \frac{\tau}{\sigma_Y}
  \]

  where \(\tau\) is the raw treatment effect and \(\sigma_Y\) is the marginal SD of the outcome.

- **Outcome decomposition (generic \(L\)-level model):**
  
  \[
  Y = \mu + \sum_{\ell=1}^{L} u^{(\ell)} + e
  \]

  where \(u^{(\ell)}\) are random effects at level \(\ell\) and \(e\) is the residual.

- **Total variance:**
  
  \[
  \sigma_Y^2 = \sum_{\ell=1}^{L} \sigma_{\ell}^2 + \sigma_e^2
  \]

- **Intraclass correlation at level \(\ell\):**
  
  \[
  \rho_{\ell} = \frac{\sigma_{\ell}^2}{\sigma_Y^2}
  \]

---

## 2. Design degrees of freedom

- **Generic degrees of freedom for treatment effect:**
  
  \[
  \text{df}_\tau = f(\text{number of clusters, blocks, or higher-level units})
  \]

  For example, in a two-level cluster randomized design with \(J\) clusters and one treatment indicator at level 2:

  \[
  \text{df}_\tau = J - p
  \]

  where \(p\) is the number of level-2 parameters (including the intercept and treatment).

---

## 3. Variance of the treatment effect estimator

### 3.1 Generic form

- **Variance of \(\hat{\tau}\):**
  
  \[
  \operatorname{Var}(\hat{\tau}) = \frac{\sigma_Y^2}{n_{\text{eff}}} \cdot A
  \]

  where:
  - \(n_{\text{eff}}\) is an effective sample size term (depends on design, clustering, and allocation),
  - \(A\) is an adjustment factor capturing ICCs, covariates, and unequal allocation.

### 3.2 Example: simple individual random assignment

- **Setup:**
  - Total sample size: \(N\)
  - Proportion treated: \(P_T\)
  - No clustering, no covariates.

- **Variance:**
  
  \[
  \operatorname{Var}(\hat{\tau}) =
  \frac{\sigma_Y^2}{N P_T (1 - P_T)}
  \]

---

## 4. Covariate adjustment

- **Proportion of variance explained by covariates at level \(\ell\):**
  
  \[
  R_{\ell}^2 = 1 - \frac{\sigma_{\ell,\text{resid}}^2}{\sigma_{\ell}^2}
  \]

- **Adjusted variance components:**
  
  \[
  \sigma_{\ell,\text{adj}}^2 = (1 - R_{\ell}^2)\,\sigma_{\ell}^2
  \]

- **Adjusted total variance:**
  
  \[
  \sigma_{Y,\text{adj}}^2 = \sum_{\ell=1}^{L} \sigma_{\ell,\text{adj}}^2 + \sigma_{e,\text{adj}}^2
  \]

- **Adjusted variance of \(\hat{\tau}\):**
  
  \[
  \operatorname{Var}_{\text{adj}}(\hat{\tau}) =
  \operatorname{Var}(\hat{\tau}) \cdot B
  \]

  where \(B\) is a design-specific function of the \(R_{\ell}^2\) values.

---

## 5. Standard error, MDES, and power

### 5.1 Standard error

- **Standard error of \(\hat{\tau}\):**
  
  \[
  \operatorname{SE}(\hat{\tau}) = \sqrt{\operatorname{Var}(\hat{\tau})}
  \]

- **Standard error of standardized effect:**
  
  \[
  \operatorname{SE}(\hat{\delta}) =
  \frac{\operatorname{SE}(\hat{\tau})}{\sigma_Y}
  \]

### 5.2 MDES

For a two-sided test with significance level \(\alpha\) and power \(1 - \beta\):

- **Critical values:**
  
  \[
  t_{\alpha/2, \text{df}_\tau}, \quad t_{\beta, \text{df}_\tau}
  \]

- **MDES:**
  
  \[
  \text{MDES} =
  \left( t_{\alpha/2, \text{df}_\tau} + t_{\beta, \text{df}_\tau} \right)
  \cdot \operatorname{SE}(\hat{\delta})
  \]

### 5.3 Power given a target effect size

Given a target standardized effect \(\delta^\ast\):

- **Noncentrality parameter:**
  
  \[
  \lambda = \frac{\delta^\ast}{\operatorname{SE}(\hat{\delta})}
  \]

- **Power (two-sided):**
  
  \[
  \text{Power} =
  P\left( |T_{\text{df}_\tau}(\lambda)| > t_{\alpha/2, \text{df}_\tau} \right)
  \]

  where \(T_{\text{df}_\tau}(\lambda)\) is a noncentral \(t\)-distributed random variable.

---

## 6. Design-specific modules

Each design in the engine plugs into the generic structure above by specifying:

- **Cluster structure and sample sizes**
  
  \[
  (J, n, K, \dots)
  \]

- **ICCs and variance components**
  
  \[
  (\rho_1, \rho_2, \dots), \quad (\sigma_1^2, \sigma_2^2, \dots)
  \]

- **Covariate \(R^2\) values**
  
  \[
  (R_1^2, R_2^2, \dots)
  \]

- **Allocation ratios and blocking factors**

These feed into:

1. **Effective sample size \(n_{\text{eff}}\)**  
2. **Adjustment factors \(A\) and \(B\)**  
3. **Degrees of freedom \(\text{df}_\tau\)**  

Once those are defined for a given design, the engine uses Sections 3–5 to compute:

- \(\operatorname{Var}(\hat{\tau})\)
- \(\operatorname{SE}(\hat{\delta})\)
- MDES and/or power.

---

## 7. Design-specific formulas

The following subsections document the variance formula, degrees of freedom, and covariate adjustment for each design supported by the engine. All designs feed into the generic MDES formula in Section 5.2.

**Common notation recap:**
- \(P\) = proportion treated (default 0.5)
- \(N\) = total individuals; \(J\) = level-2 units; \(K\) = level-3 units; \(L\) = level-4 units; \(n\) = individuals per lowest cluster
- \(\rho_\ell\) = ICC at level \(\ell\); \(\omega_\ell = \operatorname{Var}(\tau_k) / \rho_\ell\) (treatment effect heterogeneity)
- \(R^2_\ell\) = proportion of level-\(\ell\) variance explained by covariates
- \(R^2_{t\ell}\) = proportion of treatment-effect variance explained by block/cluster-level covariates
- \(g_\ell\) = number of covariates at level \(\ell\) (for df adjustment)

---

### 7.1 IRA: Simple Individual Random Assignment

- **Structure:**  
  Single level. Each individual is independently randomized to treatment or control. No clustering, no blocking.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) = \frac{1 - R^2_1}{P(1-P)\,N}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = N - g_1 - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_1\) enters directly into the numerator above; no separate adjustment step.

---

### 7.2 BIRA2\_1c: Two-Level Blocked IRA (Constant Block Effect)

- **Structure:**  
  Two levels: individuals (1) within blocks (2). Individuals are randomized within blocks. Block effects are constant (treatment effect does not vary across blocks). Equivalent to a fixed intercept shift per block.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) = \frac{1 - R^2_1}{P(1-P)\,J\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = J(n - 1) - g_1 - 1
    \]

  - **Adjustment for covariates:**  
    \(R^2_1\) enters directly into the numerator; no between-block variance term because block effects are constant.

---

### 7.3 BIRA2\_1f: Two-Level Blocked IRA (Fixed Block Effect)

- **Structure:**  
  Two levels: individuals (1) within blocks (2). Individuals are randomized within blocks. Block effects are fixed; the block–treatment interaction is also absorbed (treatment effect does not vary randomly).

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) = \frac{1 - R^2_1}{P(1-P)\,N} \cdot \frac{J}{J - 1}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = J - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_1\) enters directly into the numerator; the \(\frac{J}{J-1}\) factor is the finite-block correction for fixed effects.

---

### 7.4 BIRA2\_1r: Two-Level Blocked IRA (Random Block Effect)

- **Structure:**  
  Two levels: individuals (1) within blocks (2). Individuals are randomized within blocks. Block effects are random; the treatment effect may vary across blocks (characterized by \(\omega_2\)).

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_2\,\omega_2\,(1 - R^2_{t2})}{J}
    + \frac{(1 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = J - 1
    \]

  - **Adjustment for covariates:**  
    Block-level covariates reduce \(\rho_2\,\omega_2\) via \(R^2_{t2}\); individual-level covariates reduce the within-block term via \(R^2_1\).

---

### 7.5 BIRA3\_1r: Three-Level Blocked IRA (Random Effects)

- **Structure:**  
  Three levels: individuals (1) within clusters (2) within blocks (3). Individuals are randomized within clusters; blocks and clusters have random effects. Treatment effect may vary at both the cluster and block level.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_3\,\omega_3\,(1 - R^2_{t3})}{K}
    + \frac{\rho_2\,\omega_2\,(1 - R^2_{t2})}{J\,K}
    + \frac{(1 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,K\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = K - 1
    \]

  - **Adjustment for covariates:**  
    \(R^2_{t3}\) and \(R^2_{t2}\) reduce treatment-effect heterogeneity at levels 3 and 2; \(R^2_1\) reduces within-cluster residual variance.

---

### 7.6 BIRA4\_1r: Four-Level Blocked IRA (Random Effects)

- **Structure:**  
  Four levels: individuals (1) within clusters (2) within sites (3) within blocks (4). Individuals are randomized within clusters; sites, clusters, and blocks all have random effects.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_4\,\omega_4\,(1 - R^2_{t4})}{L}
    + \frac{\rho_3\,\omega_3\,(1 - R^2_{t3})}{K\,L}
    + \frac{\rho_2\,\omega_2\,(1 - R^2_{t2})}{J\,K\,L}
    + \frac{(1 - \rho_4 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,K\,L\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = L - 1
    \]

  - **Adjustment for covariates:**  
    Each \(R^2_{t\ell}\) reduces treatment-effect heterogeneity at the corresponding level; \(R^2_1\) reduces within-cluster residual variance.

---

### 7.7 CRA2\_2r: Two-Level Cluster Random Assignment

- **Structure:**  
  Two levels: individuals (1) within clusters (2). Entire clusters are randomly assigned to treatment or control.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_2(1 - R^2_2)}{P(1-P)\,J}
    + \frac{(1 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,n \cdot \mathrm{rel}_1}
    \]

    where \(\mathrm{rel}_1 \in (0,1]\) is the reliability of the level-1 outcome measure (default 1).

  - **Degrees of freedom:**

    \[
    \text{df} = J - g_2 - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_2\) reduces between-cluster variance; \(R^2_1\) reduces within-cluster variance.

---

### 7.8 CRA3\_3r: Three-Level Cluster Random Assignment

- **Structure:**  
  Three levels: individuals (1) within clusters (2) within districts/schools (3). Level-3 units are randomly assigned.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_3(1 - R^2_3)}{P(1-P)\,K}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,J\,K}
    + \frac{(1 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,K\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = K - g_3 - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_3\), \(R^2_2\), \(R^2_1\) reduce variance at levels 3, 2, and 1 respectively.

---

### 7.9 CRA4\_4r: Four-Level Cluster Random Assignment

- **Structure:**  
  Four levels: individuals (1) within clusters (2) within schools (3) within districts (4). Level-4 units are randomly assigned.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_4(1 - R^2_4)}{P(1-P)\,L}
    + \frac{\rho_3(1 - R^2_3)}{P(1-P)\,K\,L}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,J\,K\,L}
    + \frac{(1 - \rho_4 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,K\,L\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = L - g_4 - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_4\), \(R^2_3\), \(R^2_2\), \(R^2_1\) reduce variance at the corresponding levels.

---

### 7.10 BCRA3\_2f: Three-Level Blocked CRA (Fixed Block Effect)

- **Structure:**  
  Three levels: individuals (1) within clusters (2) within blocks (3). Clusters are randomized within blocks; block effects are fixed (absorbed as intercepts). Assignment at level 2.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \left[
      \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,J}
    + \frac{(1 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,J\,n}
    \right]
    \cdot \frac{K}{K - 1}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = K(J - 1) - 1
    \]

  - **Adjustment for covariates:**  
    \(R^2_2\) and \(R^2_1\) reduce between- and within-cluster variance; the \(\frac{K}{K-1}\) factor is the finite-block correction.

---

### 7.11 BCRA3\_2r: Three-Level Blocked CRA (Random Block Effect)

- **Structure:**  
  Three levels: individuals (1) within clusters (2) within blocks (3). Clusters are randomized within blocks; block effects are random. Treatment effect may vary across blocks (characterized by \(\omega_3\)).

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_3\,\omega_3\,(1 - R^2_{t3})}{K}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,J\,K}
    + \frac{(1 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,J\,K\,n}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = K - g_3 - 1
    \]

  - **Adjustment for covariates:**  
    \(R^2_{t3}\) reduces treatment-effect heterogeneity at the block level; \(R^2_2\) and \(R^2_1\) reduce cluster- and individual-level variance.

---

### 7.12 BCRA4\_2r: Four-Level Blocked CRA (Random Blocks, Assignment at Level 2)

- **Structure:**  
  Four levels: individuals (1) within clusters (2) within level-3 units (3) within blocks (4). Clusters are randomized within level-3 units; blocks are random. Assignment at level 2.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_4(1 - R^2_4)}{P(1-P)\,K}
    + \frac{\rho_3(1 - R^2_3)}{P(1-P)\,K\,L_3}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,L_3\,L_2}
    + \frac{(1 - \rho_4 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,L_3\,L_2\,n}
    \]

    where \(K\) = number of blocks, \(L_3\) = level-3 units per block, \(L_2\) = clusters per level-3 unit.

  - **Degrees of freedom:**

    \[
    \text{df} = K - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_4\), \(R^2_3\), \(R^2_2\), \(R^2_1\) reduce variance at the corresponding levels.

---

### 7.13 BCRA4\_3f: Four-Level Blocked CRA (Fixed Blocks, Assignment at Level 3)

- **Structure:**  
  Four levels: individuals (1) within clusters (2) within sites (3) within blocks (4). Sites are randomized within blocks; block effects are fixed (absorbed). Assignment at level 3.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \left[
      \frac{\rho_3(1 - R^2_3)}{P(1-P)\,K\,J}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,J\,L_2}
    + \frac{(1 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,J\,L_2\,n}
    \right]
    \cdot \frac{K}{K - 1}
    \]

    where \(K\) = blocks (fixed), \(J\) = sites per block, \(L_2\) = clusters per site. \(\rho_4\) is absorbed by the fixed block effects and drops from the variance.

  - **Degrees of freedom:**

    \[
    \text{df} = K(J - 1) - 1
    \]

  - **Adjustment for covariates:**  
    \(R^2_3\), \(R^2_2\), \(R^2_1\) reduce variance at corresponding levels; the \(\frac{K}{K-1}\) factor is the finite-block correction.

---

### 7.14 BCRA4\_3r: Four-Level Blocked CRA (Random Blocks, Assignment at Level 3)

- **Structure:**  
  Four levels: individuals (1) within clusters (2) within sites (3) within blocks (4). Sites are randomized within blocks; block effects are random. Assignment at level 3.

- **Key formulas:**

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) =
    \frac{\rho_4(1 - R^2_4)}{P(1-P)\,K}
    + \frac{\rho_3(1 - R^2_3)}{P(1-P)\,K\,J}
    + \frac{\rho_2(1 - R^2_2)}{P(1-P)\,K\,J\,L_2}
    + \frac{(1 - \rho_4 - \rho_3 - \rho_2)(1 - R^2_1)}{P(1-P)\,K\,J\,L_2\,n}
    \]

    where \(K\) = blocks (random), \(J\) = sites per block, \(L_2\) = clusters per site.

  - **Degrees of freedom:**

    \[
    \text{df} = K - 2
    \]

  - **Adjustment for covariates:**  
    \(R^2_4\), \(R^2_3\), \(R^2_2\), \(R^2_1\) reduce variance at corresponding levels.

---

### 7.15 ITS: Interrupted Time Series

- **Structure:**  
  Single time series of \(T = T_{\text{pre}} + T_{\text{post}}\) equally-spaced observations. Intervention occurs between \(T_{\text{pre}}\) and \(T_{\text{post}}\). Errors follow an AR(1) process with autocorrelation \(\varphi\).

- **Key formulas:**

  - **Effective sample size (AR(1) adjustment):**

    \[
    N_{\text{eff}} = T \cdot \frac{1 - \varphi}{1 + \varphi}
    \]

  - **Variance of the level-change estimator \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) = \frac{1}{N_{\text{eff}}}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = \lfloor N_{\text{eff}} \rceil - 2
    \]

  - **Adjustment for covariates:**  
    Not directly parameterized in the current engine; outcome variance is normalized to 1 (standardized scale).

---

### 7.16 RD2\_1f: Regression Discontinuity (2-Level, Fixed)

- **Structure:**  
  Sharp RD with a single continuous running variable, single cutoff, and global linear specification. Two-level structure; higher-level effects treated as fixed. Assignment is determined by the running variable exceeding the cutoff.

- **Key formulas:**

  - **Effective sample size near the cutoff:**

    \[
    N_{\text{eff}} = N \cdot \min\!\left(\frac{h}{\sigma_X},\, 1\right)
    \]

    where \(h\) is the bandwidth and \(\sigma_X\) is the standard deviation of the running variable.

  - **Variance of \(\hat{\delta}\):**

    \[
    \operatorname{Var}(\hat{\delta}) = \frac{1}{N_{\text{eff}}}
    \]

  - **Degrees of freedom:**

    \[
    \text{df} = \lfloor N_{\text{eff}} \rceil - 2
    \]

  - **Adjustment for covariates:**  
    Not directly parameterized in the current engine; outcome variance is normalized to 1 (standardized scale).

---

### 7.17 RD2\_1r: Regression Discontinuity (2-Level, Random)

- **Structure:**  
  Sharp RD identical in structure to RD2\_1f, but higher-level effects are treated as random. The current engine uses the same analytic approximation as RD2\_1f.

- **Key formulas:**

  Same as [Section 7.16 (RD2\_1f)](#716-rd2_1f-regression-discontinuity-2-level-fixed).

---

### 7.18 RD3\_1f: Regression Discontinuity (3-Level, Fixed)

- **Structure:**  
  Sharp RD in a three-level setting (e.g., students within classrooms within schools). Running variable operates at level 1; higher-level effects treated as fixed. The current engine uses the same bandwidth-scaled approximation as the 2-level designs.

- **Key formulas:**

  Same base formula as [Section 7.16 (RD2\_1f)](#716-rd2_1f-regression-discontinuity-2-level-fixed):

  \[
  N_{\text{eff}} = N \cdot \min\!\left(\frac{h}{\sigma_X},\, 1\right),
  \quad
  \operatorname{Var}(\hat{\delta}) = \frac{1}{N_{\text{eff}}},
  \quad
  \text{df} = \lfloor N_{\text{eff}} \rceil - 2
  \]

---

### 7.19 RD3\_1r: Regression Discontinuity (3-Level, Random)

- **Structure:**  
  Sharp RD in a three-level setting. Higher-level effects treated as random. The current engine uses the same analytic approximation as RD3\_1f.

- **Key formulas:**

  Same as [Section 7.18 (RD3\_1f)](#718-rd3_1f-regression-discontinuity-3-level-fixed).
