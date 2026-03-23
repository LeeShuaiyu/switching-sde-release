# Report Outline

## Section 1. Introduction and Repository Scope

Purpose: establish the actual project identity, explain why switching-time inference matters, and motivate the need for uncertainty-aware changepoint estimation under distribution shift.

Notation decisions:

- define the observable trajectory as `$x_{1:L}$`
- reserve `$\\tau$` for the switching-time index

Visuals:

- `R-F1`

## Section 2. Notation

Purpose: define the trajectory, latent regime sequence, switching index, occupancy ratio, observation horizon, posterior, and evaluation metrics in one place.

Notation decisions:

- `$x_{1:L}$`, `$s_{1:L}$`, `$\\tau$`, `$\\rho$`, `$q_\\theta(\\tau \\mid x_{1:L})$`, `$T_h$`

Visuals:

- explicit no-visual exception

## Section 3. Problem Formulation

Purpose: formalize the single-switch inference task for linear OU and nonlinear Duffing settings and define what the model must estimate.

Notation decisions:

- admissible switch set
- posterior target and point summaries

Visuals:

- explicit no-visual exception

## Section 4. Experimental Design

Purpose: define the benchmark suites, baseline families, and evaluation protocol.

Notation decisions:

- use prose labels for baselines and model families rather than raw experiment IDs

Visuals:

- `R-T1`

## Section 5. Fixed-v2 Linear Benchmark

Purpose: show the main linear comparison, the stability contrast, and the backbone nuance.

Visuals:

- `R-F2`
- `R-F3`
- `R-T1`

## Section 6. Linear Stress Robustness

Purpose: show why S1 is a success case but S2 and S3 remain failure cases.

Visuals:

- `R-F4`
- `R-T2`

## Section 7. Nonlinear Robustness

Purpose: present the nonlinear results with equal attention to point metrics and collapse diagnostics.

Visuals:

- `R-F5`
- `R-F6`
- `R-T3`

## Section 8. Ablations, Limitations, and Release Notes

Purpose: summarize what the ablations actually validate, record unresolved weaknesses, and explain how the release wrapper should be interpreted.

Visuals:

- optional reference back to prior visuals, no new required visual
