---
title: Line Geometry for Endplates
tags:
  - learning/geometry
  - project/ai-scoliosis
---

# Line geometry for endplates

For endpoints $(x_1, y_1)$ and $(x_2, y_2)$, orientation is:

$$
\theta = \operatorname{atan2}(y_2-y_1, x_2-x_1)
$$

Image coordinates increase downward, so positive visual slopes produce positive angles in the
implemented convention. Because an endplate is an undirected line, orientations that differ by
180° are equivalent. Normalize to $[-90°, 90°)$, calculate the absolute difference modulo 180°,
and select the smaller supplementary angle:

$$
\alpha = \min(\Delta, 180°-\Delta)
$$

The result is in $[0°, 90°]$. A zero-length segment has undefined orientation and must fail rather
than silently return zero. See [[Cobb Angle Basics]].

