"""Generate the README visual from the actual synthetic image pipeline."""

from pathlib import Path

import matplotlib.pyplot as plt

from star_tracker.attitude import euler_rotation
from star_tracker.camera import CameraModel
from star_tracker.image_processing import extract_centroids, render_star_field
from star_tracker.lost_in_space import TriangleCatalog
from star_tracker.simulation import simulate_observation, synthetic_catalog


def main() -> None:
    camera = CameraModel(width=640, height=480, horizontal_fov_deg=90)
    catalog = synthetic_catalog(120)
    truth = euler_rotation(18, -9, 6)
    observation = simulate_observation(catalog, truth, camera, noise_px=0.15, dropout=0.05)
    image = render_star_field(observation["pixels"], camera.width, camera.height, hot_pixels=10)
    centroids = extract_centroids(image)
    solution = TriangleCatalog(catalog).solve(camera.unproject(centroids))

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5), facecolor="#07101f")
    for axis in axes:
        axis.set_facecolor("#07101f")
    axes[0].imshow(image, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title("1. Synthetic camera frame", color="white")
    axes[0].axis("off")
    axes[1].imshow(image, cmap="gray", vmin=0, vmax=255)
    axes[1].scatter(centroids[:, 0], centroids[:, 1], s=90, facecolors="none", edgecolors="#39e6ff", linewidths=1.5)
    axes[1].set_title("2. Detected stars and solved orientation", color="white")
    axes[1].axis("off")
    axes[1].text(
        0.02, 0.04,
        f"matched stars: {solution['matched_stars']}\nrejected false points: {solution['rejected_observations']}",
        transform=axes[1].transAxes,
        color="white",
        fontsize=10,
        bbox={"facecolor": "#07101f", "alpha": 0.85, "edgecolor": "#39e6ff"},
    )
    figure.suptitle("Lost-in-space matching: identify the sky pattern without a starting direction", color="white", fontsize=14)
    asset_dir = Path(__file__).resolve().parents[1] / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(asset_dir / "star-tracker-pipeline.png", dpi=160, bbox_inches="tight", facecolor=figure.get_facecolor())
    figure.savefig(asset_dir / "star-tracker-pipeline.svg", bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)


if __name__ == "__main__":
    main()
