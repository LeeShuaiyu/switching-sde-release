# Paper Paragraph Plan

## I1

- Section: Introduction
- Purpose: state the problem and the active project scope.
- Evidence source: README and release mappings
- Terminology anchor: `$x_{1:L}$`, `$\\tau$`
- Visual anchor: `P-F1`
- Target length: 130 to 150 words

## I2

- Section: Introduction
- Purpose: explain why posterior changepoint inference is more appropriate than a pure point estimate for this task family.
- Evidence source: README and method code
- Terminology anchor: `$q_\\theta(\\tau \\mid x_{1:L})$`
- Visual anchor: `P-F1`
- Target length: 120 to 150 words

## I3

- Section: Introduction
- Purpose: summarize the empirical arc of the paper in one paragraph without overselling.
- Evidence source: fixed-v2, P5, and P6 tables
- Terminology anchor: stability, shift, nonlinear robustness
- Visual anchor: no new visual
- Target length: 120 to 150 words

## N1

- Section: Notation
- Purpose: define the discrete trajectory, regime sequence, switching index, horizon, occupancy ratio, and posterior.
- Evidence source: dataset and generator code
- Terminology anchor: core notation section
- Visual anchor: no-visual exception
- Target length: 140 to 170 words

## N2

- Section: Notation
- Purpose: define the evaluation metrics and the collapse diagnostic.
- Evidence source: benchmark tables and metrics usage
- Terminology anchor: `$\\mathrm{MAE}_{\\tau}$`, `$\\mathrm{F1}_{0.02}$`, `$\\mathrm{NLL}_{cal}$`, `$\\mathrm{ECE}_{cal}$`
- Visual anchor: no-visual exception
- Target length: 120 to 140 words

## P1

- Section: Problem Formulation
- Purpose: formalize the single-switch inference problem and the admissible switching set.
- Evidence source: config and posterior utilities
- Terminology anchor: admissible index set
- Visual anchor: no-visual exception
- Target length: 140 to 170 words

## P2

- Section: Problem Formulation
- Purpose: state the linear OU and nonlinear Duffing regimes in a compact mathematical form and define the inference outputs.
- Evidence source: generator code
- Terminology anchor: regime-specific dynamics and posterior summaries
- Visual anchor: no-visual exception
- Target length: 140 to 180 words

## E1

- Section: Experiments
- Purpose: define the benchmark suites and baseline families.
- Evidence source: benchmark scripts
- Terminology anchor: prose display names for baselines
- Visual anchor: `P-T1`
- Target length: 130 to 150 words

## E2

- Section: Experiments
- Purpose: present the fixed-v2 linear comparison and interpret the selected table.
- Evidence source: paper-full tables
- Terminology anchor: posterior split family
- Visual anchor: `P-T1`
- Target length: 130 to 160 words

## E3

- Section: Experiments
- Purpose: interpret the paper-full scatter plot and extract the stability message.
- Evidence source: `P-F2`
- Terminology anchor: tradeoff between switching-time error and tolerant-window hit quality
- Visual anchor: `P-F2`
- Target length: 120 to 150 words

## E4

- Section: Experiments
- Purpose: describe the linear stress result and highlight the split between S1 and S2/S3.
- Evidence source: p5 OOD tables and `P-F3`
- Terminology anchor: moderate versus severe shift
- Visual anchor: `P-F3`
- Target length: 130 to 160 words

## E5

- Section: Experiments
- Purpose: present the nonlinear summary with attention to both point metrics and collapse diagnostics.
- Evidence source: p6 OOD tables and `P-F4`
- Terminology anchor: point accuracy versus stability warning
- Visual anchor: `P-F4`, `P-T2`
- Target length: 140 to 170 words

## E6

- Section: Experiments
- Purpose: close the section with ablations and limitations.
- Evidence source: paper-full ablation table, p5 degradation table, p6 OOD-NL1 rows
- Terminology anchor: hard posterior supervision, ranking distillation, segment-statistics augmentation
- Visual anchor: `P-T2`
- Target length: 130 to 160 words
