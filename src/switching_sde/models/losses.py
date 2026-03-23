from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/losses.py", explicit_legacy_root)


def compute_multitask_loss(*args, explicit_legacy_root: str = "", **kwargs):
    mod = legacy_module(explicit_legacy_root)
    if not hasattr(mod, "compute_multitask_loss"):
        raise AttributeError("Legacy module missing compute_multitask_loss")
    return mod.compute_multitask_loss(*args, **kwargs)
