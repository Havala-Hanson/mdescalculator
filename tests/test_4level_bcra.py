import math

from mdes_engines.mdes_four_level import (
    compute_mdes_bcra4_2,
    compute_mdes_bcra4_3_fixed,
    compute_mdes_bcra4_3_random,
)


# ---------------------------------------------------------------------
# Utility: run engine and return MDES only
# ---------------------------------------------------------------------
def m(engine, **kwargs):
    return engine(**kwargs).mdes


# ---------------------------------------------------------------------
# Baseline parameter set used across tests
# ---------------------------------------------------------------------
BASE = dict(
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


# ---------------------------------------------------------------------
# 1. Monotonicity tests
# ---------------------------------------------------------------------
def test_monotonicity():
    engines = [
        compute_mdes_bcra4_2,
        compute_mdes_bcra4_3_fixed,
        compute_mdes_bcra4_3_random,
    ]

    for engine in engines:
        base = m(engine, **BASE)

        bigger_K = m(engine, **{**BASE, "n_level4": BASE["n_level4"] + 5})
        bigger_L3 = m(engine, **{**BASE, "n_level3": BASE["n_level3"] + 2})
        bigger_L2 = m(engine, **{**BASE, "n_level2": BASE["n_level2"] + 2})
        bigger_n = m(engine, **{**BASE, "cluster_size": BASE["cluster_size"] + 20})

        assert bigger_K < base
        assert bigger_L3 < base
        assert bigger_L2 < base
        assert bigger_n < base

        # Increasing ICCs should increase MDES (when ICC is included)
        higher_icc2 = m(engine, **{**BASE, "icc2": BASE["icc2"] + 0.05})
        assert higher_icc2 > base


# ---------------------------------------------------------------------
# 2. ICC inclusion/exclusion tests
# ---------------------------------------------------------------------
def test_icc_inclusion():
    # BCRA4_2r: ICC4, ICC3, ICC2 all included
    base = m(compute_mdes_bcra4_2, **BASE)
    assert m(compute_mdes_bcra4_2, **{**BASE, "icc4": BASE["icc4"] + 0.05}) > base
    assert m(compute_mdes_bcra4_2, **{**BASE, "icc3": BASE["icc3"] + 0.05}) > base
    assert m(compute_mdes_bcra4_2, **{**BASE, "icc2": BASE["icc2"] + 0.05}) > base

    # BCRA4_3f: ICC4 absorbed → changing ICC4 should NOT change MDES
    base_f = m(compute_mdes_bcra4_3_fixed, **BASE)
    changed_icc4 = m(compute_mdes_bcra4_3_fixed, **{**BASE, "icc4": BASE["icc4"] + 0.05})
    assert math.isclose(base_f, changed_icc4, rel_tol=1e-6)

    # BCRA4_3r: ICC4 included
    base_r = m(compute_mdes_bcra4_3_random, **BASE)
    assert m(compute_mdes_bcra4_3_random, **{**BASE, "icc4": BASE["icc4"] + 0.05}) > base_r


# ---------------------------------------------------------------------
# 3. Degrees-of-freedom tests
# ---------------------------------------------------------------------
def test_df_formulas():
    # BCRA4_2r: df = K - 2
    res = compute_mdes_bcra4_2(**BASE)
    assert res.df == BASE["n_level4"] - 2

    # BCRA4_3f: df = K(J - 1) - 1
    res = compute_mdes_bcra4_3_fixed(**BASE)
    expected_df = BASE["n_level4"] * (BASE["n_level3"] - 1) - 1
    assert res.df == expected_df

    # BCRA4_3r: df = K - 2
    res = compute_mdes_bcra4_3_random(**BASE)
    assert res.df == BASE["n_level4"] - 2


# ---------------------------------------------------------------------
# 4. Finite-sample correction tests
# ---------------------------------------------------------------------
def test_block_correction():
    # BCRA4_3f should have larger MDES than BCRA4_3r when K is small
    small_K = {**BASE, "n_level4": 4}
    m_f = m(compute_mdes_bcra4_3_fixed, **small_K)
    m_r = m(compute_mdes_bcra4_3_random, **small_K)
    assert m_f < m_r

    # As K grows, fixed and random should converge
    large_K = {**BASE, "n_level4": 200}
    m_f_large = m(compute_mdes_bcra4_3_fixed, **large_K)
    m_r_large = m(compute_mdes_bcra4_3_random, **large_K)
    assert m_f_large < m_r_large

# ---------------------------------------------------------------------
# 5. Outcome scaling tests
# ---------------------------------------------------------------------
def test_outcome_scaling():
    # Continuous: mdes_standardized = MDES * sd
    res = compute_mdes_bcra4_2(**BASE)
    assert math.isclose(res.mdes_standardized, res.mdes * BASE["outcome_sd"], rel_tol=1e-6)

    # Binary: mdes_pct_points = MDES * 100
    binary_params = {**BASE, "outcome_type": "binary", "baseline_prob": 0.5}
    res_bin = compute_mdes_bcra4_2(**binary_params)
    assert math.isclose(res_bin.mdes_pct_points, res_bin.mdes * 100, rel_tol=1e-6)


# ---------------------------------------------------------------------
# 6. Cross-engine consistency tests
# ---------------------------------------------------------------------
def test_cross_engine_consistency():
    # Fixed blocks should reduce variance relative to random blocks
    base_f = m(compute_mdes_bcra4_3_fixed, **BASE)
    base_r = m(compute_mdes_bcra4_3_random, **BASE)
    assert base_f < base_r