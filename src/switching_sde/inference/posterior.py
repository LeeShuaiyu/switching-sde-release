from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/posterior_utils.py", explicit_legacy_root)


def build_posterior_predictions(*args, explicit_legacy_root: str = "", **kwargs):
    mod = legacy_module(explicit_legacy_root)
    return mod.build_posterior_predictions(*args, **kwargs)
