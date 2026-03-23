from __future__ import annotations

from pathlib import Path

from switching_sde.config.schema import load_experiment_config
from switching_sde.data.io import write_json
from switching_sde.pipelines.evaluate import run_eval
from switching_sde.utils.paths import legacy_root, repo_root


def cmd_eval(args) -> int:
    cfg = load_experiment_config(args.experiment)
    legacy = legacy_root(args.legacy_root)
    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (repo_root() / "reports" / "paper" / "eval")
    payload = run_eval(cfg, mode=args.mode, legacy_root=legacy, out_dir=out_dir)
    write_json(out_dir / f"{args.experiment}_last.json", payload)
    print(f"[ok] eval finished: {out_dir}")
    return 0
