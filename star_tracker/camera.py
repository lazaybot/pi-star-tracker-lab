"""Pinhole camera projection and inverse projection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CameraModel:
    width: int = 1280
    height: int = 960
    horizontal_fov_deg: float = 30.0

    @property
    def focal_px(self) -> float:
        return self.width / (2 * np.tan(np.radians(self.horizontal_fov_deg) / 2))

    def project(self, vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        vectors = np.asarray(vectors, dtype=float)
        visible = vectors[:, 2] > 0
        x = self.focal_px * vectors[:, 0] / np.where(visible, vectors[:, 2], 1) + self.width / 2
        y = self.height / 2 - self.focal_px * vectors[:, 1] / np.where(visible, vectors[:, 2], 1)
        pixels = np.column_stack((x, y))
        visible &= (x >= 0) & (x < self.width) & (y >= 0) & (y < self.height)
        return pixels, visible

    def unproject(self, pixels: np.ndarray) -> np.ndarray:
        pixels = np.asarray(pixels, dtype=float)
        vectors = np.column_stack((
            (pixels[:, 0] - self.width / 2) / self.focal_px,
            -(pixels[:, 1] - self.height / 2) / self.focal_px,
            np.ones(len(pixels)),
        ))
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
