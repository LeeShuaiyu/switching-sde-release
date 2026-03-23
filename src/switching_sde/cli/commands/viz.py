from __future__ import annotations

from pathlib import Path

from switching_sde.config.schema import load_experiment_config
from switching_sde.data.io import write_json
from switching_sde.pipelines.visualize import run_visualization
from switching_sde.utils.paths import legacy_root, repo_root


def cmd_viz(args) -> int:
    cfg = load_experiment_config(args.experiment)
    legacy = legacy_root(args.legacy_root)
    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (repo_root() / "reports" / "paper" / "figures")
    payload = run_visualization(cfg, mode=args.mode, legacy_root=legacy, out_dir=out_dir)
    write_json(out_dir / f"{args.experiment}_viz_summary.json", payload)
    print(f"[ok] visualization finished: {out_dir}")
    return 0
