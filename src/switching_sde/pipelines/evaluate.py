from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

from switching_sde.artifacts.frozen_loader import export_frozen_eval_summary
from switching_sde.artifacts.registry import load_registry
from switching_sde.config.schema import ExperimentConfig
from switching_sde.utils.logging import get_logger
from switching_sde.utils.paths import manifests_dir

logger = get_logger(__name__)


def _method_match(candidate: str, target: str) -> bool:
    c = candidate.lower()
    t = target.lower()
    return t in c or c in t


def _resolve_live_dataset(cfg: ExperimentConfig, legacy_root: Path) -> Path | None:
    data_root = legacy_root / "data" / "switching_ou"
    if cfg.data_version:
        p = data_root / f"switching_ou_test_{cfg.data_version}.pkl"
        if p.exists():
            return p
    if cfg.data_version == "fixed_v2":
        p = data_root / "switching_ou_test.pkl"
        if p.exists():
            return p
    return None


def _resolve_live_checkpoint(cfg: ExperimentConfig, legacy_root: Path) -> Path | None:
    lock = manifests_dir() / "artifacts.lock.json"
    records = []
    if lock.exists():
        try:
            reg = load_registry(lock)
            records = [r for r in reg.records if r.kind == "checkpoint" and r.status == "ready"]
        except Exception:
            records = []

    if records:
        scen = (cfg.scenario or "").strip().lower()
        method = (cfg.primary_method or "").strip()
        filtered = records
        if scen:
            filtered = [r for r in filtered if str(r.scenario).strip().lower() == scen]
        if method:
            filtered = [r for r in filtered if _method_match(str(r.method), method)]

        def _score(r):
            # Prefer seed42, then smaller seed, then lexical path.
            seed = r.seed if isinstance(r.seed, int) else 10**9
            pref = 0 if seed == 42 else 1
            return (pref, seed, r.path)

        for r in sorted(filtered, key=_score):
            p = Path(r.path)
            if p.exists():
                return p

    data_root = legacy_root / "data" / "switching_ou"
    # Fallback heuristics from filesystem when lock is unavailable/outdated.
    method = (cfg.primary_method or "").strip()
    if method:
        pattern42 = f"**/*{method}*seed42*/model/best.ckpt"
        hits = sorted(data_root.glob(pattern42))
        if hits:
            return hits[0]
        pattern_any = f"**/*{method}*/model/best.ckpt"
        hits = sorted(data_root.glob(pattern_any))
        if hits:
            return hits[0]

    # Legacy fallback for earliest linear run.
    fallback = data_root / "switching_ou_transformer_dual_ce10" / "model" / "best.ckpt"
    if fallback.exists():
        return fallback
    return None


def resolve_live_assets_for_experiment(cfg: ExperimentConfig, legacy_root: Path) -> tuple[Path | None, Path | None]:
    ckpt = _resolve_live_checkpoint(cfg, legacy_root)
    data = _resolve_live_dataset(cfg, legacy_root)
    return ckpt, data


def run_live_eval(cfg: ExperimentConfig, legacy_root: Path, out_json: Path) -> dict:
    ckpt, data_file = resolve_live_assets_for_experiment(cfg, legacy_root)
    if ckpt is None or data_file is None:
        raise FileNotFoundError(
            f"Live assets not available for experiment={cfg.experiment_name}. "
            f"checkpoint={ckpt}, data={data_file}"
        )

    script = legacy_root / "switching" / "eval_switching.py"
    if not script.exists():
        raise FileNotFoundError(f"Legacy eval script missing: {script}")

    cmd = [
        sys.executable,
        str(script),
        "--checkpoint",
        str(ckpt),
        "--split",
        "test",
        "--output-file",
        str(out_json),
    ]
    env = os.environ.copy()
    # Some AutoDL images set invalid OMP_NUM_THREADS values; enforce a safe numeric default.
    omp = str(env.get("OMP_NUM_THREADS", "")).strip()
    if not omp.isdigit() or int(omp) <= 0:
        env["OMP_NUM_THREADS"] = "1"

    logger.info("Running live eval: %s", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(legacy_root),
        env=env,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        raise RuntimeError(f"Live eval failed: {stderr or stdout}")

    from switching_sde.data.io import read_json

    payload = read_json(out_json)
    payload["mode"] = "live"
    return payload


def run_eval(cfg: ExperimentConfig, *, mode: str, legacy_root: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"{cfg.experiment_name}_eval_{mode}.json"

    if mode == "frozen":
        payload = export_frozen_eval_summary(legacy_root, cfg.experiment_name, out_json)
        payload["mode"] = "frozen"
        return payload

    if mode == "live":
        return run_live_eval(cfg, legacy_root, out_json)

    if mode == "auto":
        try:
            return run_live_eval(cfg, legacy_root, out_json)
        except Exception as exc:
            logger.warning("Auto mode fallback to frozen: %s", exc)
            out_json = out_dir / f"{cfg.experiment_name}_eval_frozen.json"
            payload = export_frozen_eval_summary(legacy_root, cfg.experiment_name, out_json)
            payload["mode"] = "frozen"
            payload["fallback_reason"] = str(exc)
            return payload

    raise ValueError(f"Unsupported mode: {mode}")
