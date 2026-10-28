"""Monte Carlo acquisition benchmark across centroid noise and star dropout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .attitude import euler_rotation, rotation_error_deg
from .camera import CameraModel
from .lost_in_space import TriangleCatalog
from .simulation import simulate_observation, synthetic_catalog


def run_benchmark(trials: int = 20) -> dict:
    camera = CameraModel(horizontal_fov_deg=90)
    catalog = synthetic_catalog(120)
    matcher = TriangleCatalog(catalog)
    cases = []
    for noise_px, dropout in ((0.05, 0.0), (0.15, 0.10), (0.30, 0.20)):
        errors, failures = [], 0
        for trial in range(trials):
            truth = euler_rotation(3 + trial * 2.1, -12 + trial * 0.7, 4 - trial * 0.3)
            observation = simulate_observation(
                catalog, truth, camera, noise_px, dropout, seed=1000 + trial
            )
            try:
                solution = matcher.solve(observation["camera_vectors"])
                errors.append(rotation_error_deg(solution["rotation"], truth))
            except ValueError:
                failures += 1
        cases.append({
            "noise_px": noise_px,
            "dropout": dropout,
            "trials": trials,
            "successes": len(errors),
            "failures": failures,
            "median_error_deg": float(np.median(errors)) if errors else None,
            "p95_error_deg": float(np.percentile(errors, 95)) if errors else None,
        })
    return {"mode": "synthetic-monte-carlo", "cases": cases}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--output", default="outputs/benchmark.json")
    args = parser.parse_args(argv)
    if args.trials < 1:
        parser.error("trials must be positive")
    result = run_benchmark(args.trials)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
