"""Generate calibrated synthetic star centroids with controlled noise."""

from __future__ import annotations

import numpy as np

from .camera import CameraModel


def synthetic_catalog(count: int = 250, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vectors = rng.normal(size=(count, 3))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def simulate_observation(
    catalog: np.ndarray,
    rotation: np.ndarray,
    camera: CameraModel,
    noise_px: float = 0.25,
    dropout: float = 0.05,
    seed: int = 11,
) -> dict:
    rng = np.random.default_rng(seed)
    camera_vectors = np.einsum("ij,nj->ni", rotation, catalog)
    pixels, visible = camera.project(camera_vectors)
    indexes = np.flatnonzero(visible)
    if len(indexes):
        indexes = indexes[rng.random(len(indexes)) >= dropout]
    noisy_pixels = pixels[indexes] + rng.normal(0, noise_px, size=(len(indexes), 2))
    return {
        "catalog_indexes": indexes,
        "inertial_vectors": catalog[indexes],
        "camera_vectors": camera.unproject(noisy_pixels),
        "pixels": noisy_pixels,
    }
