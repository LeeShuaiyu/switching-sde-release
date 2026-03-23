from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/models/switching_estimator.py", explicit_legacy_root)


def estimator_class(explicit_legacy_root: str = ""):
    mod = legacy_module(explicit_legacy_root)
    if not hasattr(mod, "SwitchingEstimator"):
        raise AttributeError("Legacy module missing SwitchingEstimator")
    return mod.SwitchingEstimator
