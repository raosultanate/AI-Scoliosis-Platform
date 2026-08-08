---
title: ADR-001 Canonical Landmark Domain Model
tags:
  - project/ai-scoliosis
  - adr
status: accepted
date: 2026-08-05
---

# ADR-001 — Canonical landmark domain model

## Problem

Public datasets and future AI detectors can expose incompatible file layouts. Geometry must not
depend on any one format.

## Alternatives

1. Pass raw dictionaries and arrays through the whole pipeline.
2. Make geometry understand every dataset format.
3. Translate external inputs into immutable typed domain objects at the boundary.

## Decision

Choose option 3. `StudyLandmarks` contains ordered `VertebraLandmarks`; every vertebra carries four
named corners. Normalized input is converted once to pixel space before geometry.

## Reasoning

Named, typed inputs make point semantics reviewable, localize parsing risk, support deterministic
tests, and give a future AI detector a stable output contract.

## Tradeoffs

Adapters require deliberate mapping work, and four-corner landmarks may not represent every future
task. The explicit conversion is worthwhile because format ambiguity is otherwise hidden.

## Future impact

ML inference, API handlers, and database records should translate to or from this contract rather
than bypass it. Schema evolution must be versioned when richer landmarks are required.

