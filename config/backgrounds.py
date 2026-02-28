FAMILY_BACKGROUNDS = {
    "IRA": r"""
**Model:** \(Y_i = \beta_0 + \delta T_i + e_i\)

**MDES formula** (Bloom et al., 2007):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{\frac{1 - R^2}{P(1-P)N}}
\]

where \(N\) is total sample size and \(P\) is the treatment proportion.
""",

    "CRA": r"""
**Model:** \(Y_{ij} = \beta_0 + \delta T_j + u_j + e_{ij}\)

**MDES formula** (Bloom et al., 2007; Dong & Maynard, 2013):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho(1 - R^2_2)}{P(1-P)J}
    + \frac{(1-\rho)(1 - R^2_1)}{P(1-P)Jn}
}
\]

where \(\rho\) is the ICC, \(J\) clusters, \(n\) cluster size.
""",

    "BCRA": r"""
**Model:** \(Y_{ijb} = \beta_0 + \delta T_{jb} + \gamma_b + u_{jb} + e_{ijb}\)

Blocked CRTs adjust for block‑level differences.

**MDES formula** (Dong & Maynard, 2013):

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{\rho(1 - R^2_2)}{P(1-P)J}
    + \frac{(1-\rho)(1 - R^2_1)}{P(1-P)Jn}
    - \frac{\text{BlockVar}}{P(1-P)J}
}
\]

where BlockVar depends on fixed vs random block effects.
""",

    "BIRA": r"""
Blocked individual random assignment adjusts for block‑level differences.

**Model:** \(Y_{ib} = \beta_0 + \delta T_{ib} + \gamma_b + e_{ib}\)

**MDES formula**:

\[
\text{MDES} = M_{\alpha,\nu} \cdot \sqrt{
    \frac{1 - R^2}{P(1-P)N}
    - \frac{\text{BlockVar}}{P(1-P)B}
}
\]

where \(B\) is number of blocks.
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