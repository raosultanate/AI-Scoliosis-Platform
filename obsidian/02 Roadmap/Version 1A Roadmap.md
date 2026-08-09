---
title: Version 1A Roadmap
tags:
  - project/ai-scoliosis
  - roadmap
status: in-progress
---

# Version 1A roadmap

## Completed foundation

- [x] Professional Python `src` layout
- [x] Modular image and landmark loading
- [x] JSON, CSV, and flat-text annotation support
- [x] Pixel and normalized coordinate handling
- [x] Landmark and endplate visualization
- [x] Deterministic Cobb geometry
- [x] Optional reference validation
- [x] Annotated PNG and versioned JSON/Markdown report
- [x] Synthetic fixture and deterministic tests
- [x] Architecture, schema, validation, and data-handling documentation

## Completed web foundation

- [x] FastAPI application and health endpoint
- [x] Capability endpoint that reports model readiness honestly
- [x] Synthetic analysis endpoint using the existing pipeline
- [x] Responsive plain-language website and local PNG/JPEG preview
- [x] Annotated synthetic Cobb-angle result in the browser
- [x] Docker image, Docker Compose service, health check, and persistent artifact volume

Real-X-ray upload and landmark inference remain outside Version 1A until a validated detector and
the required security controls are available. See [[End-to-End AI Web App Roadmap]].

## Dataset-dependent work

- [ ] Select and document the initial public scoliosis dataset
- [ ] Implement its exact adapter and case manifest
- [ ] Verify image orientation and annotation semantics
- [ ] Establish a locked evaluation split or evaluation manifest
- [ ] Run reference comparison and analyze failures
- [ ] Review results with a qualified clinical stakeholder

Later versions remain intentionally out of scope. See [[Product Vision]].
