from __future__ import annotations

import csv
from pathlib import Path

from switching_sde.artifacts.frozen_loader import export_suite_tables
from switching_sde.config.schema import load_experiment_config
from switching_sde.data.io import write_json
from switching_sde.pipelines.evaluate import run_eval
from switching_sde.utils.logging import get_logger

logger = get_logger(__name__)


_SUITE_EXPERIMENTS = {
    "paper_full": ["id_linear"],
    "p5": ["ood_linear_s1"],
    "p6": ["id_nonlinear", "ood_nonlinear_s1"],
}


def run_benchmark(*, suite: str, mode: str, legacy_root: Path, output_root: Path) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    table_dir = output_root / "tables"
    fig_dir = output_root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    if mode == "frozen":
        written = export_suite_tables(legacy_root, suite, table_dir)
        payload = {
            "suite": suite,
            "mode": "frozen",
            "tables": written,
            "output_root": str(output_root.resolve()),
        }
        write_json(output_root / "benchmark_summary.json", payload)
        return payload

    # Live/auto benchmark: evaluate mapped experiments, with optional fallback.
    if mode in {"live", "auto"}:
        rows = []
        eval_mode = "live" if mode == "live" else "auto"
        for exp_name in _SUITE_EXPERIMENTS.get(suite, []):
            cfg = load_experiment_config(exp_name)
            out_dir = output_root / "eval"
            try:
                summary = run_eval(cfg, mode=eval_mode, legacy_root=legacy_root, out_dir=out_dir)
            except Exception as exc:
                summary = {"experiment": exp_name, "error": str(exc), "mode": "failed"}
            rows.append(summary)

        csv_file = table_dir / f"{suite}_live_summary.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        keys = sorted({k for r in rows for k in r.keys()})
        with csv_file.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow(r)

        tables = {}
        if mode == "auto":
            # Auto mode should still materialize suite-level frozen tables for reproducible reporting.
            tables = export_suite_tables(legacy_root, suite, table_dir)

        payload = {
            "suite": suite,
            "mode": mode,
            "summary_csv": str(csv_file.resolve()),
            "rows": rows,
            "tables": tables,
            "output_root": str(output_root.resolve()),
        }
        write_json(output_root / "benchmark_summary.json", payload)
        return payload

    raise ValueError(f"Unsupported mode: {mode}")
