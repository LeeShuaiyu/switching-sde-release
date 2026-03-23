from __future__ import annotations

import csv
import statistics
from pathlib import Path

from switching_sde.data.io import read_json, write_json


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with path.open("w", encoding="utf-8") as f:
            f.write("")
        return
    keys = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def suite_table_files(suite: str) -> dict[str, str]:
    if suite == "paper_full":
        return {
            "main": "reports/paper_full/benchmark_main_table.csv",
            "appendix": "reports/paper_full/benchmark_appendix_backbone_table.csv",
            "ablation": "reports/paper_full/ablation_table.csv",
            "stability": "reports/paper_full/seed_stability_table.csv",
            "posterior_quality": "reports/paper_full/posterior_quality_table.csv",
        }
    if suite == "p5":
        return {
            "id_deep": "reports/p5/benchmark_id_deep_table.csv",
            "ood_full": "reports/p5/benchmark_ood_full_table.csv",
            "degradation": "reports/p5/degradation_table.csv",
            "stability": "reports/p5/seed_stability_table.csv",
        }
    if suite == "p6":
        return {
            "id_nl": "reports/p6_nonlinear_full_v3/benchmark_id_nl_deep_table.csv",
            "ood_nl1": "reports/p6_nonlinear_full_v3/benchmark_ood_nl1_main_table.csv",
            "ood_nl23": "reports/p6_nonlinear_full_v3/benchmark_ood_nl23_appendix_table.csv",
            "ood_nl_full": "reports/p6_nonlinear_full_v3/benchmark_ood_nl_full_table.csv",
            "degradation": "reports/p6_nonlinear_full_v3/degradation_nl_table.csv",
            "stability": "reports/p6_nonlinear_full_v3/seed_stability_nl_table.csv",
        }
    raise ValueError(f"Unsupported suite: {suite}")


def load_suite_tables(legacy_root: Path, suite: str) -> dict[str, dict]:
    files = suite_table_files(suite)
    out: dict[str, dict] = {}
    for key, rel in files.items():
        p = legacy_root / rel
        if p.exists():
            out[key] = {"path": str(p.resolve()), "rows": _read_csv(p)}
        else:
            out[key] = {"path": str(p.resolve()), "rows": []}
    return out


def export_suite_tables(legacy_root: Path, suite: str, output_tables_dir: Path) -> dict[str, str]:
    tables = load_suite_tables(legacy_root, suite)
    written = {}
    for key, payload in tables.items():
        out_file = output_tables_dir / f"{suite}_{key}.csv"
        _write_csv(out_file, payload["rows"])
        written[key] = str(out_file.resolve())
    return written


def _to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def summarize_table(rows: list[dict]) -> dict:
    summary = {"num_rows": len(rows)}
    if not rows:
        return summary
    numeric_cols = {}
    for r in rows:
        for k, v in r.items():
            fv = _to_float(v)
            if fv is None:
                continue
            numeric_cols.setdefault(k, []).append(fv)
    for k, vals in numeric_cols.items():
        if vals:
            summary[f"{k}_mean"] = statistics.mean(vals)
    return summary


def load_experiment_eval_json(legacy_root: Path, experiment_name: str) -> list[dict]:
    # Frozen experiment mapping to legacy eval json directories.
    mapping = {
        "id_linear": (legacy_root / "reports/paper_full/test_eval", "fixed_v2"),
        "ood_linear_s1": (legacy_root / "reports/p5/raw/eval_json", "fixed_v4_s1"),
        "id_nonlinear": (legacy_root / "reports/p6_nonlinear_full_v3/raw/eval_json", "fixed_v5_nl_id"),
        "ood_nonlinear_s1": (legacy_root / "reports/p6_nonlinear_full_v3/raw/eval_json", "fixed_v5_nl_s1"),
    }
    if experiment_name not in mapping:
        raise ValueError(f"Unknown experiment: {experiment_name}")
    folder, data_version = mapping[experiment_name]
    if not folder.exists():
        return []
    rows = []
    for p in sorted(folder.glob("*_test.json")):
        try:
            payload = read_json(p)
        except Exception:
            # Keep frozen mode robust when legacy folders contain partial/corrupted files.
            continue
        if payload.get("data_version") == data_version:
            payload["_file"] = str(p.resolve())
            rows.append(payload)
    return rows


def export_frozen_eval_summary(legacy_root: Path, experiment_name: str, out_json: Path) -> dict:
    rows = load_experiment_eval_json(legacy_root, experiment_name)
    metrics = ["mae_time", "mae_idx", "f1@0.02", "topk_hit", "nll_cal", "ece_cal", "brier"]
    agg = {"experiment": experiment_name, "num_runs": len(rows), "runs": rows}
    for m in metrics:
        vals = [_to_float(r.get(m)) for r in rows]
        vals = [v for v in vals if v is not None]
        if vals:
            agg[f"{m}_mean"] = statistics.mean(vals)
    write_json(out_json, agg)
    return agg
