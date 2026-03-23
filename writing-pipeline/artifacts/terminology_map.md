# Terminology Map

This map is the required translation layer between repository-internal labels and manuscript-ready language.

## Core Objects

| Raw repo label | Preferred prose term | Preferred notation | Narrative policy | Notes |
|---|---|---|---|---|
| `X` / `x` | observed trajectory | `$x_{1:L}$` | use notation after first definition | One scalar trajectory sampled on a discrete grid. |
| `H` / `h` | observation horizon or total duration | `$T_h$` | use notation after first definition | In the dataset, this stores the physical time span rather than the number of steps. |
| `length` | number of valid time steps | `$L$` | use notation after first definition | Distinguish from the physical duration `$T_h$`. |
| `Z` / `z` | validity mask for padded minibatches | `$m_{1:L_{\max}}$` | implementation-only | Do not use `z` as narrative notation. |
| `CP_IDX` / `cp_idx` | switching-time index or changepoint index | `$\\tau$` | use notation after first definition | The core prediction target. |
| `CP_MASK` / `cp_mask` | soft supervision mask around the switching index | `$w_{\\tau}$` or "soft target mask" | implementation-only unless discussing training targets | Avoid the raw name in prose. |
| `STATE_SEQ` / `state_seq` | latent regime sequence | `$s_{1:L}$` | use notation after first definition | Binary regime indicator. |
| `STATE_RATIO` / `ratio` | regime-occupancy ratio | `$\\rho = (\\rho_0, \\rho_1)$` | use notation after first definition | Derived from the switching location. |
| `teacher_probs` | teacher posterior distribution | `$q^{\\mathrm{teach}}(\\tau \\mid x_{1:L})$` | use notation or prose | Use when discussing distillation only. |
| `teacher_weight` | teacher reliability weight | `$\\omega^{\\mathrm{teach}}$` | use notation or prose | Reliability gate weight. |

## Task and Model Terms

| Raw repo label | Preferred prose term | Preferred notation | Narrative policy | Notes |
|---|---|---|---|---|
| `switching_cp_ratio` | switching-time and occupancy estimation task | none required | do not use raw name in prose | This is a task identifier, not paper terminology. |
| `head_mode = dual` | dual-branch architecture | none required | prose only | Refers to separate changepoint and ratio prediction branches. |
| `posterior_head_type = split_dual` | constrained dual-branch posterior head | `$q_\\theta(\\tau \\mid x_{1:L})$` | prefer prose plus posterior notation | Avoid using `split_dual` as polished scientific wording. |
| `posterior_type = categorical` | discrete posterior over admissible switching indices | `$q_\\theta(\\tau \\mid x_{1:L})$` | use notation after definition | This is the main released posterior formulation. |
| `soft_target_mode = teacher` | teacher-guided supervision | none required | prose only | |
| `distill_mode = rank_distill` | reliability-weighted ranking distillation | none required | prose only | |
| `use_segment_stats` | segment-statistics augmentation | none required | prose only | Use only when describing the failed ablation. |

## Experiment Labels

| Raw repo label | Preferred prose term | Preferred notation | Narrative policy | Notes |
|---|---|---|---|---|
| `Ours_lstm_A0` | LSTM posterior changepoint model | none required | do not use raw label in narrative prose | May appear in monospaced implementation notes or artifact references only. |
| `Ours_transformer_A0` | transformer posterior changepoint model | none required | do not use raw label in narrative prose | |
| `Ours_lstm_hard` | LSTM posterior changepoint model on the fixed-v2 linear benchmark | none required | do not use raw label in narrative prose | |
| `Ours_transformer_hard` | transformer posterior changepoint model on the fixed-v2 linear benchmark | none required | do not use raw label in narrative prose | |
| `Transformer_regression` / `D1` / `D2` | deterministic regression baseline | none required | prose only | Mention backbone when needed. |
| `Transformer_segmentation` / `D4` | segmentation-based posterior baseline | none required | prose only | |
| `S1_cusum_lr` | CUSUM/LR baseline | none required | prose only | |
| `S2_bocpd_offline` | Bayesian CPD baseline | none required | prose only | |
| `M1_switching_hmm` | switching HMM baseline | none required | prose only | |
| `M2_plugin_split` | plugin split baseline | none required | prose only | |
| `A0` | hard posterior supervision baseline | none required | prose only | |
| `A1` | ranking-distillation variant | none required | prose only | |
| `A2` | confidence-gated distillation variant | none required | prose only | |
| `A3` | segment-statistics augmentation variant | none required | prose only | |

## Suite and Scenario Terms

| Raw repo label | Preferred prose term | Preferred notation | Narrative policy | Notes |
|---|---|---|---|---|
| `paper_full` | fixed-v2 linear benchmark suite | none required | prose only | Use when describing the main linear benchmark. |
| `p5` | linear stress-robustness suite | none required | prose only | |
| `p6_nonlinear_full_v3` | nonlinear Duffing benchmark suite | none required | prose only | |
| `ID_fixed_v2` | in-distribution linear split | none required | prose only | |
| `S1` / `S2` / `S3` | stress scenarios S1, S2, and S3 | none required | prose only | Scenario label is acceptable when paired with prose. |
| `ID_NL` | in-distribution nonlinear split | none required | prose only | |
| `OOD_NL1` / `OOD_NL2` / `OOD_NL3` | nonlinear stress scenarios 1, 2, and 3 | none required | prose only | |

## Metrics

| Raw repo label | Preferred prose term | Preferred notation | Narrative policy | Notes |
|---|---|---|---|---|
| `mae_time` | mean absolute switching-time error | `$\\mathrm{MAE}_{\\tau}$` | notation or prose | |
| `f1@0.02` | F1 score with a 2% tolerance window | `$\\mathrm{F1}_{0.02}$` | notation or prose | |
| `topk_hit` | top-k hit rate | `Top-k` | prose or notation | |
| `nll_cal` | calibrated negative log-likelihood | `$\\mathrm{NLL}_{\\mathrm{cal}}$` | notation or prose | |
| `ece_cal` | calibrated expected calibration error | `$\\mathrm{ECE}_{\\mathrm{cal}}$` | notation or prose | |
| `ci90_coverage` | 90% interval coverage | `Cov@90` | prose or notation | |
| `ci90_width_mean_time` | mean width of the 90% posterior interval | `Width@90` | prose or notation | |
| `collapse_rate` | collapse rate under the release diagnostics | none required | prose only | Do not euphemize this metric away when it is nonzero. |

## Banned Raw Identifiers in Narrative Prose

- `split_dual`
- `switching_cp_ratio`
- `cp_idx`
- `cp_mask`
- `state_ratio`
- `teacher_probs`
- `teacher_weight`
- raw experiment IDs such as `Ours_lstm_A0` or `D3_transformer_hazard`

These labels may still appear in:

- artifact references
- inline code or monospace implementation notes
- evidence maps and review diagnostics
