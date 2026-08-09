---
title: 2026-08-08 - Web MVP and Docker
tags:
  - project/ai-scoliosis
  - journal
  - web-app
  - docker
status: complete
date: 2026-08-08
---

# Web MVP and Docker

## Completed

- Added a FastAPI composition layer around the existing `analyze_study()` service.
- Added health, capability, and deterministic synthetic-analysis endpoints.
- Built a responsive website that explains Cobb angles in plain language.
- Added local PNG/JPEG selection and preview without transmitting the selected image.
- Added a safe 30° synthetic workflow with T4/T12 and an annotated result.
- Added API tests and updated packaging so static web assets ship in the wheel.
- Added a non-root multi-stage Docker image and hardened Docker Compose service.
- Verified the rebuilt container as healthy and exercised the sample workflow in Chrome.

## Safety boundary

> [!warning]
> Real X-rays are not uploaded or analyzed. The interface reports that automated landmark
> detection is unavailable and refuses to fabricate a Cobb angle.

## Next milestone

Define the validated real-image upload and landmark contract, select the first legally usable
dataset, and train or fine-tune a vertebral keypoint detector that produces the canonical
`StudyLandmarks` representation. See [[End-to-End AI Web App Roadmap]].

## Related

- [[Project Home]]
- [[Version 1A Roadmap]]
- [[Version 1A Architecture]]
- [[ADR-001 Canonical Landmark Domain Model]]
