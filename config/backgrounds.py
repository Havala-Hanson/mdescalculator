FAMILY_BACKGROUNDS = {
    "IRA": r"""
**Model:** \(Y_i = \beta_0 + \delta T_i + e_i\)

**MDES formula** (Bloom et al., 2007):

\[
	ext{MDES} = M_{\alpha,\nu} \cdot \sqrt{\frac{1 - R^2}{P(1-P)N}}
\]

where \(N\) is total sample size and \(P\) is the treatment proportion.
""",
    "BCRA3_2f": r"""
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
"""
,
    "BCRA3_2r": r"""
**Model:** [Placeholder for BCRA3_2r model]

**MDES formula:**

\[
	ext{[Placeholder for BCRA3_2r formula]}
\]
""",
    "BCRA4_2r": r"""
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


\[
	ext{[Placeholder for BCRA4_2r formula]}
\]
""",
    "BCRA4_3f": r"""
**Model:** [Placeholder for BCRA4_3f model]

**MDES formula:**

\[
	ext{[Placeholder for BCRA4_3f formula]}
\]
""",
    "BCRA4_3r": r"""
**Model:** [Placeholder for BCRA4_3r model]

**MDES formula:**

\[
	ext{[Placeholder for BCRA4_3r formula]}
\]
""",
    "BIRA2_1c": r"""
**Model:** [Placeholder for BIRA2_1c model]

**MDES formula:**

\[
	ext{[Placeholder for BIRA2_1c formula]}
\]
""",
    "BIRA2_1f": r"""
**Model:** [Placeholder for BIRA2_1f model]

**MDES formula:**

\[
	ext{[Placeholder for BIRA2_1f formula]}
\]
""",
    "BIRA2_1r": r"""
**Model:** [Placeholder for BIRA2_1r model]

**MDES formula:**

\[
	ext{[Placeholder for BIRA2_1r formula]}
\]
""",
    "BIRA3_1r": r"""
**Model:** [Placeholder for BIRA3_1r model]

**MDES formula:**

\[
	ext{[Placeholder for BIRA3_1r formula]}
\]
""",
    "BIRA4_1r": r"""
**Model:** [Placeholder for BIRA4_1r model]

**MDES formula:**

\[
	ext{[Placeholder for BIRA4_1r formula]}
\]
""",
    "CRA2_2r": r"""
**Model:** [Placeholder for CRA2_2r model]

**MDES formula:**

\[
	ext{[Placeholder for CRA2_2r formula]}
\]
""",
    "CRA3_3r": r"""
**Model:** [Placeholder for CRA3_3r model]

**MDES formula:**

\[
	ext{[Placeholder for CRA3_3r formula]}
\]
""",
    "CRA4_4r": r"""
**Model:** [Placeholder for CRA4_4r model]

**MDES formula:**

\[
	ext{[Placeholder for CRA4_4r formula]}
\]
""",
    "ITS": r"""
**Model:** [Placeholder for ITS model]

**MDES formula:**

\[
	ext{[Placeholder for ITS formula]}
\]
""",
    "RD2_1f": r"""
**Model:** [Placeholder for RD2_1f model]

**MDES formula:**

\[
	ext{[Placeholder for RD2_1f formula]}
\]
""",
    "RD2_1r": r"""
**Model:** [Placeholder for RD2_1r model]

**MDES formula:**

\[
	ext{[Placeholder for RD2_1r formula]}
\]
""",
    "RD3_1f": r"""
**Model:** [Placeholder for RD3_1f model]

**MDES formula:**

\[
	ext{[Placeholder for RD3_1f formula]}
\]
""",
    "RD3_1r": r"""
**Model:** [Placeholder for RD3_1r model]

**MDES formula:**

\[
	ext{[Placeholder for RD3_1r formula]}
\]
""",
}

DESIGN_BACKGROUNDS = {
    "RD": r"""
**Model:** \(Y_i = \beta_0 + \tau D_i + f(X_i - c) + e_i\)

Regression discontinuity identifies a local treatment effect at the cutoff \(c\).

**MDES formula** depends on:
- running variable variance
- bandwidth
- functional form
- cluster structure (if applicable)
""",

    "ITS": r"""
**Model:** \(Y_t = \beta_0 + \beta_1 t + \delta D_t + \beta_2 (t \cdot D_t) + e_t\)

Interrupted time series estimates level and slope changes after an intervention.

**MDES formula** depends on:
- pre/post timepoints
- autocorrelation
- trend variance
""",
}

# Optional overrides for specific designs
DESIGN_OVERRIDES = {
    "CRA2_2r": r"""...""",
    "RD3_2f": r"""...""",
}