from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/generator_switching_duffing.py", explicit_legacy_root)


def sample_data(*args, explicit_legacy_root: str = "", **kwargs):
    mod = legacy_module(explicit_legacy_root)
    fn = getattr(mod, "sample_data", None) or getattr(mod, "sample_switching_duffing", None)
    if fn is None:
        raise AttributeError("Legacy Duffing generator module does not expose sample_data/sample_switching_duffing")
    return fn(*args, **kwargs)
