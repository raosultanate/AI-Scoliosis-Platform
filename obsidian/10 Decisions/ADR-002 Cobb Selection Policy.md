---
title: ADR-002 Cobb Selection Policy
tags:
  - project/ai-scoliosis
  - adr
status: accepted-for-1a
date: 2026-08-05
---

# ADR-002 — Version 1A Cobb selection policy

## Problem

Landmarks alone do not identify clinician-selected end vertebrae or multiple curves, yet Version 1A
needs a deterministic automatic measurement for geometry validation.

## Alternatives

1. Require explicit upper/lower end-vertebra metadata.
2. Compare every line indiscriminately.
3. Select the maximum acute angle between each upper vertebra's superior endplate and every caudally
   lower vertebra's inferior endplate.

## Decision

Use option 3 for the bootstrap, preserve the exact winning pair in the result, and label the policy
in reports. Reject studies with fewer than two vertebrae or degenerate selected lines.

## Reasoning

This implements a reproducible global single-curve heuristic while respecting anatomical ordering.
It is easy to test and does not pretend to infer curve structure.

## Tradeoffs

It may disagree with a clinician, choose across separate curves, or select an anatomically
inappropriate pair. A scalar reference alone cannot explain such disagreement.

## Future impact

Add an explicit selection strategy interface once the first dataset protocol is known. Clinician
selection and multi-curve strategies should produce the same auditable measurement type or a
versioned collection of it.

