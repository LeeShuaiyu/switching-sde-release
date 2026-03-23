from __future__ import annotations

import argparse

from switching_sde.cli.commands.artifacts import cmd_index, cmd_link
from switching_sde.cli.commands.benchmark import cmd_benchmark
from switching_sde.cli.commands.eval import cmd_eval
from switching_sde.cli.commands.report import cmd_report
from switching_sde.cli.commands.viz import cmd_viz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="switching-sde", description="Switching SDE release CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_art = sub.add_parser("artifacts", help="Artifact registry operations")
    sub_art = p_art.add_subparsers(dest="art_cmd", required=True)

    p_idx = sub_art.add_parser("index", help="Scan legacy repo and build artifact lock")
    p_idx.add_argument("--legacy-root", required=True)
    p_idx.set_defaults(func=cmd_index)

    p_link = sub_art.add_parser("link", help="Create symlink view for indexed artifacts")
    p_link.add_argument("--legacy-root", required=False, default="")
    p_link.add_argument("--link-root", default="")
    p_link.set_defaults(func=cmd_link)

    p_eval = sub.add_parser("eval", help="Run evaluation")
    p_eval.add_argument("--experiment", required=True)
    p_eval.add_argument("--mode", choices=["live", "frozen", "auto"], default="auto")
    p_eval.add_argument("--legacy-root", default="")
    p_eval.add_argument("--output-dir", default="")
    p_eval.set_defaults(func=cmd_eval)

    p_viz = sub.add_parser("viz", help="Run visualization")
    p_viz.add_argument("--experiment", required=True)
    p_viz.add_argument("--mode", choices=["live", "frozen", "auto"], default="auto")
    p_viz.add_argument("--legacy-root", default="")
    p_viz.add_argument("--output-dir", default="")
    p_viz.set_defaults(func=cmd_viz)

    p_bm = sub.add_parser("benchmark", help="Run suite benchmark")
    p_bm.add_argument("--suite", choices=["paper_full", "p5", "p6"], required=True)
    p_bm.add_argument("--mode", choices=["live", "frozen", "auto"], default="frozen")
    p_bm.add_argument("--legacy-root", default="")
    p_bm.add_argument("--output-root", default="")
    p_bm.set_defaults(func=cmd_benchmark)

    p_rep = sub.add_parser("report", help="Generate readable markdown report")
    p_rep.add_argument("--suite", choices=["paper_full", "p5", "p6"], required=True)
    p_rep.add_argument("--legacy-root", default="")
    p_rep.add_argument("--output-root", default="")
    p_rep.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
