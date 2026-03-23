#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import tarfile
from pathlib import Path


_SKIP_PATTERNS = [
    "._*",
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".venv",
    "dist",
]


def _should_skip(path: Path) -> bool:
    name = path.name
    for pat in _SKIP_PATTERNS:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


def _add_path(tf: tarfile.TarFile, src: Path, arcname: str) -> None:
    if not src.exists():
        return
    if _should_skip(src):
        return
    if src.is_file():
        tf.add(src, arcname=arcname, recursive=False)
        return

    # Directory: walk explicitly to keep strict filtering.
    tf.add(src, arcname=arcname, recursive=False)
    for child in sorted(src.iterdir(), key=lambda p: p.name):
        child_arc = f"{arcname}/{child.name}"
        _add_path(tf, child, child_arc)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build release bundle (lite/full)")
    ap.add_argument("--mode", choices=["lite", "full"], default="lite")
    ap.add_argument("--output", default="dist/switching_sde_release.tar.gz")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    out = (root / args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    always_include = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "setup.py",
        "Makefile",
        ".gitignore",
        ".github/workflows/ci.yml",
        "src",
        "scripts",
        "tests",
        "assets/manifests",
        "reports/paper",
    ]

    with tarfile.open(out, "w:gz") as tf:
        for rel in always_include:
            src = root / rel
            _add_path(tf, src, rel)
        if args.mode == "full":
            _add_path(tf, root / "assets/linked", "assets/linked")

    print(f"[ok] bundle created: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
