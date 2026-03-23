# Revision Decisions

## Round 1

- Comment: "Frame the contribution around stable posterior changepoint inference."
  - Decision: adopt
  - Reason: improves truthfulness and avoids backbone-centric overstatement.

- Comment: "Keep S2, S3, and OOD-NL1 limitations explicit."
  - Decision: adopt
  - Reason: directly required by the final benchmark tables.

- Comment: "Remove raw experiment identifiers from narrative prose."
  - Decision: adopt
  - Reason: mandated by the upgraded terminology rules and improves manuscript quality.

- Comment: "Add introduction, notation, and problem formulation."
  - Decision: adopt
  - Reason: the new configured scope requires these sections.

- Comment: "Integrate real figures and tables instead of staying text-only."
  - Decision: adopt
  - Reason: the repository already contains final visual assets and the workflow now requires them.

- Comment: "Distinguish point accuracy from diagnostic stability in the nonlinear section."
  - Decision: adopt
  - Reason: necessary for factual correctness.

## Round 2

- Comment: "The revised framing matches the evidence."
  - Decision: reject
  - Reason: acknowledgment only.

- Comment: "The limitations are visible enough."
  - Decision: reject
  - Reason: acknowledgment only.

- Comment: "Notation and figure references are now consistent."
  - Decision: reject
  - Reason: acknowledgment only.

## Round 3

- Comment: "Clarify that the strongest nominal linear claim should rely on the controlled transformer comparison, while the stronger LSTM row reflects family-level headroom rather than a head-only gain."
  - Decision: adopt
  - Reason: this removes a fairness ambiguity without changing the underlying evidence.

- Comment: "Explain that the collapse thresholds are inherited from the released evaluation scripts rather than universally justified statistical cutoffs."
  - Decision: adopt
  - Reason: the benchmark code defines these constants, and the manuscript should present them with that provenance.

- Comment: "Acknowledge that the released tables average over three seeds without confidence intervals or error bars."
  - Decision: partially adopt
  - Reason: the released artifacts do not contain interval estimates to add directly, but the prose can disclose that the comparisons are directional rather than interval-estimated.

- Comment: "Tighten the nonlinear figure-to-text linkage so the visual evidence carries more of the explanation."
  - Decision: adopt
  - Reason: this improves readability and uses the existing visual evidence more effectively.

## Summary

- Adopted: 9
- Partially adopted: 1
- Rejected: 3
- Deferred: 0
