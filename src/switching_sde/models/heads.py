from __future__ import annotations

from switching_sde.utils.legacy_import import load_legacy_module


def legacy_module(explicit_legacy_root: str = ""):
    return load_legacy_module("switching/models/heads.py", explicit_legacy_root)


def available_heads(explicit_legacy_root: str = "") -> list[str]:
    mod = legacy_module(explicit_legacy_root)
    names = []
    for attr, tag in [
        ("SequenceCPHead", "sequence_cp"),
        ("CPRegHead", "cp_regression"),
        ("SplitPosteriorHead", "split_posterior"),
        ("StateSegHead", "state_segmentation"),
    ]:
        if hasattr(mod, attr):
            names.append(tag)
    return names
