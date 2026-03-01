import inspect
import pytest

from config.designs import DESIGNS
from config.calculator_defaults import DESIGN_CONFIGS
from services.calculator_ui import ENGINE_MAP


def test_engine_signatures_match_configs():
    """
    Ensures that:
    1. Every design's engine exists in ENGINE_MAP.
    2. Every field in calculator_config is accepted by the engine.
    3. Every required engine parameter is provided by calculator_config.
    """

    errors = []

    for d in DESIGNS:
        cfg = DESIGN_CONFIGS[d.code]
        engine_name = cfg.get("engine")

        # 1. Engine must exist
        if engine_name not in ENGINE_MAP:
            errors.append(f"{d.code}: engine '{engine_name}' not found in ENGINE_MAP")
            continue

        engine_fn = ENGINE_MAP[engine_name]
        sig = inspect.signature(engine_fn)
        params = list(sig.parameters.keys())

        # 2. Fields UI will pass to engine
        config_fields = (
            cfg["sample_fields"]
            + cfg["icc_fields"]
            + cfg["covariate_fields"]
            + cfg["block_fields"]
            + cfg["cluster_fields"]
            + cfg["rd_fields"]
            + cfg["its_fields"]
            + ["alpha", "power", "outcome_type", "baseline_prob", "outcome_sd"]
        )

        # 3. Check: config fields must be accepted by engine
        for field in config_fields:
            if field not in params:
                errors.append(
                    f"{d.code}: field '{field}' is in calculator_config "
                    f"but not accepted by engine '{engine_name}'"
                )

        # 4. Check: engine required parameters must be in config
        for p in params:
            if sig.parameters[p].default is inspect._empty and p not in config_fields:
                errors.append(
                    f"{d.code}: engine '{engine_name}' requires parameter '{p}' "
                    f"but calculator_config does not provide it"
                )

    assert not errors, "Engine signature mismatches:\n" + "\n".join(errors)