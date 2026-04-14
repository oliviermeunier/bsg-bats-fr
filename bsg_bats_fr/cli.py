"""Command-line entry point for bsg-bats-fr."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .infer import classify_wav
from .sinp import to_sinp


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bsg-bats-fr",
        description=(
            "Run BSG-BATS on a WAV file and emit a SINP-compatible JSON payload. "
            "Proof-of-concept — not production-ready."
        ),
    )
    parser.add_argument("wav", type=Path, help="Input WAV file (mono, any sample rate — resampled to 384 kHz)")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output JSON file (default: stdout)",
    )
    parser.add_argument(
        "--observer",
        default="unknown",
        help="Observer name / identifier (free text)",
    )
    parser.add_argument(
        "--date",
        default="1970-01-01T00:00:00+00:00",
        help="ISO-8601 date of observation (default: epoch)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=None,
        help="Latitude in WGS84 decimal degrees",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=None,
        help="Longitude in WGS84 decimal degrees",
    )
    parser.add_argument(
        "--device",
        default="AudioMoth",
        help="Recording device (default: AudioMoth)",
    )
    parser.add_argument(
        "--model",
        default="model_v0.21_r1.pt",
        help="BSG-BATS model file name (one of model_v0.21_r1..r6.pt)",
    )
    parser.add_argument(
        "--logit-threshold",
        type=float,
        default=0.0,
        help="Logit threshold for detection (default: 0.0, i.e. p=0.5)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Emit the raw inference result instead of the SINP payload",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    result = classify_wav(
        args.wav,
        model_filename=args.model,
        logit_threshold=args.logit_threshold,
    )

    if args.raw:
        payload = result.to_dict()
    else:
        payload = to_sinp(
            result,
            observer=args.observer,
            date_observation=args.date,
            latitude=args.lat,
            longitude=args.lon,
            device=args.device,
        )

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output is None:
        print(text)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
