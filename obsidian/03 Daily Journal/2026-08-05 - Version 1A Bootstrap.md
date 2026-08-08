---
title: 2026-08-05 - Version 1A Bootstrap
date: 2026-08-05
tags:
  - project/ai-scoliosis
  - journal
  - version/1a
status: complete
---

# 2026-08-05 — Version 1A bootstrap

## Completed work

- Created the production-oriented repository structure.
- Implemented immutable landmark and measurement domain objects.
- Added raster image loading and three annotation adapters.
- Implemented pure endplate geometry, automatic single Cobb selection, and reference validation.
- Added annotated visualization and auditable JSON/Markdown reporting.
- Added CLI/configuration, Docker packaging, deterministic fixtures, tests, and documentation.
- Verified the installed Python 3.12 environment: 8 tests passed with 81% line coverage, Ruff found
  no issues, strict mypy found no issues across 15 source files, and bytecode compilation passed.
- Ran and visually inspected the CLI smoke case: 29.999° calculated against a 30.0° reference,
  selecting T4 superior and T12 inferior endplates within the configured tolerance.

## Files modified

New repository files under `src/`, `tests/`, `apps/`, `config/`, `docs/`, and `obsidian/`, plus root
packaging and container files. See Git status/history for the exhaustive list.

## Problems encountered

- The workspace and project vault were initially empty.
- Obsidian was not running, so the Obsidian CLI could not inspect a previously focused vault.
- No public dataset, sample image, annotation file, or source annotation schema was supplied.
- Base Python lacked the required scientific/test dependencies.
- The initial normalized synthetic landmarks assumed a square image, so non-square pixel scaling
  correctly changed the apparent slopes and exposed a fixture error.
- Matplotlib could not use the sandboxed home cache during the smoke run and used a temporary cache.

## Solutions

- Created an Obsidian-compatible vault inside the repository and recorded the absence of prior state.
- Isolated external formats behind adapters and documented a canonical JSON contract.
- Added a deterministic synthetic, explicitly non-clinical fixture for end-to-end verification.
- Declared reproducible dependencies in `pyproject.toml` for installation before verification.
- Corrected the fixture using the image aspect ratio and kept a regression assertion for 30°.
- Used a project-local Python 3.12 virtual environment; the cache warning does not affect artifacts.

## Ideas discovered

- Preserve the landmark contract when a detector arrives so ML cannot leak into geometry.
- Future multi-curve analysis should return multiple typed measurements, never overload the current
  single scalar.
- Dataset reference comparison is only meaningful after matching its end-vertebra protocol.

## Research consulted

No external papers or websites were consulted. Implementation followed the supplied engineering
brief and standard line geometry.

## Questions remaining

- Which public dataset is first?
- What exact annotation ordering and coordinate normalization does it use?
- Are end vertebrae supplied, or only landmarks and a scalar reference?
- What acceptance criteria will the clinical stakeholder approve?

## Next actions

Follow [[Version 1A TODO]] and begin with [[Dataset Integration Status]].

## Time spent

Approximately 30 minutes of agent execution; not captured by an external time tracker.

## Architecture changes

Established the domain model as the boundary between data acquisition, geometry, and all future AI
inference. See [[Version 1A Architecture]] and the two ADRs.

## Technical debt

- Only one automatic global curve is selected.
- CSV/TXT formats cannot currently carry a reference angle or explicit schema version.
- No DICOM support, batch manifest, dataset checksum, or golden clinical case exists.
- The package is verified on Python 3.12; the declared Python 3.10/3.11 compatibility is not yet
  exercised in a CI version matrix.

## Future improvements

Add dataset manifests, DICOM handling, clinician-selected end vertebrae, multi-curve results,
structured QC flags, and longitudinal comparison only after Version 1A dataset validation.

## Lessons learned

The annotation protocol—not just point coordinates—is part of the clinical measurement definition.
Keeping that metadata explicit is necessary for interpretable validation.
