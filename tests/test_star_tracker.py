import unittest

import numpy as np

from star_tracker.attitude import euler_rotation, estimate_rotation, rotation_error_deg
from star_tracker.camera import CameraModel
from star_tracker.lost_in_space import TriangleCatalog
from star_tracker.image_processing import extract_centroids, render_star_field
from star_tracker.simulation import simulate_observation, synthetic_catalog


class StarTrackerTests(unittest.TestCase):
    def test_exact_vector_fit_recovers_rotation(self):
        catalog = synthetic_catalog(20)
        truth = euler_rotation(14, -7, 3)
        camera_vectors = np.einsum("ij,nj->ni", truth, catalog)
        estimate = estimate_rotation(catalog, camera_vectors)
        self.assertLess(rotation_error_deg(estimate, truth), 1e-5)

    def test_projection_round_trip(self):
        camera = CameraModel()
        vectors = np.array([[0.02, 0.01, 1.0], [-0.05, 0.03, 1.0]])
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        pixels, visible = camera.project(vectors)
        recovered = camera.unproject(pixels)
        self.assertTrue(visible.all())
        self.assertTrue(np.allclose(vectors, recovered, atol=1e-10))

    def test_noisy_simulation_stays_below_half_degree(self):
        camera = CameraModel()
        catalog = synthetic_catalog(500)
        truth = euler_rotation(8, -5, 3)
        observation = simulate_observation(catalog, truth, camera, noise_px=0.5, dropout=0.15)
        self.assertGreaterEqual(len(observation["catalog_indexes"]), 3)
        estimate = estimate_rotation(observation["inertial_vectors"], observation["camera_vectors"])
        self.assertLess(rotation_error_deg(estimate, truth), 0.5)

    def test_requires_three_stars(self):
        with self.assertRaisesRegex(ValueError, "three"):
            estimate_rotation(np.eye(3)[:2], np.eye(3)[:2])

    def test_lost_in_space_recovers_unknown_attitude(self):
        camera = CameraModel(horizontal_fov_deg=90)
        catalog = synthetic_catalog(120)
        truth = euler_rotation(18, -9, 6)
        observation = simulate_observation(catalog, truth, camera, noise_px=0.15, dropout=0.05)
        solution = TriangleCatalog(catalog).solve(observation["camera_vectors"])
        self.assertGreaterEqual(solution["matched_stars"], 5)
        self.assertLess(rotation_error_deg(solution["rotation"], truth), 0.15)

    def test_lost_in_space_rejects_false_star(self):
        camera = CameraModel(horizontal_fov_deg=90)
        catalog = synthetic_catalog(120)
        truth = euler_rotation(-12, 4, 9)
        observation = simulate_observation(catalog, truth, camera, noise_px=0.1, dropout=0.0)
        false_star = np.array([[0.0, 0.0, 1.0]])
        observed = np.vstack((observation["camera_vectors"], false_star))
        solution = TriangleCatalog(catalog).solve(observed)
        self.assertGreaterEqual(solution["rejected_observations"], 1)
        self.assertLess(rotation_error_deg(solution["rotation"], truth), 0.15)

    def test_image_centroids_recover_star_positions(self):
        expected = np.array([[40.4, 35.7], [100.2, 70.6], [150.8, 110.3]])
        image = render_star_field(expected, 200, 150, hot_pixels=12)
        measured = extract_centroids(image)
        self.assertEqual(len(measured), len(expected))
        for point in expected:
            self.assertLess(np.min(np.linalg.norm(measured - point, axis=1)), 0.25)

    def test_end_to_end_image_to_unknown_attitude(self):
        camera = CameraModel(width=640, height=480, horizontal_fov_deg=90)
        catalog = synthetic_catalog(120)
        truth = euler_rotation(11, -6, 4)
        observation = simulate_observation(catalog, truth, camera, noise_px=0.0, dropout=0.0)
        image = render_star_field(observation["pixels"], camera.width, camera.height, hot_pixels=10)
        centroids = extract_centroids(image)
        solution = TriangleCatalog(catalog).solve(camera.unproject(centroids))
        self.assertLess(rotation_error_deg(solution["rotation"], truth), 0.15)


if __name__ == "__main__":
    unittest.main()
