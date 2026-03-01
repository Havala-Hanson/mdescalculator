import pytest

from config.designs import DESIGNS
from config.calculator_defaults import DESIGN_CONFIGS

REQUIRED_KEYS = {
    "sample_fields",
    "icc_fields",
    "covariate_fields",
    "block_fields",
    "cluster_fields",
    "rd_fields",
    "its_fields",
    "engine",
}

def test_all_designs_have_configs():
    design_codes = {d.code for d in DESIGNS}
    config_codes = set(DESIGN_CONFIGS.keys())

    missing = design_codes - config_codes
    extra = config_codes - design_codes

    assert not missing, f"Missing configs for: {sorted(missing)}"
    assert not extra, f"Configs exist for unknown designs: {sorted(extra)}"


def test_all_configs_have_required_keys():
    errors = []

    for code, cfg in DESIGN_CONFIGS.items():
        missing = REQUIRED_KEYS - set(cfg.keys())
        if missing:
            errors.append(f"{code} missing keys: {sorted(missing)}")

    assert not errors, "Some configs are missing required keys:\n" + "\n".join(errors)


def test_covariate_fields_match_levels():
    """
    Ensures r2_levelK fields match the design's number of levels.
    Example: levels=3 → r2_level1, r2_level2, r2_level3
    """
    errors = []

    for d in DESIGNS:
        cfg = DESIGN_CONFIGS[d.code]
        cov = cfg["covariate_fields"]

        expected = [f"r2_level{i}" for i in range(1, d.levels + 1)]
        if cov != expected:
            errors.append(
                f"{d.code}: covariate_fields={cov} but expected {expected} "
                f"(levels={d.levels})"
            )

    assert not errors, "Covariate field mismatches:\n" + "\n".join(errors)


def test_block_fields_only_when_blocked():
    errors = []

    for d in DESIGNS:
        cfg = DESIGN_CONFIGS[d.code]
        block_fields = cfg["block_fields"]

        if d.is_blocked and "n_blocks" not in block_fields:
            errors.append(f"{d.code} is blocked but missing n_blocks")

        if not d.is_blocked and block_fields:
            errors.append(f"{d.code} is not blocked but has block_fields={block_fields}")

    assert not errors, "Block field inconsistencies:\n" + "\n".join(errors)


def test_rd_fields_only_for_rd_designs():
    errors = []

    for d in DESIGNS:
        cfg = DESIGN_CONFIGS[d.code]
        rd_fields = cfg["rd_fields"]

        if d.design_family == "RD":
            if rd_fields != ["bandwidth", "running_var_sd"]:
                errors.append(f"{d.code}: RD fields incorrect: {rd_fields}")
        else:
            if rd_fields:
                errors.append(f"{d.code}: non-RD design has rd_fields={rd_fields}")

    assert not errors, "RD field inconsistencies:\n" + "\n".join(errors)


def test_its_fields_only_for_its_designs():
    errors = []

    for d in DESIGNS:
        cfg = DESIGN_CONFIGS[d.code]
        its_fields = cfg["its_fields"]

        if d.design_family == "ITS":
            if its_fields != ["autocorrelation"]:
                errors.append(f"{d.code}: ITS fields incorrect: {its_fields}")
        else:
            if its_fields:
                errors.append(f"{d.code}: non-ITS design has its_fields={its_fields}")

    assert not errors, "ITS field inconsistencies:\n" + "\n".join(errors)