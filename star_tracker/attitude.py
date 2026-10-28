"""Three-axis attitude estimation from associated inertial/body star vectors."""

from __future__ import annotations

import numpy as np


def euler_rotation(yaw_deg: float, pitch_deg: float, roll_deg: float) -> np.ndarray:
    """Return inertial-to-camera rotation using Z-Y-X Euler angles."""
    yaw, pitch, roll = np.radians([yaw_deg, pitch_deg, roll_deg])
    cz, sz = np.cos(yaw), np.sin(yaw)
    cy, sy = np.cos(pitch), np.sin(pitch)
    cx, sx = np.cos(roll), np.sin(roll)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    return rz @ ry @ rx


def estimate_rotation(inertial: np.ndarray, camera: np.ndarray) -> np.ndarray:
    """Solve Wahba's problem with an SVD/Kabsch rotation fit."""
    inertial = np.asarray(inertial, dtype=float)
    camera = np.asarray(camera, dtype=float)
    if inertial.shape != camera.shape or inertial.ndim != 2 or inertial.shape[1] != 3:
        raise ValueError("inertial and camera vectors must both have shape (N, 3)")
    if len(inertial) < 3:
        raise ValueError("at least three associated stars are required")
    inertial /= np.linalg.norm(inertial, axis=1, keepdims=True)
    camera /= np.linalg.norm(camera, axis=1, keepdims=True)
    u, _, vt = np.linalg.svd(camera.T @ inertial)
    correction = np.eye(3)
    correction[-1, -1] = np.linalg.det(u @ vt)
    return u @ correction @ vt


def rotation_error_deg(estimate: np.ndarray, truth: np.ndarray) -> float:
    delta = estimate @ truth.T
    cosine = np.clip((np.trace(delta) - 1) / 2, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def rotation_to_quaternion(rotation: np.ndarray) -> list[float]:
    """Convert a rotation matrix to normalized [w, x, y, z]."""
    matrix = np.asarray(rotation, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(
        np.array([
            [matrix[0, 0] - matrix[1, 1] - matrix[2, 2], matrix[1, 0] + matrix[0, 1], matrix[2, 0] + matrix[0, 2], matrix[1, 2] - matrix[2, 1]],
            [matrix[1, 0] + matrix[0, 1], matrix[1, 1] - matrix[0, 0] - matrix[2, 2], matrix[2, 1] + matrix[1, 2], matrix[2, 0] - matrix[0, 2]],
            [matrix[2, 0] + matrix[0, 2], matrix[2, 1] + matrix[1, 2], matrix[2, 2] - matrix[0, 0] - matrix[1, 1], matrix[0, 1] - matrix[1, 0]],
            [matrix[1, 2] - matrix[2, 1], matrix[2, 0] - matrix[0, 2], matrix[0, 1] - matrix[1, 0], matrix.trace()],
        ]) / 3.0
    )
    xyzw = eigenvectors[:, np.argmax(eigenvalues)]
    quaternion = np.array([xyzw[3], xyzw[0], xyzw[1], xyzw[2]])
    if quaternion[0] < 0:
        quaternion *= -1
    return quaternion.tolist()
