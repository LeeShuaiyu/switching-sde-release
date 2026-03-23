# Paper Review Comments

## Round 1

### Advisor

- Severity: medium
- Comment: frame the contribution around stable posterior changepoint inference, not around raw experiment labels or an unconditional backbone win.

### Reviewer

- Severity: high
- Comment: the draft must explicitly acknowledge that the linear stress suite fails on S2 and S3 and that OOD-NL1 still triggers the collapse diagnostic.

### Local Reviewer

- Severity: high
- Comment: repository identifiers such as raw method names and internal head labels should not appear as narrative terminology.

### Logic Reviewer

- Severity: medium
- Comment: introduction, notation, and problem formulation need to be present before the experiments section if the enabled scope includes them.

### Outline Compliance Reviewer

- Severity: high
- Comment: the prior run did not satisfy the expanded section scope and did not meet the required visual integration standard.

### Fact Consistency Reviewer

- Severity: high
- Comment: the nonlinear section must distinguish strong point metrics from full diagnostic stability.

## Round 2

### Advisor

- Severity: low
- Comment: the revised framing now matches the evidence and the target style.

### Reviewer

- Severity: low
- Comment: the limitations are visible enough that the experiment section no longer reads as overclaimed.

### Local Reviewer

- Severity: low
- Comment: notation and figure references are now consistent across sections.

## Round 3

### Major Issues

- Severity: high
- Comment: the strongest linear result compares the LSTM posterior model against Transformer baselines, so backbone choice and posterior formulation change together in [report.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/report.md):134-147 and [paper_sections.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/paper_sections.md):138-151. As written, the draft does not cleanly separate "posterior inference helps" from "the LSTM backbone helps". A same-backbone control or an explicit caveat is needed for a fair comparison.

- Severity: high
- Comment: the collapse diagnostic in [report.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/report.md):124-132 and [paper_sections.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/paper_sections.md):126-132 depends on hard thresholds (`5.30`, `0.15`, `0.025`) that are not justified or sensitivity-tested. Those thresholds drive the most important failure claims in Linear Scenarios 2-3 and Nonlinear Scenario 1, so the current wording is too brittle for a reproducible manuscript.

### Minor Issues

- Severity: medium
- Comment: the draft reports averages over three random seeds in [report.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/report.md):120-132 and [paper_sections.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/paper_sections.md):122-132, but no variance, confidence interval, or error bar is shown in Tables 2-4 or the figures. That makes the robustness claims harder to assess than the prose suggests.

- Severity: low
- Comment: the nonlinear section is readable, but the figure-to-text linkage is slightly weaker than in the linear sections. In [paper_sections.md](file:///Users/lishuaiyu/Documents/Playground/switching-sde-release/writing-pipeline/outputs/paper_sections.md):177-206, Figure 4 is introduced after the first paragraph of results and Figure 5 only after the caveat about Scenario 1; consider tightening the order so the figures carry more of the explanatory load instead of the prose.
