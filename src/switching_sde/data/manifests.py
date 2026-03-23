from __future__ import annotations

from pathlib import Path

from switching_sde.data.io import read_json, write_json


def load_manifest(path: str | Path):
    return read_json(path)


def save_manifest(path: str | Path, manifest) -> None:
    write_json(path, manifest)
