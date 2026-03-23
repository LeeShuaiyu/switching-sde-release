# Report Paragraph Plan

## P1

- Section: Introduction and Repository Scope
- Purpose: distinguish the switching-SDE project from the legacy PENN headline and state the central research question.
- Target evidence: README plus release mappings
- Terminology anchor: `$x_{1:L}$`, `$\\tau$`
- Visual anchor: `R-F1`
- Target length: 130 to 160 words

## P2

- Section: Introduction and Repository Scope
- Purpose: interpret the sample-path figure and motivate uncertainty-aware changepoint inference under stress.
- Target evidence: `R-F1`
- Terminology anchor: changepoint, posterior, regime
- Visual anchor: `R-F1`
- Target length: 110 to 140 words

## P3

- Section: Notation
- Purpose: define the main symbols used throughout the report.
- Target evidence: dataset and generator code
- Terminology anchor: `$x_{1:L}$`, `$s_{1:L}$`, `$\\tau$`, `$\\rho$`, `$T_h$`, `$q_\\theta(\\tau \\mid x_{1:L})$`
- Visual anchor: no-visual exception
- Target length: 120 to 150 words

## P4

- Section: Problem Formulation
- Purpose: formalize the single-switch inference task and the admissible switching set.
- Target evidence: config and posterior utility code
- Terminology anchor: admissible switch set and posterior summaries
- Visual anchor: no-visual exception
- Target length: 140 to 170 words

## P5

- Section: Experimental Design
- Purpose: define benchmark suites, baseline families, and evaluation metrics.
- Target evidence: benchmark scripts and final tables
- Terminology anchor: calibrated likelihood, tolerant-window F1, collapse rate
- Visual anchor: `R-T1`
- Target length: 130 to 160 words

## P6

- Section: Fixed-v2 Linear Benchmark
- Purpose: interpret the fixed-v2 comparison table and the paper-full scatter plot.
- Target evidence: paper-full tables and `R-F2`
- Terminology anchor: posterior split family, regression baseline, segmentation baseline
- Visual anchor: `R-F2`, `R-T1`
- Target length: 140 to 170 words

## P7

- Section: Fixed-v2 Linear Benchmark
- Purpose: explain the calibration figure and the appendix backbone nuance.
- Target evidence: `R-F3` and appendix table
- Terminology anchor: calibrated NLL, expected calibration error, backbone choice
- Visual anchor: `R-F3`
- Target length: 130 to 160 words

## P8

- Section: Linear Stress Robustness
- Purpose: interpret the degradation plot and explain the split between S1 and S2/S3.
- Target evidence: p5 OOD table, degradation table, `R-F4`, `R-T2`
- Terminology anchor: moderate shift, severe shift, collapse diagnostic
- Visual anchor: `R-F4`, `R-T2`
- Target length: 150 to 180 words

## P9

- Section: Nonlinear Robustness
- Purpose: summarize the nonlinear MAE figure and the nonlinear summary table.
- Target evidence: p6 tables and `R-F5`
- Terminology anchor: nonlinear in-distribution, nonlinear stress scenarios
- Visual anchor: `R-F5`, `R-T3`
- Target length: 150 to 180 words

## P10

- Section: Nonlinear Robustness
- Purpose: interpret the nonlinear sample-path figure and explain the OOD-NL1 caveat.
- Target evidence: `R-F6` plus OOD-NL table
- Terminology anchor: point accuracy versus stability warning
- Visual anchor: `R-F6`
- Target length: 130 to 160 words

## P11

- Section: Ablations, Limitations, and Release Notes
- Purpose: explain why the hard posterior baseline remains the strongest released recipe and record remaining environment and provenance cautions.
- Target evidence: ablation table, README, release wrapper
- Terminology anchor: hard supervision, ranking distillation, frozen-result release
- Visual anchor: no new visual
- Target length: 140 to 170 words
