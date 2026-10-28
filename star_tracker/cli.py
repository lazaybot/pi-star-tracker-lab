"""Command-line synthetic star-field experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .attitude import euler_rotation, estimate_rotation, rotation_error_deg, rotation_to_quaternion
from .camera import CameraModel
from .lost_in_space import TriangleCatalog
from .simulation import simulate_observation, synthetic_catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a synthetic star-tracker attitude experiment")
    parser.add_argument("--yaw", type=float, default=8.0)
    parser.add_argument("--pitch", type=float, default=-5.0)
    parser.add_argument("--roll", type=float, default=3.0)
    parser.add_argument("--noise-px", type=float, default=0.25)
    parser.add_argument("--dropout", type=float, default=0.05)
    parser.add_argument("--output", default="outputs/result.json")
    parser.add_argument("--mode", choices=("tracking", "lost-in-space"), default="tracking")
    args = parser.parse_args(argv)
    if args.noise_px < 0 or not 0 <= args.dropout < 1:
        parser.error("noise must be nonnegative and dropout must be in [0, 1)")
    camera = CameraModel(horizontal_fov_deg=90.0 if args.mode == "lost-in-space" else 30.0)
    truth = euler_rotation(args.yaw, args.pitch, args.roll)
    catalog = synthetic_catalog(120 if args.mode == "lost-in-space" else 2000)
    observation = simulate_observation(catalog, truth, camera, args.noise_px, args.dropout)
    if len(observation["catalog_indexes"]) < 3:
        print("ERROR: fewer than three visible associated stars")
        return 2
    if args.mode == "lost-in-space":
        solution = TriangleCatalog(catalog).solve(observation["camera_vectors"])
        estimate = solution["rotation"]
        matched_stars = solution["matched_stars"]
        rejected = solution["rejected_observations"]
        boundary = "Synthetic triangle-pattern acquisition; not real-sky or flight validated."
    else:
        estimate = estimate_rotation(observation["inertial_vectors"], observation["camera_vectors"])
        matched_stars = int(len(observation["catalog_indexes"]))
        rejected = 0
        boundary = "Associated-star tracking mode; not lost-in-space identification."
    result = {
        "mode": f"synthetic-{args.mode}",
        "associated_stars": int(len(observation["catalog_indexes"])),
        "matched_stars": matched_stars,
        "rejected_observations": rejected,
        "input_euler_deg": [args.yaw, args.pitch, args.roll],
        "noise_px": args.noise_px,
        "dropout": args.dropout,
        "estimated_quaternion_wxyz": rotation_to_quaternion(estimate),
        "attitude_error_deg": rotation_error_deg(estimate, truth),
        "claim_boundary": boundary,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
