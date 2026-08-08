---
title: Dataset Integration Status
tags:
  - project/ai-scoliosis
  - dataset
status: blocked-on-selection
---

# Dataset integration status

No real dataset has been supplied or selected. No external data was downloaded during the bootstrap.

The code accepts a canonical JSON schema plus CSV and sequential flat TXT. Before integrating a
named public dataset, capture:

- License and official source
- Dataset version/checksum
- Image format and orientation
- Point order and coordinate space
- Vertebral labels or ordering
- Missing/corrupt case policy
- Reference Cobb methodology and end-vertebra metadata
- De-identification and local access controls

The synthetic case exists only to test software plumbing and a known 30° geometry. It is not a
clinical validation sample.

