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

## 7. Placeholders for design-specific formulas

Add subsections here for each concrete design, for example:

### 7.1 Design X: [plain-language name]

- **Structure:**  
  Brief description (levels, randomization unit, blocking).

- **Key formulas:**

  - **Variance of \(\hat{\tau}\):**
    
    \[
    \operatorname{Var}(\hat{\tau}) = \dots
    \]

  - **Degrees of freedom:**
    
    \[
    \text{df}_\tau = \dots
    \]

  - **Adjustment for covariates:**
    
    \[
    \operatorname{Var}_{\text{adj}}(\hat{\tau}) = \dots
    \]

Repeat for each design supported by the engine.
