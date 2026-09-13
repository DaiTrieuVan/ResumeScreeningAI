<!-- SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai -->
<!-- SPDX-License-Identifier: MIT -->

# Competition v1 labeling guide

This locked baseline validates evaluation plumbing and deterministic offline behavior with synthetic boundary cases. It is deliberately not presented as external-validity or production accuracy evidence.

- `PASS`: the synthetic CV directly satisfies the criterion.
- `FAIL`: the synthetic CV directly contradicts or fails the criterion.
- `UNKNOWN`: the CV does not contain enough evidence for either conclusion.
- `evidence.verified`: a human author checked the citation against the synthetic source page.
- `expert_rank`: the reference order within one job; lower is better.
- `batch_status`: terminal pipeline outcome used by batch-completion measurement.

Any label change requires a new dataset version and independent review before publication.
