---
title: AI Scoliosis Platform Home
tags:
  - project/ai-scoliosis
  - status/active
status: active
version: 1A
---

# AI Scoliosis Platform

> [!warning]
> Research software only. Nothing in this repository is approved for diagnosis or treatment.

## Resume here

The active milestone is [[Version 1A Roadmap|Version 1A]]. It uses clinician-provided vertebral
landmarks directly; there is ==no machine learning, training, neural network, or PyTorch model==.

The planned product path from this foundation to a FastAPI application with keypoint inference,
clinician correction, deployment, and validation is documented in
[[End-to-End AI Web App Roadmap]].

- Latest session: [[2026-08-05 - Version 1A Bootstrap]]
- Current roadmap: [[Version 1A Roadmap]]
- End-to-end AI plan: [[End-to-End AI Web App Roadmap]]
- Architecture: [[Version 1A Architecture]]
- Active decisions: [[ADR-001 Canonical Landmark Domain Model]], [[ADR-002 Cobb Selection Policy]]
- Dataset state: [[Dataset Integration Status]]
- Work queue: [[Version 1A TODO]]
- Medical context: [[Cobb Angle Basics]]

## Current state

A runnable single-study pipeline loads common raster images and JSON/CSV/TXT annotations, converts
normalized coordinates to pixels, draws all landmarks and endplates, calculates a single maximum
Cobb angle, compares it to an optional reference, and writes annotated PNG plus JSON/Markdown
reports. A deterministic 30° synthetic case and automated tests are included.

## Immediate next action

Select the first public dataset and document its license, download method, image format, exact point
ordering, coordinate system, anatomical labeling, and reference-angle protocol before writing its
adapter.
