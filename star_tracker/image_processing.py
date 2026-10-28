"""Synthetic grayscale sensor frames and dependency-free centroid extraction."""

from __future__ import annotations

from collections import deque

import numpy as np


def render_star_field(
    pixels: np.ndarray,
    width: int,
    height: int,
    sigma_px: float = 1.2,
    background: float = 12.0,
    read_noise: float = 1.5,
    hot_pixels: int = 8,
    seed: int = 21,
) -> np.ndarray:
    """Render Gaussian star point-spread functions into an 8-bit sensor frame."""
    if sigma_px <= 0 or width <= 0 or height <= 0:
        raise ValueError("image dimensions and point-spread sigma must be positive")
    rng = np.random.default_rng(seed)
    image = rng.normal(background, read_noise, size=(height, width))
    radius = max(2, int(np.ceil(4 * sigma_px)))
    for index, (x, y) in enumerate(np.asarray(pixels, dtype=float)):
        amplitude = 150.0 + 90.0 * ((index * 0.61803398875) % 1.0)
        x0, y0 = int(round(x)), int(round(y))
        left, right = max(0, x0 - radius), min(width, x0 + radius + 1)
        top, bottom = max(0, y0 - radius), min(height, y0 + radius + 1)
        if left >= right or top >= bottom:
            continue
        yy, xx = np.mgrid[top:bottom, left:right]
        image[top:bottom, left:right] += amplitude * np.exp(
            -((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma_px**2)
        )
    if hot_pixels:
        ys = rng.integers(0, height, size=hot_pixels)
        xs = rng.integers(0, width, size=hot_pixels)
        image[ys, xs] = 255
    return np.clip(image, 0, 255).astype(np.uint8)


def extract_centroids(
    image: np.ndarray,
    threshold_sigma: float = 6.0,
    min_area: int = 3,
    max_area: int = 150,
) -> np.ndarray:
    """Return intensity-weighted [x, y] centroids of connected bright regions."""
    frame = np.asarray(image)
    if frame.ndim != 2:
        raise ValueError("centroid extraction requires a grayscale image")
    background = float(np.median(frame))
    mad = float(np.median(np.abs(frame.astype(float) - background)))
    noise = max(1.0, 1.4826 * mad)
    mask = frame > background + threshold_sigma * noise
    visited = np.zeros(mask.shape, dtype=bool)
    centroids: list[tuple[float, float]] = []
    height, width = mask.shape
    for start_y, start_x in zip(*np.nonzero(mask)):
        if visited[start_y, start_x]:
            continue
        queue = deque([(int(start_y), int(start_x))])
        visited[start_y, start_x] = True
        component: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            component.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if (
                        0 <= ny < height
                        and 0 <= nx < width
                        and not visited[ny, nx]
                        and mask[ny, nx]
                    ):
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        if not min_area <= len(component) <= max_area:
            continue
        ys = np.array([point[0] for point in component])
        xs = np.array([point[1] for point in component])
        weights = np.maximum(frame[ys, xs].astype(float) - background, 1.0)
        centroids.append((float(np.average(xs, weights=weights)), float(np.average(ys, weights=weights))))
    return np.asarray(centroids, dtype=float).reshape(-1, 2)
