from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class ExperimentConfig:
    experiment_name: str
    suite: str
    data_version: str
    split_hash: str
    drift_family: str
    task_mode: str
    inference_mode: str
    backbone: str
    artifact_policy: str
    legacy_root: str
    output_root: str
    scenario: str = ""
    primary_method: str = ""
    legacy_report_root: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_ALLOWED = {
    "drift_family": {"ou", "duffing"},
    "task_mode": {"changepoint", "segmentation"},
    "inference_mode": {"deterministic", "posterior"},
    "artifact_policy": {"live", "frozen", "auto"},
}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is not None:
        with path.open("r", encoding="utf-8") as f:
            obj = yaml.safe_load(f) or {}
    else:
        # Minimal parser for flat "key: value" files used in this repository.
        obj = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            key = k.strip()
            val = v.strip()
            if val.startswith("\"") and val.endswith("\""):
                val = val[1:-1]
            elif val.lower() in {"true", "false"}:
                val = val.lower() == "true"
            obj[key] = val
    if not isinstance(obj, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return obj


def _validate(cfg: ExperimentConfig) -> None:
    for k, allowed in _ALLOWED.items():
        val = getattr(cfg, k)
        if val not in allowed:
            raise ValueError(f"Invalid {k}={val!r}, allowed={sorted(allowed)}")


def load_experiment_config(experiment_name: str, *, config_root: Path | None = None) -> ExperimentConfig:
    root = config_root or Path(__file__).resolve().parent
    defaults = _read_yaml(root / "defaults.yaml")
    exp_file = root / "experiments" / f"{experiment_name}.yaml"
    if not exp_file.exists():
        raise FileNotFoundError(f"Experiment config not found: {exp_file}")
    exp = _read_yaml(exp_file)
    merged = {**defaults, **exp}
    merged.setdefault("experiment_name", experiment_name)
    merged.setdefault("suite", "paper_full")
    merged.setdefault("data_version", "")
    merged.setdefault("split_hash", "")
    merged.setdefault("drift_family", "ou")
    merged.setdefault("task_mode", "changepoint")
    merged.setdefault("inference_mode", "posterior")
    merged.setdefault("backbone", "lstm")
    merged.setdefault("artifact_policy", "auto")
    merged.setdefault("legacy_root", "")
    merged.setdefault("output_root", "")
    cfg = ExperimentConfig(**merged)
    _validate(cfg)
    return cfg
