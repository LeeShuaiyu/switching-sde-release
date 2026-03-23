from __future__ import annotations

import os
import shutil
import sys
import subprocess
from pathlib import Path

try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    plt = None

from switching_sde.artifacts.frozen_loader import load_experiment_eval_json
from switching_sde.config.schema import ExperimentConfig
from switching_sde.pipelines.evaluate import resolve_live_assets_for_experiment
from switching_sde.utils.logging import get_logger

logger = get_logger(__name__)


def _live_assets_for_viz(cfg: ExperimentConfig, legacy_root: Path) -> tuple[Path | None, Path | None]:
    return resolve_live_assets_for_experiment(cfg, legacy_root)


def _plot_metric_bars(rows: list[dict], metric: str, out_file: Path, title: str) -> None:
    if plt is None:
        return
    vals = []
    labels = []
    for r in rows:
        method = r.get("method", r.get("method_id", r.get("Method", "unknown")))
        try:
            v = float(r.get(metric, "nan"))
        except Exception:
            continue
        if v != v:
            continue
        labels.append(str(method))
        vals.append(v)

    if not vals:
        return

    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(max(8, len(labels) * 0.6), 4.5))
    plt.bar(range(len(vals)), vals)
    plt.xticks(range(len(vals)), labels, rotation=40, ha="right")
    plt.ylabel(metric)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()


def run_frozen_viz(cfg: ExperimentConfig, legacy_root: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    # Prefer copying existing legacy figures for fidelity.
    if cfg.suite == "paper_full":
        figure_dir = legacy_root / "reports" / "paper_full" / "figures"
    elif cfg.suite == "p5":
        figure_dir = legacy_root / "reports" / "p5" / "figures"
    else:
        figure_dir = legacy_root / "reports" / "p6_nonlinear_full_v3" / "figures"

    if figure_dir.exists():
        for p in sorted(figure_dir.glob("*.png")):
            target = out_dir / p.name
            shutil.copy2(p, target)
            copied.append(str(target.resolve()))

    # Also generate compact metric bars from frozen eval json.
    rows = load_experiment_eval_json(legacy_root, cfg.experiment_name)
    _plot_metric_bars(rows, "mae_time", out_dir / f"{cfg.experiment_name}_mae_time.png", f"{cfg.experiment_name}: MAE(time)")
    _plot_metric_bars(rows, "f1@0.02", out_dir / f"{cfg.experiment_name}_f1_002.png", f"{cfg.experiment_name}: F1@2%")

    return {
        "mode": "frozen",
        "copied_figures": copied,
        "output_dir": str(out_dir.resolve()),
    }


def run_live_viz(cfg: ExperimentConfig, legacy_root: Path, out_dir: Path) -> dict:
    ckpt, data_file = _live_assets_for_viz(cfg, legacy_root)
    if ckpt is None or data_file is None:
        raise FileNotFoundError("Live visualization assets not available.")

    script = legacy_root / "switching" / "visualize_predictions.py"
    if not script.exists():
        raise FileNotFoundError(f"Legacy visualize script missing: {script}")

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(script),
        "--checkpoint",
        str(ckpt),
        "--split",
        "test",
        "--output-dir",
        str(out_dir),
    ]
    env = os.environ.copy()
    omp = str(env.get("OMP_NUM_THREADS", "")).strip()
    if not omp.isdigit() or int(omp) <= 0:
        env["OMP_NUM_THREADS"] = "1"

    logger.info("Running live viz: %s", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(legacy_root),
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Live viz failed: {proc.stderr.strip()}")
    return {"mode": "live", "output_dir": str(out_dir.resolve())}


def run_visualization(cfg: ExperimentConfig, *, mode: str, legacy_root: Path, out_dir: Path) -> dict:
    if mode == "frozen":
        return run_frozen_viz(cfg, legacy_root, out_dir)
    if mode == "live":
        return run_live_viz(cfg, legacy_root, out_dir)
    if mode == "auto":
        try:
            return run_live_viz(cfg, legacy_root, out_dir)
        except Exception as exc:
            logger.warning("Auto mode fallback to frozen viz: %s", exc)
            payload = run_frozen_viz(cfg, legacy_root, out_dir)
            payload["fallback_reason"] = str(exc)
            return payload
    raise ValueError(f"Unsupported mode: {mode}")
