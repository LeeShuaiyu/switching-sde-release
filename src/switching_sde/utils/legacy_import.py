from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path

from switching_sde.utils.paths import legacy_root


@lru_cache(maxsize=32)
def load_legacy_module(module_rel_path: str, explicit_legacy_root: str = ""):
    root = legacy_root(explicit_legacy_root)
    file_path = (root / module_rel_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Legacy module not found: {file_path}")

    module_name = "_legacy_" + module_rel_path.replace("/", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec from: {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_legacy_file(path_rel: str, explicit_legacy_root: str = "") -> Path:
    root = legacy_root(explicit_legacy_root)
    return (root / path_rel).resolve()
