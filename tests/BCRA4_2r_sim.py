import numpy as np
import pandas as pd
from statsmodels.regression.mixed_linear_model import MixedLM
from mdes_engines.mdes_four_level import compute_mdes_bcra4_2

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

def simulate_bcra4_2r_once(
    K=10, L3=4, L2=3, n=20,
    icc4=0.05, icc3=0.1, icc2=0.15,
    delta=0.20,  # true effect size
):
    # Variance decomposition
    sigma2_total = 1.0
    sigma2_4 = icc4 * sigma2_total
    sigma2_3 = icc3 * sigma2_total
    sigma2_2 = icc2 * sigma2_total
    sigma2_1 = (1 - icc4 - icc3 - icc2) * sigma2_total

    rows = []
    cluster_id = 0

    for b in range(K):
        u4 = np.random.normal(0, np.sqrt(sigma2_4))

        for s in range(L3):
            u3 = np.random.normal(0, np.sqrt(sigma2_3))

            # Randomize clusters within site
            treat_assign = np.random.binomial(1, 0.5, size=L2)

            for c in range(L2):
                u2 = np.random.normal(0, np.sqrt(sigma2_2))
                T = treat_assign[c]

                for i in range(n):
                    e = np.random.normal(0, np.sqrt(sigma2_1))
                    Y = delta * T + u4 + u3 + u2 + e

                    rows.append({
                        "Y": Y,
                        "T": T,
                        "block": b,
                        "site": f"{b}-{s}",
                        "cluster": f"{b}-{s}-{c}",
                    })

    return pd.DataFrame(rows)


def estimate_once(df):
    model = MixedLM.from_formula(
        "Y ~ T",
        groups="block",
        re_formula="1",
        vc_formula={
            "site": "0 + C(site)",
            "cluster": "0 + C(cluster)",
        },
        data=df,
    )
    result = model.fit(reml=True, method="lbfgs", disp=False)
    return result.params["T"], result.bse["T"]


res = compute_mdes_bcra4_2(
    n_level4=10,
    n_level3=4,
    n_level2=3,
    cluster_size=20,
    icc4=0.02,
    icc3=0.05,
    icc2=0.10,
    r2_level1=0.0,
    r2_level2=0.0,
    r2_level3=0.0,
    alpha=0.05,
    power=0.80,
    outcome_type="continuous",
    outcome_sd=1.0,
)
print(res.mdes, res.se)


def run_simulation(
    reps=500,
    K=10, L3=4, L2=3, n=20,
    icc4=0.02, icc3=0.05, icc2=0.10,
    delta=res.mdes,
):
    ests = []
    ses = []

    for _ in range(reps):
        df = simulate_bcra4_2r_once(K, L3, L2, n, icc4, icc3, icc2, delta)
        est, se = estimate_once(df)
        ests.append(est)
        ses.append(se)

    return np.array(ests), np.array(ses)

x =  run_simulation()
print(f"Empirical power: {(np.abs(x[0]) > 1.96 * x[1]).mean():.3f}")
print(f"Empirical SE: {x[0].std():.3f}")
print(f"Analytic SE: {x[1].mean():.3f}")
print(f"Average estimate: {x[0].mean():.3f}, Average SE: {x[1].mean():.3f}")
print(f"MDES from simulation: {x[0].mean() / x[1].mean():.3f}")
