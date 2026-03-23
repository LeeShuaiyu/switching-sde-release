from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/calibration.py", explicit_legacy_root)


def fit_temperature_scaling(*args, explicit_legacy_root: str = "", **kwargs):
    mod = legacy_module(explicit_legacy_root)
    return mod.fit_temperature_scaling(*args, **kwargs)
