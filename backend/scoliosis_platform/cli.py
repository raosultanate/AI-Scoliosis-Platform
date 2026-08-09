"""Command-line entrypoint for reproducible Version 1A single-study analysis."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from scoliosis_platform.config import load_config
from scoliosis_platform.pipeline import analyze_study


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser without reading process-global arguments."""

    parser = argparse.ArgumentParser(prog="scoliosis-v1a")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Analyze one image and annotation file")
    analyze.add_argument("--image", required=True, type=Path, help="Path to a raster X-ray image")
    analyze.add_argument(
        "--landmarks", required=True, type=Path, help="Path to JSON/CSV/TXT landmarks"
    )
    analyze.add_argument(
        "--output-dir", required=True, type=Path, help="Directory for generated artifacts"
    )
    analyze.add_argument("--config", type=Path, default=None, help="YAML configuration path")
    analyze.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help="Override reference comparison tolerance in degrees",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested command and return a process exit code."""

    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    if args.tolerance is not None:
        from dataclasses import replace

        config = replace(config, reference_tolerance_degrees=args.tolerance)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    artifacts = analyze_study(args.image, args.landmarks, args.output_dir, config)
    print(f"Cobb angle: {artifacts.measurement.angle_degrees:.2f}°")
    print(f"Annotated image: {artifacts.annotated_image_path}")
    print(f"JSON report: {artifacts.json_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
