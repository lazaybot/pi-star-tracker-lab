"""Triangle-invariant lost-in-space star-pattern matching."""

from __future__ import annotations

from itertools import combinations, permutations

import numpy as np

from .attitude import estimate_rotation


def _angles(vectors: np.ndarray, triangle: tuple[int, int, int]) -> np.ndarray:
    a, b, c = vectors[list(triangle)]
    dots = np.clip([a @ b, a @ c, b @ c], -1.0, 1.0)
    return np.sort(np.arccos(dots))


class TriangleCatalog:
    """Precomputed rotation-invariant triangles for a bright-star catalog."""

    def __init__(self, catalog_vectors: np.ndarray) -> None:
        vectors = np.asarray(catalog_vectors, dtype=float)
        if vectors.ndim != 2 or vectors.shape[1] != 3 or len(vectors) < 4:
            raise ValueError("catalog must contain at least four 3D vectors")
        self.vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        self.triangles = np.asarray(list(combinations(range(len(vectors)), 3)), dtype=np.int32)
        a = self.vectors[self.triangles[:, 0]]
        b = self.vectors[self.triangles[:, 1]]
        c = self.vectors[self.triangles[:, 2]]
        descriptors = np.column_stack((
            np.arccos(np.clip(np.einsum("ij,ij->i", a, b), -1, 1)),
            np.arccos(np.clip(np.einsum("ij,ij->i", a, c), -1, 1)),
            np.arccos(np.clip(np.einsum("ij,ij->i", b, c), -1, 1)),
        ))
        self.descriptors = np.sort(descriptors, axis=1)

    def solve(
        self,
        observed_vectors: np.ndarray,
        descriptor_tolerance_deg: float = 0.08,
        match_tolerance_deg: float = 0.12,
        max_observed: int = 10,
        minimum_matches: int = 5,
    ) -> dict:
        """Estimate attitude without prior attitude or known star associations."""
        observed = np.asarray(observed_vectors, dtype=float)
        if observed.ndim != 2 or observed.shape[1] != 3 or len(observed) < 3:
            raise ValueError("at least three observed 3D vectors are required")
        observed = observed / np.linalg.norm(observed, axis=1, keepdims=True)
        search = observed[:max_observed]
        descriptor_tolerance = np.radians(descriptor_tolerance_deg)
        match_cosine = np.cos(np.radians(match_tolerance_deg))
        best = None

        for observed_triangle in combinations(range(len(search)), 3):
            descriptor = _angles(search, observed_triangle)
            errors = np.max(np.abs(self.descriptors - descriptor), axis=1)
            candidate_rows = np.flatnonzero(errors <= descriptor_tolerance)
            if len(candidate_rows) > 30:
                candidate_rows = candidate_rows[np.argsort(errors[candidate_rows])[:30]]
            observed_triplet = search[list(observed_triangle)]
            for row in candidate_rows:
                catalog_triangle = self.triangles[row]
                for ordered_catalog in permutations(catalog_triangle.tolist()):
                    rotation = estimate_rotation(
                        self.vectors[list(ordered_catalog)], observed_triplet.copy()
                    )
                    rotated_catalog = np.einsum("ij,nj->ni", rotation, self.vectors)
                    similarities = np.einsum("ij,kj->ik", observed, rotated_catalog)
                    nearest_catalog = np.argmax(similarities, axis=1)
                    nearest_scores = similarities[np.arange(len(observed)), nearest_catalog]
                    accepted = nearest_scores >= match_cosine
                    unique_matches = len(set(nearest_catalog[accepted].tolist()))
                    residual = float(np.mean(1 - nearest_scores[accepted])) if accepted.any() else float("inf")
                    score = (unique_matches, -residual)
                    if best is None or score > best[0]:
                        best = (score, rotation, nearest_catalog, accepted, residual)

        if best is None or best[0][0] < minimum_matches:
            raise ValueError("no reliable lost-in-space solution found")
        _, rotation, nearest_catalog, accepted, residual = best
        associations = [
            {"observation": int(index), "catalog": int(nearest_catalog[index])}
            for index in np.flatnonzero(accepted)
        ]
        return {
            "rotation": rotation,
            "associations": associations,
            "matched_stars": len(associations),
            "rejected_observations": int(len(observed) - len(associations)),
            "mean_residual": residual,
        }
