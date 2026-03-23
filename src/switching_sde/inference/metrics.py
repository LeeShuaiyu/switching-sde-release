from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/metrics.py", explicit_legacy_root)


def compute_event_metrics(*args, explicit_legacy_root: str = "", **kwargs):
    mod = legacy_module(explicit_legacy_root)
    return mod.compute_event_metrics(*args, **kwargs)
