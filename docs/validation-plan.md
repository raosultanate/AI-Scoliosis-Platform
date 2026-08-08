# Version 1A validation plan

The current suite verifies mathematical determinism and software composition, not clinical validity.

## Implemented checks

- Known line orientations and a known 30° endplate pair
- Undirected line equivalence
- Maximum-pair selection constrained by cranio-caudal ordering
- Inclusive tolerance boundary
- Degenerate endplate rejection
- JSON normalization and CSV/TXT parser behavior
- End-to-end generation of visualization and traceable report artifacts

## Required when a public dataset is selected

1. Freeze a de-identified evaluation manifest and its dataset/version hash.
2. Confirm whether the published reference used identical end vertebrae and angle convention.
3. Report mean absolute error, median absolute error, standard deviation, percent within 3° and 5°,
   and stratified error by curve magnitude.
4. Inspect outliers with landmark, endplate, and reference overlays.
5. Measure inter-observer variation when multiple clinician annotations exist.
6. Never interpret agreement with a single annotation source as clinical efficacy.

Acceptance thresholds must be chosen with clinical stakeholders after the reference protocol is
known; no threshold is invented in this bootstrap.

