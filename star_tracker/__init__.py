"""Synthetic spacecraft star-tracker laboratory."""

from .attitude import estimate_rotation, rotation_error_deg
from .camera import CameraModel
from .lost_in_space import TriangleCatalog
from .image_processing import extract_centroids, render_star_field
from .simulation import simulate_observation

__all__ = [
    "CameraModel",
    "TriangleCatalog",
    "estimate_rotation",
    "extract_centroids",
    "render_star_field",
    "rotation_error_deg",
    "simulate_observation",
]
