# Figure and Table Plan

## Purpose

This plan records the visual set used by the current final outputs and the evidence behind each selection. The editable sources are the markdown drafts in `writing-pipeline/outputs/`; the rendered human-readable deliverables are `report.html` and `paper.html`. Every cited figure is normalized into `writing-pipeline/outputs/assets/`, and the citation locations are tracked in `writing-pipeline/outputs/figure_manifest.md`.

## Selection Rules

- Prefer the current neutralized output assets under `writing-pipeline/outputs/assets/`.
- Keep one visual per distinct claim when possible.
- Use figures for trajectory shape, tradeoff, calibration, and robustness trends.
- Use tables for exact benchmark rows and scenario summaries.
- Avoid visuals that only repeat a table without adding a different interpretation.
- Treat report-only figures as useful context and paper figures as the tighter manuscript subset.

## Current Output Visual Set

### Report figures

| ID | Output file(s) | Output asset | Upstream evidence | Target section | Claim supported | Caption angle | Caveat |
|---|---|---|---|---|---|---|---|
| R-F1 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_linear_examples.png` | Normalized from legacy `../PENN/reports/p5/figures/F4_sample_paths.png` | Executive Summary, problem motivation | Stressed trajectories can remain ambiguous even after the full path is observed, so the task is posterior localization rather than plain regression. | Representative linear stress trajectories with the reference switch and competing predictions. | Scenario-level panel, not an aggregate statistic. |
| R-F2 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_linear_tradeoff.png` | Normalized from legacy `../PENN/reports/paper_full/figures/method_comparison_map_scatter.png` | Reference linear results | The posterior changepoint family improves the MAE/F1 tradeoff relative to the weaker neural baselines. | MAE-F1 tradeoff among the released deep baselines. | Summarizes the main neural rows; classical baselines are better read from the table. |
| R-F3 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_linear_calibration.png` | Normalized from legacy `../PENN/reports/paper_full/figures/posterior_calibration_compare.png` | Reference linear results | Uncertainty quality and collapse behavior matter alongside point accuracy. | Posterior calibration and calibration error across posterior-style methods. | Report-only figure; intentionally omitted from the shorter paper fragment. |
| R-F4 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_linear_degradation.png` | Normalized from legacy `../PENN/reports/p5/figures/F3_degradation.png` | Linear stress robustness | Scenario S1 preserves much more performance than S2 and S3, so robustness is partial rather than uniform. | Relative degradation across the three linear stress scenarios. | Aggregate scenario summary; the exact values live in the table. |
| R-F5 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_nonlinear_error.png` | Normalized from legacy `../PENN/reports/p6_nonlinear_full_v3/figures/F1_mae_time_by_scenario.png` | Nonlinear robustness | Nonlinear MAE trends differ materially from the linear stress story and justify a separate discussion. | Switching-time error across nonlinear scenarios. | Trend figure only; does not replace the scenario table. |
| R-F6 | `report.md`, `report.html` | `writing-pipeline/outputs/assets/figure_nonlinear_examples.png` | Normalized from legacy `../PENN/reports/p6_nonlinear_full_v3/figures/F4_sample_paths.png` | Nonlinear robustness | Nonlinear trajectories remain interpretable enough for qualitative comparison, but uncertainty can change sharply by scenario. | Representative nonlinear trajectories and predictions. | Report-only figure; useful for intuition, not required in the shorter paper. |

### Report tables

| ID | Output file(s) | Source evidence | Target section | Claim supported | Caption angle | Caveat |
|---|---|---|---|---|---|---|
| R-T1 | `report.md`, `report.html` | `../PENN/reports/paper_full/benchmark_main_table.csv`, `../PENN/reports/paper_full/benchmark_appendix_backbone_table.csv` | Benchmark design and reference linear results | The benchmark definitions and main linear comparisons are explicit and reproducible. | Benchmark suites, scenario semantics, and reference rows. | Main quantitative anchor for the paper-style narrative. |
| R-T2 | `report.md`, `report.html` | `../PENN/reports/p5/benchmark_ood_full_table.csv` | Linear stress robustness | The posterior model remains strong on S1 but degrades on S2 and S3. | Scenario-wise linear stress summary for the posterior family. | Best read together with R-F4. |
| R-T3 | `report.md`, `report.html` | `../PENN/reports/p6_nonlinear_full_v3/benchmark_ood_nl_full_table.csv` | Nonlinear robustness | Nonlinear OOD point metrics are strong, but the collapse diagnostic still matters on OOD-NL1. | Nonlinear scenario summary for the posterior family. | Best read together with R-F5 and R-F6. |
| R-T4 | `report.md`, `report.html` | Current final narrative and the same upstream benchmark tables as above | Overall conclusion | The full empirical picture is only legible when point metrics and collapse diagnostics are read together. | Cross-scenario synthesis table. | This is a narrative synthesis, not a new benchmark source. |

### Paper figures

| ID | Output file(s) | Output asset | Upstream evidence | Target section | Claim supported | Caption angle | Caveat |
|---|---|---|---|---|---|---|---|
| P-F1 | `paper_sections.md`, `paper.html` | `writing-pipeline/outputs/assets/figure_linear_examples.png` | Normalized from legacy `../PENN/reports/p5/figures/F4_sample_paths.png` | Introduction | The task is a changepoint localization problem with real ambiguity under stress. | Representative stressed trajectories and changepoint predictions. | Shared with the report; retained because it anchors the paper introduction. |
| P-F2 | `paper_sections.md`, `paper.html` | `writing-pipeline/outputs/assets/figure_linear_tradeoff.png` | Normalized from legacy `../PENN/reports/paper_full/figures/method_comparison_map_scatter.png` | Experiments | The posterior changepoint family sits on a more favorable point-accuracy / hit-rate tradeoff. | MAE-F1 tradeoff plot. | Supports the main linear comparison in the paper. |
| P-F3 | `paper_sections.md`, `paper.html` | `writing-pipeline/outputs/assets/figure_linear_degradation.png` | Normalized from legacy `../PENN/reports/p5/figures/F3_degradation.png` | Experiments | Linear robustness is partial rather than uniform. | Linear stress degradation across scenarios. | Paper keeps this instead of the calibration figure to preserve scope. |
| P-F4 | `paper_sections.md`, `paper.html` | `writing-pipeline/outputs/assets/figure_nonlinear_error.png` | Normalized from legacy `../PENN/reports/p6_nonlinear_full_v3/figures/F1_mae_time_by_scenario.png` | Experiments | Nonlinear point-error trends differ from the linear stress suite and justify a separate robustness discussion. | Nonlinear MAE summary by scenario. | Paper uses the trend plot and drops the nonlinear example panel for brevity. |

### Paper tables

| ID | Output file(s) | Source evidence | Target section | Claim supported | Caption angle | Caveat |
|---|---|---|---|---|---|---|
| P-T1 | `paper_sections.md`, `paper.html` | `../PENN/reports/paper_full/benchmark_main_table.csv`, `../PENN/reports/paper_full/benchmark_appendix_backbone_table.csv` | Problem formulation and experiments | The paper can define the benchmark family and then ground the main linear result in exact rows. | Reference benchmark and comparison rows. | Main quantitative table for the paper. |
| P-T2 | `paper_sections.md`, `paper.html` | `../PENN/reports/p5/benchmark_ood_full_table.csv`, `../PENN/reports/p6_nonlinear_full_v3/benchmark_ood_nl_full_table.csv` | Experiments | Point metrics and collapse diagnostics should be interpreted jointly across stress settings. | Cross-scenario stress and nonlinear summary. | Supports the paper’s robustness discussion. |

## Explicit No-Visual Exceptions

- Notation section: no standalone visual required; symbolic clarity is more useful than adding another figure.
- Problem formulation section: no standalone visual required; definitions and equations carry the argument.

## Rerun Notes

- If the upstream repository changes, regenerate the neutralized assets in `writing-pipeline/outputs/assets/` and update `writing-pipeline/outputs/figure_manifest.md`.
- If the shorter paper fragment changes scope, re-evaluate whether R-F3 and R-F6 should stay report-only or be reintroduced into the paper.
- If a new benchmark table or stress suite is added, it should first appear here as a claim-backed visual or table candidate before drafting starts.
