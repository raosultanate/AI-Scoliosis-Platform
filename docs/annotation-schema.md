# Landmark annotation schema

Version 1A uses four corners per vertebral body in image coordinates. The canonical point order is
top-left, top-right, bottom-left, bottom-right. “Left” and “right” refer to positions as displayed
in the image array, not anatomical laterality.

## Canonical JSON

```json
{
  "schema_version": "1.0",
  "study_id": "case-001",
  "coordinate_space": "normalized",
  "reference_cobb_angle_degrees": 31.5,
  "vertebrae": [
    {
      "label": "T4",
      "ordinal": 0,
      "top_left": [0.41, 0.20],
      "top_right": [0.59, 0.22],
      "bottom_left": [0.41, 0.25],
      "bottom_right": [0.59, 0.27]
    }
  ]
}
```

- `schema_version`: reserved for evolution; current writer uses `1.0`.
- `study_id`: stable de-identified case identifier.
- `coordinate_space`: `pixel`, `normalized`, or `auto`. JSON defaults to `auto` if omitted.
- `reference_cobb_angle_degrees`: optional dataset reference, not training data in Version 1A.
- `ordinal`: unique integer cranio-caudal order; it is authoritative for candidate selection.
- Points accept either `[x, y]` or `{ "x": x, "y": y }`.

## CSV

One row represents one vertebra. Required columns are `label`, `ordinal`, and `{corner}_{axis}` for
each of `top_left`, `top_right`, `bottom_left`, and `bottom_right`. CSV has no standard field for a
reference angle; convert to canonical JSON when reference validation is required.

## Flat text

Each non-comment line contains `x y` (comma or whitespace separated). Every consecutive four lines
form one vertebra in canonical corner order. Labels become `V01`, `V02`, and so on. Use only when
the source format has a guaranteed point order.

## Assumptions and limits

- The image has already been oriented consistently and is not mirrored unexpectedly.
- All annotations describe the same image dimensions supplied to the pipeline.
- Normalized coordinates are relative to full image width and height.
- The adapter does not infer anatomy from points.
- Version 1A does not parse DICOM metadata, identify multiple curves, or adjudicate annotators.

